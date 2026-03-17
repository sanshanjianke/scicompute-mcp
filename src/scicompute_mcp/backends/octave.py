import base64
import os
import signal
import tempfile
import threading
from typing import Optional

from .base import ComputeBackend, Result, TextContent, ImageContent, ErrorContent

# Global singleton session
_octave_session = None
_octave_lock = threading.Lock()


class OctaveBackend(ComputeBackend):
    name = "octave"
    description = "GNU Octave - MATLAB-compatible numerical computation"
    capabilities = ["numeric", "plot"]

    def __init__(self):
        pass  # Uses global singleton, no instance variables needed

    @property
    def is_running(self) -> bool:
        return _octave_session is not None

    @classmethod
    def is_available(cls) -> bool:
        """Check if octave command is available."""
        import shutil
        return shutil.which('octave') is not None

    def start(self) -> bool:
        global _octave_session
        with _octave_lock:
            if _octave_session is not None:
                return True

            try:
                # 延迟导入，只在需要时才触发
                import oct2py
                _octave_session = oct2py.octave
                _octave_session.eval("graphics_toolkit('gnuplot')")
                _octave_session.eval("set(0, 'DefaultFigureVisible', 'off')")
                return True
            except Exception as e:
                print(f"Failed to start Octave: {e}", file=__import__("sys").stderr)
                return False

    def evaluate(self, code: str, timeout: float = 30.0) -> Result:
        # start() 应该由 manager 调用
        if _octave_session is None:
            return Result(success=False, content=[ErrorContent(message="Octave not started")])

        session = _octave_session
        
        temp_path = ""
        temp_file = None
        try:
            temp_file = tempfile.NamedTemporaryFile(suffix=".png", delete=False)
            temp_path = temp_file.name
            temp_file.close()
            
            wrapped_code = f'''
graphics_toolkit('gnuplot');
set(0, 'DefaultFigureVisible', 'off');
set(0, 'DefaultFigurePaperPositionMode', 'auto');
set(0, 'DefaultFigurePaperSize', [8, 6]);

try
    close all;
    {code}
    
    figs = findall(0, 'Type', 'Figure');
    if ~isempty(figs)
        print(figs(1), "{temp_path}", "-dpng", "-r150");
        close all;
        disp("__PLOT_GENERATED__");
    endif
catch err
    disp(err.message);
end_try_catch
'''
            
            result = session.eval(wrapped_code, timeout=timeout)

            if os.path.exists(temp_path) and os.path.getsize(temp_path) > 0:
                with open(temp_path, "rb") as f:
                    image_data = base64.b64encode(f.read()).decode("utf-8")
                os.unlink(temp_path)
                return Result(success=True, content=[ImageContent(data=image_data, mimeType="image/png")])

            return self._process_result(result)

        except Exception as e:
            if temp_file and os.path.exists(temp_path):
                os.unlink(temp_path)
            error_msg = str(e)
            if "Octave evaluation error" in error_msg:
                lines = error_msg.split('\n')
                error_msg = '\n'.join(lines[1:]) if len(lines) > 1 else error_msg
            return Result(success=False, content=[ErrorContent(message=error_msg)])

    def _process_result(self, result) -> Result:
        import numpy as np

        if result is None:
            return Result(success=True, content=[TextContent(text="(no output)")])

        if isinstance(result, str):
            text = result.strip()
            text = text.replace("__PLOT_GENERATED__", "").strip()
            return Result(success=True, content=[TextContent(text=text if text else "(no output)")])

        if isinstance(result, (int, float)):
            return Result(success=True, content=[TextContent(text=str(result))])

        if isinstance(result, np.ndarray):
            text = self._format_array(result)
            return Result(success=True, content=[TextContent(text=text)])
        
        if isinstance(result, dict):
            if 'flat' in result:
                flat = result.get('flat', '')
                if isinstance(flat, str) and flat:
                    if flat.startswith('Matrix('):
                        ascii_repr = result.get('ascii', flat)
                        return Result(success=True, content=[TextContent(text=ascii_repr)])
                    return Result(success=True, content=[TextContent(text=flat)])
                unicode_repr = result.get('unicode', '')
                if isinstance(unicode_repr, str) and unicode_repr:
                    return Result(success=True, content=[TextContent(text=unicode_repr)])
            return Result(success=True, content=[TextContent(text=str(result))])
        
        return Result(success=True, content=[TextContent(text=str(result))])
    
    def _format_array(self, arr) -> str:
        if arr.ndim == 1:
            return "  ".join(self._format_number(x) for x in arr)
        elif arr.ndim == 2:
            lines = []
            for row in arr:
                lines.append("  ".join(self._format_number(x) for x in row))
            return "\n".join(lines)
        else:
            return str(arr)
    
    def _format_number(self, x) -> str:
        if isinstance(x, float):
            if abs(x) < 1e-10:
                return "0"
            elif abs(x) >= 1000 or (abs(x) < 0.01 and x != 0):
                return f"{x:.4e}"
            else:
                return f"{x:.4f}"
        return str(x)
    
    def reset(self) -> None:
        global _octave_session
        if _octave_session:
            try:
                _octave_session.eval("clear all; close all;")
            except:
                pass

    def stop(self) -> None:
        global _octave_session
        with _octave_lock:
            if _octave_session is None:
                return

            try:
                # 获取进程 PID 用于强制终止
                try:
                    pid = _octave_session._engine.repl.child.pid
                except Exception:
                    pid = None

                # 尝试优雅关闭
                try:
                    _octave_session.eval("exit")
                except Exception:
                    pass

                # 强制终止进程
                if pid:
                    try:
                        import os
                        import signal
                        os.kill(pid, signal.SIGTERM)
                    except Exception:
                        pass
            except Exception:
                pass
            finally:
                _octave_session = None