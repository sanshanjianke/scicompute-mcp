import base64
import os
import signal
import tempfile
from typing import Optional

from oct2py import Oct2Py, Oct2PyError
import numpy as np

from .base import ComputeBackend, Result, TextContent, ImageContent, ErrorContent


class OctaveBackend(ComputeBackend):
    name = "octave"
    description = "GNU Octave - MATLAB-compatible numerical computation"
    capabilities = ["numeric", "plot"]
    
    def __init__(self):
        self._session: Optional[Oct2Py] = None
        self._started = False
    
    def is_available(self) -> bool:
        try:
            import oct2py
            return True
        except ImportError:
            return False
    
    def start(self) -> bool:
        if self._started:
            return True
        
        try:
            self._session = Oct2Py()
            self._session.eval("graphics_toolkit('gnuplot')")
            self._session.eval("set(0, 'DefaultFigureVisible', 'off')")
            self._started = True
            return True
        except Exception as e:
            print(f"Failed to start Octave: {e}", file=__import__("sys").stderr)
            return False
    
    def evaluate(self, code: str, timeout: float = 30.0) -> Result:
        if not self._started or self._session is None:
            if not self.start():
                return Result(success=False, content=[ErrorContent(message="Octave not available")])
        
        session = self._session
        if session is None:
            return Result(success=False, content=[ErrorContent(message="Octave session not initialized")])
        
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
            
        except Oct2PyError as e:
            if temp_file and os.path.exists(temp_path):
                os.unlink(temp_path)
            error_msg = str(e)
            if "Octave evaluation error" in error_msg:
                lines = error_msg.split('\n')
                error_msg = '\n'.join(lines[1:]) if len(lines) > 1 else error_msg
            return Result(success=False, content=[ErrorContent(message=error_msg)])
        except Exception as e:
            if temp_file and os.path.exists(temp_path):
                os.unlink(temp_path)
            return Result(success=False, content=[ErrorContent(message=str(e))])
    
    def _process_result(self, result) -> Result:
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
    
    def _format_array(self, arr: np.ndarray) -> str:
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
        if self._session:
            try:
                self._session.eval("clear all; close all;")
            except:
                pass
    
    def stop(self) -> None:
        if self._session:
            try:
                pid = self._session._engine.repl.pid if self._session._engine else None
                self._session.exit()
                if pid:
                    try:
                        os.waitpid(pid, os.WNOHANG)
                    except ChildProcessError:
                        pass
            except Exception:
                pass
        self._session = None
        self._started = False