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

---

## stdout Not Captured for py_scientific, octave, julia Backends

**Status**: Open
**Priority**: Medium
**Reported**: 2026-04-17

### Problem

The following backends do not capture stdout output (print/disp/println), only expression return values:
- py_scientific
- octave
- julia

These backends work correctly (both print and return values):
- mathematica (Print works)
- r (print works)
- maxima (print works)
- sage (print works)

### Test Results

| Backend | print/disp/println | Expression Return |
|---------|-------------------|-------------------|
| py_scientific | ❌ No output | ✅ Normal |
| octave | ❌ No output | ✅ Normal |
| julia | ❌ No output | ✅ Normal |
| mathematica | ✅ Print works | ✅ Normal |
| r | ✅ print works | ✅ Normal |
| maxima | ✅ print works | ✅ Normal |
| sage | ✅ print works | ✅ Normal |

### Impact

Users cannot use print statements for debugging or output in py_scientific, octave, and julia backends.

### Workaround

For these backends, use expression return values instead of print:
- py_scientific: Just type the expression without print
- octave: Type the expression without semicolon
- julia: Type the expression (it will return the value)

### To Investigate

- Check how stdout is captured in each backend
- Compare implementation with working backends (mathematica, r, maxima, sage)
- May need to redirect/capture subprocess stdout properly

### Related Files

- src/scicompute_mcp/backends/py_scientific.py
- src/scicompute_mcp/backends/octave.py
- src/scicompute_mcp/backends/julia.py
