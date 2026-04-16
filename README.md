# SciCompute MCP Server

MCP server for scientific computing with multiple backends. Provides AI coding assistants with mathematical computation and visualization capabilities.

## Features

- Multiple computing backends (Mathematica, Octave, Python Scientific, R, SageMath)
- Image output support (plots, graphics)
- Automatic backend selection
- Persistent session state (variables persist across calls)
- Documentation query for unknown symbols
- Multi-platform support (Claude Code, Claude Desktop, OpenCode/Crush)
- **Recommended**: Use alongside [official MATLAB MCP Server](https://github.com/matlab/matlab-mcp-core-server) for MATLAB support

## Supported Backends

| Backend | Status | Capabilities |
|---------|--------|--------------|
| Mathematica | ✅ Ready | symbolic, numeric, plot, image, audio |
| SageMath | ✅ Ready | symbolic, numeric, plot |
| Python Scientific | ✅ Ready | symbolic, numeric, plot |
| R | ✅ Ready | numeric, plot |
| Octave | ✅ Ready | numeric, plot |
| Julia | ✅ Ready | numeric, plot |
| Maxima | ✅ Ready | symbolic, numeric, plot |

### MATLAB Support

For **MATLAB** support, we recommend using the official [MATLAB MCP Core Server](https://github.com/matlab/matlab-mcp-core-server) from MathWorks alongside SciCompute:

**Why use the official server?**
- No Python version restrictions (works with any Python version)
- No library installation or patching required
- Standalone Go binary with no dependencies
- Additional features: code analysis, test running, toolbox detection

**Installation:**

1. Download the MATLAB MCP Core Server binary from the [latest release](https://github.com/matlab/matlab-mcp-core-server/releases/latest):
   ```bash
   # Linux x86_64
   curl -L -o ~/matlab-mcp-core-server https://github.com/matlab/matlab-mcp-core-server/releases/latest/download/matlab-mcp-core-server-glnxa64
   chmod +x ~/matlab-mcp-core-server
   ```

2. Configure both servers in your MCP config:
   ```json
   {
     "mcpServers": {
       "scicompute": {
         "command": "uvx",
         "args": ["scicompute-mcp"]
       },
       "matlab": {
         "command": "/home/username/matlab-mcp-core-server",
         "args": ["--matlab-root=/usr/local/MATLAB/R2024a"]
       }
     }
   }
   ```

See the [MATLAB MCP Core Server documentation](https://github.com/matlab/matlab-mcp-core-server) for more details.

## Installation

### Quick Start (Recommended)

```bash
# Install and run with uvx (auto-manages environment)
uvx scicompute-mcp

# Or install with pip
pip install scicompute-mcp
scicompute-mcp
```

### Debian 12+ / Ubuntu 23.04+

These systems enable PEP 668 by default, which prevents direct pip installs. Use one of these methods:

```bash
# Method 1: Use --break-system-packages (quick)
pip install --break-system-packages scicompute-mcp

# Method 2: Use pipx (recommended for CLI tools)
sudo apt install -y pipx
pipx install scicompute-mcp

# Method 3: Use China mirror (faster in China)
pip install --break-system-packages -i https://pypi.tuna.tsinghua.edu.cn/simple scicompute-mcp
```

After installation, add `~/.local/bin` to PATH if needed:

```bash
echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.bashrc
source ~/.bashrc
```

### Install with Optional Backends

```bash
# With Mathematica support
pip install scicompute-mcp[mathematica]

# With Octave support
pip install scicompute-mcp[octave]

# With all backends
pip install scicompute-mcp[all]
```

### Environment Architecture

```
┌───────────────────────────────────────────────────────────────────────────┐
│                    MCP Server (Python 3.10+)                              │
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐ ┌────────────────────┐  │
│  │ Mathematica │ │   Octave    │ │   MATLAB    │ │   py_scientific    │  │
│  │   Backend   │ │   Backend   │ │   Backend   │ │  (same Python env) │  │
│  └──────┬──────┘ └──────┬──────┘ └──────┬──────┘ └────────────────────┘  │
│         │               │               │                                  │
│         ▼               ▼               ▼                                  │
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐ ┌─────────────┐         │
│  │  Wolfram    │ │   octave    │ │   MATLAB    │ │      R      │  sage   │
│  │  Kernel     │ │   process   │ │   process   │ │   process   │ process │
│  └─────────────┘ └─────────────┘ └─────────────┘ └─────────────┘         │
│         │               │               │               │         │       │
│         ▼               ▼               ▼               ▼         ▼       │
│   Independent     Independent      Independent     Independent  conda     │
│   (official)      (apt/brew)       (official)      (apt/brew)  env       │
└───────────────────────────────────────────────────────────────────────────┘
```

**Key Points**:
- MCP server only needs **one** Python environment
- Each backend (except py_scientific) runs as independent process, not sharing Python environment
- SageMath requires separate conda environment (Python < 3.13)

### Step 1: Install Computing Backends

Install the computing backends you need (not all required):

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

#### Julia Backend

```bash
# Install Julia (recommended: use juliaup)
curl -fsSL https://install.julialang.org | sh

# Or download from https://julialang.org/downloads/

# Install Python package
pip install juliacall
```

#### Mathematica Backend

1. Purchase and install from [Wolfram website](https://www.wolfram.com/mathematica/)
2. Configure path:

```bash
export MATHEMATICA_KERNEL_PATH="/usr/local/Wolfram/Wolfram/14.3/Executables/WolframKernel"
```

## Configuration

### Environment Variables

| Variable | Description | Example |
|----------|-------------|---------|
| `SAGE_PATH` | SageMath path | `$HOME/miniconda3/envs/sage/bin/sage` |
| `MATHEMATICA_KERNEL_PATH` | WolframKernel path | `/usr/local/Wolfram/Wolfram/14.3/Executables/WolframKernel` |
| `JULIA_PATH` | Julia executable path | `$HOME/.juliaup/bin/julia` |
| `SCICOMPUTE_PRIORITY` | Backend priority | `mathematica,sage,julia,py_scientific` |

### Claude Code (`.mcp.json`)

```json
{
  "mcpServers": {
    "scicompute": {
      "command": "uvx",
      "args": ["scicompute-mcp"]
    }
  }
}
```

### Claude Desktop (`claude_desktop_config.json`)

```json
{
  "mcpServers": {
    "scicompute": {
      "command": "uvx",
      "args": ["scicompute-mcp"]
    }
  }
}
```

### OpenCode / Crush

#### OpenCode 1.4.6+

OpenCode 1.4.6+ reads configuration from `~/.config/opencode/opencode.json`:

```json
{
  "$schema": "https://opencode.ai/config.json",
  "mcp": {
    "scicompute": {
      "type": "local",
      "command": ["/home/username/.local/bin/scicompute-mcp"]
    }
  }
}
```

> **Important**: Use absolute path to `scicompute-mcp` (from `pip install`). Avoid `uvx` because it downloads dependencies on first run, which may timeout.

To verify:
```bash
opencode mcp list
```

#### Using `opencode mcp add` (Interactive)

Alternatively, add via interactive command:

```bash
opencode mcp add
# Name: scicompute
# Type: Local
# Command: /home/username/.local/bin/scicompute-mcp
```

#### Older OpenCode versions

For older versions, use `~/.opencode.json`:

```json
{
  "mcpServers": {
    "scicompute": {
      "type": "stdio",
      "command": "/home/username/.local/bin/scicompute-mcp"
    }
  }
}
```

### Local Development

For development or if you want to use a local installation:

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

### Calling Convention

Different MCP clients have different naming conventions for calling tools:

| Client | Format | Example |
|--------|--------|---------|
| Claude Code | `mcp__{server}__{tool}` | `mcp__scicompute__compute(code="1+1")` |
| OpenCode | `{server}_{tool}` | `scicompute_compute(code="1+1")` |

The examples below use the base tool names (`compute`, `list_backends`, `stop`). Your AI assistant will automatically use the correct format for its client.

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

# Julia
compute("plot(rand(10))", "julia")
compute("sqrt(2.0)", "julia")

# MATLAB
compute("plot(1:10, rand(1,10))", "matlab")
compute("[V,D] = eig(magic(3))", "matlab")
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

## Usage Examples

Ask your AI assistant:

```
Plot sin(x) from 0 to 2π

Calculate ∫x²dx from 0 to 1

Solve x² - 4 = 0

Look up NDSolve documentation
```

## Getting Documentation

When you need detailed documentation for a function:

1. The AI can use the **doc-expert skill** (`.opencode/skills/doc-expert.md`)
2. Launch a subagent with Task tool to fetch and extract documentation
3. Supported backends: Mathematica, Python Scientific, R, Julia, Octave, SageMath, Maxima, MATLAB

Example:
```
Task(
  description="Fetch Plot3D docs",
  prompt="Fetch Mathematica documentation for Plot3D from https://reference.wolfram.com/language/ref/plot3d.html",
  subagent_type="general"
)
```

## Documentation

- `docs/sage.md` - SageMath collaboration guide
- `docs/r.md` - R collaboration guide
- `docs/maxima.md` - Maxima collaboration guide
- `docs/octave.md` - Octave collaboration guide
- `.opencode/skills/doc-expert.md` - Documentation URLs and fetch guide

## Requirements

- Miniconda (recommended) or Python 3.10+
- For SageMath backend: conda environment with Python 3.11
- For R backend: R installation
- For Octave backend: GNU Octave + gnuplot
- For Mathematica backend: Wolfram Mathematica
- For MATLAB backend: MATLAB + MATLAB Engine for Python

## License

Unlicense - Public Domain