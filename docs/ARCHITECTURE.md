# ACTO Architecture

Layers:

1. SDK (`acto/`)
2. CLI (`acto_cli/`)
3. Verification API (`acto_server/`)

Principles:

- Smart-contract-free by default
- Deterministic hashing + Ed25519 signatures
- Optional Solana integrations are isolated behind lazy imports

## Developer Experience

The SDK and CLI include several developer-friendly features:

### SDK Features

- **Async/Await Support**: Asynchronous versions of proof and registry operations (`acto/proof/async_engine.py`, `acto/registry/async_service.py`)
- **Context Managers**: Resource management via `with` statements for `ProofRegistry` and `AsyncProofRegistry`
- **Type Hints**: Complete type annotations throughout the codebase
- **Comprehensive Docstrings**: Function documentation with code examples

### CLI Features

- **Interactive Mode**: Menu-driven interface (`acto interactive`)
- **Shell Completion**: Auto-completion for bash, zsh, fish, and PowerShell
- **Progress Bars**: Visual feedback for long-running operations
- **Color-Coded Output**: Consistent, readable terminal output
- **Config File Support**: User configuration via `~/.acto/config.toml`
