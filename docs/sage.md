# SageMath 使用指南

SageMath 是一个开源数学软件系统，整合了 NumPy, SciPy, SymPy, Maxima, GAP, FLINT, R 等众多数学软件的功能。

## 基本计算

### 算术运算

```sage
# 基本运算
2 + 3
2^10
sqrt(2)
```

### 符号计算

```sage
# 定义符号变量
x, y, z = var('x y z')

# 符号表达式
expr = x^2 + 2*x + 1
expr.expand()
expr.factor()

# 化简
simplify(x^2 - 2*x + 1)
```

## 微积分

### 求导

```sage
# 求导
diff(x^3, x)
diff(x^2 * y, x, y)  # 偏导

# 符号函数求导
f(x) = x^2 * sin(x)
f.diff(x)
```

### 积分

```sage
# 不定积分
integrate(x^2, x)
integrate(sin(x), x)

# 定积分
integrate(x^2, x, 0, 1)
integrate(exp(-x^2), x, -infinity, infinity)
```

### 极限

```sage
limit(sin(x)/x, x=0)
limit(1/x, x=0, dir='+')
limit(1/x, x=0, dir='-')
```

### 级数展开

```sage
# 泰勒展开
series(sin(x), x, 0, 5)
exp(x).series(x, 5)
```

## 方程求解

### 代数方程

```sage
# 求解方程
solve(x^2 - 4 == 0, x)
solve([x + y == 3, x - y == 1], x, y)

# 数值求解
find_root(cos(x) == x, 0, 1)
```

### 微分方程

```sage
# 常微分方程
y = function('y')(x)
desolve(diff(y, x) + y == x, y)
```

## 线性代数

### 矩阵运算

```sage
# 创建矩阵
A = matrix([[1, 2], [3, 4]])
B = matrix([[2, 0], [1, 3]])

# 基本运算
A + B
A * B
A.inverse()
A.det()
A.rank()

# 特征值和特征向量
A.eigenvalues()
A.eigenvectors_right()
```

### 向量空间

```sage
# 向量
v = vector([1, 2, 3])
w = vector([4, 5, 6])

v + w
v.dot_product(w)
v.cross_product(w)
```

## 数论

### 素数

```sage
# 素数判定
is_prime(17)

# 第 n 个素数
nth_prime(10)

# 素数列表
prime_range(10, 50)

# 素因数分解
factor(123456)
```

### 整数运算

```sage
# 最大公约数
gcd(12, 18)

# 最小公倍数
lcm(12, 18)

# 模运算
power_mod(2, 100, 17)
```

## 绘图

### 2D 绘图

```sage
# 函数绘图
plot(sin(x), x, -pi, pi)

# 多个函数
plot([sin(x), cos(x)], x, -2*pi, 2*pi)

# 参数方程
parametric_plot([cos(t), sin(t)], (t, 0, 2*pi))

# 极坐标
polar_plot(sin(3*t), (t, 0, 2*pi))
```

### 3D 绘图

```sage
# 3D 曲面
plot3d(sin(x*y), (x, -2, 2), (y, -2, 2))

# 参数曲面
var('u v')
parametric_plot3d([cos(u)*sin(v), sin(u)*sin(v), cos(v)],
                   (u, 0, 2*pi), (v, 0, pi))
```

## 组合数学

```sage
# 排列组合
binomial(10, 3)

# 斐波那契数列
fibonacci(10)

# 集合划分
Set([1,2,3]).subsets()
```

## 注意事项

1. **持久化会话**: 变量和函数在调用之间保持有效
2. **Python 语法**: SageMath 基于 Python，可以使用 Python 语法
3. **帮助系统**: 使用 `?` 查询文档，如 `integrate?`
4. **自动输出**: 表达式会自动打印结果，赋值语句不打印

## 安装说明

SageMath 需要通过 conda 安装，并且要求 Python 3.11：

```bash
# 创建环境
conda create -n sage python=3.11 -y

# 安装 SageMath
conda install -n sage -c conda-forge sage -y
```

安装后更新 `src/scicompute_mcp/backends/sage.py` 中的 `SAGE_PATH`。