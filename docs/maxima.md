# Maxima AI Collaboration Guide

This guide is for users familiar with Maxima, introducing how to use the Maxima backend through AI conversation.

> **Note**: Maxima backend is disabled by default. To enable, uncomment the line in `manager.py`.

## What AI Can Do

- Symbolic computation (integration, differentiation, limits)
- Equation solving
- Matrix operations
- 2D/3D plotting

## Conversation Examples

### Symbolic Computation

```
User: Calculate ∫sin(x)dx
AI: integrate(sin(x), x)
Result: -cos(x)
```

```
User: Find derivative of x³e^x
AI: diff(x^3 * exp(x), x)
Result: 3x²e^x + x³e^x
```

### Equation Solving

```
User: Solve equation x² - 5x + 6 = 0
AI: solve(x^2 - 5*x + 6 = 0, x)
Result: x = 2 or x = 3
```

## AI Collaboration Tips

### 1. Series Summation Needs simpsum

Maxima doesn't calculate infinite series by default, add `simpsum`:

```
User: Calculate Σ(1/n²) from 1 to ∞
AI: sum(1/n^2, n, 1, inf), simpsum
Result: %pi^2/6
```

### 2. Output Format

Maxima outputs ASCII art format, use `string()` for linear format:

```
User: Output integration result in linear format
AI: string(integrate(x^2, x))
Result: x^3/3
```

### 3. Silent Execution

Use `$` suffix to suppress intermediate output:

```maxima
x: 5$     # No display
y: 10$    # No display
x + y;    # Displays 15
```

## Backend Comparison

| Feature | Maxima | SageMath | Mathematica |
|---------|--------|----------|-------------|
| Symbolic Computing | ⭐ Strong | Strong | ⭐ Best |
| Open Source Free | ✅ | ✅ | ❌ |
| Output Format | ASCII Art | LaTeX | Graphical |
| Learning Curve | Medium | Medium | Steep |

**Best for Maxima**: Open source symbolic computation, educational use, lightweight needs

## Special Notes

### Constant Symbols

| Maxima | Math |
|--------|------|
| `%pi` | π |
| `%e` | e |
| `%i` | i (imaginary unit) |
| `inf` | ∞ |
| `%` | Previous result |

### Statement Terminators

- `;` - Display result
- `$` - Silent execution

### Matrix Multiplication

```maxima
m: matrix([1, 2], [3, 4]);
m . m;    # Matrix multiplication (note the dot)
```

## FAQ

**Q: Series sum not evaluating?**

Add `simpsum` option: `sum(...), simpsum`

**Q: Output garbled?**

Maxima uses ASCII art format. Use `string()` to convert or ask AI to interpret the result.

**Q: How to enable Maxima backend?**

Edit `src/scicompute_mcp/manager.py`, uncomment:
```python
self._backend_classes["maxima"] = MaximaBackend
```