"""
R Backend - R Statistical Computing
Supports R statistical computing and plotting
"""
import base64
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
_lock = threading.Lock()


class RBackend(ComputeBackend):
    name = "r"
    description = "R Statistical Computing - data analysis, statistics, visualization"
    capabilities = ["numeric", "plot"]

    @property
    def is_running(self) -> bool:
        return _process is not None and _process.poll() is None

    @classmethod
    def is_available(cls) -> bool:
        try:
            result = subprocess.run(['Rscript', '--version'], capture_output=True, timeout=5)
            return result.returncode == 0
        except Exception:
            return False

    def start(self) -> bool:
        global _process
        with _lock:
            # Check if process is alive
            if _process is not None and _process.poll() is None:
                return True
            
            # Process died or doesn't exist, reset and restart
            _process = None

            try:
                _process = subprocess.Popen(
                    ['R', '--vanilla', '--no-save', '--quiet'],
                    stdin=subprocess.PIPE,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True
                )

                # Set non-blocking read
                import fcntl
                fd = _process.stdout.fileno()
                fl = fcntl.fcntl(fd, fcntl.F_GETFL)
                fcntl.fcntl(fd, fcntl.F_SETFL, fl | os.O_NONBLOCK)

                fd_err = _process.stderr.fileno()
                fl_err = fcntl.fcntl(fd_err, fcntl.F_GETFL)
                fcntl.fcntl(fd_err, fcntl.F_SETFL, fl_err | os.O_NONBLOCK)

                time.sleep(0.3)
                self._read_available()

                return True
            except Exception as e:
                print(f"Failed to start R: {e}", file=__import__("sys").stderr)
                return False

    def _read_available(self, timeout: float = 0.1) -> str:
        output = ""
        start = time.time()
        while time.time() - start < timeout:
            ready, _, _ = select.select([_process.stdout, _process.stderr], [], [], 0.05)
            for stream in ready:
                try:
                    chunk = stream.read()
                    if chunk:
                        output += chunk
                except Exception:
                    pass
        return output

    def evaluate(self, code: str, timeout: float = 30.0) -> Result:
        # Check if process is alive, restart if dead
        if _process is None or _process.poll() is not None:
            if not self.start():
                return Result(success=False, content=[ErrorContent(message="R not started and cannot restart")])

        # Detect if code contains plotting
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

        # Determine if expression (needs print) or statement (assignment, function call, etc.)
        is_assignment = bool(re.match(r'^[a-zA-Z_][a-zA-Z0-9_\.]*\s*<-', code) or
                             re.match(r'^[a-zA-Z_][a-zA-Z0-9_\.]*\s*=', code))
        is_function_call = code.endswith(')') and not is_assignment
        is_library = code.startswith('library') or code.startswith('source')

        if is_assignment or is_library:
            # Assignment or library loading, no print needed
            wrapped_code = code + '\n'
        elif is_function_call:
            # Function call, may have return value, wrap with print
            wrapped_code = f'print({code})\n'
        else:
            # Expression, wrap with print
            wrapped_code = f'print({code})\n'

        _process.stdin.write(wrapped_code)
        _process.stdin.flush()

        time.sleep(0.1)
        # Only wait short time to read output, not the full timeout
        output = self._read_available(timeout=1.0)

        # Clean output
        result_text = self._clean_output(output)

        if not result_text:
            result_text = "(no output)"

        return Result(success=True, content=[TextContent(text=result_text)])

    def _execute_plot(self, code: str, temp_path: str, timeout: float) -> Result:
        # Wrap plotting code - ensure png() and dev.off() are correct
        wrapped_code = f'png("{temp_path}", width=800, height=600, res=150)\n{code}\ndev.off()\n'

        _process.stdin.write(wrapped_code)
        _process.stdin.flush()

        # Wait for plot generation
        start_time = time.time()
        max_wait = min(timeout - 1.0, 10.0)
        while time.time() - start_time < max_wait:
            time.sleep(0.3)
            if os.path.exists(temp_path) and os.path.getsize(temp_path) > 0:
                self._read_available(0.1)
                return Result(success=True, content=[TextContent(text="Plot created")])

        self._read_available(0.2)
        if os.path.exists(temp_path) and os.path.getsize(temp_path) > 0:
            return Result(success=True, content=[TextContent(text="Plot created")])
        return Result(success=False, content=[ErrorContent(message="Plot file not created")])

    def _clean_output(self, output: str) -> str:
        """Clean R output: remove prompts, line numbers, and input echo"""
        lines = output.strip().split('\n')
        cleaned = []
        for line in lines:
            # Remove R prompts
            line = re.sub(r'^>\s*', '', line)
            line = re.sub(r'^\+\s*', '', line)
            # Remove line numbers [1] [2] etc
            line = re.sub(r'^\[\d+\]\s*', '', line)
            # Skip print(...) input lines
            if re.match(r'^print\(', line):
                continue
            # Skip input echo for assignment statements
            if re.match(r'^[a-zA-Z_][a-zA-Z0-9_\.]*\s*<-', line):
                continue
            # Skip empty lines and pure prompt lines
            if line.strip() and line.strip() not in ['>', '+']:
                cleaned.append(line)
        return '\n'.join(cleaned)

    def _detect_plot(self, code: str) -> bool:
        """Detect if code contains plotting functions"""
        plot_funcs = [
            'plot', 'hist', 'barplot', 'pie', 'boxplot', 'ggplot',
            'qplot', 'geom_', 'image', 'contour', 'persp', 'curve',
            'matplot', 'pairs', 'coplot', 'dotchart', 'sunflowerplot'
        ]
        for func in plot_funcs:
            if re.search(rf'\b{func}\s*\(', code):
                return True
        return False

    def reset(self) -> None:
        if _process:
            try:
                _process.stdin.write('rm(list=ls())\n')
                _process.stdin.flush()
                time.sleep(0.1)
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
                _process.stdin.write('q("no")\n')
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