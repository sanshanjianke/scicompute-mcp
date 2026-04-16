"""
Julia Backend - High-performance numerical computing
Uses persistent Julia process for better performance
"""
import base64
import os
import re
import select
import shutil
import signal
import subprocess
import sys
import tempfile
import threading
import time
import traceback
from datetime import datetime
from typing import Optional

from .base import ComputeBackend, Result, TextContent, ImageContent, ErrorContent

# Global singleton
_process: Optional[subprocess.Popen] = None
_lock = threading.Lock()

LOG_FILE = "/tmp/scicompute_mcp.log"

def _jlog(msg):
    try:
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]
        log_line = f"[{timestamp}] [JULIA BACKEND] {msg}\n"
        with open(LOG_FILE, "a") as f:
            f.write(log_line)
            f.flush()
    except:
        pass


def _find_julia_path() -> str:
    env_path = os.environ.get("JULIA_PATH")
    if env_path and os.path.exists(env_path):
        return env_path
    which_path = shutil.which("julia")
    if which_path:
        return which_path
    home = os.path.expanduser("~")
    for path in [f"{home}/.juliaup/bin/julia", "/usr/local/bin/julia", "/usr/bin/julia"]:
        if os.path.exists(path):
            return path
    return "julia"


JULIA_PATH = _find_julia_path()


class JuliaBackend(ComputeBackend):
    name = "julia"
    description = "Julia - High-performance numerical computing"
    capabilities = ["numeric", "plot"]

    @property
    def is_running(self) -> bool:
        return _process is not None and _process.poll() is None

    @classmethod
    def is_available(cls) -> bool:
        return shutil.which("julia") is not None or os.path.exists(JULIA_PATH)

    def start(self) -> bool:
        global _process
        with _lock:
            if _process is not None and _process.poll() is None:
                return True

            try:
                _process = subprocess.Popen(
                    [JULIA_PATH, "--banner=no", "-q"],
                    stdin=subprocess.PIPE,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True,
                    close_fds=True,
                    start_new_session=True
                )

                import fcntl
                fd = _process.stdout.fileno()
                fl = fcntl.fcntl(fd, fcntl.F_GETFL)
                fcntl.fcntl(fd, fcntl.F_SETFL, fl | os.O_NONBLOCK)

                fd_err = _process.stderr.fileno()
                fl_err = fcntl.fcntl(fd_err, fcntl.F_GETFL)
                fcntl.fcntl(fd_err, fcntl.F_SETFL, fl_err | os.O_NONBLOCK)

                time.sleep(0.3)
                self._read_available(0.2)

                return True
            except Exception as e:
                print(f"Failed to start Julia: {e}", file=__import__("sys").stderr)
                return False

    def _read_available(self, timeout: float = 0.1) -> tuple:
        """Returns (stdout, stderr)"""
        stdout_out = ""
        stderr_out = ""
        start = time.time()
        total_reads = 0
        while time.time() - start < timeout:
            if _process is None:
                break
            try:
                ready, _, _ = select.select([_process.stdout, _process.stderr], [], [], 0.05)
            except:
                break
            for stream in ready:
                try:
                    chunk = stream.read()
                    total_reads += 1
                    if chunk:
                        if stream == _process.stdout:
                            stdout_out += chunk
                        else:
                            stderr_out += chunk
                except Exception as e:
                    _jlog(f"  _read_available exception: {e}")
                    pass
        if total_reads > 0 or stdout_out or stderr_out:
            _jlog(f"  _read_available: {total_reads} reads, stdout={len(stdout_out)}, stderr={len(stderr_out)}")
        return stdout_out, stderr_out

    def evaluate(self, code: str, timeout: float = 30.0) -> Result:
        _jlog(f"evaluate() START, code={code[:50]}...")
        try:
            if _process is None or _process.poll() is not None:
                _jlog("  process not running, trying to start...")
                if not self.start():
                    return Result(success=False, content=[ErrorContent(message="Julia not started and cannot restart")])

            has_plot = self._detect_plot(code)
            _jlog(f"  has_plot={has_plot}")

            if has_plot:
                result = self._execute_plot(code, timeout)
            else:
                result = self._execute_code(code, timeout)
            
            _jlog(f"evaluate() END, success={result.success}")
            return result
        except Exception as e:
            _jlog(f"evaluate() EXCEPTION: {type(e).__name__}: {e}")
            _jlog(f"  Traceback:\n{traceback.format_exc()}")
            return Result(success=False, content=[ErrorContent(message=f"Unexpected error: {e}")])

    def _execute_code(self, code: str, timeout: float) -> Result:
        global _process
        _jlog(f"_execute_code() START")
        code = code.strip()

        is_assignment = re.match(r'^[a-zA-Z_]\w*\s*=\s', code) is not None
        is_import = code.startswith('using ') or code.startswith('import ')
        is_function_def = code.startswith('function ') or code.startswith('macro ') or code.startswith('struct ')
        is_for_loop = code.startswith('for ') or code.startswith('while ')
        is_if = code.startswith('if ')
        is_try = code.startswith('try')
        is_begin = code.startswith('begin ') or code.startswith('let ')
        
        # 多行结构需要 end 结尾
        needs_end = is_function_def or is_for_loop or is_if or is_try or is_begin

        if is_assignment or is_import:
            wrapped = code + '\n'
        elif needs_end:
            # 检查是否有 end
            if not code.rstrip().endswith('end'):
                return Result(success=False, content=[ErrorContent(message=f"Syntax error: {code.split()[0]} block missing 'end'")])
            wrapped = code + '\n'
        else:
            wrapped = f'println({code})\n'
        
        _jlog(f"  wrapped code: {wrapped[:60]}...")

        try:
            # 清理之前残留的输出
            _jlog("  clearing buffer...")
            self._clear_buffer()
            
            # 检查进程是否存活
            if _process is None or _process.poll() is not None:
                _jlog("  ERROR: process died")
                return Result(success=False, content=[ErrorContent(message="Julia process died")])
            
            _jlog(f"  writing to stdin...")
            _process.stdin.write(wrapped)
            _process.stdin.flush()
            _jlog(f"  stdin flushed, waiting for output...")

            # 等待输出
            time.sleep(0.15)
            stdout_out, stderr_out = self._read_available(1.5)
            _jlog(f"  read_available returned: stdout_len={len(stdout_out)}, stderr_len={len(stderr_out)}")
            
            # 如果检测到错误开始但没有完整信息，继续等待
            combined = stdout_out + stderr_out
            if 'ERROR:' in combined and len(combined) < 50:
                time.sleep(0.5)
                stdout_out2, stderr_out2 = self._read_available(1.0)
                stdout_out += stdout_out2
                stderr_out += stderr_out2
                combined = stdout_out + stderr_out
                _jlog(f"  extended read: stdout_len={len(stdout_out)}, stderr_len={len(stderr_out)}")
            
            # 如果没有输出，再等待一下
            if not stdout_out and not stderr_out:
                _jlog("  no output, waiting more...")
                time.sleep(0.5)
                stdout_out, stderr_out = self._read_available(1.0)
                _jlog(f"  second read: stdout_len={len(stdout_out)}, stderr_len={len(stderr_out)}")

            # Julia 错误输出到 stdout 或 stderr，检查 ERROR 关键字
            combined = stdout_out + stderr_out
            if 'ERROR:' in combined or 'ParseError' in combined or 'DomainError' in combined or 'MethodError' in combined or 'UndefVarError' in combined:
                error_text = self._clean_error(combined)
                _jlog(f"  detected error: {error_text[:50]}...")
                # 错误后彻底清理缓冲区，确保下次调用干净
                self._clear_buffer()
                return Result(success=False, content=[ErrorContent(message=error_text)])

            result_text = self._clean_output(stdout_out)
            _jlog(f"  cleaned output: {result_text[:50]}...")

            if not result_text:
                result_text = "(no output)"

            # 最后再清理一次缓冲区，确保没有残留
            self._clear_buffer()
            _jlog(f"_execute_code() END successfully")
            return Result(success=True, content=[TextContent(text=result_text)])

        except BrokenPipeError:
            _jlog(f"  BrokenPipeError!")
            # 进程管道断开，尝试重启
            _process = None
            return Result(success=False, content=[ErrorContent(message="Julia process crashed (BrokenPipe)")])
        except Exception as e:
            _jlog(f"  EXCEPTION: {type(e).__name__}: {e}")
            return Result(success=False, content=[ErrorContent(message=f"Execution error: {e}")])

    def _execute_plot(self, code: str, timeout: float) -> Result:
        _jlog(f"_execute_plot() START, code_len={len(code)}")
        temp_file = tempfile.NamedTemporaryFile(suffix=".png", delete=False)
        temp_path = temp_file.name
        temp_file.close()
        _jlog(f"  temp_path={temp_path}")

        env = os.environ.copy()
        env["GKSwstype"] = "100"

        wrapped_code = f'''
using Plots
gr()
{code}
savefig("{temp_path}")
'''

        plot_timeout = max(timeout, 120.0)
        _jlog(f"  running subprocess, timeout={plot_timeout}")
        try:
            result = subprocess.run(
                [JULIA_PATH, "-e", wrapped_code],
                capture_output=True,
                text=True,
                timeout=plot_timeout,
                env=env
            )
            _jlog(f"  subprocess completed, returncode={result.returncode}")

            if os.path.exists(temp_path) and os.path.getsize(temp_path) > 0:
                file_size = os.path.getsize(temp_path)
                _jlog(f"  plot file exists, size={file_size}")
                with open(temp_path, "rb") as f:
                    raw_data = f.read()
                _jlog(f"  raw data read, len={len(raw_data)}")
                image_data = base64.b64encode(raw_data).decode("utf-8")
                _jlog(f"  base64 encoded, len={len(image_data)}")
                os.unlink(temp_path)
                _jlog(f"  temp file deleted, returning ImageContent")
                return Result(success=True, content=[ImageContent(data=image_data, mimeType="image/png")])
            else:
                _jlog(f"  plot file not created or empty")

            os.unlink(temp_path)
            error_msg = result.stderr if result.stderr else "Plot file not created"
            return Result(success=False, content=[ErrorContent(message=error_msg)])

        except subprocess.TimeoutExpired:
            _jlog(f"  TIMEOUT")
            if os.path.exists(temp_path):
                os.unlink(temp_path)
            return Result(success=False, content=[ErrorContent(message="Evaluation timed out")])
        except Exception as e:
            _jlog(f"  EXCEPTION: {type(e).__name__}: {e}")
            _jlog(f"  Traceback:\n{traceback.format_exc()}")
            if os.path.exists(temp_path):
                os.unlink(temp_path)
            return Result(success=False, content=[ErrorContent(message=str(e))])

    def _clean_output(self, output: str) -> str:
        lines = output.strip().split('\n')
        cleaned = []
        for line in lines:
            line = re.sub(r'^julia>\s*', '', line)
            line = re.sub(r'^\s*\d+\s+', '', line)
            if line.strip() and not line.strip().startswith('julia>'):
                if not re.match(r'^\s*println\(', line):
                    cleaned.append(line)
        return '\n'.join(cleaned)

    def _clean_error(self, stderr: str) -> str:
        """Clean Julia error output"""
        lines = stderr.strip().split('\n')
        cleaned = []
        for line in lines:
            line = re.sub(r'^julia>\s*', '', line)
            # 跳过堆栈跟踪中的行号
            if re.match(r'^\s*\[\d+\]', line):
                continue
            if line.strip() and not line.strip().startswith('julia>'):
                cleaned.append(line)
        result = '\n'.join(cleaned[:15])
        # 清理重复的 ERROR: 前缀
        result = re.sub(r'^(ERROR:\s*)+', 'ERROR: ', result)
        if len(result) > 500:
            result = result[:500] + "..."
        return result

    def _clear_buffer(self) -> None:
        """彻底清理输出缓冲区"""
        total_cleared = 0
        for i in range(5):
            stdout_out, stderr_out = self._read_available(0.2)
            if not stdout_out and not stderr_out:
                break
            total_cleared += len(stdout_out) + len(stderr_out)
        if total_cleared > 0:
            _jlog(f"  _clear_buffer: cleared {total_cleared} chars")

    def _detect_plot(self, code: str) -> bool:
        plot_funcs = ['plot', 'plot!', 'scatter', 'scatter!', 'bar', 'bar!', 
                      'histogram', 'histogram!', 'heatmap', 'heatmap!', 
                      'contour', 'contour!', 'surface', 'surface!',
                      'pie', 'boxplot', 'violin']
        for func in plot_funcs:
            if f'{func}(' in code:
                return True
        return False

    def reset(self) -> None:
        if _process and _process.poll() is None:
            try:
                _process.stdin.write('\n')
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
                _process.stdin.write('exit()\n')
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
