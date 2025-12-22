# Access Control

Check token balance for API access.

## Endpoint

<div class="endpoint-card">
  <span class="method-badge post">POST</span>
  <span class="path">/v1/access/check</span>
</div>

## Request

### Headers

```http
Authorization: Bearer YOUR_API_KEY
X-Wallet-Address: YOUR_WALLET_ADDRESS
Content-Type: application/json
```

### Body

```json
{
  "owner": "WALLET_ADDRESS",
  "mint": "TOKEN_MINT_ADDRESS",
  "minimum": 50000
}
```

### Schema

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `owner` | string | Yes | Wallet address to check |
| `mint` | string | Yes | Token mint address |
| `minimum` | number | Yes | Minimum required balance |
| `rpc_url` | string | No | Custom RPC URL (optional) |

::: tip RPC URL
The `rpc_url` field is optional. If omitted, the server uses its configured Helius RPC endpoint for better rate limits.
:::

## Response

### Access Granted

```json
{
  "allowed": true,
  "reason": "Sufficient balance",
  "balance": 125000.0
}
```

### Access Denied

```json
{
  "allowed": false,
  "reason": "Insufficient balance. Required: 50000, Found: 25000",
  "balance": 25000.0
}
```

## Examples

### cURL

```bash
curl -X POST https://api.actobotics.net/v1/access/check \
  -H "Authorization: Bearer acto_abc123..." \
  -H "X-Wallet-Address: 5K8vK..." \
  -H "Content-Type: application/json" \
  -d '{
    "owner": "5K8vK...",
    "mint": "ACTO_TOKEN_MINT",
    "minimum": 50000
  }'
```

### Python SDK

```python
from acto.client import ACTOClient

client = ACTOClient(api_key="...", wallet_address="...")

result = client.check_access(
    owner="5K8vK...",
    mint="ACTO_TOKEN_MINT",
    minimum=50000
)

if result.allowed:
    print(f"✅ Access granted. Balance: {result.balance}")
else:
    print(f"❌ Access denied: {result.reason}")
```

### CLI

```bash
# Simple (uses configured ACTO token)
acto access check --owner 5K8vK...

# With explicit parameters
acto access check \
  --owner 5K8vK... \
  --mint ACTO_TOKEN_MINT \
  --minimum 50000
```

## Use Cases

- Pre-flight access check
- Balance monitoring
- Multi-wallet validation

