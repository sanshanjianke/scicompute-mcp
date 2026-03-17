# SciCompute MCP Server - 设计文档

## 项目目标

构建一个统一的科学计算 MCP 服务，为 AI 编程助手提供数学和科学计算能力：

- 支持多种计算后端（Mathematica、MATLAB、SymPy、Julia 等）
- 模块化架构，后端可插拔
- AI 自动选择或用户指定后端
- 持久状态管理，变量跨调用保持

## MCP 调用流程

```
┌─────────────────────────────────────────────────────────────────┐
│                         opencode                                │
│                                                                 │
│  1. 启动 MCP Server，调用 tools/list 获取工具描述               │
│  2. 把工具描述塞进发给 LLM 的消息中（tools 参数）                │
│                          ↓                                      │
│                     LLM API                                     │
│                          ↓                                      │
│  3. LLM 返回结构化的 tool_calls                                 │
│     {"name": "compute", "arguments": {"code": "1+1"}}           │
│                          ↓                                      │
│  4. opencode 通过 MCP 协议发送给 Server                         │
│                          ↓                                      │
│  5. Server 返回结果，opencode 根据模型能力处理                  │
│     - 多模态模型：图片直接发给模型                               │
│     - 纯文本模型：忽略图片或转为文字描述                         │
└─────────────────────────────────────────────────────────────────┘
```

## 架构设计

### 整体架构

```
┌─────────────────────────────────────────────────────┐
│                 MCP Server (stdio)                  │
│  ┌─────────────────────────────────────────────┐   │
│  │            BackendManager                    │   │
│  │  - 检测/管理可用后端（懒加载）               │   │
│  │  - 路由请求                                 │   │
│  │  - 统一返回格式                             │   │
│  └─────────────────────────────────────────────┘   │
│          │        │        │        │              │
│     ┌────┴───┐ ┌──┴───┐ ┌──┴───┐ ┌──┴────┐        │
│     │Mathema-│ │Octave│ │SymPy │ │Maxima │ ...    │
│     │ tica   │ │      │ │      │ │       │        │
│     └────────┘ └──────┘ └──────┘ └───────┘        │
└─────────────────────────────────────────────────────┘
```

### 后端接口规范

每个后端实现统一接口：

```python
class ComputeBackend(ABC):
    name: str                    # 后端标识
    description: str             # 能力描述（给 AI 看）
    capabilities: list[str]      # ["symbolic", "numeric", "plot", ...]
    
    @classmethod
    @abstractmethod
    def is_available(cls) -> bool: ...  # 类方法，无需实例化即可检查
    
    @abstractmethod
    def start() -> bool: ...
    
    @abstractmethod
    def evaluate(code: str, timeout: float) -> Result: ...
    
    @abstractmethod
    def reset() -> None: ...
```

### 懒加载机制

后端采用懒加载，避免启动时占用过多内存：

1. **注册阶段**：`BackendManager` 只存储后端类，不实例化
2. **检查阶段**：`is_available()` 是类方法，无需创建实例
3. **使用阶段**：调用 `compute()` 时才实例化并启动对应后端

```python
# 创建 manager 时不实例化任何后端
mgr = BackendManager()
print(mgr._instances)  # {}

# list_available 用类方法检查，仍不实例化
mgr.list_available()
print(mgr._instances)  # {}

# 只有实际调用 compute 才实例化
mgr.compute("1+1", backend="maxima")
print(mgr._instances)  # {"maxima": <MaximaBackend>}
```

### 返回类型

返回 content 数组，支持多种类型：

```python
@dataclass
class Result:
    success: bool
    content: list[Content]  # 可包含多种类型

@dataclass
class TextContent:
    type: Literal["text"] = "text"
    text: str

@dataclass
class ImageContent:
    type: Literal["image"] = "image"
    data: str       # base64
    mimeType: str   # "image/png", "image/gif"

@dataclass
class AudioContent:
    type: Literal["audio"] = "audio"
    data: str       # base64
    mimeType: str   # "audio/wav", "audio/mp3"

@dataclass
class ErrorContent:
    type: Literal["error"] = "error"
    message: str
```

**示例返回：**
```json
{
  "content": [
    {"type": "text", "text": "计算完成"},
    {"type": "image", "data": "base64...", "mimeType": "image/png"}
  ]
}
```

## MCP Tools 定义

共 5 个工具：

### 1. compute

执行科学计算代码。也可用于查询变量（直接传入变量名即可）。

**参数：**
- `code` (string, required): 代码字符串
- `backend` (string, optional): 后端名称，默认 "auto"

**返回：**
- 成功：content 数组（文本/图片/音频）
- 失败：错误信息 + 可用后端列表

**示例：**
```json
// 执行代码
{"name": "compute", "arguments": {"code": "Plot[Sin[x], {x, 0, 10}]", "backend": "mathematica"}}

// 查询变量
{"name": "compute", "arguments": {"code": "x", "backend": "mathematica"}}
```

### 2. list_backends

列出所有检测到的可用后端及其能力。

**参数：** 无

**返回：**
```json
{
  "backends": [
    {"name": "mathematica", "description": "...", "capabilities": ["symbolic", "numeric", "plot"]},
    {"name": "sympy", "description": "...", "capabilities": ["symbolic"]}
  ]
}
```

### 3. reset

重置后端状态，清除所有变量。

**参数：**
- `backend` (string, optional): 后端名称，不填则重置全部

**返回：** 操作结果

### 4. stop_backend

停止并关闭后端，释放内存。后端可在需要时重新启动。

**参数：**
- `backend` (string, optional): 后端名称，不填则停止全部

**返回：** 操作结果

**使用场景：**
- 长时间不用某后端，释放内存
- 后端出问题时重启
- 切换到其他后端前清理

### 5. doc

查询符号的文档信息。当 AI 遇到不熟悉的函数时，可主动查询用法。

**参数：**
- `symbol` (string, required): 符号名称（如 "Plot", "NDSolve"）
- `backend` (string, optional): 后端名称，默认 "mathematica"

**返回：**
- USAGE: 函数用法说明
- ATTRIBUTES: 属性（HoldAll, Protected 等）
- OPTIONS: 可用选项及默认值

**示例：**
```json
{"name": "doc", "arguments": {"symbol": "Plot3D"}}
```

**使用场景：**
- AI 不确定函数用法时主动查询
- 查看函数有哪些可用选项
- 了解函数的调用签名

## Mathematica 后端实现

### 连接方式

优先使用 `wolframclient`，备选子进程 + MathLink。

```python
from wolframclient.evaluation import WolframLanguageSession

session = WolframLanguageSession()
result = session.evaluate(code)
```

### 状态管理

- 服务启动时延迟初始化 Kernel
- Kernel 持久运行，变量跨调用保持
- 支持手动 reset 清除状态

### 输出类型检测

```wolfram
(* 检测输出类型 *)
Which[
  ImageQ[expr], "image",
  GraphicsQ[expr], "image",  
  Graphics3DQ[expr], "image",
  AudioQ[expr], "audio",
  True, "text"
]

(* 导出为各格式 *)
ExportString[expr, {"PNG", "Base64"}]    (* 图片 *)
ExportString[expr, {"WAV", "Base64"}]    (* 音频 *)
```

### 错误处理

| 错误类型 | 处理方式 |
|---------|---------|
| 语法错误 | 返回错误信息 |
| 运行时错误 | 返回 $Failed / Message |
| 执行超时 | 终止 Kernel 并重启 |
| Kernel 崩溃 | 自动重启 |

## 自动选择策略

当 `backend="auto"` 时：

1. 用户在提示词中指定 → 使用指定后端
2. 未指定 → 按优先级选择第一个可用的：
   - 默认优先级：`mathematica > maxima > sympy > octave`
   - 可通过 `SCICOMPUTE_PRIORITY` 环境变量调整

如果只有一个后端可用，自动使用该后端。

## 客户端兼容性

MCP Server 本身遵循标准协议，可在多个客户端间通用。但各客户端配置格式不同：

### opencode (`opencode.json`)

```json
{
  "mcp": {
    "scicompute": {
      "type": "local",
      "command": ["/path/to/python", "-m", "scicompute_mcp.server"],
      "enabled": true
    }
  }
}
```

### Claude Code (`.mcp.json`)

```json
{
  "mcpServers": {
    "scicompute": {
      "command": "/path/to/python",
      "args": ["-m", "scicompute_mcp.server"],
      "cwd": "/home/user/project"
    }
  }
}
```

### Claude Desktop (`claude_desktop_config.json`)

```json
{
  "mcpServers": {
    "scicompute": {
      "command": "/path/to/python",
      "args": ["-m", "scicompute_mcp.server"]
    }
  }
}
```

**主要区别：**
- 顶层 key 不同：`mcp` vs `mcpServers`
- command 格式：opencode 用数组，其他客户端分 command + args
- opencode 有 `type` 和 `enabled` 字段

## 配置

### 环境变量

| 变量 | 说明 |
|-----|------|
| `MATHEMATICA_PATH` | Mathematica 可执行文件路径 |
| `MATLAB_PATH` | MATLAB 路径 |
| `JULIA_PATH` | Julia 路径 |
| `SCICOMPUTE_TIMEOUT` | 默认超时时间（秒），默认 30 |
| `SCICOMPUTE_PRIORITY` | 后端优先级，逗号分隔 |

## 文件结构

```
scicompute_mcp/
├── pyproject.toml
├── README.md
├── DESIGN.md
├── .mcp.json              # Claude Code 配置
└── src/
    └── scicompute_mcp/
        ├── __init__.py
        ├── server.py           # MCP 服务器入口
        ├── manager.py          # BackendManager（懒加载）
        ├── backends/
        │   ├── __init__.py
        │   ├── base.py         # Backend 基类
        │   ├── mathematica.py  # Mathematica 后端
        │   ├── octave.py       # Octave 后端
        │   ├── maxima.py       # Maxima 后端
        │   └── sympy.py        # SymPy/NumPy/Matplotlib 后端
        └── utils/
            └── __init__.py
```
scicompute_mcp/
├── pyproject.toml
├── README.md
├── DESIGN.md
└── src/
    └── scicompute_mcp/
        ├── __init__.py
        ├── server.py           # MCP 服务器入口
        ├── manager.py          # BackendManager
        ├── backends/
        │   ├── __init__.py
│         ├── base.py         # Backend 基类
│         ├── mathematica.py  # Mathematica 后端
│         ├── octave.py       # Octave 后端
│         └── ...             # 其他后端（后续添加）
        └── utils/
            ├── __init__.py
            └── output.py       # 输出类型检测与转换
```

## 开发计划

### Phase 1: 框架 + Mathematica ✅
- [x] 设计文档
- [x] 项目骨架
- [x] Backend 基类
- [x] BackendManager
- [x] Mathematica 后端
- [x] MCP Server 入口
- [x] 文档查询工具 (doc)
- [x] 基础测试

### Phase 1.5: Octave 后端 ✅
- [x] Octave 后端实现
- [x] 绘图函数支持 (plot, plot3, surf, mesh, contour, imagesc, histogram, bar)
- [x] 图片输出 (PNG)
- [x] 基础测试

### Phase 1.6: 其他后端 ✅
- [x] Maxima 后端（符号计算）
- [x] SymPy 后端（Python 生态）

### Phase 2: Python 生态
- [x] SymPy 后端
- [x] NumPy/SciPy 后端（集成在 SymPy 后端中）
- [x] Matplotlib 图像输出

### Phase 3: 商业软件
- [ ] MATLAB 后端
- [ ] Julia 后端
- [ ] Maple 后端（可选）

### Phase 4: 优化与扩展
- [ ] 性能优化
- [ ] 更多后端支持
- [ ] 向量数据库文档检索（可选）