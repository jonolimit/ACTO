# acto access

Check token balance for API access.

## Commands

| Command | Description |
|---------|-------------|
| `acto access check` | Check if wallet has sufficient tokens |

## Check Access

```bash
acto access check [OPTIONS]
```

### Options

| Option | Description | Required |
|--------|-------------|----------|
| `--owner`, `-o` | Wallet address to check | Yes |
| `--mint`, `-m` | Token mint address | No (uses configured ACTO token) |
| `--minimum`, `-min` | Minimum required balance | No (default: 50000) |
| `--rpc`, `-r` | Solana RPC URL | No (uses configured RPC) |

::: tip Default Configuration
If `--mint`, `--minimum`, or `--rpc` are not provided, the CLI uses defaults from your configuration (environment variables or `~/.acto/config.toml`).
:::

### Examples

```bash
# Simple check (uses configured ACTO token)
acto access check --owner 5K8vK...

# With explicit token mint
acto access check \
  --owner 5K8vK... \
  --mint CUSTOM_TOKEN_MINT \
  --minimum 100000

# With custom RPC
acto access check \
  --owner 5K8vK... \
  --rpc https://your-rpc-url.com
```

### Output

```
✅ Access Allowed
   Wallet: 5K8vK...
   Balance: 125,000 tokens
   Required: 50,000 tokens
```

Or if insufficient:

```
❌ Access Denied
   Wallet: 5K8vK...
   Balance: 25,000 tokens
   Required: 50,000 tokens
   Reason: Insufficient balance
```

## Environment Variables

The CLI uses these environment variables for defaults:

| Variable | Description |
|----------|-------------|
| `ACTO_TOKEN_GATING_MINT` | Default token mint address |
| `ACTO_TOKEN_GATING_MINIMUM` | Default minimum balance |
| `ACTO_HELIUS_API_KEY` | Helius API key for RPC |
| `ACTO_SOLANA_RPC_URL` | Custom Solana RPC URL |

