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

---

## doc 工具改为 RAG 系统

**状态**: Open
**优先级**: Low
**发现时间**: 2026-03-18

### 问题描述

当前 `doc` 工具只是调用各后端的内置帮助命令，功能有限：

| 后端 | 当前实现 | 问题 |
|------|----------|------|
| Mathematica | `Information[symbol, "Usage"]` | 只有简短用法 |
| Octave | `help("symbol")` | 终端帮助文本 |
| SageMath | `symbol?` | IPython 帮助 |
| Python | `inspect.getdoc()` | 只有 docstring |
| R | `?symbol` | 简短帮助 |

### 改进方案：RAG 系统

将 `doc` 改为基于 RAG (Retrieval-Augmented Generation) 的文档检索系统：

1. **离线文档库** - 预下载各后端的官方文档
2. **向量数据库** - 如 FAISS、ChromaDB
3. **语义检索** - 根据用户问题检索相关文档片段
4. **返回给 AI** - 作为上下文提供给 AI 生成回答

### 技术方案

```python
# 示例架构
class DocRAG:
    def __init__(self):
        self.vector_db = ChromaDB()  # 向量数据库
        self.embeddings = SentenceTransformer()  # 嵌入模型

    def query(self, question: str, backend: str) -> str:
        # 1. 向量检索
        docs = self.vector_db.search(question, backend)
        # 2. 返回相关文档片段
        return docs
```

### 待办事项

- [ ] 调研离线文档获取方式（各后端官网/文档站点）
- [ ] 选择向量数据库（FAISS vs ChromaDB vs 其他）
- [ ] 设计文档分块策略
- [ ] 实现嵌入和检索
- [ ] 集成到 MCP 工具

### 当前状态

保留现有 `doc` 工具作为临时方案，RAG 系统作为长期目标。

---

## MATLAB 和 Maple 后端

**状态**: Pending
**优先级**: Medium
**发现时间**: 2026-03-18

### 问题描述

计划添加 MATLAB 和 Maple 后端支持，但软件尚未安装完成。

### 待办事项

- [ ] 安装 MATLAB
- [ ] 安装 Maple
- [ ] 实现 MATLAB 后端（类似 Octave 但使用官方 API）
- [ ] 实现 Maple 后端（符号计算）
- [ ] 测试和文档

