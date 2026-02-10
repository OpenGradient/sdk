# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

OpenGradient Python SDK - A decentralized model management and inference platform SDK. The SDK enables programmatic access to model repositories and decentralized AI infrastructure, including end-to-end verified AI execution. Use virtualenv for dependency management locally (in `venv` folder).

## Development Commands

### Build & Installation
```bash
# Install in development mode
pip install -e .

# Build distribution
make build

# Publish to PyPI (requires credentials)
make publish
```

### Testing
```bash
# Run all tests
make test

# Run unit tests only
make utils_test

# Run integration tests
make integrationtest
```

### Code Quality
```bash
# Run linting and formatting (uses ruff)
make check

# Generate documentation
make docs
```

### CLI Testing
```bash
# Test model inference
make infer

# Test LLM completion
make completion

# Test chat functionality
make chat

# Test tool usage
make tool

# Test TEE mode
make tee_completion
make tee_chat
```

## Architecture Overview

### Core Components

1. **Client (`src/opengradient/client.py`)**: Central client class managing authentication and API interactions
   - Handles Model Hub authentication (email/password)
   - Manages blockchain interactions (private key)
   - Provides high-level APIs for model management and inference

2. **CLI (`src/opengradient/cli.py`)**: Command-line interface using Click
   - Commands: `config`, `infer`, `completion`, `chat`
   - Supports file-based input for messages and tools

3. **LLM Module (`src/opengradient/llm/`)**: Language model specific functionality
   - Chat completions
   - Tool calling support
   - Streaming responses

4. **Blockchain Integration**: 
   - Smart contract ABIs in `src/opengradient/abi/`
   - Web3 integration for decentralized inference
   - Support for TEE (Trusted Execution Environment) mode

5. **Protocol Buffers (`src/opengradient/proto/`)**: gRPC service definitions for inference

### Key Concepts

- **Inference Modes**: VANILLA, TEE (end-to-end verified)
- **Model CID**: Content-addressed model identifiers
- **Dual Authentication**: Model Hub (email/password) + blockchain (private key)

## Configuration

The SDK uses environment-based configuration with defaults:
- `DEFAULT_RPC_URL`: Blockchain RPC endpoint
- `DEFAULT_API_URL`: Model Hub API endpoint
- `DEFAULT_INFERENCE_CONTRACT_ADDRESS`: Smart contract address

User configuration stored via `opengradient config init` wizard.

## Testing Strategy

- Unit tests: `tests/utils_test.py` using pytest
- Integration tests: `integrationtest/` for agent and workflow models
- CLI command testing via Makefile targets

## Documentation (pdoc)

Docs are generated with `pdoc3` using a custom Mako template at `templates/text.mako`. Run `make docs` to regenerate into `docs/`. Do not edit generated documentation files in `docs/` by hand.

### Cross-referencing in docstrings

To link to another module or class from a docstring, use fully qualified names in backticks:

```python
"""
- **`opengradient.client.llm`** -- description here
- **`opengradient.client.onchain_inference`** -- description here
"""
```

The template's `linkify` function automatically converts `` `opengradient.x.y.z` `` references into relative markdown links. Always use fully qualified names starting with `opengradient.` — never hardcode relative URLs in docstrings.

### Docstring style

- Use Google-style docstrings (Args, Returns, Raises, Note, Attributes sections)
- The template parses these sections and renders them as structured markdown
- For classes, Args in the `__init__` docstring are rendered under the Constructor heading

## Dependencies

Key dependencies (Python >=3.10):
- `web3` & `eth-account`: Blockchain interaction
- `grpcio`: Service communication
- `langchain` & `openai`: LLM integrations
- `click`: CLI framework
- `firebase-rest-api`: Backend services