# 缓存 - 恢复上下文

## 当前状态

- Octave 后端已完成 ✅
- oct2py 使用 git 版本（含 PR #384 修复）✅
- sym 对象输出格式已优化 ✅
- 文档已更新 ✅

## 已完成

### oct2py 修复 (2026-03-16)
- Issue #166 挂了 6 年，2026-03-15 被修复
- sym 对象现在返回 struct 格式
- 已优化 `_process_result()` 提取 `flat`/`unicode` 字段

### 依赖更新
- pyproject.toml 使用 git 依赖: `oct2py @ git+https://github.com/blink1073/oct2py.git@main`
- README 添加后端安装说明

## 待办

### 优先级高
1. **修复文档查询** - Octave `help` 命令返回 0.0，需要改用其他方式
2. **提交代码** - 今天改动未提交

### 优先级中
3. 添加 SymPy 后端
4. 添加 Julia 后端
5. 完善测试覆盖

## 文件位置

- 后端实现：`src/scicompute_mcp/backends/`
- Manager：`src/scicompute_mcp/manager.py`
- Server：`src/scicompute_mcp/server.py`
- 测试：`tests/`

## 已知问题

| 问题 | 状态 | 说明 |
|------|------|------|
| sym 对象序列化 | ✅ 已修复 | oct2py git 版本 |
| help 返回 0.0 | 🔲 待修复 | 需要改用 type 或其他方式 |