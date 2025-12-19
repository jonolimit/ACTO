// Documentation module for API usage guide

const documentation = {
    overview: {
        title: "Overview",
        content: `
            <h3>What is ACTO?</h3>
            <p>ACTO (Robotics Proof-of-Execution Toolkit) is a system for generating deterministic, signed execution proofs from robot telemetry and logs. These proofs are verifiable locally or via API.</p>
            
            <h3>What are API Keys?</h3>
            <p>API keys are secure tokens that authenticate your requests to the ACTO Verification API. Each key is unique to your account and allows you to:</p>
            <ul>
                <li>Submit robot execution proofs for verification</li>
                <li>Verify proof integrity and authenticity</li>
                <li>Check access permissions based on Solana token holdings</li>
                <li>Score proofs for reputation systems</li>
            </ul>
            
            <h3>Key Features</h3>
            <ul>
                <li><strong>Deterministic Proofs:</strong> Canonicalized telemetry ensures consistent proof generation</li>
                <li><strong>Signed Verification:</strong> Ed25519 signatures guarantee proof authenticity</li>
                <li><strong>Portable Format:</strong> JSON envelope format for easy integration</li>
                <li><strong>Local Verification:</strong> Verify proofs without a trusted server</li>
            </ul>
        `
    },
    gettingStarted: {
        title: "Getting Started",
        content: `
            <h3>Step 1: Create an API Key</h3>
            <p>Use the dashboard to create a new API key. Give it a descriptive name (e.g., "Production Key" or "Development Key").</p>
            
            <h3>Step 2: Store Your Key Securely</h3>
            <p><strong>Important:</strong> Copy and store your API key immediately after creation. You won't be able to see it again!</p>
            <p>Store it in a secure location such as:</p>
            <ul>
                <li>Environment variables</li>
                <li>Secret management systems (Vault, AWS Secrets Manager)</li>
                <li>Encrypted configuration files</li>
            </ul>
            
            <h3>Step 3: Use Your Key in Requests</h3>
            <p>Include your API key in the <code>Authorization</code> header of all API requests:</p>
            <pre><code>Authorization: Bearer YOUR_API_KEY_HERE</code></pre>
        `
    },
    authentication: {
        title: "Authentication",
        content: `
            <h3>Bearer Token Authentication</h3>
            <p>All API endpoints require Bearer token authentication. Include your API key in the request header:</p>
            
            <h4>Example Request</h4>
            <pre><code>curl -X POST https://api.actobotics.net/v1/proofs \\
  -H "Authorization: Bearer YOUR_API_KEY" \\
  -H "Content-Type: application/json" \\
  -d '{"envelope": {...}}'</code></pre>
            
            <h4>JavaScript/Fetch Example</h4>
            <pre><code>fetch('https://api.actobotics.net/v1/proofs', {
  method: 'POST',
  headers: {
    'Authorization': 'Bearer YOUR_API_KEY',
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({ envelope: {...} })
})</code></pre>
            
            <h4>Python Example</h4>
            <pre><code>import requests

headers = {
    'Authorization': 'Bearer YOUR_API_KEY',
    'Content-Type': 'application/json'
}

response = requests.post(
    'https://api.actobotics.net/v1/proofs',
    headers=headers,
    json={'envelope': {...}}
)</code></pre>
        `
    },
    endpoints: {
        title: "API Endpoints",
        content: `
            <h3>Submit Proof</h3>
            <p><strong>POST</strong> <code>/v1/proofs</code></p>
            <p>Submit a robot execution proof for storage and verification.</p>
            <pre><code>{
  "envelope": {
    "payload": {...},
    "signature_b64": "...",
    "signer_public_key_b64": "..."
  }
}</code></pre>
            
            <h3>Get Proof</h3>
            <p><strong>GET</strong> <code>/v1/proofs/{proof_id}</code></p>
            <p>Retrieve a stored proof by its ID.</p>
            
            <h3>Verify Proof</h3>
            <p><strong>POST</strong> <code>/v1/verify</code></p>
            <p>Verify the integrity and authenticity of a proof without storing it.</p>
            <pre><code>{
  "envelope": {...}
}</code></pre>
            <p><strong>Response:</strong></p>
            <pre><code>{
  "valid": true,
  "reason": "ok"
}</code></pre>
            
            <h3>Score Proof</h3>
            <p><strong>POST</strong> <code>/v1/score</code></p>
            <p>Get a reputation score for a proof based on various factors.</p>
            
            <h3>Check Access</h3>
            <p><strong>POST</strong> <code>/v1/access/check</code></p>
            <p>Check if a Solana wallet address has sufficient token holdings for access.</p>
            <pre><code>{
  "rpc_url": "https://api.mainnet-beta.solana.com",
  "owner": "WALLET_ADDRESS",
  "mint": "TOKEN_MINT_ADDRESS",
  "minimum": 1.0
}</code></pre>
        `
    },
    useCases: {
        title: "Use Cases",
        content: `
            <h3>Robotics Execution Verification</h3>
            <p>Generate and verify proofs of robot task execution for:</p>
            <ul>
                <li>Quality assurance and compliance</li>
                <li>Audit trails and accountability</li>
                <li>Performance benchmarking</li>
                <li>Insurance and liability documentation</li>
            </ul>
            
            <h3>Reputation Systems</h3>
            <p>Use proof scoring to build reputation systems that:</p>
            <ul>
                <li>Rank robot performance</li>
                <li>Enable trust networks</li>
                <li>Facilitate robot-to-robot interactions</li>
            </ul>
            
            <h3>Access Control</h3>
            <p>Integrate Solana token-based access control for:</p>
            <ul>
                <li>Gated robot services</li>
                <li>Premium feature access</li>
                <li>DAO-governed permissions</li>
            </ul>
        `
    },
    bestPractices: {
        title: "Best Practices",
        content: `
            <h3>Security</h3>
            <ul>
                <li><strong>Never commit API keys to version control</strong></li>
                <li><strong>Rotate keys regularly</strong> - Delete old keys and create new ones</li>
                <li><strong>Use different keys for different environments</strong> (development, staging, production)</li>
                <li><strong>Monitor key usage</strong> - Check statistics regularly for suspicious activity</li>
                <li><strong>Revoke compromised keys immediately</strong></li>
            </ul>
            
            <h3>Performance</h3>
            <ul>
                <li>Cache verification results when possible</li>
                <li>Batch requests when submitting multiple proofs</li>
                <li>Use appropriate rate limits for your use case</li>
            </ul>
            
            <h3>Error Handling</h3>
            <ul>
                <li>Always check HTTP status codes</li>
                <li>Handle 401 (Unauthorized) errors by checking your API key</li>
                <li>Handle 429 (Rate Limited) errors with exponential backoff</li>
                <li>Log errors for debugging and monitoring</li>
            </ul>
        `
    }
};

let currentDocSection = 'overview';

function showDocumentation(section = 'overview') {
    currentDocSection = section;
    const docContent = document.getElementById('docContent');
    if (!docContent) return;
    
    const doc = documentation[section];
    if (!doc) return;
    
    docContent.innerHTML = doc.content;
    
    // Update active menu item
    document.querySelectorAll('.doc-menu-item').forEach(item => {
        item.classList.remove('active');
        if (item.dataset.section === section) {
            item.classList.add('active');
        }
    });
}

function initDocumentation() {
    showDocumentation('overview');
}

