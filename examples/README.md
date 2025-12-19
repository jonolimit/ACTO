# Examples

This directory contains example scripts, telemetry data, and Jupyter notebooks demonstrating ACTO usage.

## Jupyter Notebooks

Interactive examples for SDK usage:

- **`notebooks/01_basic_proof_creation.ipynb`** - Basic proof creation and verification
- **`notebooks/02_async_proof_operations.ipynb`** - Async/await support examples
- **`notebooks/03_registry_operations.ipynb`** - Registry usage with context managers

To run the notebooks:

```bash
# Install Jupyter if needed
pip install jupyter

# Start Jupyter
jupyter notebook notebooks/
```

## CLI Examples

### Create a proof from sample telemetry

```bash
acto keys generate --out data/keys/acto_keypair.json
acto proof create --task-id cleaning-run-001 --source examples/telemetry/sample_telemetry.jsonl --out examples/proofs/sample_proof.json
acto proof verify --proof examples/proofs/sample_proof.json
```

### Interactive Mode

Use the interactive mode for guided workflows:

```bash
acto interactive start
```

### Submit to local API

Start the server:

```bash
acto server run
```

Then:

```bash
python examples/scripts/submit_proof.py examples/proofs/sample_proof.json
```

### Pipeline mode

```bash
acto pipeline run --task-id cleaning-run-002 --source examples/telemetry/sample_telemetry.jsonl --out examples/proofs/sample_proof_pipeline.json
acto score compute --proof examples/proofs/sample_proof_pipeline.json
acto registry list
```

## SDK Examples

See the Jupyter notebooks in `notebooks/` for comprehensive SDK usage examples including:

- Basic proof creation and verification
- Async/await operations
- Registry management with context managers
- Batch operations
