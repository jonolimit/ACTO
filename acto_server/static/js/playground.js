// API Playground module for testing API endpoints

const API_BASE = window.location.origin;

const API_ENDPOINTS = {
    'GET /v1/proofs': {
        method: 'GET',
        path: '/v1/proofs',
        description: 'List all proofs',
        requiresBody: false,
        params: ['limit']
    },
    'GET /v1/proofs/{id}': {
        method: 'GET',
        path: '/v1/proofs',
        description: 'Get a specific proof by ID',
        requiresBody: false,
        params: ['proof_id'],
        isDynamic: true
    },
    'POST /v1/proofs': {
        method: 'POST',
        path: '/v1/proofs',
        description: 'Submit a new proof',
        requiresBody: true,
        exampleBody: {
            envelope: {
                payload: {
                    version: "1",
                    subject: {
                        task_id: "example-task",
                        robot_id: "example-robot",
                        run_id: "run-001"
                    },
                    created_at: new Date().toISOString(),
                    telemetry_normalized: {},
                    telemetry_hash: "example-hash",
                    payload_hash: "example-payload-hash",
                    hash_alg: "blake3",
                    signature_alg: "ed25519",
                    meta: {}
                },
                signature_b64: "example-signature",
                signer_public_key_b64: "example-public-key"
            }
        }
    },
    'POST /v1/verify': {
        method: 'POST',
        path: '/v1/verify',
        description: 'Verify a proof without storing it',
        requiresBody: true,
        exampleBody: {
            envelope: {
                payload: {
                    version: "1",
                    subject: {
                        task_id: "example-task"
                    },
                    created_at: new Date().toISOString(),
                    telemetry_normalized: {},
                    telemetry_hash: "example-hash",
                    payload_hash: "example-payload-hash",
                    hash_alg: "blake3",
                    signature_alg: "ed25519",
                    meta: {}
                },
                signature_b64: "example-signature",
                signer_public_key_b64: "example-public-key"
            }
        }
    },
    'POST /v1/score': {
        method: 'POST',
        path: '/v1/score',
        description: 'Get reputation score for a proof',
        requiresBody: true,
        exampleBody: {
            envelope: {
                payload: {
                    version: "1",
                    subject: {
                        task_id: "example-task"
                    },
                    created_at: new Date().toISOString(),
                    telemetry_normalized: {},
                    telemetry_hash: "example-hash",
                    payload_hash: "example-payload-hash",
                    hash_alg: "blake3",
                    signature_alg: "ed25519",
                    meta: {}
                },
                signature_b64: "example-signature",
                signer_public_key_b64: "example-public-key"
            }
        }
    },
    'POST /v1/access/check': {
        method: 'POST',
        path: '/v1/access/check',
        description: 'Check if a wallet has sufficient token balance',
        requiresBody: true,
        exampleBody: {
            rpc_url: "https://api.mainnet-beta.solana.com",
            owner: "WALLET_ADDRESS",
            mint: "9whFgsoNMhUukn3qsyT5xHTN9Q1dzzkr2qK2PAxtpump",
            minimum: 50000.0
        }
    }
};

let currentEndpoint = null;
let playgroundApiKey = '';

function initPlayground() {
    const endpointSelect = document.getElementById('playgroundEndpoint');
    if (!endpointSelect) return;
    
    // Populate endpoint dropdown
    Object.keys(API_ENDPOINTS).forEach(key => {
        const option = document.createElement('option');
        option.value = key;
        option.textContent = `${key} - ${API_ENDPOINTS[key].description}`;
        endpointSelect.appendChild(option);
    });
    
    // Set default
    if (endpointSelect.options.length > 0) {
        endpointSelect.value = endpointSelect.options[0].value;
        selectEndpoint(endpointSelect.value);
    }
    
    // Load API keys for selection
    loadPlaygroundApiKeys();
}

async function loadPlaygroundApiKeys() {
    const apiKeySelect = document.getElementById('playgroundApiKeySelect');
    if (!apiKeySelect) return;
    
    const token = window.accessToken || (typeof accessToken !== 'undefined' ? accessToken : null);
    if (!token) {
        apiKeySelect.innerHTML = '<option value="">Please connect your wallet first</option>';
        return;
    }
    
    try {
        const response = await fetch(`${API_BASE}/v1/keys`, {
            headers: {
                'Authorization': `Bearer ${token}`,
                'Content-Type': 'application/json'
            }
        });
        
        if (response.ok) {
            const data = await response.json();
            apiKeySelect.innerHTML = '<option value="">Select API Key...</option>';
            
            if (data.keys && data.keys.length > 0) {
                data.keys.forEach(key => {
                    const option = document.createElement('option');
                    option.value = key.key_id;
                    option.textContent = `${key.name} (${key.key_id.substring(0, 8)}...)`;
                    option.dataset.keyId = key.key_id;
                    apiKeySelect.appendChild(option);
                });
            } else {
                apiKeySelect.innerHTML = '<option value="">No API keys found. Create one in the API Keys tab.</option>';
            }
        } else {
            apiKeySelect.innerHTML = '<option value="">Failed to load API keys</option>';
        }
    } catch (error) {
        apiKeySelect.innerHTML = '<option value="">Error loading API keys</option>';
        console.error('Failed to load API keys:', error);
    }
}

function selectPlaygroundApiKey(keyId) {
    const apiKeyInput = document.getElementById('playgroundApiKey');
    if (!apiKeyInput || !keyId) return;
    
    // Try to get from localStorage if available (stored when key was created)
    const storedKey = localStorage.getItem(`api_key_${keyId}`);
    if (storedKey) {
        apiKeyInput.value = storedKey;
        playgroundApiKey = storedKey;
    } else {
        // Key not in localStorage - user needs to enter it manually
        apiKeyInput.placeholder = `API key for this ID not found. Please enter it manually.`;
        apiKeyInput.value = '';
        playgroundApiKey = '';
        if (typeof showAlert === 'function') {
            showAlert('API key not found in storage. Please enter it manually.', 'info');
        }
    }
}

function updatePlaygroundApiKey(key) {
    playgroundApiKey = key;
}

function selectEndpoint(endpointKey) {
    currentEndpoint = API_ENDPOINTS[endpointKey];
    if (!currentEndpoint) return;
    
    const bodyEditor = document.getElementById('playgroundBody');
    const paramsContainer = document.getElementById('playgroundParams');
    const descriptionEl = document.getElementById('playgroundDescription');
    
    if (descriptionEl) {
        descriptionEl.textContent = currentEndpoint.description;
    }
    
    // Show/hide body editor
    if (bodyEditor) {
        if (currentEndpoint.requiresBody) {
            bodyEditor.parentElement.style.display = 'block';
            if (currentEndpoint.exampleBody) {
                bodyEditor.value = JSON.stringify(currentEndpoint.exampleBody, null, 2);
            } else {
                bodyEditor.value = '{}';
            }
        } else {
            bodyEditor.parentElement.style.display = 'none';
        }
    }
    
    // Show/hide params
    if (paramsContainer) {
        paramsContainer.innerHTML = '';
        if (currentEndpoint.params && currentEndpoint.params.length > 0) {
            currentEndpoint.params.forEach(param => {
                const div = document.createElement('div');
                div.className = 'form-group';
                div.innerHTML = `
                    <label for="param_${param}">${param.replace('_', ' ').replace(/\b\w/g, l => l.toUpperCase())}</label>
                    <input type="text" id="param_${param}" class="form-control" placeholder="Enter ${param}">
                `;
                paramsContainer.appendChild(div);
            });
            paramsContainer.style.display = 'block';
        } else {
            paramsContainer.style.display = 'none';
        }
    }
}

async function executePlaygroundRequest() {
    if (!currentEndpoint) {
        showAlert('Please select an endpoint', 'error');
        return;
    }
    
    // Get API key from input or select
    const apiKeyInput = document.getElementById('playgroundApiKey');
    const apiKey = apiKeyInput ? apiKeyInput.value.trim() : playgroundApiKey;
    
    if (!apiKey) {
        showAlert('Please enter or select an API key', 'error');
        return;
    }
    
    const endpointSelect = document.getElementById('playgroundEndpoint');
    const bodyEditor = document.getElementById('playgroundBody');
    const paramsContainer = document.getElementById('playgroundParams');
    const responseEl = document.getElementById('playgroundResponse');
    const statusEl = document.getElementById('playgroundStatus');
    const executeBtn = document.getElementById('playgroundExecute');
    
    if (!executeBtn || !responseEl || !statusEl) return;
    
    executeBtn.disabled = true;
    executeBtn.textContent = 'Sending...';
    responseEl.textContent = 'Loading...';
    statusEl.textContent = '';
    
    try {
        // Build URL with params
        let url = currentEndpoint.path;
        if (currentEndpoint.params && paramsContainer) {
            currentEndpoint.params.forEach(param => {
                const input = document.getElementById(`param_${param}`);
                if (input && input.value) {
                    if (currentEndpoint.isDynamic && param === 'proof_id') {
                        url = `${currentEndpoint.path}/${input.value}`;
                    } else {
                        url += (url.includes('?') ? '&' : '?') + `${param}=${encodeURIComponent(input.value)}`;
                    }
                }
            });
        }
        
        // Get wallet address from current user
        let walletAddress = '';
        if (currentUser && currentUser.wallet_address) {
            walletAddress = currentUser.wallet_address;
        } else if (window.currentUser && window.currentUser.wallet_address) {
            walletAddress = window.currentUser.wallet_address;
        }
        
        if (!walletAddress) {
            showAlert('Wallet address not found. Please reconnect your wallet.', 'error');
            return;
        }
        
        // Build request options
        const options = {
            method: currentEndpoint.method,
            headers: {
                'Authorization': `Bearer ${apiKey}`,
                'X-Wallet-Address': walletAddress,
                'Content-Type': 'application/json'
            }
        };
        
        // Add body if needed
        if (currentEndpoint.requiresBody && bodyEditor) {
            try {
                const body = JSON.parse(bodyEditor.value);
                options.body = JSON.stringify(body);
            } catch (e) {
                throw new Error('Invalid JSON in request body: ' + e.message);
            }
        }
        
        // Execute request
        const startTime = Date.now();
        const response = await fetch(`${API_BASE}${url}`, options);
        const duration = Date.now() - startTime;
        
        const responseData = await response.json();
        
        // Display status
        const statusClass = response.ok ? 'status-success' : 'status-error';
        statusEl.innerHTML = `
            <span class="${statusClass}">${response.status} ${response.statusText}</span>
            <span class="status-time">(${duration}ms)</span>
        `;
        
        // Display response
        responseEl.textContent = JSON.stringify(responseData, null, 2);
        
        if (!response.ok) {
            showAlert(`Request failed: ${responseData.detail || response.statusText}`, 'error');
        } else {
            showAlert('Request successful!', 'success');
        }
        
    } catch (error) {
        statusEl.innerHTML = `<span class="status-error">Error</span>`;
        responseEl.textContent = `Error: ${error.message}`;
        showAlert(`Request failed: ${error.message}`, 'error');
    } finally {
        executeBtn.disabled = false;
        executeBtn.textContent = 'Execute Request';
    }
}

function formatPlaygroundResponse() {
    const responseEl = document.getElementById('playgroundResponse');
    if (!responseEl) return;
    
    try {
        const json = JSON.parse(responseEl.textContent);
        responseEl.textContent = JSON.stringify(json, null, 2);
    } catch (e) {
        // Not valid JSON, ignore
    }
}

function copyPlaygroundResponse() {
    const responseEl = document.getElementById('playgroundResponse');
    if (!responseEl) return;
    
    navigator.clipboard.writeText(responseEl.textContent).then(() => {
        showAlert('Response copied to clipboard!', 'success');
    }).catch(err => {
        showAlert('Failed to copy: ' + err.message, 'error');
    });
}

function clearPlaygroundResponse() {
    const responseEl = document.getElementById('playgroundResponse');
    const statusEl = document.getElementById('playgroundStatus');
    if (responseEl) responseEl.textContent = '';
    if (statusEl) statusEl.textContent = '';
}

