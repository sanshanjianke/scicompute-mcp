# SciCompute MCP Server

MCP server for scientific computing with multiple backends. Provides AI coding assistants with mathematical computation and visualization capabilities.

## Features

- Multiple computing backends (Mathematica, Octave, Python Scientific, R, SageMath)
- Image output support (plots, graphics)
- Automatic backend selection
- Persistent session state (variables persist across calls)
- Documentation query for unknown symbols
- Multi-platform support (Claude Code, Claude Desktop, OpenCode/Crush)

## Supported Backends

| Backend | Status | Capabilities |
|---------|--------|--------------|
| Mathematica | ✅ Ready | symbolic, numeric, plot, image, audio |
| SageMath | ✅ Ready | symbolic, numeric, plot |
| Python Scientific | ✅ Ready | symbolic, numeric, plot |
| R | ✅ Ready | numeric, plot |
| Octave | ✅ Ready | numeric, plot |
| Maxima | 🔒 Reserved | symbolic, numeric, plot |
| MATLAB | 🔲 Planned | numeric, plot |
| Julia | 🔲 Planned | numeric, plot |

> **Note**: Maxima backend is available but disabled by default. To enable, uncomment the registration line in `manager.py`.

## Installation

### 1. Install Miniconda

```bash
# Download and install Miniconda (command-line only, no GUI needed)
wget https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh
bash Miniconda3-latest-Linux-x86_64.sh -b -p $HOME/miniconda3

# Initialize conda (optional, for shell integration)
$HOME/miniconda3/bin/conda init bash
source ~/.bashrc
```

### 2. Create Environment and Install

```bash
# Clone repository
git clone <repo-url>
cd scicompute_mcp

# Create conda environment
conda create -n scicompute python=3.12 -y
conda activate scicompute

# Install package
pip install -e .
```

### Backend Requirements

#### SageMath Backend

SageMath requires a separate conda environment with Python 3.11 (not compatible with Python 3.13+).

```bash
# Configure conda mirror (optional, for faster downloads in China)
conda config --add channels https://mirrors.tuna.tsinghua.edu.cn/anaconda/cloud/conda-forge/

# Create SageMath environment with Python 3.11
conda create -n sage python=3.11 -y

# Install SageMath
conda install -n sage -c conda-forge sage -y
```

After installation, update the `SAGE_PATH` in `src/scicompute_mcp/backends/sage.py` to match your conda environment path:
```python
SAGE_PATH = "/path/to/miniconda3/envs/sage/bin/sage"
```

#### Python Scientific Backend

Pre-installed with the main package. Includes NumPy, SciPy, SymPy, Matplotlib, Pandas.

#### R Backend

```bash
# Ubuntu/Debian
sudo apt install r-base

# macOS
brew install r

# Or via conda
conda install -n scicompute r-base -c conda-forge
```

#### Octave Backend

```bash
# Ubuntu/Debian
sudo apt install octave gnuplot

# macOS
brew install octave gnuplot

# Or via conda
conda install -n scicompute octave -c conda-forge
```

#### Maxima Backend (Reserved)

```bash
# Ubuntu/Debian
sudo apt install maxima gnuplot

# macOS
brew install maxima gnuplot
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
      "command": "/path/to/miniconda3/envs/scicompute/bin/python",
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
      "command": "/path/to/miniconda3/envs/scicompute/bin/python",
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
      "command": "/path/to/miniconda3/envs/scicompute/bin/python",
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

# Symbolic computation with SageMath
compute("integrate(sin(x), x)", "sage")
compute("diff(x^3 * exp(x), x)", "sage")

# Mathematica
compute("Plot[Sin[x], {x, 0, 2 Pi}]", "mathematica")
compute("Integrate[x^2, x]", "mathematica")

# R Statistics
compute("mean(rnorm(1000))", "r")
compute("hist(rnorm(1000))", "r")

# Python Scientific
compute("sp.integrate(sp.sin(sp.Symbol('x')), sp.Symbol('x'))", "py_scientific")
```

### list_backends()

List all available backends and their capabilities.

### stop(backend?)

Stop backend process and clear all state. Useful to reset variables or free memory. Backend will restart automatically when needed.

```python
stop()          # Stop all backends
stop("octave")  # Stop specific backend
```

### doc(symbol, backend?)

Query documentation for a symbol.

```python
doc("Plot3D", "mathematica")  # Mathematica usage
doc("integrate", "sage")       # SageMath usage
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

- `docs/sage.md` - SageMath 使用指南
- `docs/r.md` - R 语言使用指南
- `docs/maxima.md` - Maxima 使用指南
- `docs/octave.md` - Octave 使用指南
- `DESIGN.md` - 项目设计文档

## Requirements

- Miniconda (recommended) or Python 3.10+
- For SageMath backend: conda environment with Python 3.11
- For R backend: R installation
- For Octave backend: GNU Octave + gnuplot
- For Mathematica backend: Wolfram Mathematica

## License

MIT