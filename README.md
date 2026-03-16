# SciCompute MCP Server

MCP server for scientific computing with multiple backends. Provides AI coding assistants with mathematical computation and visualization capabilities.

## Features

- Multiple computing backends (Mathematica, more coming soon)
- Image output support (plots, graphics)
- Automatic backend selection
- Persistent session state (variables persist across calls)
- Documentation query for unknown symbols

## Supported Backends

| Backend | Status | Capabilities |
|---------|--------|--------------|
| Mathematica | ✅ Ready | symbolic, numeric, plot, image, audio |
| MATLAB | 🔲 Planned | numeric, plot |
| SymPy | 🔲 Planned | symbolic |
| Julia | 🔲 Planned | numeric, plot |

## Installation

```bash
# Clone and install
git clone <repo-url>
cd scicompute_mcp
python -m venv .venv
source .venv/bin/activate
pip install -e .
```

## Configuration

Add to your `opencode.json`:

```json
{
  "mcp": {
    "scicompute": {
      "type": "local",
      "command": ["/path/to/.venv/bin/python", "-m", "scicompute_mcp.server"],
      "enabled": true
    }
  }
}
```

## Tools

### compute(code, backend?)

Execute scientific computing code.

```python
# Plot a function
compute("Plot[Sin[x], {x, 0, 2 Pi}]", "mathematica")

# Symbolic computation
compute("Integrate[x^2, x]", "mathematica")
```

### list_backends()

List all available backends and their capabilities.

### reset(backend?)

Reset backend state, clear all variables.

### doc(symbol, backend?)

Query documentation for a symbol. Useful when you need to understand how to use a function.

```python
doc("Plot3D")  # Returns usage, attributes, and options
```

## Usage Examples

Ask your AI assistant:

```
画一个 sin(x) 的图像

计算 ∫x²dx 从 0 到 1

查一下 NDSolve 的用法
```

## Requirements

- Python 3.10+
- For Mathematica backend: Wolfram Mathematica with `wolframclient` Python package

## License

MIT