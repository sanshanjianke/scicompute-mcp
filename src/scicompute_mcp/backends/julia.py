"""
Julia Backend - Using HTTP server to avoid stdio issues
Starts a Julia HTTP server and communicates via HTTP requests
"""
import base64
import json
import os
import subprocess
import tempfile
import threading
import time
import urllib.request
import urllib.error
from typing import Optional

from .base import ComputeBackend, Result, TextContent, ImageContent, ErrorContent

# Global state
_server_process = None
_server_port = 8765
_server_lock = threading.Lock()
_server_ready = threading.Event()  # 用于标记服务器是否就绪
_prestarting = False  # 是否正在预启动

JULIA_SERVER_CODE = '''
using HTTP
using JSON3

const PORT = {port}

function handle_eval(code::String)
    try
        expr = Meta.parse(code)
        result = Core.eval(Main, expr)
        return Dict("success" => true, "result" => string(result))
    catch e
        return Dict("success" => false, "error" => string(e))
    end
end

function handle_plot(code::String, path::String)
    try
        Core.eval(Main, Meta.parse("using Plots"))
        Core.eval(Main, Meta.parse("gr()"))
        Core.eval(Main, Meta.parse(code))
        Core.eval(Main, Meta.parse("savefig(\\"" * path * "\\")"))
        return Dict("success" => true)
    catch e
        return Dict("success" => false, "error" => string(e))
    end
end

HTTP.serve("127.0.0.1", PORT) do req
    if req.method == "POST"
        body = String(HTTP.payload(req))
        data = JSON3.read(body)
        
        if haskey(data, "eval")
            result = handle_eval(data["eval"])
            return HTTP.Response(200, ["Content-Type" => "application/json"], body=JSON3.write(result))
        elseif haskey(data, "plot")
            result = handle_plot(data["plot"], data["path"])
            return HTTP.Response(200, ["Content-Type" => "application/json"], body=JSON3.write(result))
        end
    end
    HTTP.Response(404)
end
'''


def _find_julia() -> str:
    import shutil
    path = shutil.which("julia")
    if path:
        return path
    home = os.path.expanduser("~")
    for p in [f"{home}/.juliaup/bin/julia", "/usr/local/bin/julia", "/usr/bin/julia"]:
        if os.path.exists(p):
            return p
    return "julia"


JULIA_PATH = _find_julia()


def _prestart_server():
    """在后台线程中预启动 Julia 服务器"""
    global _server_process, _prestarting
    with _server_lock:
        if _server_process is not None and _server_process.poll() is None:
            return
        if _prestarting:
            return
        _prestarting = True

    try:
        server_code = JULIA_SERVER_CODE.format(port=_server_port)
        _server_process = subprocess.Popen(
            [JULIA_PATH, "-e", server_code],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )
        # 等待服务器就绪
        start_time = time.time()
        while time.time() - start_time < 10:
            try:
                req = urllib.request.Request(
                    f"http://127.0.0.1:{_server_port}",
                    data=json.dumps({"eval": "1"}).encode(),
                    headers={"Content-Type": "application/json"},
                    method="POST"
                )
                urllib.request.urlopen(req, timeout=1)
                _server_ready.set()
                break
            except:
                time.sleep(0.05)
    except Exception as e:
        print(f"Julia prestart failed: {e}", file=__import__("sys").stderr)
    finally:
        _prestarting = False


# 在模块加载时启动后台线程预启动 Julia 服务器
def _init_julia():
    """初始化 Julia 后台服务"""
    if JuliaBackend.is_available():
        t = threading.Thread(target=_prestart_server, daemon=True, name="julia-prestart")
        t.start()


# 延迟初始化（不阻塞模块导入）
_init_julia()


class JuliaBackend(ComputeBackend):
    name = "julia"
    description = "Julia - High-performance numerical computing"
    capabilities = ["numeric", "plot"]

    def __init__(self):
        pass

    @property
    def is_running(self) -> bool:
        return _server_process is not None and _server_process.poll() is None

    @classmethod
    def is_available(cls) -> bool:
        import shutil
        return shutil.which("julia") is not None or os.path.exists(JULIA_PATH)

    def _wait_for_server(self, timeout: float = 10.0) -> bool:
        """等待服务器启动（非阻塞方式）"""
        start_time = time.time()
        poll_interval = 0.05  # 50ms 轮询间隔
        while time.time() - start_time < timeout:
            try:
                req = urllib.request.Request(
                    f"http://127.0.0.1:{_server_port}",
                    data=json.dumps({"eval": "1"}).encode(),
                    headers={"Content-Type": "application/json"},
                    method="POST"
                )
                urllib.request.urlopen(req, timeout=1)
                return True
            except:
                time.sleep(poll_interval)
        return False

    def start(self) -> bool:
        global _server_process, _server_ready
        with _server_lock:
            if _server_process is not None and _server_process.poll() is None:
                # 服务器已在运行，检查是否真的就绪
                if self._wait_for_server(1.0):
                    return True
                # 服务器进程存在但无法连接，可能已崩溃
                _server_process.terminate()
                _server_process = None

            try:
                server_code = JULIA_SERVER_CODE.format(port=_server_port)

                # Start Julia server
                _server_process = subprocess.Popen(
                    [JULIA_PATH, "-e", server_code],
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL
                )

                # 非阻塞等待 - 给一个短暂的时间让进程启动
                # 但不阻塞整个事件循环
                return self._wait_for_server(15.0)

            except Exception as e:
                print(f"Failed to start Julia server: {e}", file=__import__("sys").stderr)
                return False

    def evaluate(self, code: str, timeout: float = 30.0) -> Result:
        if not self.is_running:
            return Result(success=False, content=[ErrorContent(message="Julia server not running")])

        has_plot = self._detect_plot(code)
        
        if has_plot:
            return self._execute_plot(code, timeout)
        
        return self._execute_code(code, timeout)

    def _execute_code(self, code: str, timeout: float) -> Result:
        try:
            data = json.dumps({"eval": code}).encode()
            req = urllib.request.Request(
                f"http://127.0.0.1:{_server_port}",
                data=data,
                headers={"Content-Type": "application/json"},
                method="POST"
            )
            
            with urllib.request.urlopen(req, timeout=timeout) as response:
                result = json.loads(response.read().decode())
            
            if result.get("success"):
                return Result(success=True, content=[TextContent(text=result.get("result", "(no output)"))])
            else:
                return Result(success=False, content=[ErrorContent(message=result.get("error", "Unknown error"))])
                
        except Exception as e:
            return Result(success=False, content=[ErrorContent(message=str(e))])

    def _execute_plot(self, code: str, timeout: float) -> Result:
        tmp = tempfile.NamedTemporaryFile(suffix=".png", delete=False)
        tmp_path = tmp.name
        tmp.close()
        
        try:
            data = json.dumps({"plot": code, "path": tmp_path}).encode()
            req = urllib.request.Request(
                f"http://127.0.0.1:{_server_port}",
                data=data,
                headers={"Content-Type": "application/json"},
                method="POST"
            )
            
            with urllib.request.urlopen(req, timeout=max(timeout, 60)) as response:
                result = json.loads(response.read().decode())
            
            if result.get("success") and os.path.exists(tmp_path) and os.path.getsize(tmp_path) > 0:
                with open(tmp_path, "rb") as f:
                    image_data = base64.b64encode(f.read()).decode()
                os.unlink(tmp_path)
                return Result(success=True, content=[ImageContent(data=image_data, mimeType="image/png")])
            
            if os.path.exists(tmp_path):
                os.unlink(tmp_path)
            return Result(success=False, content=[ErrorContent(message=result.get("error", "Plot failed"))])
            
        except Exception as e:
            if os.path.exists(tmp_path):
                os.unlink(tmp_path)
            return Result(success=False, content=[ErrorContent(message=str(e))])

    def _detect_plot(self, code: str) -> bool:
        funcs = ['plot', 'scatter', 'bar', 'histogram', 'heatmap', 'contour', 'surface', 'pie']
        return any(f'{f}(' in code for f in funcs)

    def reset(self) -> None:
        pass

    def stop(self) -> None:
        global _server_process
        with _server_lock:
            if _server_process is not None:
                _server_process.terminate()
                try:
                    _server_process.wait(timeout=2)
                except:
                    _server_process.kill()
                _server_process = None
