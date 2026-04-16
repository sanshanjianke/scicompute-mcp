# 安装问题记录

**服务器**: [已移除]
**系统**: Debian 12 (Linux 6.1.0-18-amd64)
**Python**: 3.11.2
**日期**: 2026-04-16

## 问题列表

### 1. uv/uvx 安装失败

**问题描述**: 
README 推荐使用 `uvx scicompute-mcp` 安装，但服务器上没有安装 uv/uvx。

**尝试方案**:
- `curl -LsSf https://astral.sh/uv/install.sh | sh` - 网络超时失败
- `pip install --user uv` - PEP 668 externally-managed-environment 错误

**解决方案**:
```bash
# 方案1: 使用 apt 安装 pipx
sudo apt install -y pipx
pipx install uv

# 方案2: 使用国内镜像直接 pip 安装
pip install --break-system-packages -i https://pypi.tuna.tsinghua.edu.cn/simple scicompute-mcp
```

### 2. PEP 668 externally-managed-environment

**问题描述**:
Debian 12 默认禁止使用 pip 直接安装包，会报错：
```
error: externally-managed-environment
× This environment is externally managed
```

**解决方案**:
- 使用 `--break-system-packages` 参数
- 或使用 pipx 安装应用
- 或创建虚拟环境

### 3. ~/.local/bin 不在 PATH 中

**问题描述**:
pip 安装后警告：
```
WARNING: The script scicompute-mcp is installed in '/home/ssjk/.local/bin' which is not on PATH.
```

**解决方案**:
```bash
# 添加到 PATH
echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.bashrc
source ~/.bashrc
```

### 4. 计算后端未安装

**问题描述**:
服务器上只有 py_scientific 后端可用，其他后端未安装：
- Mathematica: 未安装
- SageMath: 未安装
- Octave: 未安装
- R: 未安装
- Julia: 未安装
- MATLAB: 未安装

**影响**: 
用户只能使用 Python 科学计算功能，无法使用其他后端。

### 5. 网络问题

**问题描述**:
- 官方 PyPI 源速度很慢或超时
- uv 官方安装脚本下载失败

**解决方案**:
使用国内镜像源：
```bash
pip install -i https://pypi.tuna.tsinghua.edu.cn/simple scicompute-mcp
```

## README 改进建议

1. **添加 Debian/Ubuntu 特殊说明**:
   ```markdown
   ### Debian 12+ / Ubuntu 23.04+
   
   这些系统默认启用 PEP 668，需要使用以下方式之一：
   
   ```bash
   # 方式1: 使用 --break-system-packages
   pip install --break-system-packages scicompute-mcp
   
   # 方式2: 使用 pipx
   sudo apt install -y pipx
   pipx install scicompute-mcp
   
   # 方式3: 使用国内镜像（推荐）
   pip install --break-system-packages -i https://pypi.tuna.tsinghua.edu.cn/simple scicompute-mcp
   ```
   ```

2. **添加 PATH 配置说明**:
   ```markdown
   ### 配置 PATH
   
   如果提示命令未找到，需要将 ~/.local/bin 添加到 PATH：
   
   ```bash
   echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.bashrc
   source ~/.bashrc
   ```
   ```

3. **添加后端安装检查**:
   ```markdown
   ### 检查可用后端
   
   安装后可以检查哪些后端可用：
   
   ```bash
   python3 -c 'from scicompute_mcp.manager import BackendManager; print(BackendManager().list_available())'
   ```
   ```

## 成功安装步骤（Debian 12）

```bash
# 1. 安装 scicompute-mcp（使用国内镜像）
pip install --break-system-packages -i https://pypi.tuna.tsinghua.edu.cn/simple scicompute-mcp

# 2. 配置 PATH
echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.bashrc
source ~/.bashrc

# 3. 创建 OpenCode 配置
mkdir -p ~/.config/opencode
cat > ~/.config/opencode/opencode.json << 'EOF'
{
  "mcpServers": {
    "scicompute": {
      "type": "stdio",
      "command": "/home/ssjk/.local/bin/scicompute-mcp"
    }
  }
}
EOF

# 4. 验证安装
scicompute-mcp --help
```
