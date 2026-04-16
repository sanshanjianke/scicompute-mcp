# Known Issues

## MCP ImageContent Display Issue

**Status**: Open
**Priority**: High
**Reported**: 2026-03-18

### Problem

MCP tools returning `ImageContent` behave inconsistently across different clients:

| Client | AI Can See Image | Notes |
|--------|------------------|-------|
| OpenCode | ✅ | Works |
| Claude Code CLI | ✅ | Works |
| Claude Code VSCode Extension | ❌ | Empty output |

### Test Results

- MCP server returns correctly: `ImageContent` contains valid base64 data
- User can see the image in UI
- But AI model cannot receive the image content

### Related Issues

- [anthropics/claude-code#31208](https://github.com/anthropics/claude-code/issues/31208) - MCP ImageContent returned as text in tool results
- [anthropics/claude-code#34517](https://github.com/anthropics/claude-code/issues/34517) - API Error 400 for tool_result image media type

### Workaround

Use Claude Code CLI or OpenCode instead of VSCode extension.

---

## SageMath Plot Display Issue

**Status**: Open
**Priority**: Medium
**Reported**: 2026-03-18

### Problem

SageMath backend plots don't display in any client (OpenCode, Claude Code CLI), while other backends (Octave, R, Mathematica, py_scientific) work correctly.

| Backend | OpenCode | Claude Code CLI |
|---------|----------|-----------------|
| Octave | ✅ | ✅ |
| R | ✅ | ✅ |
| Mathematica | ✅ | ✅ |
| py_scientific | ✅ | ✅ |
| SageMath | ❌ | ❌ |

### Possible Cause

SageMath's `_execute_plot()` method wraps code as matplotlib format, but SageMath native `plot()` returns Graphics object, which are incompatible.

### To Investigate

- Check `_detect_plot()` and `_execute_plot()` logic
- Test SageMath native plotting vs matplotlib plotting
- Consider removing matplotlib wrapper, let users call `.save()` manually

---

## doc Tool RAG Improvement

**Status**: ✅ Resolved
**Priority**: Low
**Reported**: 2026-03-18
**Resolved**: 2026-04-16

### Problem

Original `doc` tool only called built-in help commands with limited functionality.

### Solution

Removed `doc` tool entirely. Instead, use skill-based approach:

1. Created `.opencode/skills/doc-expert.md` with documentation URLs for all backends
2. AI uses Task tool to launch subagent for fetching documentation
3. Subagent uses webfetch to get online documentation

This approach:
- No need for RAG/vector database complexity
- Always gets latest documentation from official sources
- Simpler implementation, no additional dependencies

---

## MATLAB and Maple Backends

**Status**: Pending
**Priority**: Medium
**Reported**: 2026-03-18

### Problem

Planned to add MATLAB and Maple backend support, but software not yet installed.

### TODO

- [ ] Install MATLAB
- [ ] Install Maple
- [ ] Implement MATLAB backend (similar to Octave but using official API)
- [ ] Implement Maple backend (symbolic computation)
- [ ] Testing and documentation

---

## Julia Backend MCP Connection Issue

**Status**: ✅ **FIXED**
**Priority**: High
**Reported**: 2026-04-15
**Updated**: 2026-04-16

### Problem

Julia 后端在客户端中会在几次调用后断开 MCP 连接。

### Root Cause

**子进程继承了父进程的 stdin 文件描述符！**

Julia 后端使用 `subprocess.Popen` 启动子进程时，默认情况下子进程会继承父进程的 stdin。这会干扰 MCP 服务器的 stdio 通信，导致连接断开。

### Fix

在 `subprocess.Popen` 中添加 `stdin=subprocess.DEVNULL`：

```python
_process = subprocess.Popen(
    [JULIA_PATH, "-e", server_code],
    stdin=subprocess.DEVNULL,  # 关键：不继承 stdin
    stdout=subprocess.DEVNULL,
    stderr=subprocess.DEVNULL
)
```

### Impact

| Backend | Before Fix | After Fix |
|---------|------------|-----------|
| Julia | ❌ Disconnect after 2-3 calls | ✅ Works correctly |
| py_scientific | ❌ Same issue | Needs same fix |

### Lesson Learned

当 MCP 服务器使用 stdio 通信时，所有子进程必须明确设置 `stdin=subprocess.DEVNULL`，否则子进程会干扰父进程的 stdio 通信。

---

## R Backend Process Recovery Issue

**Status**: ✅ **FIXED**
**Priority**: High
**Reported**: 2026-04-16

### Problem

R 后端在进程崩溃后无法自动恢复，后续调用都会失败。

### Root Cause

1. `is_running` 属性只检查 `_process is not None`，没有检查进程是否真的活着
2. `start()` 方法检查 `_process is not None` 但进程可能已经死亡
3. `evaluate()` 方法没有在进程死亡时尝试重启

### Fix

```python
# 1. is_running 检查进程是否真的活着
@property
def is_running(self) -> bool:
    return _process is not None and _process.poll() is None

# 2. start() 检查进程是否存活
def start(self) -> bool:
    if _process is not None and _process.poll() is None:
        return True
    _process = None  # 重置死亡进程
    # ... 启动新进程

# 3. evaluate() 自动重启死亡进程
def evaluate(self, code: str, timeout: float = 30.0) -> Result:
    if _process is None or _process.poll() is not None:
        if not self.start():
            return Result(success=False, ...)
```

### Test Results

| 功能 | 状态 |
|------|------|
| 变量持久化 | ✅ |
| 文件读写 | ✅ |
| 统计分析 | ✅ |
| 绘图 | ✅ |
| 进程崩溃后自动恢复 | ✅ |

---

## Octave Backend oct2py Dependency

**Status**: Known Limitation
**Priority**: Low
**Reported**: 2026-03-18

### Problem

For PyPI compatibility, `oct2py` dependency uses PyPI version (5.8.0) instead of GitHub version. The GitHub version has bug fixes not yet released to PyPI.

### Changes Made

- Moved `oct2py` from required to optional dependency: `pip install scicompute-mcp[octave]`
- Uses PyPI version `oct2py>=5.8.0` instead of `git+https://github.com/blink1073/oct2py.git@main`

### Workaround

If you encounter issues with PyPI version:

```bash
pip uninstall oct2py
pip install git+https://github.com/blink1073/oct2py.git@main
```

### Related

- [blink1073/oct2py](https://github.com/blink1073/oct2py) - GitHub repository