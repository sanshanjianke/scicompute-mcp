# R 与 AI 协作指南

本文档面向已熟悉 R 的用户，介绍如何通过与 AI 对话来使用 R 后端。

## AI 能做什么

- 执行 R 代码进行统计分析
- 绑制统计图形
- 保持会话状态（变量持久化）
- 查询 R 函数文档

## 与 AI 对话示例

### 统计分析

```
用户：生成 1000 个正态分布随机数，计算均值和标准差
AI：data <- rnorm(1000)
     mean(data)  # 约 0
     sd(data)    # 约 1
```

```
用户：做一组数据的 t 检验
AI：t.test(x, mu=5)
(输出检验结果)
```

### 绑图

```
用户：画一个正态分布的直方图
AI：hist(rnorm(1000), main="Normal Distribution")
(图片自动显示)
```

```
用户：画 x 和 y 的散点图，加回归线
AI：plot(x, y)
     abline(lm(y ~ x), col="red")
```

### 数据处理

```
用户：筛选 age > 25 的数据
AI：subset(df, age > 25)
```

## AI 协作技巧

### 1. 描述统计需求，AI 写代码

```
好：计算这组数据的中位数和四分位数
差：median(x); quantile(x, 0.25)  # 你自己写了代码
```

### 2. 利用会话持久性

```
用户：读取 data.csv 文件
AI：df <- read.csv("data.csv")

用户：分析 age 列的分布
AI：hist(df$age)  # 直接使用之前读取的数据
```

### 3. 指定后端

```
用 R 做线性回归分析
用 Python 画这个图
```

### 4. 分步工作流

```
用户：生成 100 个随机数
AI：x <- rnorm(100)

用户：画直方图
AI：hist(x)  # 使用之前生成的数据

用户：检验是否正态分布
AI：shapiro.test(x)
```

## 绘图注意事项

### 基础绑图

R 的基础 `plot()` 函数会自动生成图片：

```r
# 散点图
plot(x, y)

# 直方图
hist(rnorm(1000))

# 箱线图
boxplot(x, y)
```

### 多图布局

```r
par(mfrow=c(2,2))
plot(1:10)
hist(rnorm(100))
boxplot(rnorm(50))
```

### ggplot2

如果安装了 ggplot2，可以直接使用：

```r
library(ggplot2)
ggplot(df, aes(x, y)) + geom_point() + geom_smooth()
```

## 常见统计分析场景

### 假设检验

```
用户：检验两组数据是否有显著差异
AI：t.test(group1, group2)
```

### 回归分析

```
用户：做 y 对 x 的线性回归
AI：model <- lm(y ~ x)
     summary(model)
```

### 方差分析

```
用户：做单因素方差分析
AI：aov(result ~ group, data=df)
```

## 与其他后端对比

| 功能 | R | Python Scientific | SageMath |
|------|---|-------------------|----------|
| 统计分析 | ⭐ 最强 | 强 | 一般 |
| 数据可视化 | 强 | 强 | 强 |
| 机器学习 | 一般 | ⭐ 最强 | 一般 |
| 符号计算 | 一般 | 强 | ⭐ 最强 |

## 常见问题

**Q: 中文显示乱码？**

A: R 绑图对中文支持有限，建议使用英文标签或安装中文字体。

**Q: 包没安装？**

A: 告诉 AI："安装并加载 dplyr 包"，AI 会执行 `install.packages("dplyr")`。

**Q: 数据文件路径？**

A: 使用绝对路径，或相对于项目根目录的路径。AI 可以帮你读取本地文件。