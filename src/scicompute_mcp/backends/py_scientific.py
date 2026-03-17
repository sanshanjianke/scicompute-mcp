"""
Python Scientific Computing Backend
Integrates NumPy, SciPy, SymPy, Matplotlib, and other scientific libraries
"""
import base64
import io
import sys
import threading
import traceback
from typing import Optional

from .base import ComputeBackend, Result, TextContent, ImageContent, ErrorContent

# Global state
_globals: Optional[dict] = None
_lock = threading.Lock()


class PyScientificBackend(ComputeBackend):
    name = "py_scientific"
    description = "Python Scientific Computing - NumPy, SciPy, SymPy, Matplotlib, Pandas"
    capabilities = ["symbolic", "numeric", "plot"]

    @property
    def is_running(self) -> bool:
        return _globals is not None

    @classmethod
    def is_available(cls) -> bool:
        try:
            import numpy
            return True
        except ImportError:
            return False

    def start(self) -> bool:
        global _globals
        with _lock:
            if _globals is not None:
                return True

            try:
                _globals = self._create_globals()
                return True
            except Exception as e:
                print(f"Failed to start Python backend: {e}", file=sys.stderr)
                return False

    def _create_globals(self) -> dict:
        """Create global namespace with pre-imported scientific libraries"""
        g = {'__builtins__': __builtins__}

        # NumPy - numerical computing
        try:
            import numpy as np
            g['numpy'] = np
            g['np'] = np
        except ImportError:
            pass

        # SciPy - scientific computing
        try:
            import scipy
            g['scipy'] = scipy
            from scipy import integrate, optimize, linalg, stats, special, fft, interpolate
            g['integrate'] = integrate
            g['optimize'] = optimize
            g['linalg'] = linalg
            g['stats'] = stats
            g['special'] = special
            g['fft'] = fft
            g['interpolate'] = interpolate
        except ImportError:
            pass

        # SymPy - symbolic computing
        try:
            import sympy as sp
            g['sympy'] = sp
            g['sp'] = sp
            # Import commonly used symbolic functions directly
            for name in ['sin', 'cos', 'tan', 'exp', 'log', 'sqrt', 'diff',
                         'integrate', 'limit', 'series', 'expand', 'factor',
                         'simplify', 'solve', 'dsolve', 'symbols', 'Symbol',
                         'Matrix', 'Eq', 'pi', 'E', 'oo', 'I']:
                try:
                    g[name] = getattr(sp, name)
                except AttributeError:
                    pass
            # Special symbols
            g['pi'] = sp.pi
            g['E'] = sp.E
            g['oo'] = sp.oo
            g['I'] = sp.I
        except ImportError:
            pass

        # Matplotlib - plotting
        try:
            import matplotlib
            matplotlib.use('Agg')  # Non-interactive backend
            import matplotlib.pyplot as plt
            g['matplotlib'] = matplotlib
            g['plt'] = plt
            g['pyplot'] = plt
        except ImportError:
            pass

        # pandas - data analysis
        try:
            import pandas as pd
            g['pandas'] = pd
            g['pd'] = pd
        except ImportError:
            pass

        return g

    def evaluate(self, code: str, timeout: float = 30.0) -> Result:
        global _globals
        if _globals is None:
            return Result(success=False, content=[ErrorContent(message="Python backend not started")])

        try:
            # Clear previous figures
            if 'plt' in _globals:
                _globals['plt'].close('all')

            # Determine if code is expression or statement
            code = code.strip()
            lines = code.split('\n')

            # Check if last line is an expression (can be evaluated)
            last_line = lines[-1].strip() if lines else ""
            is_expr = False

            # If not assignment, import, function definition, etc., try as expression
            if last_line and not any(last_line.startswith(kw) or last_line.endswith(':')
                                      for kw in ['=', 'import ', 'from ', 'def ', 'class ',
                                                 'for ', 'while ', 'if ', 'with ', 'try']):
                # Try with eval
                try:
                    compile(last_line, '<string>', 'eval')
                    is_expr = True
                except SyntaxError:
                    is_expr = False

            # Execute code
            if len(lines) > 1:
                # Multi-line code: execute preceding lines first
                exec('\n'.join(lines[:-1]) if is_expr else code, _globals)

            if is_expr:
                # Evaluate last line with eval
                result = eval(last_line, _globals)
                # Check for plots first
                img_result = self._check_plot()
                if img_result:
                    return img_result
                return self._format_result(result)
            else:
                # Single statement with exec
                if len(lines) == 1:
                    exec(code, _globals)
                # Check for plots
                img_result = self._check_plot()
                if img_result:
                    return img_result
                return Result(success=True, content=[TextContent(text="(no output)")])

        except SyntaxError as e:
            return Result(success=False, content=[ErrorContent(message=f"SyntaxError: {e}")])
        except Exception as e:
            tb = traceback.format_exc()
            tb_lines = tb.split('\n')
            relevant = [l for l in tb_lines if '<string>' not in l or 'exec' not in l]
            if len(relevant) > 5:
                relevant = relevant[-5:]
            return Result(success=False, content=[ErrorContent(message='\n'.join(relevant))])

    def _check_plot(self) -> Optional[Result]:
        """Check if a plot was generated, return ImageContent if so"""
        global _globals
        if _globals and 'plt' in _globals:
            figs = _globals['plt'].get_fignums()
            if figs:
                buf = io.BytesIO()
                _globals['plt'].figure(figs[0]).savefig(buf, format='png', dpi=150, bbox_inches='tight')
                buf.seek(0)
                image_data = base64.b64encode(buf.read()).decode('utf-8')
                _globals['plt'].close('all')
                return Result(success=True, content=[ImageContent(data=image_data, mimeType="image/png")])
        return None

    def _format_result(self, result) -> Result:
        """Format output result"""
        if result is None:
            return Result(success=True, content=[TextContent(text="None")])

        # SymPy expressions
        try:
            import sympy as sp
            if isinstance(result, (sp.Expr, sp.Eq, sp.Matrix, sp.Basic)):
                return Result(success=True, content=[TextContent(text=sp.pretty(result, use_unicode=True))])
        except ImportError:
            pass

        # NumPy arrays
        try:
            import numpy as np
            if isinstance(result, np.ndarray):
                return Result(success=True, content=[TextContent(text=str(result))])
        except ImportError:
            pass

        # pandas DataFrame
        try:
            import pandas as pd
            if isinstance(result, pd.DataFrame):
                return Result(success=True, content=[TextContent(text=str(result))])
        except ImportError:
            pass

        # Basic types
        if isinstance(result, (int, float, str, bool, list, tuple, dict)):
            return Result(success=True, content=[TextContent(text=str(result))])

        return Result(success=True, content=[TextContent(text=str(result))])

    def reset(self) -> None:
        global _globals
        with _lock:
            if _globals is not None:
                if 'plt' in _globals:
                    try:
                        _globals['plt'].close('all')
                    except:
                        pass
                _globals = self._create_globals()

    def stop(self) -> None:
        global _globals
        with _lock:
            if _globals is not None:
                if 'plt' in _globals:
                    try:
                        _globals['plt'].close('all')
                    except:
                        pass
                _globals = None