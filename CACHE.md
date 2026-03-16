# 缓存 - 恢复上下文

## 当前状态

- Octave 后端已完成 ✅
- oct2py 使用 git 版本（含 PR #384 修复）✅
- sym 对象输出格式已优化 ✅
- **进程清理已修复** ✅ (atexit + stop_all + waitpid)
- **stop_backend 功能已测试** ✅
- 代码已提交 ✅

## 重启后需要做的事

### 1. 重载 MCP 插件

重启 opencode，或热重载 MCP server。

### 2. 修复 Octave 文档查询

**问题：** `help eig` 返回 `0.0`

**位置：** `src/scicompute_mcp/manager.py:120-121`

**当前代码：**
```python
elif selected.name == "octave":
    doc_code = f'help {symbol}'
```

**可能的解决方案：**
1. 使用 `type` 命令查看函数源码
2. 使用 `lookfor` 搜索相关函数
3. 直接调用 `help()` 函数并捕获输出到变量
4. 使用 Octave 的 `doc` 函数（如果有）

**测试命令：**
```python
# 测试各种获取文档的方式
compute("type eig", "octave")
compute("lookfor eigenvalue", "octave")
compute("doc eig", "octave")
```

### 3. 其他待办

- 添加 SymPy 后端
- 添加 Julia 后端
- 完善测试覆盖
- 考虑 Docker 打包

## 已完成

### oct2py 修复 (2026-03-16)
- Issue #166 挂了 6 年，2026-03-15 被修复
- sym 对象现在返回 struct 格式
- 已优化 `_process_result()` 提取 `flat`/`unicode` 字段

### 依赖更新
- pyproject.toml 使用 git 依赖
- README 添加后端安装说明

### 提交记录
```
d70b3cb Refactor Octave backend with oct2py persistent session
90ac24a Fix Octave plot detection using findall instead of function wrapping
27ff465 Add Octave backend with plot support and tests
```

### 进程清理修复 (2026-03-16)
- 问题：Octave/Mathematica 子进程在 MCP server 退出后不关闭，导致内存泄漏
- 修复：
  - `octave.py`: `close()` → `exit()` (oct2py 正确的关闭方法)
  - `manager.py`: 添加 `stop_all()` 方法
  - `server.py`: 注册 `atexit` 回调自动清理
- 新增 `stop_backend` MCP tool：AI 可主动关闭后端释放内存

## 文件位置

| 文件 | 说明 |
|------|------|
| `src/scicompute_mcp/backends/octave.py` | Octave 后端实现 |
| `src/scicompute_mcp/manager.py` | 后端管理器，doc 函数在这里 |
| `src/scicompute_mcp/server.py` | MCP server 入口 |
| `tests/test_octave.py` | Octave 测试 |
| `tests/test_manager.py` | Manager 测试 |

## 测试清单

### 基础功能
```python
compute("2 + 2", "octave")  # → 4
```

### 持久会话
```python
compute("x = 10", "octave")
compute("x * 2", "octave")  # → 20
```

### 符号计算
```python
compute("pkg load symbolic; syms x; diff(x^2, x)", "octave")  # → 2*x
```

### 绘图
```python
compute("x = 0:0.1:10; y = sin(x); plot(x, y)", "octave")  # → PNG
```

### 文档查询（待修复）
```python
doc("eig", "octave")  # 当前返回 0.0
```