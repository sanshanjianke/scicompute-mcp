# Documentation Expert Skill

Use this skill when you need detailed documentation for a computing backend.

## How to Use

Launch a subagent with the Task tool to fetch and extract documentation:

```
Task tool → subagent_type: "general"
           → prompt: "You are a documentation expert. Fetch documentation for {symbol} from {backend}.

           Documentation URL: {url}

           Extract and return:
           1. Syntax / function signature
           2. Key parameters and options
           3. 1-2 basic examples
           4. Related functions (if any)

           Be concise. Focus on information needed for the current task."
```

## Documentation URLs by Backend

### Mathematica / Wolfram Language
- **Function Reference**: `https://reference.wolfram.com/language/ref/{symbol}.html`
- **Guide Pages**: `https://reference.wolfram.com/language/guide/{topic}.html`
- **Example**: Plot3D → `https://reference.wolfram.com/language/ref/Plot3D.html`

### Python Scientific

#### NumPy
- **Reference**: `https://numpy.org/doc/stable/reference/generated/numpy.{symbol}.html`
- **Example**: array → `https://numpy.org/doc/stable/reference/generated/numpy.array.html`

#### SciPy
- **Module Reference**: `https://docs.scipy.org/doc/scipy/reference/{module}.html`
- **Example**: integrate → `https://docs.scipy.org/doc/scipy/reference/integrate.html`

#### Matplotlib
- **Pyplot**: `https://matplotlib.org/stable/api/_as_gen/matplotlib.pyplot.{symbol}.html`
- **Example**: plot → `https://matplotlib.org/stable/api/_as_gen/matplotlib.pyplot.plot.html`

#### SymPy
- **Reference**: `https://docs.sympy.org/latest/reference/`
- **Modules**: `https://docs.sympy.org/latest/modules/{module}.html`
- **Example**: calculus → `https://docs.sympy.org/latest/modules/calculus.html`

#### Pandas
- **API Reference**: `https://pandas.pydata.org/docs/reference/api/pandas.{symbol}.html`
- **Example**: DataFrame → `https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.html`

#### Python Standard Library
- **Library Docs**: `https://docs.python.org/3/library/{module}.html`
- **Example**: math → `https://docs.python.org/3/library/math.html`

### R
- **RDocumentation**: `https://www.rdocumentation.org/packages/{package}/functions/{symbol}`
- **Note**: Common packages: `base`, `graphics`, `stats`, `utils`, `ggplot2`, `dplyr`
- **Example**: plot (graphics) → `https://www.rdocumentation.org/packages/graphics/functions/plot`
- **Example**: lm (stats) → `https://www.rdocumentation.org/packages/stats/functions/lm`
- **Search**: `https://www.rdocumentation.org/`

### Julia
- **Base Functions**: `https://docs.julialang.org/en/v1/base/math/#Base.{symbol}`
- **Standard Library**: `https://docs.julialang.org/en/v1/stdlib/{package}/`
- **Manual**: `https://docs.julialang.org/en/v1/`
- **Example**: sin → `https://docs.julialang.org/en/v1/base/math/#Base.sin`
- **Example**: LinearAlgebra → `https://docs.julialang.org/en/v1/stdlib/LinearAlgebra/`

### Octave / GNU Octave
- **Manual**: `https://docs.octave.org/interpreter/`
- **Function Index**: `https://docs.octave.org/interpreter/Function-Index.html`
- **Specific Function**: `https://docs.octave.org/interpreter/XREF{symbol}.html`
- **Example**: plot → `https://docs.octave.org/interpreter/XREFplot.html`
- **Example**: linspace → `https://docs.octave.org/interpreter/XREFlinspace.html`

### SageMath
- **Reference Manual**: `https://doc.sagemath.org/html/en/reference/`
- **Search**: `https://doc.sagemath.org/html/en/reference/search.html?q={symbol}`
- **By Topic**:
  - Calculus: `https://doc.sagemath.org/html/en/reference/calculus/`
  - Plotting: `https://doc.sagemath.org/html/en/reference/plotting/`
  - Symbolic: `https://doc.sagemath.org/html/en/reference/symbolic/`
- **Example**: Search for integrate → `https://doc.sagemath.org/html/en/reference/search.html?q=integrate`

### Maxima
- **Manual**: `https://maxima.sourceforge.io/docs/manual/maxima.html`
- **Note**: The manual is a single page. Use browser search (Ctrl+F) to find functions.
- **In Maxima**: Use `? functionname` or `?? keyword` to search within Maxima
- **Example**: integrate is in "Functions and Variables for Integration" section

### MATLAB
- **MathWorks Help**: `https://www.mathworks.com/help/matlab/ref/{symbol}.html`
- **Search**: `https://www.mathworks.com/help/search.html?q={symbol}`
- **Example**: plot3 → `https://www.mathworks.com/help/matlab/ref/plot3.html`
- **Example**: ode45 → `https://www.mathworks.com/help/matlab/ref/ode45.html`

## Example Usage

### Example 1: Mathematica Plot3D

```
Task(
  description="Fetch Plot3D docs",
  prompt="You are a documentation expert. Fetch Mathematica documentation for Plot3D.

URL: https://reference.wolfram.com/language/ref/Plot3D.html

Use webfetch to get the page, then extract:
1. Syntax
2. Key options (PlotRange, ColorFunction, Mesh, etc.)
3. One basic example
4. Related functions

Return concise summary.",
  subagent_type="general"
)
```

### Example 2: NumPy array

```
Task(
  description="Fetch numpy.array docs",
  prompt="Fetch NumPy documentation for numpy.array.

URL: https://numpy.org/doc/stable/reference/generated/numpy.array.html

Extract: syntax, key parameters (dtype, copy, order, etc.), basic example.",
  subagent_type="general"
)
```

### Example 3: R ggplot

```
Task(
  description="Fetch ggplot docs",
  prompt="Fetch R documentation for ggplot from ggplot2 package.

URL: https://www.rdocumentation.org/packages/ggplot2/functions/ggplot

Extract: syntax, key aesthetics, basic example.",
  subagent_type="general"
)
```

### Example 4: Octave linspace

```
Task(
  description="Fetch linspace docs",
  prompt="Fetch Octave documentation for linspace.

URL: https://docs.octave.org/interpreter/XREFlinspace.html

Extract: syntax, parameters, basic example.",
  subagent_type="general"
)
```

## Tips

1. **URL Construction**: Replace `{symbol}` or `{package}` with actual names (lowercase for URLs)
2. **Search First**: If unsure of exact URL, use search/index pages
3. **Extract Key Info**: Don't return entire page, just syntax + options + example
4. **Be Concise**: Main agent needs focused info, not full documentation
5. **Package Matters**: For R, identify the correct package (base, graphics, stats, ggplot2, etc.)
