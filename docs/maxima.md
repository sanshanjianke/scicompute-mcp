# Maxima 后端使用指南

## 简介

Maxima 是一个通用的计算机代数系统，支持符号计算、数值计算和绑图。

## 基本使用

### 算术运算

```maxima
1 + 2;
2^10;
sqrt(2);
```

### 符号计算

```maxima
x + 2*x;                    /* 符号运算 */
integrate(sin(x), x);       /* 不定积分 */
diff(x^3 * exp(x), x);      /* 微分 */
limit(sin(x)/x, x, 0);      /* 极限 */
```

### 矩阵运算

```maxima
m: matrix([1, 2], [3, 4]);  /* 定义矩阵 */
determinant(m);              /* 行列式 */
invert(m);                   /* 逆矩阵 */
m . m;                       /* 矩阵乘法 */
```

### 方程求解

```maxima
solve(x^2 - 5*x + 6 = 0, x);           /* 代数方程 */
ode2('diff(y, x) + y = x, y, x);       /* 微分方程 */
```

## 绑图功能

### 2D 绑图

```maxima
plot2d(sin(x), [x, -%pi, %pi]);
plot2d([sin(x), cos(x)], [x, 0, 2*%pi]);  /* 多条曲线 */
```

### 3D 绑图

```maxima
plot3d(sin(x) * cos(y), [x, -%pi, %pi], [y, -%pi, %pi]);
```

### 参数图

```maxima
plot2d([parametric, cos(t), sin(t), [t, 0, 2*%pi]]);
```

## 注意事项

### 输出格式

Maxima 默认输出 ASCII 艺术格式，例如：

```maxima
/* 默认输出 */
integrate(sin(x), x);
/* 结果:
                                      x
(%o1)                             - cos(x)
*/
```

如果需要线性格式，使用 `string()` 函数：

```maxima
string(integrate(sin(x), x));
/* 结果: -cos(x) */
```

### 级数求和

级数求和默认不自动计算，需要添加 `simpsum` 选项：

```maxima
/* 不自动计算 */
sum(1/n^2, n, 1, inf);
/* 输出: 求和符号表示 */

/* 自动计算 */
sum(1/n^2, n, 1, inf), simpsum;
/* 输出: %pi^2/6 */
```

或者在会话中设置：

```maxima
simpsum: true;
sum(1/n^2, n, 1, inf);
/* 输出: %pi^2/6 */
```

### 语句结束符

- `;` - 显示结果
- `$` - 不显示结果（静默执行）

```maxima
x: 5;     /* 显示: 5 */
y: 10$    /* 不显示结果 */
x + y;    /* 显示: 15 */
```

### 常用常量

| 符号 | 含义 |
|------|------|
| `%pi` | 圆周率 π |
| `%e` | 自然常数 e |
| `%i` | 虚数单位 i |
| `inf` | 无穷大 ∞ |
| `%` | 上一个计算结果 |

## 常见问题

### Q: 输出看起来很乱？

Maxima 使用 ASCII 艺术格式显示数学表达式。如果觉得难读，可以用 `string()` 转换：

```maxima
string(你的表达式);
```

### Q: 级数求和不给出具体值？

添加 `simpsum` 选项：

```maxima
sum(表达式, n, a, b), simpsum;
```

### Q: 如何清除变量？

```maxima
kill(x);      /* 清除变量 x */
kill(all);    /* 清除所有变量 */
```

### Q: 如何查看函数帮助？

```maxima
? integrate;  /* 查看 integrate 的帮助 */
```

## 参考资源

- [Maxima 官方手册](https://maxima.sourceforge.io/docs/manual/)
- [Maxima 教程](https://maxima.sourceforge.io/docs/tutorial/en/gaertner-tutorial-revision/Contents.htm)