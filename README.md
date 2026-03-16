# SciCompute MCP Server

MCP server for scientific computing with multiple backends. Provides AI coding assistants with mathematical computation and visualization capabilities.

## Features

- Multiple computing backends (Mathematica, Octave)
- Image output support (plots, graphics)
- Automatic backend selection
- Persistent session state (variables persist across calls)
- Documentation query for unknown symbols

## Supported Backends

| Backend | Status | Capabilities |
|---------|--------|--------------|
| Mathematica | ✅ Ready | symbolic, numeric, plot, image, audio |
| Octave | ✅ Ready | numeric, plot, symbolic |
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

### Backend Requirements

#### Octave Backend

1. Install GNU Octave:
   ```bash
   # Ubuntu/Debian
   sudo apt install octave octave-symbolic gnuplot
   
   # macOS
   brew install octave gnuplot
   
   # Windows: download from https://octave.org/download
   ```

2. Install symbolic package (for symbolic computation):
   ```bash
   octave --eval "pkg install -forge symbolic"
   ```

3. oct2py dependency:
   - Uses git version with bug fixes for symbolic objects
   - Will switch to PyPI once oct2py releases a new version

#### Mathematica Backend

- Install [Wolfram Mathematica](https://www.wolfram.com/mathematica/)
- License required

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
# Plot with Octave
compute("x = 0:0.1:10; y = sin(x); plot(x, y)", "octave")

# Symbolic computation with Octave
compute("pkg load symbolic; syms x; diff(x^2, x)", "octave")

# Mathematica
compute("Plot[Sin[x], {x, 0, 2 Pi}]", "mathematica")
compute("Integrate[x^2, x]", "mathematica")
```

### list_backends()

List all available backends and their capabilities.

### reset(backend?)

Reset backend state, clear all variables.

### doc(symbol, backend?)

Query documentation for a symbol.

```python
doc("Plot3D", "mathematica")  # Mathematica usage
doc("eig", "octave")          # Octave usage
```

## Usage Examples

Ask your AI assistant:

```
画一个 sin(x) 的图像

计算 ∫x²dx 从 0 到 1

求解 x² - 4 = 0

查一下 NDSolve 的用法
```

## Requirements

- Python 3.10+
- Git (for oct2py git dependency)
- For Octave backend: GNU Octave + gnuplot + symbolic package
- For Mathematica backend: Wolfram Mathematica

## License

MIT