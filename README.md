# SciCompute MCP Server

MCP server for scientific computing with multiple backends.

## Supported Backends

- Mathematica (Wolfram Language)
- More coming soon...

## Installation

```bash
pip install -e .
```

## Usage

Add to your opencode.json:

```json
{
  "mcp": {
    "scicompute": {
      "type": "local",
      "command": ["python", "-m", "scicompute_mcp.server"],
      "enabled": true
    }
  }
}
```

## Tools

- `compute(code, backend)` - Execute code
- `list_backends()` - List available backends
- `reset(backend)` - Reset backend state