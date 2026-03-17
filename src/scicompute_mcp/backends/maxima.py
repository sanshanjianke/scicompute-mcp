import base64
import fcntl
import os
import re
import select
import signal
import subprocess
import tempfile
import threading
import time
from typing import Optional

from .base import ComputeBackend, Result, TextContent, ImageContent, ErrorContent

# Global singleton
_process: Optional[subprocess.Popen] = None
_input_num: int = 0
_lock = threading.Lock()


class MaximaBackend(ComputeBackend):
    name = "maxima"
    description = "Maxima - Computer Algebra System"
    capabilities = ["symbolic", "numeric", "plot"]

    @classmethod
    def is_available(cls) -> bool:
        try:
            result = subprocess.run(['maxima', '--version'], capture_output=True, timeout=5)
            return result.returncode == 0
        except Exception:
            return False

    def start(self) -> bool:
        global _process, _input_num
        with _lock:
            if _process is not None:
                return True

            try:
                _process = subprocess.Popen(
                    ['maxima', '--quiet'],
                    stdin=subprocess.PIPE,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True
                )

                fd = _process.stdout.fileno()
                fl = fcntl.fcntl(fd, fcntl.F_GETFL)
                fcntl.fcntl(fd, fcntl.F_SETFL, fl | os.O_NONBLOCK)

                _input_num = 0

                time.sleep(0.3)
                self._read_available()

                return True
            except Exception as e:
                print(f"Failed to start Maxima: {e}", file=__import__("sys").stderr)
                return False

    def _read_available(self, timeout: float = 0.1) -> str:
        output = ""
        start = time.time()
        while time.time() - start < timeout:
            ready, _, _ = select.select([_process.stdout], [], [], 0.05)
            if ready:
                try:
                    chunk = _process.stdout.read()
                    if chunk:
                        output += chunk
                except Exception:
                    pass
        return output

    def evaluate(self, code: str, timeout: float = 30.0) -> Result:
        global _process
        if _process is None:
            return Result(success=False, content=[ErrorContent(message="Maxima not started")])

        has_plot = self._detect_plot(code)
        is_interactive = self._is_interactive_plot(code)

        if has_plot and is_interactive:
            return self._execute_code(code, timeout)

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
        global _input_num
        code = self._normalize_code(code)
        _input_num += 1

        _process.stdin.write(code + '\n')
        _process.stdin.flush()

        output = self._wait_for_output(_input_num, timeout)
        result_text = self._extract_output(output, _input_num)

        result_text = result_text.strip()
        if not result_text:
            result_text = "(no output)"

        if self._is_error(result_text):
            return Result(success=False, content=[ErrorContent(message=result_text)])

        return Result(success=True, content=[TextContent(text=result_text)])

    def _execute_plot(self, code: str, temp_path: str, timeout: float) -> Result:
        global _input_num
        setup_code = f'set_plot_option([gnuplot_term, png]); set_plot_option([gnuplot_out_file, "{temp_path}"]);'
        _process.stdin.write(setup_code + '\n')
        _process.stdin.flush()
        time.sleep(0.1)
        self._read_available(0.3)
        _input_num += 2

        code = code.rstrip(';').rstrip('$')
        _process.stdin.write(code + '$\n')
        _process.stdin.flush()
        _input_num += 1

        start_time = time.time()
        max_wait = min(timeout - 1.0, 10.0)
        while time.time() - start_time < max_wait:
            time.sleep(0.2)
            if os.path.exists(temp_path) and os.path.getsize(temp_path) > 0:
                self._read_available(0.1)
                return Result(success=True, content=[TextContent(text="Plot created")])

        self._read_available(0.2)
        if os.path.exists(temp_path) and os.path.getsize(temp_path) > 0:
            return Result(success=True, content=[TextContent(text="Plot created")])
        return Result(success=False, content=[ErrorContent(message="Plot file not created")])

    def _wait_for_output(self, input_num: int, timeout: float = 30.0) -> str:
        output_marker = f"(%o{input_num})"
        next_marker = f"(%i{input_num + 1})"
        error_markers = ["-- an error", "Cannot find documentation", "debugmode"]
        start_time = time.time()
        output = ""

        while True:
            elapsed = time.time() - start_time
            if elapsed >= timeout:
                raise TimeoutError("Read timeout")

            ready, _, _ = select.select([_process.stdout], [], [], 0.1)
            if ready:
                try:
                    chunk = _process.stdout.read()
                    if chunk:
                        output += chunk
                except Exception:
                    pass

            if next_marker in output:
                break

            if output_marker in output and not ready:
                break

            for err_marker in error_markers:
                if err_marker in output and next_marker in output:
                    break
            else:
                continue
            break

        return output

    def reset(self) -> None:
        global _input_num
        if _process:
            try:
                _process.stdin.write("kill(all);\n")
                _process.stdin.flush()
                time.sleep(0.2)
                self._read_available()
                _input_num = 0
            except Exception:
                pass

    def stop(self) -> None:
        global _process, _input_num
        with _lock:
            if _process is None:
                return

            pid = _process.pid
            try:
                _process.stdin.write("quit();\n")
                _process.stdin.flush()
            except Exception:
                pass

            try:
                _process.wait(timeout=1)
            except subprocess.TimeoutExpired:
                try:
                    os.kill(pid, signal.SIGTERM)
                    _process.wait(timeout=1)
                except subprocess.TimeoutExpired:
                    _process.kill()
                    _process.wait()
                except ProcessLookupError:
                    pass
            except ProcessLookupError:
                pass

            _process = None
            _input_num = 0

    def _normalize_code(self, code: str) -> str:
        code = code.strip()
        if not code.endswith(';') and not code.endswith('$'):
            code += ';'
        return code

    def _detect_plot(self, code: str) -> bool:
        plot_funcs = ['plot2d', 'plot3d', 'draw2d', 'draw3d', 'contour_plot']
        for func in plot_funcs:
            if re.search(rf'\b{func}\s*\(', code):
                return True
        return False

    def _is_interactive_plot(self, code: str) -> bool:
        interactive_terminals = ['x11', 'wxt', 'qt', 'aqua', 'windows']
        for term in interactive_terminals:
            if re.search(rf'\[gnuplot_term\s*,\s*{term}\]', code, re.IGNORECASE):
                return True
        return False

    def _extract_output(self, raw: str, input_num: int) -> str:
        output_marker = f"(%o{input_num})"

        idx = raw.find(output_marker)
        if idx == -1:
            return ""

        start = idx + len(output_marker)
        while start < len(raw) and raw[start] == ' ':
            start += 1

        end = len(raw)

        for pattern in [f"(%i{input_num + 1})", "(%i"]:
            next_i = raw.find(pattern, start)
            if next_i != -1 and next_i < end:
                end = next_i

        result = raw[start:end]

        return result.strip()

    def _is_error(self, text: str) -> bool:
        error_patterns = [
            r'^\s*incorrect syntax',
            r'^\s*invalid',
            r'^\s*unexpected',
            r'^\s*out of memory',
            r'^\s*wrong number of arguments',
        ]
        for pattern in error_patterns:
            if re.search(pattern, text, re.IGNORECASE):
                return True
        return False