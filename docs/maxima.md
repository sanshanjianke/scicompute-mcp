# Maxima 与 AI 协作指南

本文档面向已熟悉 Maxima 的用户，介绍如何通过与 AI 对话来使用 Maxima 后端。

> **注意**：Maxima 后端默认未启用。要启用，取消 `manager.py` 中的注释行。

## AI 能做什么

- 符号计算（积分、微分、极限）
- 方程求解
- 矩阵运算
- 2D/3D 绑图

## 与 AI 对话示例

### 符号计算

```
用户：计算 ∫sin(x)dx
AI：integrate(sin(x), x)
结果：-cos(x)
```

```
用户：求 x³e^x 的导数
AI：diff(x^3 * exp(x), x)
结果：3x²e^x + x³e^x
```

### 方程求解

```
用户：解方程 x² - 5x + 6 = 0
AI：solve(x^2 - 5*x + 6 = 0, x)
结果：x = 2 或 x = 3
```

## AI 协作技巧

### 1. 级数求和需要 simpsum

Maxima 默认不计算无穷级数，需要添加 `simpsum`：

```
用户：计算 Σ(1/n²) 从 1 到 ∞
AI：sum(1/n^2, n, 1, inf), simpsum
结果：%pi^2/6
```

### 2. 输出格式

Maxima 输出 ASCII 艺术格式，用 `string()` 转为线性：

```
用户：用线性格式输出积分结果
AI：string(integrate(x^2, x))
结果：x^3/3
```

### 3. 静默执行

用 `$` 结尾不显示中间结果：

```maxima
x: 5$     % 不显示
y: 10$    % 不显示
x + y;    % 显示 15
```

## 与其他后端对比

| 功能 | Maxima | SageMath | Mathematica |
|------|--------|----------|-------------|
| 符号计算 | ⭐ 强 | 强 | ⭐ 最强 |
| 开源免费 | ✅ | ✅ | ❌ |
| 输出格式 | ASCII 艺术 | LaTeX | 图形化 |
| 学习曲线 | 中等 | 中等 | 陡峭 |

**适合 Maxima 的场景**：开源符号计算、教育用途、轻量级需求

## 特殊注意事项

### 常量符号

| Maxima | 数学 |
|--------|------|
| `%pi` | π |
| `%e` | e |
| `%i` | i (虚数单位) |
| `inf` | ∞ |
| `%` | 上一个结果 |

### 语句结束符

- `;` - 显示结果
- `$` - 静默执行

### 矩阵乘法

```maxima
m: matrix([1, 2], [3, 4]);
m . m;    % 矩阵乘法（注意是点号）
```

## 常见问题

**Q: 级数求和不计算？**

添加 `simpsum` 选项：`sum(...), simpsum`

**Q: 输出乱码？**

Maxima 使用 ASCII 艺术格式。用 `string()` 转换或让 AI 解释结果。

**Q: 如何启用 Maxima 后端？**

编辑 `src/scicompute_mcp/manager.py`，取消注释：
```python
self._backend_classes["maxima"] = MaximaBackend
```