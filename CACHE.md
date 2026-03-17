# 缓存 - 恢复上下文

## 项目概述

SciCompute MCP Server - 为 AI 编程助手提供科学计算能力的 MCP 服务。

## 当前状态

### 已完成后端

| 后端 | 状态 | 功能 |
|------|------|------|
| Mathematica | ✅ 完成 | symbolic, numeric, plot, image, audio |
| Octave | ✅ 完成 | numeric, plot, symbolic |
| Maxima | ✅ 完成 | symbolic, numeric, plot |

### Maxima 后端测试结果

| 功能 | 命令示例 | 状态 |
|------|----------|------|
| 微分 | `diff(x^3, x)` | ✅ |
| 积分 | `integrate(exp(x), x)` | ✅ |
| 方程求解 | `solve(x^2-4=0, x)` | ✅ |
| 因式分解 | `factor(x^2-1)` | ✅ |
| 展开 | `expand((a+b)^2)` | ✅ |
| 化简 | `ratsimp(...)` | ✅ |
| 极限 | `limit(sin(x)/x, x, 0)` | ✅ |
| 泰勒展开 | `taylor(sin(x), x, 0, 5)` | ✅ |
| 绘图 | `plot2d(sin(x), [x, 0, 2*%pi])` | ✅ |
| 变量持久化 | `a: 100` 后 `a` | ✅ |
| reset | 清除所有变量 | ✅ |
| stop | 关闭进程 | ✅ |
| 文档查询 | `doc("integrate", "maxima")` | ✅ |

### Maxima 后端关键修复

1. **绘图修复** - `maxima.py:97-152`
   - 原问题：`_wrap_plot_code` 生成的多行代码导致输入计数混乱，等待超时
   - 解决方案：分步执行 `set_plot_option` + 绘图命令，用 `time.sleep` 等待文件生成

2. **reset 修复** - `maxima.py:190-199`
   - 原问题：`reset()` 不清除变量
   - 解决方案：改用 `kill(all)` 清除所有变量

3. **绘图超时修复** - `maxima.py:136-163` (2026-03-16)
   - 原问题：`_execute_plot` 中 `_read_available(timeout - 1.5)` 会等待整个超时时间
   - 解决方案：改为循环检测文件是否生成，最多等待 10 秒，文件生成后立即返回

4. **绘图后计算超时修复** - `maxima.py:136-148` (2026-03-16)
   - 原问题：绘图后后续计算超时，因为 `_input_num` 没有正确更新
   - 原因：`setup_code` 包含两条命令，产生两个输出，`_input_num` 应该 +2；绘图命令 +1
   - 解决方案：在 `_execute_plot` 中正确更新 `_input_num`（setup后 +2，绘图后 +1）

### 进程清理修复 (2026-03-17)

**问题**：用户退出 opencode 时，MCP 后端进程未被清理，导致内存泄漏。

**修复**：
1. `server.py` - 添加 SIGTERM/SIGINT 信号处理器，确保退出时调用 `manager.stop_all()`
2. `octave.py` - 修复 stop 方法：
   - 原问题：`session._engine.repl.pid` 不存在，导致无法强制终止
   - 解决方案：正确路径是 `session._engine.repl.child.pid`，并添加 SIGTERM/SIGKILL 强制终止
3. `maxima.py` - 增强 stop 方法：
   - 添加 SIGTERM 信号终止，避免强制 kill
   - 正确处理 ProcessLookupError 异常
   - 确保 wait() 回收子进程，避免僵尸进程

### MCP 测试结果 (2026-03-17 更新)

| 后端 | 计算测试 | 绘图测试 | 绘图后计算 | 变量持久化 | reset | 多模态显示 |
|------|----------|----------|------------|------------|-------|------------|
| Octave | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| Maxima | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |

注意：MCP 返回的 ImageContent 包含正确的 base64 图片数据，多模态模型可直接看到。

### Maxima 绘图模式 (2026-03-17 新增)

| 模式 | 语法 | 效果 |
|------|------|------|
| 返回图片 (默认) | `plot2d(sin(x), [x, 0, 2*%pi])` | PNG base64 返回 |
| 弹窗显示 | `plot2d(sin(x), [x, 0, 2*%pi], [gnuplot_term, wxt])` | gnuplot wxt 终端弹窗 |
| 弹窗显示 | `plot2d(sin(x), [x, 0, 2*%pi], [gnuplot_term, x11])` | gnuplot x11 终端弹窗 |

实现原理：检测 `[gnuplot_term, wxt/x11/qt/...]` 时跳过 PNG 导出，直接执行原生命令。

### 下一步任务

根据 `DESIGN.md` Phase 2:

- [ ] Python Scientific 后端 (SymPy + NumPy + SciPy + Matplotlib)

## 测试方法

### 直接测试后端

```bash
.venv/bin/python -c "
import sys
sys.path.insert(0, 'src')
from scicompute_mcp.backends.maxima import MaximaBackend

backend = MaximaBackend()
backend.start()

# 测试计算
result = backend.evaluate('diff(x^2, x)')
print(result.content[0].text)

# 测试绘图
result = backend.evaluate('plot2d(sin(x), [x, 0, 2*%pi])')
print('Plot success:', result.success)

# 测试 reset
backend.evaluate('a: 100')
backend.reset()
result = backend.evaluate('a')
print('After reset:', result.content[0].text)

backend.stop()
"
```

### 通过 MCP 测试

```python
# 基础计算
compute("diff(x^2, x)", "maxima")

# 绘图
compute("plot2d(sin(x), [x, 0, 2*%pi])", "maxima")

# 文档查询
doc("integrate", "maxima")

# 重置
reset("maxima")
```

## 依赖

- Maxima: `sudo apt install maxima`
- gnuplot: `sudo apt install gnuplot` (绘图需要)