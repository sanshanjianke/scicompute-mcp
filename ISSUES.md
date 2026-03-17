# 待解决问题

## MCP ImageContent 显示问题

**状态**: Open
**优先级**: High
**发现时间**: 2026-03-18

### 问题描述

MCP 工具返回 `ImageContent` 时，不同客户端表现不一致：

| 客户端 | AI 能看到图片 | 备注 |
|--------|--------------|------|
| OpenCode | ✅ | 正常 |
| Claude Code CLI | ✅ | 正常 |
| Claude Code VSCode 扩展 | ❌ | 输出为空 |

### 测试结果

- MCP 服务器返回正确：`ImageContent` 包含有效的 base64 数据
- 用户能在 UI 上看到图片
- 但 AI 模型无法接收到图片内容

### 相关 Issue

- [anthropics/claude-code#31208](https://github.com/anthropics/claude-code/issues/31208) - MCP ImageContent returned as text in tool results
- [anthropics/claude-code#34517](https://github.com/anthropics/claude-code/issues/34517) - API Error 400 for tool_result image media type

### 临时方案

使用 CLI 版 Claude Code 或 OpenCode 代替 VSCode 扩展。

---

## 后端路径硬编码问题

**状态**: Open
**优先级**: Medium
**发现时间**: 2026-03-18

### 问题描述

部分后端路径硬编码，用户换环境后无法使用：

| 后端 | 当前状态 | 建议方案 |
|------|----------|----------|
| Mathematica | 硬编码 | 环境变量 + 自动查找 |
| SageMath | 硬编码 | 环境变量 + 自动查找 |
| Octave | ✅ 自动查找 | - |
| R | ✅ 自动查找 | - |

### 建议方案

```python
# 优先使用环境变量，否则自动查找
SAGE_PATH = os.environ.get("SAGE_PATH") or shutil.which("sage") or "/usr/bin/sage"
```

---

## 已解决

### stop() 安全设计 (2026-03-18)

**问题**: AI 可能误调用 `stop()` 导致所有后端数据丢失。

**解决方案**:
- `stop()` 不带参数时只返回运行中的后端列表，不关闭任何进程
- `stop("backend")` 关闭指定后端
- `stop("ALL")` 关闭所有后端

每个后端添加了 `is_running` 属性用于状态检测。