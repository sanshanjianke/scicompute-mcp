# R AI Collaboration Guide

This guide is for users familiar with R, introducing how to use the R backend through AI conversation.

## What AI Can Do

- Execute R code for statistical analysis
- Generate statistical plots
- Maintain session state (variable persistence)
- Query R function documentation

## Conversation Examples

### Statistical Analysis

```
User: Generate 1000 normal random numbers and calculate mean and standard deviation
AI: data <- rnorm(1000)
    mean(data)  # Approximately 0
    sd(data)    # Approximately 1
```

```
User: Perform t-test on a dataset
AI: t.test(x, mu=5)
(Output test results)
```

### Plotting

```
User: Plot a histogram of normal distribution
AI: hist(rnorm(1000), main="Normal Distribution")
(Image automatically displayed)
```

```
User: Plot scatter plot of x and y with regression line
AI: plot(x, y)
    abline(lm(y ~ x), col="red")
```

### Data Processing

```
User: Filter data where age > 25
AI: subset(df, age > 25)
```

## AI Collaboration Tips

### 1. Describe Statistical Needs, AI Writes Code

```
Good: Calculate median and quartiles of this data
Bad: median(x); quantile(x, 0.25)  # You wrote the code yourself
```

### 2. Leverage Session Persistence

```
User: Read data.csv file
AI: df <- read.csv("data.csv")

User: Analyze the distribution of age column
AI: hist(df$age)  # Uses previously read data directly
```

### 3. Specify Backend

```
Use R for linear regression analysis
Use Python to plot this
```

### 4. Step-by-step Workflow

```
User: Generate 100 random numbers
AI: x <- rnorm(100)

User: Plot histogram
AI: hist(x)  # Uses previously generated data

User: Test for normality
AI: shapiro.test(x)
```

## Plotting Notes

### Basic Plotting

R's basic `plot()` function automatically generates images:

```r
# Scatter plot
plot(x, y)

# Histogram
hist(rnorm(1000))

# Box plot
boxplot(x, y)
```

### Multiple Plots

```r
par(mfrow=c(2,2))
plot(1:10)
hist(rnorm(100))
boxplot(rnorm(50))
```

### ggplot2

If ggplot2 is installed, you can use it directly:

```r
library(ggplot2)
ggplot(df, aes(x, y)) + geom_point() + geom_smooth()
```

## Common Statistical Analysis Scenarios

### Hypothesis Testing

```
User: Test if two groups have significant difference
AI: t.test(group1, group2)
```

### Regression Analysis

```
User: Perform linear regression of y on x
AI: model <- lm(y ~ x)
    summary(model)
```

### ANOVA

```
User: Perform one-way ANOVA
AI: aov(result ~ group, data=df)
```

## Backend Comparison

| Feature | R | Python Scientific | SageMath |
|---------|---|-------------------|----------|
| Statistical Analysis | ⭐ Best | Strong | Good |
| Data Visualization | Strong | Strong | Strong |
| Machine Learning | Good | ⭐ Best | Good |
| Symbolic Computation | Good | Strong | ⭐ Best |

## FAQ

**Q: Chinese characters garbled?**

A: R plotting has limited Chinese support. Use English labels or install Chinese fonts.

**Q: Package not installed?**

A: Tell AI: "Install and load dplyr package", AI will execute `install.packages("dplyr")`.

**Q: Data file path?**

A: Use absolute paths, or paths relative to project root. AI can help read local files.