# ACTO

ACTO is a robotics-first proof-of-execution toolkit.

It helps you generate deterministic, signed execution proofs from robot telemetry and logs, then verify those proofs locally or via an API. ACTO is designed to be smart-contract-free by default and can be integrated into existing robotics stacks.

## What you get

- Python SDK to create and verify execution proofs
- Async/await support for asynchronous operations
- Context managers for better resource management
- Local-first SQLite proof registry
- FastAPI verification service (optional)
- Interactive CLI mode for guided workflows
- Shell completion support (bash, zsh, fish, PowerShell)
- Progress bars and color-coded output
- Config file support (`~/.acto/config.toml`)
- Pluggable telemetry parsers and normalizers
- Token gating module (optional) for SPL token balance checks (off-chain)
- Jupyter notebook examples for SDK usage

## Quick start

### Create a virtual environment

```bash
python -m venv .venv
# Windows:
# .venv\Scripts\activate
# macOS/Linux:
source .venv/bin/activate
```

### Install

```bash
pip install -U pip
pip install -e ".[all]"
```

### Generate a keypair

```bash
acto keys generate --out data/keys/acto_keypair.json
```

### Generate a proof from telemetry

```bash
acto proof create   --task-id "cleaning-run-001"   --source examples/telemetry/sample_telemetry.jsonl   --out examples/proofs/sample_proof.json
```

### Verify locally

```bash
acto proof verify --proof examples/proofs/sample_proof.json
```

### Run the API server (optional)

```bash
acto server run
```

## Interactive Mode

ACTO includes an interactive mode for guided workflows:

```bash
acto interactive start
```

This launches a menu-driven interface where you can:
- Generate keypairs
- Create and verify proofs
- Manage the proof registry
- Check token access

## Shell Completion

Install shell completion for better CLI experience:

```bash
# Show completion script
acto completion show --shell bash

# Install for bash (add to ~/.bashrc)
acto completion install --shell bash >> ~/.bashrc

# Install for zsh (add to ~/.zshrc)
acto completion install --shell zsh >> ~/.zshrc

# Install for PowerShell
acto completion install --shell powershell
```

Supported shells: `bash`, `zsh`, `fish`, `powershell`

## Configuration

ACTO supports configuration via environment variables or a config file:

### Config File (`~/.acto/config.toml`)

```toml
[storage]
db_url = "sqlite:///./data/acto.sqlite"

[logging]
log_level = "INFO"
json_logs = false

[proof]
proof_version = "1"
proof_hash_alg = "blake3"
proof_signature_alg = "ed25519"

[server]
host = "127.0.0.1"
port = 8080
```

### Environment Variables

All settings can also be set via environment variables with the `ACTO_` prefix:

```bash
export ACTO_LOG_LEVEL=DEBUG
export ACTO_DB_URL=sqlite:///./custom.db
```

## SDK Usage

### Basic Usage

```python
from acto.proof import create_proof, verify_proof
from acto.telemetry.models import TelemetryBundle, TelemetryEvent
from acto.crypto import KeyPair
from datetime import datetime

# Generate keypair
keypair = KeyPair.generate()

# Create telemetry bundle
bundle = TelemetryBundle(
    task_id="task-001",
    robot_id="robot-001",
    events=[
        TelemetryEvent(
            ts=datetime.now().isoformat(),
            topic="sensor",
            data={"value": 42}
        )
    ]
)

# Create proof
envelope = create_proof(
    bundle,
    keypair.private_key_b64,
    keypair.public_key_b64
)

# Verify proof
is_valid = verify_proof(envelope)
```

### Async Operations

```python
import asyncio
from acto.proof import create_proof_async, verify_proof_async

async def main():
    # Create proof asynchronously
    envelope = await create_proof_async(
        bundle,
        keypair.private_key_b64,
        keypair.public_key_b64
    )
    
    # Verify asynchronously
    is_valid = await verify_proof_async(envelope)

asyncio.run(main())
```

### Registry with Context Manager

```python
from acto.registry import ProofRegistry, AsyncProofRegistry

# Synchronous with context manager
with ProofRegistry() as registry:
    proof_id = registry.upsert(envelope)
    proof = registry.get(proof_id)

# Async with context manager
async with AsyncProofRegistry() as registry:
    proof_id = await registry.upsert(envelope)
    proof = await registry.get(proof_id)
```

### Jupyter Notebook Examples

Check out the example notebooks in `examples/notebooks/`:

- `01_basic_proof_creation.ipynb` - Basic proof creation and verification
- `02_async_proof_operations.ipynb` - Async/await examples
- `03_registry_operations.ipynb` - Registry usage with context managers

## Token gating (no smart contract required)

ACTO can gate access based on SPL token holdings by checking a wallet's token balance via Solana RPC. This is off-chain enforcement (your API decides whether to allow a request).

```bash
acto access check   --rpc https://api.mainnet-beta.solana.com   --owner <WALLET_ADDRESS>   --mint <TOKEN_MINT>   --minimum 50000
```

## License

MIT. See `LICENSE`.

## New in this expanded build

### Core Features
- Pluggable pipeline system for telemetry ingestion and proof generation
- Proof anchoring module (Solana Memo anchoring is optional and contract-free)
- API key authentication (optional) + request ID middleware
- In-memory rate limiting middleware for the API
- Proof reputation scoring module (configurable scoring policy)
- Metrics endpoint (Prometheus-compatible) for hosted deployments
- Docker + docker-compose for running the API + registry quickly
- More CLI commands (registry, score, plugins, pipeline)

### Developer Experience Improvements
- **Interactive Mode**: Menu-driven CLI interface (`acto interactive`)
- **Shell Completion**: Auto-completion for bash, zsh, fish, and PowerShell
- **Progress Bars**: Visual feedback for long-running operations
- **Color-Coded Output**: Consistent, readable CLI output
- **Config File Support**: User configuration via `~/.acto/config.toml`
- **Async/Await Support**: Asynchronous versions of proof and registry operations
- **Context Managers**: Better resource management with `with` statements
- **Type Hints**: Complete type annotations throughout the SDK
- **Comprehensive Docstrings**: Function documentation with code examples
- **Jupyter Notebooks**: Interactive examples for SDK usage
