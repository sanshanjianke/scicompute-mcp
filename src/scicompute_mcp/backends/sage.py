"""
SageMath Backend - Open Source Mathematics Software
Number theory, algebra, symbolic and numeric computation
"""
import base64
import os
import re
import select
import shutil
import signal
import subprocess
import tempfile
import threading
import time
from typing import Optional

from .base import ComputeBackend, Result, TextContent, ImageContent, ErrorContent

# Global singleton
_process: Optional[subprocess.Popen] = None
_lock = threading.Lock()


def _find_sage_path() -> str:
    """Auto-detect SageMath installation path"""
    # 1. Environment variable
    env_path = os.environ.get("SAGE_PATH")
    if env_path and os.path.exists(env_path):
        return env_path

    # 2. Search in PATH
    which_path = shutil.which("sage")
    if which_path:
        return which_path

    # 3. Common conda environment paths
    home = os.path.expanduser("~")
    conda_patterns = [
        f"{home}/miniconda3/envs/sage/bin/sage",
        f"{home}/anaconda3/envs/sage/bin/sage",
        f"{home}/miniforge3/envs/sage/bin/sage",
        "/opt/conda/envs/sage/bin/sage",
    ]
    for path in conda_patterns:
        if os.path.exists(path):
            return path

    # 4. System installation paths
    system_paths = ["/usr/bin/sage", "/usr/local/bin/sage", "/opt/sage/sage"]
    for path in system_paths:
        if os.path.exists(path):
            return path

    # 5. Default return (may not exist)
    return "/usr/bin/sage"


SAGE_PATH = _find_sage_path()


class SageBackend(ComputeBackend):
    name = "sage"
    description = "SageMath - Number theory, algebra, symbolic/numeric computation"
    capabilities = ["symbolic", "numeric", "plot"]

    @property
    def is_running(self) -> bool:
        return _process is not None

    @classmethod
    def is_available(cls) -> bool:
        return os.path.exists(SAGE_PATH)

    def start(self) -> bool:
        global _process
        with _lock:
            if _process is not None:
                return True

            try:
                _process = subprocess.Popen(
                    [SAGE_PATH, '--simple-prompt'],
                    stdin=subprocess.PIPE,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True
                )

                import fcntl
                fd = _process.stdout.fileno()
                fl = fcntl.fcntl(fd, fcntl.F_GETFL)
                fcntl.fcntl(fd, fcntl.F_SETFL, fl | os.O_NONBLOCK)

                fd_err = _process.stderr.fileno()
                fl_err = fcntl.fcntl(fd_err, fcntl.F_GETFL)
                fcntl.fcntl(fd_err, fcntl.F_SETFL, fl_err | os.O_NONBLOCK)

                time.sleep(1.0)  # Wait for welcome banner to fully output
                self._read_available(0.5)

                # Send empty statement to clear welcome banner
                _process.stdin.write("None\n")
                _process.stdin.flush()
                time.sleep(0.3)
                self._read_available(0.5)

                return True
            except Exception as e:
                print(f"Failed to start SageMath: {e}", file=__import__("sys").stderr)
                return False

    def _read_available(self, timeout: float = 0.3) -> str:
        output = ""
        start = time.time()
        while time.time() - start < timeout:
            ready, _, _ = select.select([_process.stdout, _process.stderr], [], [], 0.1)
            for stream in ready:
                try:
                    chunk = stream.read(4096)  # Limit read size to avoid blocking
                    if chunk:
                        output += chunk
                except Exception:
                    pass
        return output

    def evaluate(self, code: str, timeout: float = 60.0) -> Result:
        if _process is None:
            return Result(success=False, content=[ErrorContent(message="SageMath not started")])

        has_plot = self._detect_plot(code)

        temp_path = ""
        if has_plot:
            temp_file = tempfile.NamedTemporaryFile(suffix=".png", delete=False)
            temp_path = temp_file.name
            temp_file.close()

        try:
            if has_plot:
                result = self._execute_plot(code, temp_path, timeout)
            else:
                result = self._execute_code(code, timeout)

            if has_plot and temp_path:
                if result.success and os.path.exists(temp_path) and os.path.getsize(temp_path) > 0:
                    with open(temp_path, "rb") as f:
                        image_data = base64.b64encode(f.read()).decode("utf-8")
                    os.unlink(temp_path)
                    return Result(success=True, content=[ImageContent(data=image_data, mimeType="image/png")])
                else:
                    if os.path.exists(temp_path):
                        os.unlink(temp_path)
                    return Result(success=False, content=[ErrorContent(message="Plot file not created")])

            return result

        except TimeoutError:
            if temp_path and os.path.exists(temp_path):
                os.unlink(temp_path)
            return Result(success=False, content=[ErrorContent(message="Evaluation timed out")])
        except Exception as e:
            if temp_path and os.path.exists(temp_path):
                os.unlink(temp_path)
            return Result(success=False, content=[ErrorContent(message=str(e))])

    def _execute_code(self, code: str, timeout: float) -> Result:
        code = code.strip()

        # Determine if code is expression (needs print) or statement
        is_assignment = '=' in code and not '==' in code
        is_function_def = code.startswith('def ') or code.startswith('lambda')

        if is_assignment or is_function_def:
            wrapped_code = code + '\n'
        else:
            wrapped_code = f'print({code})\n'

        _process.stdin.write(wrapped_code)
        _process.stdin.flush()

        time.sleep(0.2)
        output = self._read_available(timeout)

        result_text = self._clean_output(output)

        if not result_text:
            result_text = "(no output)"

        return Result(success=True, content=[TextContent(text=result_text)])

    def _execute_plot(self, code: str, temp_path: str, timeout: float) -> Result:
        wrapped_code = f'''
import matplotlib.pyplot as plt
{code}
plt.savefig("{temp_path}", dpi=150, bbox_inches='tight')
plt.close()
'''
        _process.stdin.write(wrapped_code)
        _process.stdin.flush()

        start_time = time.time()
        max_wait = min(timeout - 1.0, 15.0)
        while time.time() - start_time < max_wait:
            time.sleep(0.5)
            if os.path.exists(temp_path) and os.path.getsize(temp_path) > 0:
                self._read_available(0.2)
                return Result(success=True, content=[TextContent(text="Plot created")])

        self._read_available(0.2)
        if os.path.exists(temp_path) and os.path.getsize(temp_path) > 0:
            return Result(success=True, content=[TextContent(text="Plot created")])
        return Result(success=False, content=[ErrorContent(message="Plot file not created")])

    def _clean_output(self, output: str) -> str:
        """Clean Sage output"""
        lines = output.strip().split('\n')
        cleaned = []
        for line in lines:
            # Remove prompts (at line start or middle)
            line = re.sub(r'sage:\s*', '', line)
            line = re.sub(r'^\.+\s*', '', line)
            # Skip print input lines
            if re.match(r'^print\(', line):
                continue
            if line.strip():
                cleaned.append(line)
        return '\n'.join(cleaned)

    def _detect_plot(self, code: str) -> bool:
        plot_funcs = ['plot', 'plot3d', 'contour_plot', 'parametric_plot',
                       'list_plot', 'scatter_plot', 'bar_chart', 'histogram',
                       'graphics', 'circle', 'line', 'polygon', 'text']
        for func in plot_funcs:
            if re.search(rf'\b{func}\s*\(', code):
                return True
        return False

    def reset(self) -> None:
        if _process:
            try:
                _process.stdin.write('reset()\n')
                _process.stdin.flush()
                time.sleep(0.2)
                self._read_available()
            except Exception:
                pass

    def stop(self) -> None:
        global _process
        with _lock:
            if _process is None:
                return

            pid = _process.pid
            try:
                _process.stdin.write('quit\n')
                _process.stdin.flush()
            except Exception:
                pass

            try:
                _process.wait(timeout=2)
            except subprocess.TimeoutExpired:
                try:
                    os.kill(pid, signal.SIGTERM)
                    _process.wait(timeout=2)
                except subprocess.TimeoutExpired:
                    _process.kill()
                    _process.wait()
                except ProcessLookupError:
                    pass
            except ProcessLookupError:
                pass

            _process = None