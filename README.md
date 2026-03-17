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

### Environment Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    MCP Server (Python 3.10+)                │
│  ┌─────────────┐ ┌─────────────┐ ┌────────────────────────┐ │
│  │ Mathematica │ │   Octave    │ │     py_scientific      │ │
│  │   Backend   │ │   Backend   │ │  (same Python env)     │ │
│  └──────┬──────┘ └──────┬──────┘ └────────────────────────┘ │
│         │               │                                    │
│         ▼               ▼                                    │
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐            │
│  │  Wolfram    │ │   octave    │ │      R      │   sage     │
│  │  Kernel     │ │   process   │ │   process   │  process   │
│  └─────────────┘ └─────────────┘ └─────────────┘            │
│         │               │               │          │         │
│         ▼               ▼               ▼          ▼         │
│   Independent     Independent      Independent   conda env  │
│   (official)      (apt/brew)       (apt/brew)  (Python 3.11)│
└─────────────────────────────────────────────────────────────┘
```

**Key Points**:
- MCP server only needs **one** Python environment
- Each backend (except py_scientific) runs as independent process, not sharing Python environment
- SageMath requires separate conda environment (Python < 3.13)

### Step 1: Install MCP Server

```bash
# Method A: Using venv (recommended)
python3 -m venv .venv
source .venv/bin/activate
pip install -e .

# Method B: Using conda
conda create -n scicompute python=3.12 -y
conda activate scicompute
pip install -e .
```

### Step 2: Install Computing Backends

Install as needed, not all are required:

#### Python Scientific Backend

Pre-installed with the main package, no additional configuration needed.

#### SageMath Backend

SageMath requires Python < 3.13, must be installed separately via conda:

```bash
# Configure mirror (optional, recommended for users in China)
conda config --add channels https://mirrors.tuna.tsinghua.edu.cn/anaconda/cloud/conda-forge/

# Create SageMath environment
conda create -n sage python=3.11 -y
conda install -n sage -c conda-forge sage -y
```

Configure path (choose one):

```bash
# Method A: Environment variable (recommended)
export SAGE_PATH="$HOME/miniconda3/envs/sage/bin/sage"

# Method B: Modify SAGE_PATH in code
# Edit src/scicompute_mcp/backends/sage.py
```

#### R Backend

```bash
# Ubuntu/Debian
sudo apt install r-base

# macOS
brew install r

# Windows: Download from CRAN
```

#### Octave Backend

```bash
# Ubuntu/Debian
sudo apt install octave gnuplot

# macOS
brew install octave gnuplot

# Windows: Download Octave installer
```

#### Mathematica Backend

1. Purchase and install from [Wolfram website](https://www.wolfram.com/mathematica/)
2. Configure path:

```bash
export MATHEMATICA_KERNEL_PATH="/usr/local/Wolfram/Wolfram/14.3/Executables/WolframKernel"
```

### Step 3: Configure MCP Client

Create `.mcp.json` configuration file (in project root or home directory):

```json
{
  "mcpServers": {
    "scicompute": {
      "command": "/path/to/.venv/bin/python",
      "args": ["-m", "scicompute_mcp.server"],
      "cwd": "/path/to/scicompute_mcp"
    }
  }
}
```

### Environment Variables

| Variable | Description | Example |
|----------|-------------|---------|
| `SAGE_PATH` | SageMath path | `$HOME/miniconda3/envs/sage/bin/sage` |
| `MATHEMATICA_KERNEL_PATH` | WolframKernel path | `/usr/local/Wolfram/Wolfram/14.3/Executables/WolframKernel` |
| `SCICOMPUTE_PRIORITY` | Backend priority | `mathematica,sage,py_scientific` |

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

Stop backend process and clear all state. Useful to reset variables or free memory.

```python
stop()          # List running backends (does NOT stop any)
stop("octave")  # Stop specific backend
stop("ALL")     # Stop all running backends
```

**Safety design**: Calling `stop()` without arguments will NOT stop any backends. It returns a list of running backends. This prevents accidental data loss.

### doc(symbol, backend?)

Query documentation for a symbol.

```python
doc("Plot3D", "mathematica")  # Mathematica usage
doc("integrate", "sage")       # SageMath usage
```

## Usage Examples

Ask your AI assistant:

```
Plot sin(x) from 0 to 2π

Calculate ∫x²dx from 0 to 1

Solve x² - 4 = 0

Look up NDSolve usage
```

## Documentation

- `docs/sage.md` - SageMath collaboration guide
- `docs/r.md` - R collaboration guide
- `docs/maxima.md` - Maxima collaboration guide
- `docs/octave.md` - Octave collaboration guide

## Requirements

- Miniconda (recommended) or Python 3.10+
- For SageMath backend: conda environment with Python 3.11
- For R backend: R installation
- For Octave backend: GNU Octave + gnuplot
- For Mathematica backend: Wolfram Mathematica

## License

MIT