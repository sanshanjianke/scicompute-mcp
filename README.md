# SciCompute MCP Server

MCP server for scientific computing with multiple backends. Provides AI coding assistants with mathematical computation and visualization capabilities.

## Features

- Multiple computing backends (Mathematica, Octave, Maxima, SymPy)
- Image output support (plots, graphics)
- Automatic backend selection
- Persistent session state (variables persist across calls)
- Documentation query for unknown symbols
- Multi-platform support (Claude Code, Claude Desktop, OpenCode/Crush)

## Supported Backends

| Backend | Status | Capabilities |
|---------|--------|--------------|
| Mathematica | ✅ Ready | symbolic, numeric, plot, image, audio |
| Octave | ✅ Ready | numeric, plot |
| Maxima | ✅ Ready | symbolic, numeric, plot |
| SymPy | 🚧 In Progress | symbolic, numeric, plot |
| MATLAB | 🔲 Planned | numeric, plot |
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

#### Maxima Backend

```bash
# Ubuntu/Debian
sudo apt install maxima gnuplot

# macOS
brew install maxima gnuplot
```

#### Octave Backend

```bash
# Ubuntu/Debian
sudo apt install octave gnuplot

# macOS
brew install octave gnuplot
```

#### Mathematica Backend

- Install [Wolfram Mathematica](https://www.wolfram.com/mathematica/)
- License required

## Configuration

### Claude Code (`.mcp.json`)

```json
{
  "mcpServers": {
    "scicompute": {
      "command": "/path/to/.venv/bin/python",
      "args": ["-m", "scicompute_mcp.server"]
    }
  }
}
```

### Claude Desktop (`claude_desktop_config.json`)

```json
{
  "mcpServers": {
    "scicompute": {
      "command": "/path/to/.venv/bin/python",
      "args": ["-m", "scicompute_mcp.server"]
    }
  }
}
```

### OpenCode / Crush (`.opencode.json`)

```json
{
  "mcpServers": {
    "scicompute": {
      "type": "stdio",
      "command": "/path/to/.venv/bin/python",
      "args": ["-m", "scicompute_mcp.server"]
    }
  }
}
```

## Multi-Platform Support

This project supports multiple AI assistant platforms. Configuration templates are provided in the `configs/` directory:

| File | Platform |
|------|----------|
| `configs/claude-code.json` | Claude Code |
| `configs/claude-desktop.json` | Claude Desktop |
| `configs/opencode.json` | OpenCode / Crush |

### Custom Prompts / Skills

Each platform has its own way to provide custom instructions:

| Platform | Directory | Format |
|----------|-----------|--------|
| Claude Code | `.claude/skills/*.md` | Markdown |
| OpenCode / Crush | `.opencode/commands/*.md` | Markdown |

This project includes pre-made skill files for both platforms to help the AI assistant use the computing backends effectively.

## Tools

### compute(code, backend?)

Execute scientific computing code.

```python
# Plot with Octave
compute("x = 0:0.1:10; y = sin(x); plot(x, y)", "octave")

# Symbolic computation with Maxima
compute("integrate(sin(x), x)", "maxima")
compute("diff(x^3 * exp(x), x)", "maxima")

# Mathematica
compute("Plot[Sin[x], {x, 0, 2 Pi}]", "mathematica")
compute("Integrate[x^2, x]", "mathematica")
```

### list_backends()

List all available backends and their capabilities.

### reset(backend?)

Reset backend state, clear all variables.

### stop_backend(backend?)

Stop and close a backend to free memory. The backend can be restarted when needed.

### doc(symbol, backend?)

Query documentation for a symbol.

```python
doc("Plot3D", "mathematica")  # Mathematica usage
doc("integrate", "maxima")     # Maxima usage
```

## Usage Examples

Ask your AI assistant:

```
画一个 sin(x) 的图像

计算 ∫x²dx 从 0 到 1

求解 x² - 4 = 0

查一下 NDSolve 的用法
```

## Documentation

- `docs/maxima.md` - Maxima 使用指南
- `docs/octave.md` - Octave 使用指南
- `DESIGN.md` - 项目设计文档

## Requirements

- Python 3.10+
- For Maxima backend: Maxima + gnuplot
- For Octave backend: GNU Octave + gnuplot
- For Mathematica backend: Wolfram Mathematica

## License

MIT