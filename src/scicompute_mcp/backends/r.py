"""
R Backend - R Statistical Computing
支持 R 语言统计计算和绑图
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

# 全局单例
_process: Optional[subprocess.Popen] = None
_lock = threading.Lock()


class RBackend(ComputeBackend):
    name = "r"
    description = "R Statistical Computing - data analysis, statistics, visualization"
    capabilities = ["numeric", "plot"]

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
            if _process is not None:
                return True

            try:
                _process = subprocess.Popen(
                    ['R', '--vanilla', '--no-save', '--quiet'],
                    stdin=subprocess.PIPE,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True
                )

                # 设置非阻塞读取
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
        if _process is None:
            return Result(success=False, content=[ErrorContent(message="R not started")])

        # 检测是否包含绘图
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

        # 判断是否是表达式（需要打印结果）还是语句（赋值、函数调用等）
        is_assignment = bool(re.match(r'^[a-zA-Z_][a-zA-Z0-9_\.]*\s*<-', code) or
                             re.match(r'^[a-zA-Z_][a-zA-Z0-9_\.]*\s*=', code))
        is_function_call = code.endswith(')') and not is_assignment
        is_library = code.startswith('library') or code.startswith('source')

        if is_assignment or is_library:
            # 赋值语句或库加载，不需要 print
            wrapped_code = code + '\n'
        elif is_function_call:
            # 函数调用，可能返回值，用 print 包裹
            wrapped_code = f'print({code})\n'
        else:
            # 表达式，用 print 包裹
            wrapped_code = f'print({code})\n'

        _process.stdin.write(wrapped_code)
        _process.stdin.flush()

        time.sleep(0.1)
        output = self._read_available(timeout)

        # 清理输出
        result_text = self._clean_output(output)

        if not result_text:
            result_text = "(no output)"

        return Result(success=True, content=[TextContent(text=result_text)])

    def _execute_plot(self, code: str, temp_path: str, timeout: float) -> Result:
        # 包装绘图代码 - 确保 png() 和 dev.off() 正确
        wrapped_code = f'png("{temp_path}", width=800, height=600, res=150)\n{code}\ndev.off()\n'

        _process.stdin.write(wrapped_code)
        _process.stdin.flush()

        # 等待图片生成
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
        """清理 R 输出中的提示符、行号和输入回显"""
        lines = output.strip().split('\n')
        cleaned = []
        for line in lines:
            # 移除 R 提示符
            line = re.sub(r'^>\s*', '', line)
            line = re.sub(r'^\+\s*', '', line)
            # 移除行号 [1] [2] 等
            line = re.sub(r'^\[\d+\]\s*', '', line)
            # 跳过 print(...) 输入行
            if re.match(r'^print\(', line):
                continue
            # 跳过赋值语句的输入回显
            if re.match(r'^[a-zA-Z_][a-zA-Z0-9_\.]*\s*<-', line):
                continue
            # 跳过空行和纯提示符行
            if line.strip() and line.strip() not in ['>', '+']:
                cleaned.append(line)
        return '\n'.join(cleaned)

    def _detect_plot(self, code: str) -> bool:
        """检测是否包含绘图函数"""
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