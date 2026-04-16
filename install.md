# SSH反向隧道 + SSHFS 挂载网络磁盘安装报告

## 场景说明

将本地电脑（内网）的磁盘映射到远程服务器（公网），使服务器能够访问本地磁盘内容，并通过Web服务器对外提供文件访问。

## 网络环境

- **服务器**: xxx.xxx.xxx.xxx (公网IP，Debian系统)
- **本地电脑**: 内网环境，无法被服务器直接访问

## 解决方案：SSH反向隧道

使用SSH反向隧道，让服务器通过隧道访问本地。只需要一条SSH命令，无需安装额外软件（frp等）。

## 安装步骤

### 1. 本地电脑配置

#### 1.1 安装并启动SSH服务

```bash
# 安装openssh-server
sudo apt install -y openssh-server

# 启动并启用SSH服务
sudo systemctl start ssh
sudo systemctl enable ssh
```

#### 1.2 建立SSH反向隧道

```bash
# 建立隧道（服务器上会开放2222端口，转发到本地的22端口）
ssh -NfR 2222:localhost:22 服务器用户名@xxx.xxx.xxx.xxx
```

参数说明：
- `-N`: 不执行远程命令
- `-f`: 后台运行
- `-R 2222:localhost:22`: 反向隧道，服务器2222端口 → 本地22端口

可选参数（保持连接稳定）：
```bash
ssh -o ServerAliveInterval=30 -o ServerAliveCountMax=3 -NfR 2222:localhost:22 服务器用户名@xxx.xxx.xxx.xxx
```

### 2. 服务器配置

#### 2.1 安装必要软件

```bash
# 安装sshfs（网络文件系统）
sudo apt install -y sshfs

# 安装sshpass（自动输入密码，可选）
sudo apt install -y sshpass
```

#### 2.2 配置FUSE

```bash
# 编辑fuse配置
sudo sed -i 's/#user_allow_other/user_allow_other/' /etc/fuse.conf
```

#### 2.3 创建挂载点

```bash
sudo mkdir -p /var/www/html/books
sudo chown $USER:$USER /var/www/html/books
```

#### 2.4 挂载网络磁盘

```bash
# 挂载本地磁盘到服务器
sshfs 本地用户名@localhost:/本地磁盘路径 /挂载点 -p 2222 -o StrictHostKeyChecking=no,allow_other

# 示例：挂载book目录
sshfs 用户名@localhost:/本地磁盘路径/book /var/www/html/books -p 2222 -o StrictHostKeyChecking=no,allow_other
```

### 3. 验证

```bash
# 检查挂载状态
df -h /var/www/html/books

# 查看文件
ls /var/www/html/books

# Web访问测试
curl http://localhost/books/
```

## 常用命令

### 挂载/卸载

```bash
# 挂载
sshfs 用户名@localhost:/本地路径 /挂载点 -p 2222 -o allow_other

# 卸载
fusermount -u /挂载点
```

### 隧道管理

```bash
# 查看隧道进程
ps aux | grep "ssh.*2222"

# 断开隧道
pkill -f "ssh.*2222.*服务器IP"
```

## 注意事项

1. **SSH隧道需要保持运行**: 本地SSH隧道断开后，服务器将无法访问磁盘
2. **自动重连**: 建议添加 `-o ServerAliveInterval=30 -o ServerAliveCountMax=3` 参数保持连接
3. **开机自启**: 可将隧道命令添加到本地crontab或systemd服务中
4. **安全性**: 挂载的目录可通过Web访问，注意敏感文件保护

## 架构图

```
┌─────────────────┐                    ┌─────────────────┐
│    本地电脑      │                    │    服务器        │
│   (内网Debian)   │                    │ xxx.xxx.xxx.xxx │
├─────────────────┤                    ├─────────────────┤
│                 │   SSH反向隧道        │                 │
│  /本地磁盘路径   │◄──────────────────►│  localhost:2222 │
│    /book        │    (端口2222)        │       ↓         │
│                 │                    │  sshfs挂载       │
│  SSH服务 :22    │                    │       ↓         │
│        ↑        │                    │ /var/www/html/  │
│        └────────┼────────────────────┤    books/       │
│                 │   主动建立隧道       │       ↓         │
│                 │   (ssh -R)         │   nginx:80      │
└─────────────────┘                    └─────────────────┘
```

## 替代方案对比

| 方案 | 优点 | 缺点 |
|------|------|------|
| SSH反向隧道 | 无需额外软件、配置简单 | 需要保持连接 |
| frp | 功能强大、稳定 | 需要额外安装配置 |
| WireGuard | 性能好、VPN级别 | 配置复杂、需要内核支持 |
| NFS | 标准文件系统 | 需要公网IP或VPN |

## 本次安装实际使用的命令

```bash
# === 本地电脑 ===
# 安装sshpass
sudo apt install -y sshpass

# 安装SSH服务
sudo apt install -y openssh-server
sudo systemctl start ssh
sudo systemctl enable ssh

# 建立反向隧道
sshpass -p '服务器密码' ssh -NfR 2222:localhost:22 本地用户名@xxx.xxx.xxx.xxx

# === 服务器 ===
# 安装sshfs和sshpass
sudo apt install -y sshfs sshpass

# 配置fuse
sudo sed -i 's/#user_allow_other/user_allow_other/' /etc/fuse.conf

# 创建挂载点
sudo mkdir -p /var/www/html/books
sudo chown 服务器用户名:服务器用户名 /var/www/html/books

# 挂载book目录
sshpass -p '本地密码' sshfs 本地用户名@localhost:/本地磁盘路径/book /var/www/html/books -p 2222 -o StrictHostKeyChecking=no,allow_other
```

## 访问地址

配置完成后，可通过以下地址访问本地book目录内容：

```
http://xxx.xxx.xxx.xxx/books/
```

## 挂载状态

```bash
# 服务器上查看挂载
$ mount | grep fuse.sshfs
本地用户名@127.0.0.1:/本地磁盘路径/book on /var/www/html/books type fuse.sshfs (rw,nosuid,nodev,relatime,user_id=1000,group_id=1000,allow_other)

$ df -h /var/www/html/books
Filesystem                            Size  Used Avail Use% Mounted on
本地用户名@127.0.0.1:/本地磁盘路径/book  233G  195G   38G  84% /var/www/html/books
```
