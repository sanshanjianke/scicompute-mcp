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

**Status**: Open
**Priority**: Low
**Reported**: 2026-03-18

### Problem

Current `doc` tool only calls built-in help commands, limited functionality:

| Backend | Current Implementation | Issue |
|---------|------------------------|-------|
| Mathematica | `Information[symbol, "Usage"]` | Only brief usage |
| Octave | `help("symbol")` | Terminal help text |
| SageMath | `symbol?` | IPython help |
| Python | `inspect.getdoc()` | Only docstring |
| R | `?symbol` | Brief help |

### Proposal: RAG System

Convert `doc` to a RAG (Retrieval-Augmented Generation) based documentation retrieval system:

1. **Offline Documentation** - Pre-download official docs for each backend
2. **Vector Database** - e.g., FAISS, ChromaDB
3. **Semantic Search** - Retrieve relevant doc snippets based on user queries
4. **Return to AI** - Provide as context for AI to generate answers

### Technical Approach

```python
# Example architecture
class DocRAG:
    def __init__(self):
        self.vector_db = ChromaDB()
        self.embeddings = SentenceTransformer()

    def query(self, question: str, backend: str) -> str:
        # 1. Vector search
        docs = self.vector_db.search(question, backend)
        # 2. Return relevant doc snippets
        return docs
```

### TODO

- [ ] Research offline documentation sources (official sites)
- [ ] Choose vector database (FAISS vs ChromaDB vs others)
- [ ] Design document chunking strategy
- [ ] Implement embedding and retrieval
- [ ] Integrate into MCP tool

### Current Status

Keeping existing `doc` tool as interim solution, RAG system as long-term goal.

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