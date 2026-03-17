# Octave AI Collaboration Guide

This guide is for users familiar with MATLAB/Octave, introducing how to use the Octave backend through AI conversation.

## What AI Can Do

- Execute Octave/MATLAB code
- Matrix operations and numerical computation
- Generate 2D/3D plots
- Maintain session state (variable persistence)

## Conversation Examples

### Matrix Operations

```
User: Calculate the inverse of matrix [[1,2],[3,4]]
AI: A = [1 2; 3 4];
    inv(A)
Result: [[-2, 1], [1.5, -0.5]]
```

```
User: Solve linear system Ax = b, A=[[1,2],[3,4]], b=[5,6]
AI: A = [1 2; 3 4];
    b = [5; 6];
    A \ b
```

### Numerical Computation

```
User: Calculate integral of sin(x) from 0 to π using numerical methods
AI: quad(@(x) sin(x), 0, pi)
Result: Approximately 2.0
```

### Plotting

```
User: Plot sin(x) and cos(x) from 0 to 2π
AI: x = 0:0.1:2*pi;
    plot(x, sin(x), 'b-', x, cos(x), 'r--')
    legend('sin', 'cos')
(Image automatically displayed)
```

## AI Collaboration Tips

### 1. Describe Problems in Natural Language

```
Good: Find eigenvalues and eigenvectors of a matrix
Bad: eig(A)  # You wrote the code yourself
```

### 2. Step-by-step Workflow

```
User: Create a 3x3 random matrix
AI: A = rand(3, 3)

User: Calculate its eigenvalues
AI: eig(A)

User: Plot eigenvalues as scatter
AI: e = eig(A);
    scatter(real(e), imag(e))
```

### 3. Specify Backend (vs MATLAB)

```
Use Octave to calculate this integral
Use Mathematica for symbolic integration
```

## Plotting Notes

### Basic Plotting

```octave
x = 0:0.1:2*pi;
plot(x, sin(x))          # Automatically saved and displayed
title('Sin Function')
xlabel('X')
ylabel('Y')
grid on
```

### Multiple Curves

```octave
x = 0:0.1:2*pi;
plot(x, sin(x), 'b-', x, cos(x), 'r--')
legend('sin', 'cos')
```

### 3D Plotting

```octave
[X, Y] = meshgrid(-2:0.2:2);
Z = X .* exp(-X.^2 - Y.^2);
surf(X, Y, Z)
```

### Subplots

```octave
subplot(2,2,1); plot(x, sin(x)); title('Sin')
subplot(2,2,2); plot(x, cos(x)); title('Cos')
```

## Backend Comparison

| Feature | Octave | Mathematica | Python Scientific |
|---------|--------|-------------|-------------------|
| Numerical Computing | ⭐ Strong | Strong | Strong |
| Matrix Operations | ⭐ Best | Strong | Strong |
| Symbolic Computing | ❌ | ⭐ Best | Strong |
| 3D Plotting | Strong | ⭐ Best | Strong |
| MATLAB Compatible | ✅ | ❌ | ❌ |
| Open Source Free | ✅ | ❌ | ✅ |

**Best for Octave**: Numerical computing, matrix operations, MATLAB code migration

## Special Notes

### Comment Placement

Octave may have issues with inline comments:

```octave
# Recommended (comment on separate line)
# Calculate square
y = x^2;

# May cause errors
y = x^2; % Square
```

### Indexing Starts at 1

```octave
v = [10, 20, 30];
v(1)   # Returns 10 (first element)
v(0)   # Error!
```

### Matrix vs Element Operations

```octave
A * B    # Matrix multiplication
A .* B   # Element-wise multiplication

A ^ 2    # Matrix square
A .^ 2   # Each element squared
```

## FAQ

**Q: How to clear variables?**

Tell AI: "Clear all variables" or directly say `clear`

**Q: Plot not displaying?**

Check if PNG files were generated in `/tmp/` directory. May be client display issue.

**Q: Can MATLAB code be used?**

Most MATLAB code is compatible. Unsupported functions will be flagged by AI.