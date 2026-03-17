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
│  │   Backend   │ │   Backend   │ │   (同一 Python 环境)    │ │
│  └──────┬──────┘ └──────┬──────┘ └────────────────────────┘ │
│         │               │                                    │
│         ▼               ▼                                    │
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐            │
│  │  Wolfram    │ │   octave    │ │      R      │   sage     │
│  │  Kernel     │ │   进程      │ │    进程     │   进程     │
│  └─────────────┘ └─────────────┘ └─────────────┘            │
│         │               │               │          │         │
│         ▼               ▼               ▼          ▼         │
│   独立安装        独立安装         独立安装    conda 环境     │
│   (官方安装)     (apt/brew)      (apt/brew)  (Python 3.11)  │
└─────────────────────────────────────────────────────────────┘
```

**关键理解**：
- MCP 服务器只需要 **一个** Python 环境
- 各后端（除 py_scientific）都是独立进程，不共享 Python 环境
- SageMath 需要单独的 conda 环境（Python < 3.13）

### Step 1: Install MCP Server

```bash
# 方法 A: 使用 venv (推荐)
python3 -m venv .venv
source .venv/bin/activate
pip install -e .

# 方法 B: 使用 conda
conda create -n scicompute python=3.12 -y
conda activate scicompute
pip install -e .
```

### Step 2: Install Computing Backends

按需安装，不需要全部安装：

#### Python Scientific Backend

已在 MCP 服务器环境中安装，无需额外配置。

#### SageMath Backend

SageMath 需要 Python < 3.13，必须用 conda 单独安装：

```bash
# 配置镜像（可选，国内用户推荐）
conda config --add channels https://mirrors.tuna.tsinghua.edu.cn/anaconda/cloud/conda-forge/

# 创建 SageMath 环境
conda create -n sage python=3.11 -y
conda install -n sage -c conda-forge sage -y
```

配置路径（二选一）：

```bash
# 方法 A: 环境变量（推荐）
export SAGE_PATH="$HOME/miniconda3/envs/sage/bin/sage"

# 方法 B: 修改代码中的 SAGE_PATH
# 编辑 src/scicompute_mcp/backends/sage.py
```

#### R Backend

```bash
# Ubuntu/Debian
sudo apt install r-base

# macOS
brew install r

# Windows: 下载 CRAN 安装包
```

#### Octave Backend

```bash
# Ubuntu/Debian
sudo apt install octave gnuplot

# macOS
brew install octave gnuplot

# Windows: 下载 Octave 安装包
```

#### Mathematica Backend

1. 从 [Wolfram 官网](https://www.wolfram.com/mathematica/) 购买并安装
2. 配置路径：

```bash
export MATHEMATICA_KERNEL_PATH="/usr/local/Wolfram/Wolfram/14.3/Executables/WolframKernel"
```

### Step 3: Configure MCP Client

创建配置文件 `.mcp.json`（放在项目根目录或用户目录）：

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

| 变量 | 说明 | 示例 |
|------|------|------|
| `SAGE_PATH` | SageMath 路径 | `$HOME/miniconda3/envs/sage/bin/sage` |
| `MATHEMATICA_KERNEL_PATH` | WolframKernel 路径 | `/usr/local/Wolfram/Wolfram/14.3/Executables/WolframKernel` |
| `SCICOMPUTE_PRIORITY` | 后端优先级 | `mathematica,sage,py_scientific` |

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