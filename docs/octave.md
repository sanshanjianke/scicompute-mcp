# Octave 后端使用指南

## 简介

GNU Octave 是一个与 MATLAB 兼容的科学计算语言，适合数值计算、矩阵运算和数据可视化。

## 基本使用

### 算术运算

```octave
1 + 2
2^10
sqrt(2)
```

### 矩阵运算

```octave
A = [1 2; 3 4];        % 定义矩阵
det(A)                  % 行列式: -2
inv(A)                  % 逆矩阵
A * A                   % 矩阵乘法
A'                      % 转置
```

### 向量操作

```octave
v = [1, 2, 3, 4, 5];
v'                      % 转置（列向量）
v(1)                    % 第一个元素（索引从 1 开始）
v(2:4)                  % 第 2-4 个元素
v(end)                  % 最后一个元素
```

### 数学函数

```octave
sin(pi/2)               % 三角函数
exp(1)                  % 指数函数
log(10)                 % 自然对数
log10(100)              % 以 10 为底的对数
abs(-5)                 % 绝对值
floor(3.7)              % 向下取整
ceil(3.2)               % 向上取整
```

## 绑图功能

### 2D 绑图

```octave
x = 0:0.1:2*pi;
y = sin(x);
plot(x, y)
title('Sin Function')
xlabel('X')
ylabel('Y')
grid on
```

### 多条曲线

```octave
x = 0:0.1:2*pi;
plot(x, sin(x), 'b-', x, cos(x), 'r--')
legend('sin', 'cos')
```

### 3D 绑图

```octave
[X, Y] = meshgrid(-2:0.2:2);
Z = X .* exp(-X.^2 - Y.^2);
surf(X, Y, Z)
title('3D Surface')
```

### 其他绑图类型

```octave
% 柱状图
bar([1, 3, 2, 4])

% 直方图
hist(randn(1000, 1), 30)

% 散点图
scatter(rand(100,1), rand(100,1))

% 等高线图
contour(X, Y, Z)

% 热力图
imagesc(magic(5))
```

### 子图

```octave
subplot(2, 2, 1); plot(x, sin(x)); title('Sin')
subplot(2, 2, 2); plot(x, cos(x)); title('Cos')
subplot(2, 2, 3); plot(x, tan(x)); title('Tan')
```

## 控制流

### 条件语句

```octave
if x > 0
  disp('positive')
elseif x < 0
  disp('negative')
else
  disp('zero')
end
```

### 循环

```octave
for i = 1:10
  disp(i)
end

while x > 0
  x = x - 1;
end
```

### 函数定义

```octave
function y = my_square(x)
  y = x ^ 2;
endfunction

my_square(5)  % 返回 25
```

## 注意事项

### 注释

Octave 不支持行内注释 `%` 后直接跟代码在同一行执行。

```octave
% 这是注释
x = 5;   % 这行可以正常工作

% 下面的写法可能导致解析错误：
% x = 5; % 设置 x 为 5
```

建议将注释单独放在一行。

### 索引

Octave 索引从 **1** 开始，不是 0：

```octave
v = [10, 20, 30];
v(1)   % 返回 10（第一个元素）
v(0)   % 错误！
```

### 矩阵乘法 vs 元素乘法

```octave
A * B    % 矩阵乘法
A .* B   % 元素对应相乘

A ^ 2    % 矩阵平方
A .^ 2   % 每个元素平方
```

### 字符串

使用单引号或双引号：

```octave
s1 = 'hello';
s2 = "world";
```

## 常见问题

### Q: 如何清除变量？

```octave
clear x      % 清除变量 x
clear        % 清除所有变量
clc          % 清除命令窗口
close all    % 关闭所有图形窗口
```

### Q: 如何查看帮助？

```octave
help plot    % 查看 plot 函数的帮助
doc plot     % 打开文档
```

### Q: 如何保存和加载数据？

```octave
save('data.mat', 'A', 'B')   % 保存变量 A, B 到文件
load('data.mat')              % 加载文件中的变量
```

### Q: 如何设置图形可见性？

后端默认设置 `set(0, 'DefaultFigureVisible', 'off')` 以在无显示环境下工作。如需交互式图形：

```octave
set(0, 'DefaultFigureVisible', 'on')
plot(x, y)
```

## 参考资源

- [Octave 官方文档](https://octave.org/doc/)
- [Octave Wiki](https://wiki.octave.org/)
- [MATLAB 兼容性说明](https://octave.org/doc/interpreter/MATLAB-Compatibility.html)