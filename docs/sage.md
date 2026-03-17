# SageMath AI Collaboration Guide

This guide is for users familiar with SageMath, introducing how to use the SageMath backend through AI conversation.

## What AI Can Do

- Execute SageMath code and return results
- Generate plots (automatically saved and displayed)
- Maintain session state (variables persist across calls)
- Query function documentation

## Conversation Examples

### Basic Computation

```
User: Calculate ∫sin(x)dx from 0 to π
AI: (Auto-selects SageMath backend, executes integrate(sin(x), x, 0, pi))
Result: 2
```

```
User: Factor 100 into prime factors
AI: factor(100) → 2^2 * 5^2
```

### Symbolic Computation

```
User: Solve the differential equation y' + y = x
AI: (Uses desolve)
Result: y(x) = x - 1 + C*e^(-x)
```

### Plotting

```
User: Plot sin(x) from 0 to 2π
AI: plot(sin(x), (x, 0, 2*pi))
(Image automatically displayed)
```

## AI Collaboration Tips

### 1. Describe Problems in Natural Language

No need to write complete code, AI will convert for you:

```
Good: Find roots of x² + 2x + 1 = 0
Bad: solve(x^2 + 2*x + 1 == 0, x)  # You wrote the code yourself
```

### 2. Specify Backend (Optional)

If multiple backends are available, you can specify:

```
Use SageMath to calculate integrate(x^2, x)
Use Mathematica to plot Plot[Sin[x], {x, 0, 10}]
```

### 3. Leverage Session Persistence

```
User: Define f(x) = x^2 + sin(x)
AI: (Defined)

User: Find f at x=2
AI: f(2) = 4 + sin(2)
```

Variables persist in session, you can work step by step.

### 4. Query Documentation

```
User: How to use the integrate function?
AI: (Calls doc("integrate", "sage"))
```

## Notes

### Plotting Requires Explicit Call

SageMath native `plot()` returns a Graphics object, needs saving:

```sage
# Method 1: Let AI handle automatically (recommended)
plot(sin(x), (x, 0, 2*pi))

# Method 2: Save manually
p = plot(sin(x), (x, 0, 2*pi))
p.save("/tmp/myplot.png")
```

### Session Management

- Variables persist across calls
- To clear variables, tell AI: "Reset SageMath session"
- To close backend: `stop("sage")`

## Backend Comparison

| Feature | SageMath | Mathematica | Python Scientific |
|---------|----------|-------------|-------------------|
| Number Theory | ⭐ Best | Good | Good |
| Symbolic Integration | Strong | ⭐ Best | Good |
| Differential Equations | Strong | ⭐ Best | Good |
| Plotting | Strong | ⭐ Best | Strong |
| Open Source | ✅ | ❌ | ✅ |

## FAQ

**Q: AI says SageMath is unavailable?**

A: Ensure SageMath is installed (see README.md). Backend will auto-detect the path.

**Q: Plot not showing?**

A: Image was generated, may be client display issue. Check PNG files in `/tmp/` directory.

**Q: Calculation timeout?**

A: Default timeout is 30 seconds. Tell AI: "Use longer timeout" or simplify the problem.