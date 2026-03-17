# SciCompute MCP Server

MCP 服务，为 AI 编程助手提供科学计算能力。

## 可用后端

| 后端 | 用途 |
|------|------|
| mathematica | 符号计算、数值计算、绘图 |
| sage | 数论、代数、符号计算 |
| py_scientific | Python 科学计算 (NumPy, SciPy, SymPy, Matplotlib) |
| r | 统计计算、数据可视化 |
| octave | 数值计算、绘图 |

## 使用方式

通过 MCP 工具调用：
- `mcp__scicompute__compute(code, backend)` - 执行计算代码
- `mcp__scicompute__stop(backend)` - 停止后端进程
- `mcp__scicompute__doc(symbol, backend)` - 查询文档

## 配置

后端路径配置在 `src/scicompute_mcp/backends/*.py` 中，可通过环境变量覆盖：
- `SAGE_PATH` - SageMath 路径
- `MATHEMATICA_KERNEL_PATH` - Mathematica 内核路径