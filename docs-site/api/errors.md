# Error Responses

All API errors follow a consistent format.

## Error Format

```json
{
  "detail": "Error message describing what went wrong"
}
```

## HTTP Status Codes

| Code | Name | Description |
|------|------|-------------|
| 200 | OK | Request successful |
| 400 | Bad Request | Invalid request data |
| 401 | Unauthorized | Invalid or missing API key |
| 403 | Forbidden | Insufficient permissions or token balance |
| 404 | Not Found | Resource doesn't exist |
| 422 | Unprocessable Entity | Validation error |
| 429 | Too Many Requests | Rate limit exceeded |
| 500 | Internal Server Error | Server-side error |

## Error Details

### 400 Bad Request

The request contains invalid data.

```json
{
  "detail": "Invalid JSON body"
}
```

**Common causes:**
- Malformed JSON
- Missing required fields
- Invalid data types

### 401 Unauthorized

Authentication failed.

```json
{
  "detail": "Invalid API key"
}
```

**Common causes:**
- Missing Authorization header
- Invalid API key
- Expired API key

**Solution:**
```bash
# Correct header format
Authorization: Bearer acto_your_key_here
```

### 403 Forbidden

Access denied.

```json
{
  "detail": "Insufficient token balance. Required: 50000 ACTO"
}
```

**Common causes:**
- Token balance below 50,000 ACTO
- Wrong wallet address
- Feature not available for your account

**Solution:**
- Ensure your wallet holds at least 50,000 ACTO tokens
- Verify you're using the correct wallet address

### 404 Not Found

Resource doesn't exist.

```json
{
  "detail": "Proof not found"
}
```

**Common causes:**
- Invalid proof ID
- Invalid device ID
- Resource was deleted

### 422 Unprocessable Entity

Validation error.

```json
{
  "detail": "Invalid proof envelope: missing required field 'task_id'"
}
```

**Common causes:**
- Missing required fields
- Invalid field values
- Schema validation failure

### 429 Too Many Requests

Rate limit exceeded.

```json
{
  "detail": "Rate limit exceeded. Try again in 2 seconds."
}
```

**Headers:**
```http
Retry-After: 2
```

**Solution:**
- Implement exponential backoff
- Use batch endpoints
- See [Rate Limiting](/api/rate-limiting)

### 500 Internal Server Error

Server-side error.

```json
{
  "detail": "Internal server error"
}
```

**Solution:**
- Retry the request after a delay
- Contact support if persistent

## Error Handling Examples

### Python

```python
from acto.client import ACTOClient
from acto.client.exceptions import (
    ACTOClientError,
    AuthenticationError,
    AuthorizationError,
    NotFoundError,
    ValidationError,
    RateLimitError,
    ServerError,
)

client = ACTOClient(api_key="...", wallet_address="...")

try:
    result = client.verify(envelope)
except AuthenticationError:
    print("❌ Invalid API key. Check your credentials.")
except AuthorizationError:
    print("❌ Insufficient token balance.")
except NotFoundError:
    print("❌ Proof not found.")
except ValidationError as e:
    print(f"❌ Validation error: {e}")
except RateLimitError as e:
    print(f"⏳ Rate limited. Retry after {e.retry_after}s")
except ServerError:
    print("❌ Server error. Try again later.")
except ACTOClientError as e:
    print(f"❌ Error: {e}")
```

### JavaScript

```javascript
try {
  const response = await fetch('https://api.actobotics.net/v1/verify', {
    method: 'POST',
    headers: {...},
    body: JSON.stringify({ envelope })
  });
  
  if (!response.ok) {
    const { detail } = await response.json();
    
    switch (response.status) {
      case 401:
        console.error('Invalid API key');
        break;
      case 403:
        console.error('Insufficient token balance');
        break;
      case 404:
        console.error('Not found');
        break;
      case 429:
        const retryAfter = response.headers.get('Retry-After');
        console.error(`Rate limited. Retry after ${retryAfter}s`);
        break;
      default:
        console.error(`Error: ${detail}`);
    }
    return;
  }
  
  const data = await response.json();
} catch (error) {
  console.error('Network error:', error);
}
```

## Debugging Tips

1. **Check Headers**: Ensure Authorization and X-Wallet-Address are correct
2. **Validate JSON**: Use a JSON validator before sending
3. **Check Status Codes**: Handle each status code appropriately
4. **Log Responses**: Log error details for debugging
5. **Use SDK**: The Python SDK provides typed exceptions

