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

## SageMath 绘图无法显示

**状态**: Open
**优先级**: Medium
**发现时间**: 2026-03-18

### 问题描述

在所有客户端（OpenCode、Claude Code CLI）中，SageMath 后端的绘图都无法正常显示图片，而其他后端（Octave、R、Mathematica、py_scientific）正常。

| 后端 | OpenCode | Claude Code CLI |
|------|----------|-----------------|
| Octave | ✅ | ✅ |
| R | ✅ | ✅ |
| Mathematica | ✅ | ✅ |
| py_scientific | ✅ | ✅ |
| SageMath | ❌ | ❌ |

### 可能原因

SageMath 的 `_execute_plot()` 方法将代码包装为 matplotlib 格式，但 SageMath 原生 `plot()` 返回 Graphics 对象，两者不兼容。

### 待调查

- 检查 `_detect_plot()` 和 `_execute_plot()` 的逻辑
- 测试 SageMath 原生绘图与 matplotlib 绑图的区别
- 考虑移除 matplotlib 包装，让用户手动 `.save()`

