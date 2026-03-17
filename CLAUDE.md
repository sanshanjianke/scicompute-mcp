# SciCompute MCP Server

MCP server providing scientific computing capabilities for AI coding assistants.

## Available Backends

| Backend | Use Case |
|---------|----------|
| mathematica | Symbolic computation, numerical computing, plotting |
| sage | Number theory, algebra, symbolic computation |
| py_scientific | Python scientific computing (NumPy, SciPy, SymPy, Matplotlib) |
| r | Statistical computing, data visualization |
| octave | Numerical computing, plotting |

## Usage

Call via MCP tools:
- `mcp__scicompute__compute(code, backend)` - Execute computation code
- `mcp__scicompute__stop(backend)` - Stop backend process
- `mcp__scicompute__doc(symbol, backend)` - Query documentation

## Configuration

Backend paths are configured in `src/scicompute_mcp/backends/*.py`, can be overridden via environment variables:
- `SAGE_PATH` - SageMath path
- `MATHEMATICA_KERNEL_PATH` - Mathematica kernel path