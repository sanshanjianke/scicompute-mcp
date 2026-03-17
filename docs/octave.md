# Octave 与 AI 协作指南

本文档面向已熟悉 MATLAB/Octave 的用户，介绍如何通过与 AI 对话来使用 Octave 后端。

## AI 能做什么

- 执行 Octave/MATLAB 代码
- 矩阵运算和数值计算
- 绑制 2D/3D 图形
- 保持会话状态（变量持久化）

## 与 AI 对话示例

### 矩阵运算

```
用户：计算矩阵 [[1,2],[3,4]] 的逆矩阵
AI：A = [1 2; 3 4];
     inv(A)
结果：[[-2, 1], [1.5, -0.5]]
```

```
用户：解线性方程组 Ax = b，A=[[1,2],[3,4]]，b=[5,6]
AI：A = [1 2; 3 4];
     b = [5; 6];
     A \ b
```

### 数值计算

```
用户：计算 sin(x) 在 0 到 π 的积分，用数值方法
AI：quad(@(x) sin(x), 0, pi)
结果：约 2.0
```

### 绑图

```
用户：画 sin(x) 和 cos(x) 在 0 到 2π 的图
AI：x = 0:0.1:2*pi;
     plot(x, sin(x), 'b-', x, cos(x), 'r--')
     legend('sin', 'cos')
(图片自动显示)
```

## AI 协作技巧

### 1. 用自然语言描述问题

```
好：求矩阵的特征值和特征向量
差：eig(A)  # 你自己写了代码
```

### 2. 分步工作流

```
用户：创建一个 3x3 的随机矩阵
AI：A = rand(3, 3)

用户：计算它的特征值
AI：eig(A)

用户：画特征值的散点图
AI：e = eig(A);
     scatter(real(e), imag(e))
```

### 3. 指定后端（与 MATLAB 对比）

```
用 Octave 计算这个积分
用 Mathematica 做符号积分
```

## 绑图注意事项

### 基础绑图

```octave
x = 0:0.1:2*pi;
plot(x, sin(x))          % 自动保存并显示
title('Sin Function')
xlabel('X')
ylabel('Y')
grid on
```

### 多图画在一起

```octave
x = 0:0.1:2*pi;
plot(x, sin(x), 'b-', x, cos(x), 'r--')
legend('sin', 'cos')
```

### 3D 图形

```octave
[X, Y] = meshgrid(-2:0.2:2);
Z = X .* exp(-X.^2 - Y.^2);
surf(X, Y, Z)
```

### 子图

```octave
subplot(2,2,1); plot(x, sin(x)); title('Sin')
subplot(2,2,2); plot(x, cos(x)); title('Cos')
```

## 与其他后端对比

| 功能 | Octave | Mathematica | Python Scientific |
|------|--------|-------------|-------------------|
| 数值计算 | ⭐ 强 | 强 | 强 |
| 矩阵运算 | ⭐ 最强 | 强 | 强 |
| 符号计算 | ❌ | ⭐ 最强 | 强 |
| 3D 绑图 | 强 | ⭐ 最强 | 强 |
| MATLAB 兼容 | ✅ | ❌ | ❌ |
| 开源免费 | ✅ | ❌ | ✅ |

**适合 Octave 的场景**：数值计算、矩阵运算、MATLAB 代码迁移

## 特殊注意事项

### 注释位置

Octave 对行内注释处理可能有问题：

```octave
% 推荐写法（注释单独一行）
% 计算平方
y = x^2;

% 可能出错的写法
y = x^2; % 平方
```

### 索引从 1 开始

```octave
v = [10, 20, 30];
v(1)   % 返回 10（第一个元素）
v(0)   % 错误！
```

### 矩阵运算 vs 元素运算

```octave
A * B    % 矩阵乘法
A .* B   % 元素对应相乘

A ^ 2    % 矩阵平方
A .^ 2   % 每个元素平方
```

## 常见问题

**Q: 如何清除变量？**

告诉 AI："清除所有变量" 或直接说 `clear`

**Q: 图形不显示？**

检查 `/tmp/` 目录下是否生成了 PNG 文件。可能是客户端显示问题。

**Q: MATLAB 代码能用吗？**

大部分 MATLAB 代码兼容。不支持的函数 AI 会提示。