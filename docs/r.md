# R 语言使用指南

R 是一种用于统计计算和图形绑制的编程语言和环境。

## 基本运算

### 算术运算

```r
# 基本运算
2 + 3
10 / 3
2^10
sqrt(16)
abs(-5)
```

### 向量操作

```r
# 创建向量
x <- c(1, 2, 3, 4, 5)
y <- 1:10

# 向量运算
x * 2
x + y[1:5]

# 常用函数
mean(x)
sum(x)
length(x)
max(x)
min(x)
```

## 统计分析

### 描述统计

```r
# 生成随机数据
data <- rnorm(100, mean=0, sd=1)

# 描述统计
mean(data)
median(data)
sd(data)
var(data)
summary(data)

# 分位数
quantile(data, c(0.25, 0.5, 0.75))
```

### 概率分布

```r
# 正态分布
dnorm(0)           # 密度函数
pnorm(1.96)        # 累积分布函数
qnorm(0.975)       # 分位数函数
rnorm(10)          # 随机数

# 其他分布
dbinom(5, 10, 0.5)  # 二项分布
dpois(3, 2)          # 泊松分布
dt(2.5, 10)          # t 分布
```

### 统计检验

```r
# t 检验
x <- rnorm(30, mean=5)
t.test(x, mu=5)

# 两组比较
y <- rnorm(30, mean=6)
t.test(x, y)

# 卡方检验
chisq.test(matrix(c(10, 20, 30, 40), nrow=2))

# 相关性检验
cor.test(x, y)
```

### 线性回归

```r
# 简单线性回归
x <- 1:10
y <- 2*x + rnorm(10)
model <- lm(y ~ x)
summary(model)

# 预测
predict(model, data.frame(x=15))

# 多元回归
model2 <- lm(y ~ x + I(x^2))
```

## 绘图

### 基础绑图

```r
# 散点图
x <- 1:10
y <- x^2
plot(x, y)

# 线图
plot(x, y, type="l")

# 添加标题和标签
plot(x, y, main="标题", xlab="X轴", ylab="Y轴")

# 直方图
hist(rnorm(1000))

# 箱线图
boxplot(rnorm(100), rnorm(100, mean=1))
```

### 高级绘图

```r
# 多图合一
par(mfrow=c(2,2))
plot(1:10)
hist(rnorm(100))
boxplot(rnorm(50))
pie(c(1,2,3,4))

# 添加元素
plot(1:10, type="l")
points(5, 25, col="red", pch=19)
lines(c(1,10), c(1,100), col="blue", lty=2)
legend("topleft", c("数据", "拟合"), col=c("black", "blue"), lty=1:2)
```

### ggplot2 (如果安装)

```r
library(ggplot2)

# 基础用法
df <- data.frame(x=1:10, y=(1:10)^2)
ggplot(df, aes(x, y)) + geom_point() + geom_line()

# 分组
df$group <- rep(c("A", "B"), 5)
ggplot(df, aes(x, y, color=group)) + geom_point()
```

## 数据处理

### 数据框

```r
# 创建数据框
df <- data.frame(
  name = c("Alice", "Bob", "Charlie"),
  age = c(25, 30, 35),
  score = c(85, 90, 88)
)

# 访问列
df$name
df[, "age"]
df[, 2]

# 访问行
df[1, ]
df[df$age > 25, ]

# 添加列
df$passed <- df$score > 80
```

### 数据操作

```r
# 排序
df[order(df$age), ]

# 筛选
subset(df, age > 25)

# 合并
df2 <- data.frame(name="David", age=28, score=92)
rbind(df, df2)

# 聚合
aggregate(score ~ group, data=df, mean)
```

## 函数定义

```r
# 定义函数
my_sum <- function(a, b) {
  return(a + b)
}

# 默认参数
greet <- function(name, greeting="Hello") {
  paste(greeting, name)
}

# 多返回值
stats <- function(x) {
  return(list(mean=mean(x), sd=sd(x)))
}
```

## 注意事项

1. **赋值符号**: 使用 `<-` 或 `=` 进行赋值
2. **索引从 1 开始**: 与 Python 不同，R 的索引从 1 开始
3. **向量化操作**: R 的运算默认是向量化的
4. **持久化会话**: 变量在调用之间保持有效
5. **帮助系统**: 使用 `?function_name` 查询帮助

## 安装说明

```bash
# Ubuntu/Debian
sudo apt install r-base

# macOS
brew install r

# 或通过 conda
conda install -n scicompute r-base -c conda-forge
```