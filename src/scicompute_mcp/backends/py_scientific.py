"""
Python Scientific Computing Backend
整合 NumPy, SciPy, SymPy, Matplotlib 等科学计算库
"""
import base64
import io
import sys
import threading
import traceback
from typing import Optional

from .base import ComputeBackend, Result, TextContent, ImageContent, ErrorContent

# 全局状态
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
        """创建全局命名空间，预导入常用科学计算库"""
        g = {'__builtins__': __builtins__}

        # NumPy - 数值计算
        try:
            import numpy as np
            g['numpy'] = np
            g['np'] = np
        except ImportError:
            pass

        # SciPy - 科学计算
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

        # SymPy - 符号计算
        try:
            import sympy as sp
            g['sympy'] = sp
            g['sp'] = sp
            # 常用符号函数直接导入
            for name in ['sin', 'cos', 'tan', 'exp', 'log', 'sqrt', 'diff',
                         'integrate', 'limit', 'series', 'expand', 'factor',
                         'simplify', 'solve', 'dsolve', 'symbols', 'Symbol',
                         'Matrix', 'Eq', 'pi', 'E', 'oo', 'I']:
                try:
                    g[name] = getattr(sp, name)
                except AttributeError:
                    pass
            # 特殊符号
            g['pi'] = sp.pi
            g['E'] = sp.E
            g['oo'] = sp.oo
            g['I'] = sp.I
        except ImportError:
            pass

        # Matplotlib - 绑图
        try:
            import matplotlib
            matplotlib.use('Agg')  # 非交互式后端
            import matplotlib.pyplot as plt
            g['matplotlib'] = matplotlib
            g['plt'] = plt
            g['pyplot'] = plt
        except ImportError:
            pass

        # pandas - 数据分析
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
            # 清理之前的图形
            if 'plt' in _globals:
                _globals['plt'].close('all')

            # 判断是表达式还是语句
            code = code.strip()
            lines = code.split('\n')

            # 检查最后一行是否是表达式（可以被求值）
            last_line = lines[-1].strip() if lines else ""
            is_expr = False

            # 如果不是赋值、import、函数定义等，尝试作为表达式求值
            if last_line and not any(last_line.startswith(kw) or last_line.endswith(':')
                                      for kw in ['=', 'import ', 'from ', 'def ', 'class ',
                                                 'for ', 'while ', 'if ', 'with ', 'try']):
                # 尝试用 eval
                try:
                    compile(last_line, '<string>', 'eval')
                    is_expr = True
                except SyntaxError:
                    is_expr = False

            # 执行代码
            if len(lines) > 1:
                # 多行代码：先执行前面的行
                exec('\n'.join(lines[:-1]) if is_expr else code, _globals)

            if is_expr:
                # 最后一行用 eval 求值
                result = eval(last_line, _globals)
                # 先检查图形
                img_result = self._check_plot()
                if img_result:
                    return img_result
                return self._format_result(result)
            else:
                # 单条语句用 exec
                if len(lines) == 1:
                    exec(code, _globals)
                # 检查图形
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
        """检查是否生成了图形，如果有则返回 ImageContent"""
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
        """格式化输出结果"""
        if result is None:
            return Result(success=True, content=[TextContent(text="None")])

        # SymPy 表达式
        try:
            import sympy as sp
            if isinstance(result, (sp.Expr, sp.Eq, sp.Matrix, sp.Basic)):
                return Result(success=True, content=[TextContent(text=sp.pretty(result, use_unicode=True))])
        except ImportError:
            pass

        # NumPy 数组
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

        # 基本类型
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