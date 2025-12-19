const API_BASE = window.location.origin;
let phantomWallet = null;
let currentUser = null;
let accessToken = null;

// Check for existing session
window.addEventListener('DOMContentLoaded', async () => {
    accessToken = localStorage.getItem('acto_access_token');
    if (accessToken) {
        const user = await getCurrentUser();
        if (user) {
            currentUser = user;
            showMainContent();
        } else {
            localStorage.removeItem('acto_access_token');
        }
    }
});

// Connect Phantom Wallet
async function connectWallet() {
    try {
        if (!window.solana || !window.solana.isPhantom) {
            showAlert('Phantom wallet not found. Please install Phantom wallet extension.', 'error');
            return;
        }
        
        phantomWallet = window.solana;
        const response = await phantomWallet.connect();
        const walletAddress = response.publicKey.toString();
        
        // Get challenge from server
        const challengeRes = await fetch(`${API_BASE}/v1/auth/wallet/connect`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ wallet_address: walletAddress })
        });
        
        if (!challengeRes.ok) {
            throw new Error('Failed to get challenge');
        }
        
        const { challenge } = await challengeRes.json();
        
        // Sign message with wallet
        const message = new TextEncoder().encode(challenge);
        const signature = await phantomWallet.signMessage(message, 'utf8');
        
        // Convert signature to base64
        const signatureBase64 = btoa(String.fromCharCode(...signature.signature));
        
        // Verify signature with server
        const verifyRes = await fetch(`${API_BASE}/v1/auth/wallet/verify`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                wallet_address: walletAddress,
                signature: signatureBase64,
                challenge: challenge
            })
        });
        
        if (!verifyRes.ok) {
            throw new Error('Signature verification failed');
        }
        
        const data = await verifyRes.json();
        accessToken = data.access_token;
        localStorage.setItem('acto_access_token', accessToken);
        currentUser = { user_id: data.user_id, wallet_address: data.wallet_address };
        
        showMainContent();
        showAlert('Successfully connected!', 'success');
        await loadKeys();
        
    } catch (error) {
        console.error('Wallet connection error:', error);
        showAlert(`Error: ${error.message}`, 'error');
    }
}

// Disconnect wallet
async function disconnectWallet() {
    if (phantomWallet) {
        try {
            await phantomWallet.disconnect();
        } catch (e) {
            console.error('Disconnect error:', e);
        }
    }
    phantomWallet = null;
    currentUser = null;
    accessToken = null;
    localStorage.removeItem('acto_access_token');
    document.getElementById('loginCard').classList.remove('hidden');
    document.getElementById('mainContent').classList.add('hidden');
    document.getElementById('walletInfo').style.display = 'none';
    showAlert('Disconnected successfully', 'info');
}

// Show main content
function showMainContent() {
    document.getElementById('loginCard').classList.add('hidden');
    document.getElementById('mainContent').classList.remove('hidden');
    if (currentUser) {
        document.getElementById('walletAddress').textContent = 
            `${currentUser.wallet_address.substring(0, 4)}...${currentUser.wallet_address.substring(currentUser.wallet_address.length - 4)}`;
        document.getElementById('walletInfo').style.display = 'block';
    }
}

// Get current user
async function getCurrentUser() {
    if (!accessToken) return null;
    try {
        const res = await fetch(`${API_BASE}/v1/auth/me`, {
            headers: { 'Authorization': `Bearer ${accessToken}` }
        });
        if (res.ok) {
            return await res.json();
        }
    } catch (e) {
        console.error('Get user error:', e);
    }
    return null;
}

// Show alert
function showAlert(message, type = 'info') {
    const alert = document.getElementById('alert');
    alert.className = `alert alert-${type} show`;
    alert.textContent = message;
    setTimeout(() => alert.classList.remove('show'), 5000);
}

// Make API request
async function apiRequest(endpoint, options = {}) {
    if (!accessToken) {
        showAlert('Please connect your wallet first', 'error');
        return null;
    }
    
    const headers = {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${accessToken}`,
        ...options.headers,
    };
    
    try {
        const response = await fetch(`${API_BASE}${endpoint}`, {
            ...options,
            headers,
        });
        
        if (response.status === 401) {
            showAlert('Session expired. Please reconnect your wallet.', 'error');
            disconnectWallet();
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
    if (!accessToken) return;
    
    const keysList = document.getElementById('keysList');
    keysList.innerHTML = '<div class="empty-state"><p>Loading keys...</p></div>';
    
    const result = await apiRequest('/v1/keys');
    if (!result) {
        keysList.innerHTML = '<div class="empty-state"><p>Failed to load keys.</p></div>';
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
                <p><strong>Status:</strong> <span class="status-badge status-${key.is_active ? 'active' : 'inactive'}">${key.is_active ? 'Active' : 'Inactive'}</span></p>
            </div>
            <div class="key-actions">
                ${key.is_active ? `<button class="btn btn-danger" onclick="deleteKey('${key.key_id}')">Delete</button>` : ''}
            </div>
        </div>
    `).join('');
}

// Create new key
document.addEventListener('DOMContentLoaded', () => {
    const createKeyForm = document.getElementById('createKeyForm');
    if (createKeyForm) {
        createKeyForm.addEventListener('submit', async (e) => {
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
                document.getElementById('newKeyValue').textContent = result.key;
                document.getElementById('newKeyDisplay').classList.add('show');
                showAlert('API key created successfully!', 'success');
                form.reset();
                await loadKeys();
            }
        });
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

