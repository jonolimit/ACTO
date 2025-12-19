from __future__ import annotations

import uuid

from fastapi import Depends, FastAPI, HTTPException, Request, Response
from fastapi.middleware.cors import CORSMiddleware

from acto import __version__
from acto.access import SolanaTokenGate
from acto.config import Settings
from acto.errors import AccessError, ProofError, RegistryError
from acto.metrics import MetricsRegistry
from acto.proof import verify_proof
from acto.registry import ProofRegistry
from acto.reputation import ReputationScorer
from acto.security import (
    AuditAction,
    AuditLogger,
    JWTManager,
    OAuth2TokenResponse,
    Permission,
    RBACManager,
    TokenBucketRateLimiter,
    create_jwt_dependency_optional,
    get_current_user_optional,
    require_api_key,
)
from acto.security.api_key_store import ApiKeyStore
from acto.security.audit import FileAuditBackend, MemoryAuditBackend

from .schemas import (
    AccessCheckRequest,
    AccessCheckResponse,
    ApiKeyCreateRequest,
    ApiKeyCreateResponse,
    ApiKeyDeleteResponse,
    ApiKeyListResponse,
    ProofSubmitRequest,
    ProofSubmitResponse,
    VerifyRequest,
    VerifyResponse,
)

settings = Settings()


def create_app() -> FastAPI:
    app = FastAPI(title="ACTO Verification API", version=__version__)

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    registry = ProofRegistry(settings)
    metrics = MetricsRegistry()
    scorer = ReputationScorer(settings=settings)

    # Security components initialization
    # Use database-backed API key store
    api_key_store = ApiKeyStore(settings)
    limiter = TokenBucketRateLimiter.create(rps=settings.rate_limit_rps, burst=settings.rate_limit_burst)

    # JWT/OAuth2
    jwt_manager: JWTManager | None = None
    if settings.jwt_enabled and settings.jwt_secret_key:
        jwt_manager = JWTManager(
            secret_key=settings.jwt_secret_key,
            algorithm=settings.jwt_algorithm,
            access_token_expire_minutes=settings.jwt_access_token_expire_minutes,
            refresh_token_expire_days=settings.jwt_refresh_token_expire_days,
        )

    # RBAC
    rbac_manager = RBACManager() if settings.rbac_enabled else None

    # Audit logging
    audit_logger: AuditLogger | None = None
    if settings.audit_log_enabled:
        if settings.audit_log_backend == "file":
            backend = FileAuditBackend(settings.audit_log_file)
        else:
            backend = MemoryAuditBackend()
        audit_logger = AuditLogger(backend=backend)

    # Encryption at rest, TLS, Secrets management, and PII masking are available via settings
    # but not actively used in current implementation
    # They can be enabled when needed in the future

    @app.middleware("http")
    async def request_id_middleware(request: Request, call_next):
        request_id = request.headers.get("X-Request-ID") or str(uuid.uuid4())
        request.state.request_id = request_id
        response: Response = await call_next(request)
        response.headers["X-Request-ID"] = request_id
        return response

    @app.middleware("http")
    async def rate_limit_middleware(request: Request, call_next):
        if not settings.rate_limit_enabled:
            return await call_next(request)

        client = request.headers.get("X-Forwarded-For") or (request.client.host if request.client else "unknown")
        key = f"{client}:{request.url.path}"
        try:
            limiter.check(key)
        except AccessError as e:
            raise HTTPException(status_code=429, detail=str(e)) from e
        return await call_next(request)

    @app.middleware("http")
    async def audit_middleware(request: Request, call_next):
        """Middleware for audit logging."""
        if not audit_logger:
            return await call_next(request)

        user_id = getattr(request.state, "user_id", None)
        ip_address = request.headers.get("X-Forwarded-For") or (request.client.host if request.client else None)
        user_agent = request.headers.get("User-Agent")

        try:
            response = await call_next(request)
            if response.status_code < 400:
                audit_logger.log_success(
                    AuditAction.ADMIN_ACTION,
                    user_id=user_id,
                    ip_address=ip_address,
                    user_agent=user_agent,
                    request_id=request.state.request_id,
                    details={"method": request.method, "path": request.url.path},
                )
            else:
                audit_logger.log_failure(
                    AuditAction.ADMIN_ACTION,
                    error_message=f"HTTP {response.status_code}",
                    user_id=user_id,
                    ip_address=ip_address,
                    user_agent=user_agent,
                    request_id=request.state.request_id,
                    details={"method": request.method, "path": request.url.path},
                )
            return response
        except Exception as e:
            audit_logger.log_failure(
                AuditAction.ADMIN_ACTION,
                error_message=str(e),
                user_id=user_id,
                ip_address=ip_address,
                user_agent=user_agent,
                request_id=request.state.request_id,
                details={"method": request.method, "path": request.url.path},
            )
            raise

    def auth_dependency():
        """Create authentication dependency - always require Bearer token."""
        return Depends(require_api_key(api_key_store))

    @app.get("/health")
    def health() -> dict:
        metrics.inc("acto.health.calls")
        return {"ok": True, "service": "acto", "version": __version__}

    @app.get("/metrics")
    def prometheus_metrics() -> Response:
        return Response(content=metrics.render_prometheus(), media_type="text/plain; version=0.0.4")

    @app.get("/v1/proofs", dependencies=[auth_dependency()])
    def list_proofs(limit: int = 50) -> dict:
        metrics.inc("acto.proofs.list")
        return {"items": registry.list(limit=limit)}

    @app.post("/v1/proofs", response_model=ProofSubmitResponse, dependencies=[auth_dependency()])
    def submit(
        req: ProofSubmitRequest,
        request: Request,
    ) -> ProofSubmitResponse:
        # Get current user from request state (set by JWT middleware if authenticated)
        current_user = get_current_user_optional(request)
        try:
            # RBAC check
            if rbac_manager and current_user:
                rbac_manager.require_permission(current_user.get("roles", []), Permission.PROOF_WRITE)

            verify_proof(req.envelope)
            proof_id = registry.upsert(req.envelope)
            metrics.inc("acto.proofs.submit")

            # Audit log
            if audit_logger:
                audit_logger.log_success(
                    AuditAction.PROOF_CREATE,
                    user_id=current_user.get("user_id") if current_user else None,
                    resource_type="proof",
                    resource_id=proof_id,
                    request_id=getattr(request.state, "request_id", None),
                )

            return ProofSubmitResponse(proof_id=proof_id)
        except ProofError as e:
            metrics.inc("acto.proofs.submit.invalid")
            if audit_logger:
                audit_logger.log_failure(
                    AuditAction.PROOF_CREATE,
                    error_message=str(e),
                    user_id=current_user.get("user_id") if current_user else None,
                    request_id=getattr(request.state, "request_id", None),
                )
            raise HTTPException(status_code=400, detail=str(e)) from e
        except RegistryError as e:
            if audit_logger:
                audit_logger.log_failure(
                    AuditAction.PROOF_CREATE,
                    error_message=str(e),
                    user_id=current_user.get("user_id") if current_user else None,
                    request_id=getattr(request.state, "request_id", None),
                )
            raise HTTPException(status_code=500, detail=str(e)) from e

    @app.get("/v1/proofs/{proof_id}", dependencies=[auth_dependency()])
    def get_proof(
        proof_id: str,
        request: Request,
    ) -> dict:
        # Get current user from request state (set by JWT middleware if authenticated)
        current_user = get_current_user_optional(request)
        try:
            # RBAC check
            if rbac_manager and current_user:
                rbac_manager.require_permission(current_user.get("roles", []), Permission.PROOF_READ)

            metrics.inc("acto.proofs.get")
            env = registry.get(proof_id)

            # Audit log
            if audit_logger:
                audit_logger.log_success(
                    AuditAction.PROOF_READ,
                    user_id=current_user.get("user_id") if current_user else None,
                    resource_type="proof",
                    resource_id=proof_id,
                    request_id=getattr(request.state, "request_id", None),
                )

            return {"proof_id": proof_id, "envelope": env.model_dump()}
        except RegistryError as e:
            if audit_logger:
                audit_logger.log_failure(
                    AuditAction.PROOF_READ,
                    error_message=str(e),
                    user_id=current_user.get("user_id") if current_user else None,
                    resource_id=proof_id,
                    request_id=getattr(request.state, "request_id", None),
                )
            raise HTTPException(status_code=404, detail=str(e)) from e

    @app.post("/v1/verify", response_model=VerifyResponse, dependencies=[auth_dependency()])
    def verify(
        req: VerifyRequest,
        request: Request,
    ) -> VerifyResponse:
        # Get current user from request state (set by JWT middleware if authenticated)
        current_user = get_current_user_optional(request)
        try:
            verify_proof(req.envelope)
            metrics.inc("acto.verify.ok")

            # Audit log
            if audit_logger:
                audit_logger.log_success(
                    AuditAction.PROOF_VERIFY,
                    user_id=current_user.get("user_id") if current_user else None,
                    request_id=getattr(request.state, "request_id", None),
                )

            return VerifyResponse(valid=True, reason="ok")
        except ProofError as e:
            metrics.inc("acto.verify.fail")
            if audit_logger:
                audit_logger.log_failure(
                    AuditAction.PROOF_VERIFY,
                    error_message=str(e),
                    user_id=current_user.get("user_id") if current_user else None,
                    request_id=getattr(request.state, "request_id", None),
                )
            return VerifyResponse(valid=False, reason=str(e))

    @app.post("/v1/score", dependencies=[auth_dependency()])
    def score(
        req: VerifyRequest,
        request: Request,
    ) -> dict:
        try:
            verify_proof(req.envelope)
            result = scorer.score(req.envelope)
            metrics.inc("acto.score.ok")
            return {"score": result.score, "reasons": result.reasons}
        except ProofError as e:
            metrics.inc("acto.score.fail")
            raise HTTPException(status_code=400, detail=str(e)) from e

    # OAuth2/JWT endpoints
    if jwt_manager:

        @app.post("/v1/auth/token")
        def create_token(username: str, password: str, roles: list[str] | None = None) -> dict:
            """Create access token (simplified - in production, verify credentials properly)."""
            # In production, verify username/password against user database
            access_token = jwt_manager.create_access_token(subject=username, roles=roles or ["user"])
            refresh_token = jwt_manager.create_refresh_token(subject=username)
            token_response = OAuth2TokenResponse(
                access_token=access_token,
                refresh_token=refresh_token,
                expires_in=settings.jwt_access_token_expire_minutes * 60,
            )
            return token_response.to_dict()

        @app.post("/v1/auth/refresh")
        def refresh_token(refresh_token: str) -> dict:
            """Refresh access token."""
            new_access_token = jwt_manager.refresh_access_token(refresh_token)
            token_response = OAuth2TokenResponse(
                access_token=new_access_token,
                expires_in=settings.jwt_access_token_expire_minutes * 60,
            )
            return token_response.to_dict()

    @app.post("/v1/access/check", response_model=AccessCheckResponse, dependencies=[auth_dependency()])
    def access_check(req: AccessCheckRequest) -> AccessCheckResponse:
        try:
            gate = SolanaTokenGate(rpc_url=req.rpc_url)
            decision = gate.decide(owner=req.owner, mint=req.mint, minimum=req.minimum)
            metrics.inc("acto.access.check")
            return AccessCheckResponse(**decision.model_dump())
        except AccessError as e:
            raise HTTPException(status_code=400, detail=str(e)) from e

    # API Key Management Endpoints
    # Allow creating first key without authentication, but require auth for listing/deleting
    @app.post("/v1/keys", response_model=ApiKeyCreateResponse)
    def create_api_key(req: ApiKeyCreateRequest, request: Request) -> ApiKeyCreateResponse:
        """Create a new API key."""
        try:
            # Get client identifier from request (IP or user agent)
            client_id = request.headers.get("X-Forwarded-For") or (
                request.client.host if request.client else "unknown"
            )
            result = api_key_store.create_key(name=req.name, created_by=client_id)
            metrics.inc("acto.keys.create")
            return ApiKeyCreateResponse(**result)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to create API key: {str(e)}") from e

    @app.get("/v1/keys", response_model=ApiKeyListResponse, dependencies=[auth_dependency()])
    def list_api_keys() -> ApiKeyListResponse:
        """List all API keys (without the actual key values)."""
        try:
            keys = api_key_store.list_keys(include_inactive=False)
            metrics.inc("acto.keys.list")
            return ApiKeyListResponse(keys=keys)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to list API keys: {str(e)}") from e

    @app.delete("/v1/keys/{key_id}", response_model=ApiKeyDeleteResponse, dependencies=[auth_dependency()])
    def delete_api_key(key_id: str) -> ApiKeyDeleteResponse:
        """Delete (deactivate) an API key."""
        try:
            success = api_key_store.delete_key(key_id)
            if not success:
                raise HTTPException(status_code=404, detail="API key not found")
            metrics.inc("acto.keys.delete")
            return ApiKeyDeleteResponse(success=True, key_id=key_id)
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to delete API key: {str(e)}") from e

    # Dashboard endpoint - serve static HTML
    @app.get("/dashboard")
    def dashboard() -> Response:
        """Serve the API key management dashboard."""
        html_content = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>ACTO API Key Management</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }
        
        .container {
            max-width: 1200px;
            margin: 0 auto;
        }
        
        .header {
            background: white;
            border-radius: 12px;
            padding: 30px;
            margin-bottom: 30px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.2);
        }
        
        .header h1 {
            color: #333;
            margin-bottom: 10px;
        }
        
        .header p {
            color: #666;
            font-size: 14px;
        }
        
        .card {
            background: white;
            border-radius: 12px;
            padding: 30px;
            margin-bottom: 20px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.2);
        }
        
        .form-group {
            margin-bottom: 20px;
        }
        
        .form-group label {
            display: block;
            margin-bottom: 8px;
            color: #333;
            font-weight: 500;
        }
        
        .form-group input {
            width: 100%;
            padding: 12px;
            border: 2px solid #e0e0e0;
            border-radius: 8px;
            font-size: 14px;
            transition: border-color 0.3s;
        }
        
        .form-group input:focus {
            outline: none;
            border-color: #667eea;
        }
        
        .btn {
            padding: 12px 24px;
            border: none;
            border-radius: 8px;
            font-size: 14px;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.3s;
        }
        
        .btn-primary {
            background: #667eea;
            color: white;
        }
        
        .btn-primary:hover {
            background: #5568d3;
            transform: translateY(-2px);
            box-shadow: 0 5px 15px rgba(102, 126, 234, 0.4);
        }
        
        .btn-danger {
            background: #ef4444;
            color: white;
        }
        
        .btn-danger:hover {
            background: #dc2626;
        }
        
        .btn:disabled {
            opacity: 0.6;
            cursor: not-allowed;
        }
        
        .keys-list {
            margin-top: 20px;
        }
        
        .key-item {
            background: #f8f9fa;
            border: 2px solid #e0e0e0;
            border-radius: 8px;
            padding: 20px;
            margin-bottom: 15px;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        
        .key-info {
            flex: 1;
        }
        
        .key-info h3 {
            color: #333;
            margin-bottom: 8px;
            font-size: 16px;
        }
        
        .key-info p {
            color: #666;
            font-size: 12px;
            margin: 4px 0;
        }
        
        .key-actions {
            display: flex;
            gap: 10px;
        }
        
        .alert {
            padding: 15px;
            border-radius: 8px;
            margin-bottom: 20px;
            display: none;
        }
        
        .alert-success {
            background: #d1fae5;
            color: #065f46;
            border: 1px solid #6ee7b7;
        }
        
        .alert-error {
            background: #fee2e2;
            color: #991b1b;
            border: 1px solid #fca5a5;
        }
        
        .alert-info {
            background: #dbeafe;
            color: #1e40af;
            border: 1px solid #93c5fd;
        }
        
        .alert.show {
            display: block;
        }
        
        .new-key-display {
            background: #f0f9ff;
            border: 2px solid #3b82f6;
            border-radius: 8px;
            padding: 20px;
            margin-top: 20px;
            display: none;
        }
        
        .new-key-display.show {
            display: block;
        }
        
        .new-key-display h3 {
            color: #1e40af;
            margin-bottom: 15px;
        }
        
        .key-value {
            background: white;
            border: 2px solid #3b82f6;
            border-radius: 8px;
            padding: 15px;
            font-family: 'Courier New', monospace;
            font-size: 14px;
            word-break: break-all;
            margin-bottom: 15px;
            color: #1e40af;
            font-weight: 600;
        }
        
        .warning {
            background: #fef3c7;
            border-left: 4px solid #f59e0b;
            padding: 15px;
            border-radius: 4px;
            margin-top: 15px;
            color: #92400e;
            font-size: 13px;
        }
        
        .loading {
            display: inline-block;
            width: 16px;
            height: 16px;
            border: 2px solid #f3f3f3;
            border-top: 2px solid #667eea;
            border-radius: 50%;
            animation: spin 1s linear infinite;
            margin-left: 10px;
        }
        
        @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }
        
        .empty-state {
            text-align: center;
            padding: 40px;
            color: #999;
        }
        
        .empty-state p {
            margin-top: 10px;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🔑 ACTO API Key Management</h1>
            <p>Create and manage API keys for accessing the ACTO Verification API</p>
        </div>
        
        <div id="alert" class="alert"></div>
        
        <div class="card">
            <h2 style="margin-bottom: 20px; color: #333;">Create New API Key</h2>
            <form id="createKeyForm">
                <div class="form-group">
                    <label for="keyName">Key Name</label>
                    <input 
                        type="text" 
                        id="keyName" 
                        name="name" 
                        placeholder="e.g., Production Key, Development Key"
                        required
                    >
                </div>
                <button type="submit" class="btn btn-primary" id="createBtn">
                    Create API Key
                </button>
            </form>
            
            <div id="newKeyDisplay" class="new-key-display">
                <h3>✅ API Key Created Successfully!</h3>
                <p style="color: #666; margin-bottom: 15px;">Copy this key now - you won't be able to see it again:</p>
                <div class="key-value" id="newKeyValue"></div>
                <div class="warning">
                    ⚠️ <strong>Important:</strong> Store this key securely. It will not be shown again after you close this dialog.
                </div>
            </div>
        </div>
        
        <div class="card">
            <h2 style="margin-bottom: 20px; color: #333;">Your API Keys</h2>
            <div id="keysList" class="keys-list">
                <div class="empty-state">
                    <p>Loading keys...</p>
                </div>
            </div>
        </div>
    </div>
    
    <script>
        const API_BASE = window.location.origin;
        let currentBearerToken = null;
        
        // Check if we have a token in localStorage
        function getBearerToken() {
            if (!currentBearerToken) {
                currentBearerToken = localStorage.getItem('acto_bearer_token');
            }
            return currentBearerToken;
        }
        
        // Show alert
        function showAlert(message, type = 'info') {
            const alert = document.getElementById('alert');
            alert.className = `alert alert-${type} show`;
            alert.textContent = message;
            setTimeout(() => {
                alert.classList.remove('show');
            }, 5000);
        }
        
        // Make API request
        async function apiRequest(endpoint, options = {}) {
            const token = getBearerToken();
            if (!token && endpoint !== '/v1/keys') {
                showAlert('Please set your Bearer token first. Use an existing key or create a new one.', 'error');
                return null;
            }
            
            const headers = {
                'Content-Type': 'application/json',
                ...options.headers,
            };
            
            if (token) {
                headers['Authorization'] = `Bearer ${token}`;
            }
            
            try {
                const response = await fetch(`${API_BASE}${endpoint}`, {
                    ...options,
                    headers,
                });
                
                if (response.status === 401) {
                    showAlert('Authentication failed. Please check your Bearer token.', 'error');
                    return null;
                }
                
                if (!response.ok) {
                    const error = await response.json().catch(() => ({ detail: 'Unknown error' }));
                    throw new Error(error.detail || `HTTP ${response.status}`);
                }
                
                return await response.json();
            } catch (error) {
                showAlert(`Error: ${error.message}`, 'error');
                return null;
            }
        }
        
        // Load and display keys
        async function loadKeys() {
            const keysList = document.getElementById('keysList');
            keysList.innerHTML = '<div class="empty-state"><p>Loading keys...</p></div>';
            
            const result = await apiRequest('/v1/keys');
            if (!result) {
                keysList.innerHTML = '<div class="empty-state"><p>Failed to load keys. Make sure you have a valid Bearer token set.</p></div>';
                return;
            }
            
            if (!result.keys || result.keys.length === 0) {
                keysList.innerHTML = '<div class="empty-state"><p>No API keys found. Create your first key above!</p></div>';
                return;
            }
            
            keysList.innerHTML = result.keys.map(key => `
                <div class="key-item">
                    <div class="key-info">
                        <h3>${escapeHtml(key.name)}</h3>
                        <p><strong>ID:</strong> ${escapeHtml(key.key_id)}</p>
                        <p><strong>Created:</strong> ${new Date(key.created_at).toLocaleString()}</p>
                        ${key.last_used_at ? `<p><strong>Last Used:</strong> ${new Date(key.last_used_at).toLocaleString()}</p>` : '<p><strong>Last Used:</strong> Never</p>'}
                        <p><strong>Status:</strong> <span style="color: ${key.is_active ? '#10b981' : '#ef4444'}">${key.is_active ? 'Active' : 'Inactive'}</span></p>
                    </div>
                    <div class="key-actions">
                        ${key.is_active ? `<button class="btn btn-danger" onclick="deleteKey('${key.key_id}')">Delete</button>` : ''}
                    </div>
                </div>
            `).join('');
        }
        
        // Create new key
        document.getElementById('createKeyForm').addEventListener('submit', async (e) => {
            e.preventDefault();
            
            const form = e.target;
            const name = form.name.value.trim();
            const createBtn = document.getElementById('createBtn');
            
            if (!name) {
                showAlert('Please enter a key name', 'error');
                return;
            }
            
            createBtn.disabled = true;
            createBtn.innerHTML = 'Creating... <span class="loading"></span>';
            
            const result = await apiRequest('/v1/keys', {
                method: 'POST',
                body: JSON.stringify({ name }),
            });
            
            createBtn.disabled = false;
            createBtn.innerHTML = 'Create API Key';
            
            if (result) {
                // Show the new key
                document.getElementById('newKeyValue').textContent = result.key;
                document.getElementById('newKeyDisplay').classList.add('show');
                
                // Store token for future requests
                localStorage.setItem('acto_bearer_token', result.key);
                currentBearerToken = result.key;
                
                showAlert('API key created successfully!', 'success');
                form.reset();
                
                // Reload keys list
                await loadKeys();
            }
        });
        
        // Delete key
        async function deleteKey(keyId) {
            if (!confirm('Are you sure you want to delete this API key? This action cannot be undone.')) {
                return;
            }
            
            const result = await apiRequest(`/v1/keys/${keyId}`, {
                method: 'DELETE',
            });
            
            if (result && result.success) {
                showAlert('API key deleted successfully', 'success');
                await loadKeys();
            }
        }
        
        // Escape HTML
        function escapeHtml(text) {
            const div = document.createElement('div');
            div.textContent = text;
            return div.innerHTML;
        }
        
        // Initial load
        loadKeys();
        
        // Auto-refresh every 30 seconds
        setInterval(loadKeys, 30000);
    </script>
</body>
</html>
        """
        return Response(content=html_content, media_type="text/html")

    return app
