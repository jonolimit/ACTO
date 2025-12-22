# Rate Limiting

The ACTO API implements rate limiting to ensure fair usage and service stability.

## Limits

| Limit Type | Value |
|------------|-------|
| Default Rate | 5 requests/second |
| Burst Capacity | Up to 20 requests |
| Per Key | Rate limits apply per API key + endpoint |
| Bucket TTL | 1 hour (inactive buckets expire) |

## Configuration (Contributors Only)

::: tip For Contributors
These settings are for ACTO contributors running local development servers. Regular users don't need to configure rate limiting - it's handled by the hosted platform.
:::

```toml
# config.toml
rate_limit_enabled = true
rate_limit_rps = 10.0                  # Requests per second
rate_limit_burst = 50                  # Burst capacity
rate_limit_bucket_ttl = 3600.0         # Bucket expiry in seconds (1 hour)
rate_limit_cleanup_interval = 1000     # Cleanup stale buckets every N requests
```

| Environment Variable | Default | Description |
|---------------------|---------|-------------|
| `ACTO_RATE_LIMIT_ENABLED` | `true` | Enable rate limiting |
| `ACTO_RATE_LIMIT_RPS` | `5.0` | Requests per second |
| `ACTO_RATE_LIMIT_BURST` | `20` | Maximum burst capacity |
| `ACTO_RATE_LIMIT_BUCKET_TTL` | `3600.0` | Bucket expiry (seconds) |
| `ACTO_RATE_LIMIT_CLEANUP_INTERVAL` | `1000` | Cleanup frequency |

## Rate Limit Headers

Responses include rate limit information:

```http
X-RateLimit-Limit: 5
X-RateLimit-Remaining: 4
X-RateLimit-Reset: 1705320000
```

| Header | Description |
|--------|-------------|
| `X-RateLimit-Limit` | Requests allowed per second |
| `X-RateLimit-Remaining` | Remaining requests |
| `X-RateLimit-Reset` | Unix timestamp when limit resets |

## Rate Limit Exceeded

When you exceed the rate limit, you'll receive:

```http
HTTP/1.1 429 Too Many Requests
Retry-After: 2

{
  "detail": "Rate limit exceeded. Try again in 2 seconds."
}
```

## Handling Rate Limits

### Python SDK

The SDK provides a `RateLimitError` exception:

```python
from acto.client import ACTOClient
from acto.client.exceptions import RateLimitError
import time

client = ACTOClient(api_key="...", wallet_address="...")

try:
    result = client.verify(envelope)
except RateLimitError as e:
    print(f"Rate limited. Retry after {e.retry_after} seconds")
    time.sleep(e.retry_after or 1)
    result = client.verify(envelope)  # Retry
```

### Exponential Backoff

For robust error handling:

```python
import time
from acto.client.exceptions import RateLimitError

def verify_with_retry(client, envelope, max_retries=5):
    for attempt in range(max_retries):
        try:
            return client.verify(envelope)
        except RateLimitError as e:
            if attempt == max_retries - 1:
                raise
            
            wait = e.retry_after or (2 ** attempt)
            print(f"Rate limited. Waiting {wait}s...")
            time.sleep(wait)
```

### JavaScript

```javascript
async function verifyWithRetry(envelope, maxRetries = 5) {
  for (let attempt = 0; attempt < maxRetries; attempt++) {
    const response = await fetch('https://api.actobotics.net/v1/verify', {
      method: 'POST',
      headers: {...},
      body: JSON.stringify({ envelope })
    });
    
    if (response.status === 429) {
      const retryAfter = response.headers.get('Retry-After') || Math.pow(2, attempt);
      console.log(`Rate limited. Waiting ${retryAfter}s...`);
      await new Promise(r => setTimeout(r, retryAfter * 1000));
      continue;
    }
    
    return response.json();
  }
  throw new Error('Max retries exceeded');
}
```

## Best Practices

### 1. Use Batch Endpoints

Instead of individual verification calls:

```python
# ❌ Bad: 100 individual calls
for env in envelopes:
    client.verify(env)

# ✅ Good: 1 batch call
results = client.verify_batch(envelopes)
```

### 2. Implement Request Queuing

```python
import time
from collections import deque

class RateLimitedClient:
    def __init__(self, client, rate=5):
        self.client = client
        self.rate = rate
        self.request_times = deque()
    
    def verify(self, envelope):
        self._wait_if_needed()
        return self.client.verify(envelope)
    
    def _wait_if_needed(self):
        now = time.time()
        
        # Remove requests older than 1 second
        while self.request_times and now - self.request_times[0] > 1:
            self.request_times.popleft()
        
        # Wait if at rate limit
        if len(self.request_times) >= self.rate:
            sleep_time = 1 - (now - self.request_times[0])
            if sleep_time > 0:
                time.sleep(sleep_time)
        
        self.request_times.append(time.time())
```

### 3. Cache Results

```python
from functools import lru_cache

@lru_cache(maxsize=1000)
def get_proof_cached(client, proof_id):
    return client.get_proof(proof_id)
```

### 4. Monitor Usage

Track your API usage in the dashboard to stay within limits.

## Increasing Limits

For higher rate limits, contact support:

- **Email**: support@actobotics.net
- **Dashboard**: api.actobotics.net/dashboard

Include:
- Your use case
- Expected request volume
- Wallet address

