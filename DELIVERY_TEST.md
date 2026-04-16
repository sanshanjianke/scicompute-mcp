# 交付测试报告

**测试日期**: 2026-04-16
**测试服务器**: ssjk@115.190.1.39
**系统环境**: Debian 12 (Linux 6.1.0-18-amd64)
**Python**: 3.11.2
**OpenCode**: 1.4.6

---

## 一、安装测试

### 1.1 uv/uvx 安装

| 测试项 | 结果 | 说明 |
|--------|------|------|
| `curl -LsSf https://astral.sh/uv/install.sh \| sh` | ❌ 失败 | 网络超时 |
| `pip install --user uv` | ❌ 失败 | PEP 668 错误 |
| `pipx install uv` | ⏱️ 超时 | 网络慢，安装超时 |

**结论**: uv 安装困难，建议使用 pip 直接安装

### 1.2 scicompute-mcp 安装

| 测试项 | 结果 | 说明 |
|--------|------|------|
| `pip install scicompute-mcp` | ❌ 失败 | PEP 668 错误 |
| `pip install --break-system-packages scicompute-mcp` | ⏱️ 超时 | PyPI 网络慢 |
| `pip install --break-system-packages -i https://pypi.tuna.tsinghua.edu.cn/simple scicompute-mcp` | ✅ 成功 | 使用清华镜像 |

**结论**: 需要使用 `--break-system-packages` 和国内镜像

### 1.3 PATH 配置

| 测试项 | 结果 | 说明 |
|--------|------|------|
| 安装后命令可用 | ❌ 失败 | ~/.local/bin 不在 PATH |
| 添加到 .bashrc | ✅ 成功 | `echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.bashrc` |

**结论**: 需要手动配置 PATH

---

## 二、后端测试

### 2.1 后端可用性

| 后端 | 安装状态 | 测试结果 | 说明 |
|------|----------|----------|------|
| py_scientific | ✅ 内置 | ✅ 通过 | 默认可用 |
| R | ✅ 已安装 | ✅ 通过 | `sudo apt install r-base` |
| Octave | ✅ 已安装 | ✅ 通过 | `sudo apt install octave gnuplot` + `pip install oct2py` |
| Julia | ❌ 未安装 | - | 需要单独安装 |
| Mathematica | ❌ 未安装 | - | 商业软件 |
| SageMath | ❌ 未安装 | - | 需要单独安装 |
| MATLAB | ❌ 未安装 | - | 商业软件 |

### 2.2 R 后端测试

```bash
# 安装
sudo apt install r-base

# 测试
python3 -c '
from scicompute_mcp.backends.r import RBackend
b = RBackend()
b.start()
r = b.evaluate("1 + 1")
print(r.content[0].text)  # 输出: 2
b.stop()
'
```

**结果**: ✅ 成功

### 2.3 Octave 后端测试

```bash
# 安装
sudo apt install octave gnuplot
pip install --break-system-packages oct2py

# 测试
python3 -c '
from scicompute_mcp.backends.octave import OctaveBackend
b = OctaveBackend()
b.start()
r = b.evaluate("1 + 1")
print(r.content[0].text)  # 输出: 2.0
b.stop()
'
```

**结果**: ✅ 成功（有 X11 警告，不影响功能）

### 2.4 Octave X11 警告

```
octave: X11 DISPLAY environment variable not set
octave: disabling GUI features
```

**影响**: 无，只是禁用了 GUI 功能，命令行功能正常

---

## 三、OpenCode 集成测试

### 3.1 配置文件格式

| 配置文件 | 格式 | 结果 |
|----------|------|------|
| `~/.opencode.json` | `{"mcpServers": {...}}` | ❌ 未被读取 |
| `~/.config/opencode/opencode.json` | `{"mcpServers": {...}}` | ❌ 报错 "Unrecognized key: mcpServers" |
| `.opencode/mcp.json` | `{"servers": {...}}` | ❌ 未被读取 |

### 3.2 OpenCode MCP 命令

```bash
# 查看帮助
opencode mcp --help

# 列出服务器
opencode mcp list
# 输出: No MCP servers configured

# 添加服务器（需要交互式输入）
opencode mcp add
```

### 3.3 配置问题分析

OpenCode 1.4.6 的 MCP 配置方式与 README 文档不一致：

1. **README 中的配置格式**:
   ```json
   {
     "mcpServers": {
       "scicompute": {
         "type": "stdio",
         "command": "scicompute-mcp"
       }
     }
   }
   ```

2. **OpenCode 实际接受的配置**: 
   - 不接受 `mcpServers` 键
   - 需要使用 `opencode mcp add` 命令添加（交互式）

---

## 四、问题汇总

### 4.1 安装问题

| # | 问题 | 严重程度 | 解决方案 |
|---|------|----------|----------|
| 1 | uv/uvx 安装困难 | 中 | 使用 pip + --break-system-packages |
| 2 | PEP 668 限制 | 高 | 使用 --break-system-packages 或 pipx |
| 3 | PyPI 网络慢 | 高 | 使用国内镜像源 |
| 4 | PATH 未配置 | 中 | 添加到 .bashrc |

### 4.2 后端问题

| # | 问题 | 严重程度 | 解决方案 |
|---|------|----------|----------|
| 5 | Octave 需要 oct2py | 中 | pip install oct2py |
| 6 | Octave X11 警告 | 低 | 无影响，可忽略 |

### 4.3 OpenCode 集成问题

| # | 问题 | 严重程度 | 解决方案 |
|---|------|----------|----------|
| 7 | 配置格式不匹配 | 高 | 需要更新 README 或使用 `opencode mcp add` |
| 8 | 交互式配置 | 中 | 无法自动化，需要手动操作 |

---

## 五、建议修复

### 5.1 README 改进

1. **添加 OpenCode 1.4.6+ 配置说明**:
   ```markdown
   ### OpenCode 1.4.6+
   
   OpenCode 1.4.6+ 使用命令行添加 MCP 服务器：
   
   ```bash
   opencode mcp add
   # 然后按提示输入：
   # - Name: scicompute
   # - Type: stdio
   # - Command: /home/username/.local/bin/scicompute-mcp
   ```
   ```

2. **更新配置文件格式说明**:
   ```markdown
   > **注意**: OpenCode 1.4.6+ 不再使用 JSON 配置文件添加 MCP 服务器，
   > 请使用 `opencode mcp add` 命令。
   ```

### 5.2 pyproject.toml 改进

添加 oct2py 到可选依赖（已添加）：
```toml
[project.optional-dependencies]
octave = ["oct2py>=5.8.0"]
```

---

## 六、测试命令记录

### 完整安装流程（Debian 12）

```bash
# 1. 安装 scicompute-mcp
pip install --break-system-packages -i https://pypi.tuna.tsinghua.edu.cn/simple scicompute-mcp

# 2. 配置 PATH
echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.bashrc
source ~/.bashrc

# 3. 安装后端（可选）
sudo apt install r-base                    # R 后端
sudo apt install octave gnuplot            # Octave 后端
pip install --break-system-packages oct2py # Octave Python 绑定

# 4. 配置 OpenCode（交互式）
opencode mcp add
# 输入: scicompute, stdio, /home/ssjk/.local/bin/scicompute-mcp

# 5. 验证
opencode mcp list
```

---

## 七、结论

### 成功项
- ✅ scicompute-mcp 安装成功
- ✅ R 后端工作正常
- ✅ Octave 后端工作正常
- ✅ py_scientific 后端工作正常

### 待解决项
- ⚠️ OpenCode 配置方式与 README 不一致
- ⚠️ 需要更新 README 说明 OpenCode 1.4.6+ 的配置方法
- ⚠️ uv/uvx 安装困难，建议优先使用 pip

### 建议优先级
1. **高**: 更新 README 说明 OpenCode 1.4.6+ 配置方法
2. **中**: 添加国内镜像源使用说明
3. **低**: 优化 Octave X11 警告处理
