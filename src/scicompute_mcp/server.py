import asyncio
import atexit
import json
import signal
import sys
import traceback
import os
from datetime import datetime

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent as MCPTextContent, ImageContent as MCPImageContent

from .manager import BackendManager

LOG_FILE = "/tmp/scicompute_mcp.log"

def _log(msg):
    try:
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]
        log_line = f"[{timestamp}] [MCP SERVER] {msg}\n"
        with open(LOG_FILE, "a") as f:
            f.write(log_line)
            f.flush()
    except:
        pass

def _log_stack():
    """Log call stack"""
    try:
        stack = ''.join(traceback.format_stack()[-6:-1])
        _log(f"  Call stack:\n{stack}")
    except:
        pass

try:
    with open(LOG_FILE, "w") as f:
        f.write(f"=== MCP SERVER LOG STARTED AT {datetime.now()} ===\n")
except:
    pass

_log("=== SERVER MODULE LOADING ===")
server = Server("scicompute")
_log("  MCP Server instance created")
manager = BackendManager()
_log("  BackendManager instance created")
_shutdown_requested = False


def _cleanup():
    global _shutdown_requested
    if _shutdown_requested:
        _log("=== _cleanup() SKIPPED (already shutdown) ===")
        return
    _shutdown_requested = True
    _log("=== _cleanup() called ===")
    _log_stack()
    try:
        manager.stop("ALL")
        _log("  _cleanup() completed")
    except Exception as e:
        _log(f"  _cleanup error: {e}")


@atexit.register
def _atexit_cleanup():
    _log("=== _atexit_cleanup() triggered ===")
    _log_stack()
    try:
        _cleanup()
    except Exception as e:
        _log(f"  _atexit_cleanup error: {e}")


def _signal_handler(signum, frame):
    _log(f"=== _signal_handler() triggered: signal={signum} ===")
    _log_stack()
    try:
        _cleanup()
    except Exception as e:
        _log(f"  signal_handler error: {e}")
    sys.exit(0)


signal.signal(signal.SIGTERM, _signal_handler)
signal.signal(signal.SIGINT, _signal_handler)
signal.signal(signal.SIGHUP, _signal_handler)


DOC_URLS = {
    "mathematica": {
        "function": "https://reference.wolfram.com/language/ref/{symbol}.html",
        "guide": "https://reference.wolfram.com/language/guide/{topic}.html",
        "example": "Plot3D -> https://reference.wolfram.com/language/ref/Plot3D.html"
    },
    "numpy": {
        "reference": "https://numpy.org/doc/stable/reference/generated/numpy.{symbol}.html",
        "example": "array -> https://numpy.org/doc/stable/reference/generated/numpy.array.html"
    },
    "scipy": {
        "module": "https://docs.scipy.org/doc/scipy/reference/{module}.html",
        "example": "integrate -> https://docs.scipy.org/doc/scipy/reference/integrate.html"
    },
    "matplotlib": {
        "pyplot": "https://matplotlib.org/stable/api/_as_gen/matplotlib.pyplot.{symbol}.html",
        "example": "plot -> https://matplotlib.org/stable/api/_as_gen/matplotlib.pyplot.plot.html"
    },
    "sympy": {
        "reference": "https://docs.sympy.org/latest/reference/",
        "modules": "https://docs.sympy.org/latest/modules/{module}.html",
        "example": "calculus -> https://docs.sympy.org/latest/modules/calculus.html"
    },
    "pandas": {
        "api": "https://pandas.pydata.org/docs/reference/api/pandas.{symbol}.html",
        "example": "DataFrame -> https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.html"
    },
    "python": {
        "library": "https://docs.python.org/3/library/{module}.html",
        "example": "math -> https://docs.python.org/3/library/math.html"
    },
    "r": {
        "function": "https://www.rdocumentation.org/packages/{package}/functions/{symbol}",
        "packages": "base, graphics, stats, utils, ggplot2, dplyr",
        "search": "https://www.rdocumentation.org/",
        "example": "plot (graphics) -> https://www.rdocumentation.org/packages/graphics/functions/plot"
    },
    "julia": {
        "base": "https://docs.julialang.org/en/v1/base/math/#Base.{symbol}",
        "stdlib": "https://docs.julialang.org/en/v1/stdlib/{package}/",
        "manual": "https://docs.julialang.org/en/v1/",
        "example": "sin -> https://docs.julialang.org/en/v1/base/math/#Base.sin"
    },
    "octave": {
        "function": "https://docs.octave.org/interpreter/XREF{symbol}.html",
        "index": "https://docs.octave.org/interpreter/Function-Index.html",
        "example": "plot -> https://docs.octave.org/interpreter/XREFplot.html"
    },
    "sage": {
        "search": "https://doc.sagemath.org/html/en/reference/search.html?q={symbol}",
        "calculus": "https://doc.sagemath.org/html/en/reference/calculus/",
        "plotting": "https://doc.sagemath.org/html/en/reference/plotting/",
        "example": "integrate -> https://doc.sagemath.org/html/en/reference/search.html?q=integrate"
    },
    "maxima": {
        "manual": "https://maxima.sourceforge.io/docs/manual/maxima.html",
        "note": "Single page manual, use browser search (Ctrl+F) to find functions",
        "internal": "Use '? functionname' or '?? keyword' within Maxima"
    },
    "matlab": {
        "function": "https://www.mathworks.com/help/matlab/ref/{symbol}.html",
        "search": "https://www.mathworks.com/help/search.html?q={symbol}",
        "example": "plot3 -> https://www.mathworks.com/help/matlab/ref/plot3.html"
    }
}


@server.list_tools()
async def list_tools() -> list[Tool]:
    return [
        Tool(
            name="compute",
            description="Execute scientific computing code. Supports multiple backends (mathematica, sage, py_scientific, r, octave, julia, maxima). Use 'backend' parameter to specify, or leave empty for auto-select. For documentation URLs, use the doc tool.",
            inputSchema={
                "type": "object",
                "properties": {
                    "code": {
                        "type": "string",
                        "description": "Code to execute in the selected backend"
                    },
                    "backend": {
                        "type": "string",
                        "description": "Backend name (mathematica, sage, py_scientific, r, octave, julia, maxima). Leave empty for auto-select."
                    }
                },
                "required": ["code"]
            }
        ),
        Tool(
            name="list_backends",
            description="List all available computing backends and their capabilities",
            inputSchema={
                "type": "object",
                "properties": {}
            }
        ),
        Tool(
            name="stop",
            description="Stop backend to clear variables and free memory. Use when you want a clean slate or the backend is misbehaving. The backend will restart automatically when needed.",
            inputSchema={
                "type": "object",
                "properties": {
                    "backend": {
                        "type": "string",
                        "description": "Backend name (e.g., 'octave', 'mathematica'). Leave empty to list running backends."
                    }
                }
            }
        ),
        Tool(
            name="doc",
            description="Get documentation URLs for computing backends. Use this to find where to look up function documentation. Call without args to see all backends, or specify backend to get specific URLs.",
            inputSchema={
                "type": "object",
                "properties": {
                    "backend": {
                        "type": "string",
                        "description": "Backend name (mathematica, numpy, scipy, matplotlib, sympy, pandas, python, r, julia, octave, sage, maxima, matlab). Leave empty to see all."
                    },
                    "symbol": {
                        "type": "string",
                        "description": "Function/class name to look up. If provided, returns URL template with symbol filled in."
                    }
                }
            }
        )
    ]


def _safe_process_content(item) -> list:
    """Safely process content item, catching all exceptions"""
    content = []
    try:
        _log(f"    _safe_process_content: type={type(item).__name__}")
        if isinstance(item, dict):
            item_type = item.get("type")
            if item_type == "text":
                text = item.get("text", "")
                content.append(MCPTextContent(type="text", text=text))
            elif item_type == "image":
                data = item.get("data", "")
                _log(f"      Creating MCPImageContent, data_len={len(data)}")
                content.append(MCPImageContent(
                    type="image",
                    data=data,
                    mimeType=item.get("mimeType", "image/png")
                ))
                _log(f"      MCPImageContent created successfully")
            elif item_type == "error":
                msg = item.get('message', 'Unknown error')
                content.append(MCPTextContent(type="text", text=f"Error: {msg}"))
        elif hasattr(item, 'type'):
            _log(f"      item.type={item.type}")
            if item.type == "text":
                content.append(MCPTextContent(type="text", text=item.text if item.text else ""))
            elif item.type == "image":
                _log(f"      Creating MCPImageContent from object, data_len={len(item.data)}")
                content.append(MCPImageContent(type="image", data=item.data, mimeType=item.mimeType))
                _log(f"      MCPImageContent from object created successfully")
            elif item.type == "error":
                msg = item.message if hasattr(item, 'message') else 'Unknown error'
                content.append(MCPTextContent(type="text", text=f"Error: {msg}"))
    except Exception as e:
        _log(f"    _safe_process_content EXCEPTION: {type(e).__name__}: {e}")
        _log_stack()
        content.append(MCPTextContent(type="text", text=f"Content processing error: {e}"))
    return content


@server.call_tool()
async def call_tool(name: str, arguments: dict) -> list:
    _log(f"=== call_tool() START ===")
    _log(f"  Tool name: {name}")

    try:
        if name == "compute":
            code = arguments.get("code", "")
            backend = arguments.get("backend")

            _log(f"  COMPUTE: backend={backend}, code_len={len(code)}")

            try:
                # Direct call to test if thread pool causes issues
                result = manager.compute(code, backend)
                _log(f"  compute returned: success={result.success}, content_count={len(result.content)}")
            except Exception as e:
                _log(f"  manager.compute EXCEPTION: {e}")
                _log_stack()
                return [MCPTextContent(type="text", text=f"Backend error: {e}")]

            content = []
            for i, item in enumerate(result.content):
                _log(f"  Processing content[{i}]...")
                content.extend(_safe_process_content(item))

            _log(f"=== call_tool() END - {len(content)} items ===")
            # Log the actual response being returned
            for i, c in enumerate(content):
                _log(f"  Response[{i}]: type={c.type}, text={getattr(c, 'text', 'N/A')[:50]}")
            return content

        elif name == "list_backends":
            _log(f"  LIST_BACKENDS")
            try:
                backends = manager.list_available()
                text = json.dumps(backends, indent=2)
                return [MCPTextContent(type="text", text=text)]
            except Exception as e:
                _log(f"  list_backends error: {e}")
                return [MCPTextContent(type="text", text=f"Error: {e}")]

        elif name == "stop":
            _log(f"  STOP")
            backend = arguments.get("backend")
            try:
                result = manager.stop(backend)
                return [MCPTextContent(type="text", text=json.dumps(result))]
            except Exception as e:
                _log(f"  stop error: {e}")
                return [MCPTextContent(type="text", text=f"Error: {e}")]

        elif name == "doc":
            _log(f"  DOC")
            backend = arguments.get("backend", "").lower() if arguments.get("backend") else None
            symbol = arguments.get("symbol", "").lower() if arguments.get("symbol") else None
            
            try:
                if backend and backend in DOC_URLS:
                    info = DOC_URLS[backend]
                    if symbol:
                        result = {"backend": backend, "symbol": symbol}
                        for key, url_template in info.items():
                            if key != "note" and key != "packages" and key != "example" and key != "internal":
                                if "{symbol}" in url_template:
                                    result[key] = url_template.replace("{symbol}", symbol)
                                elif "{package}" in url_template:
                                    result[key] = url_template
                                else:
                                    result[key] = url_template
                    else:
                        result = {"backend": backend, "urls": info}
                elif backend:
                    result = {"error": f"Unknown backend: {backend}", "available": list(DOC_URLS.keys())}
                else:
                    result = {"backends": list(DOC_URLS.keys()), "hint": "Call doc(backend='...') for specific backend URLs"}
                
                return [MCPTextContent(type="text", text=json.dumps(result, indent=2))]
            except Exception as e:
                _log(f"  doc error: {e}")
                return [MCPTextContent(type="text", text=f"Error: {e}")]

        else:
            return [MCPTextContent(type="text", text=f"Unknown tool: {name}")]
            
    except Exception as e:
        _log(f"=== call_tool() TOP LEVEL EXCEPTION ===")
        _log(f"  {type(e).__name__}: {e}")
        _log(f"  Traceback:\n{traceback.format_exc()}")
        return [MCPTextContent(type="text", text=f"Error: {type(e).__name__}: {e}")]


async def run():
    _log("=== run() starting ===")
    try:
        async with stdio_server() as (read_stream, write_stream):
            _log("  stdio_server context entered")
            try:
                _log("  calling server.run()...")
                await server.run(read_stream, write_stream, server.create_initialization_options())
                _log("  server.run() completed normally - client likely disconnected")
            except asyncio.CancelledError as e:
                _log(f"  server.run() CANCELLED: {e}")
                _log_stack()
                raise
            except BrokenPipeError as e:
                _log(f"  server.run() BrokenPipeError: {e}")
                _log_stack()
                raise
            except Exception as e:
                _log(f"  server.run() EXCEPTION: {type(e).__name__}: {e}")
                _log_stack()
                raise
    except Exception as e:
        _log(f"=== run() EXCEPTION: {type(e).__name__}: {e} ===")
        _log(f"  Traceback:\n{traceback.format_exc()}")
        raise
    finally:
        _log("=== run() finally block ===")
        # Ensure all output is flushed
        sys.stdout.flush()
        sys.stderr.flush()


def main():
    _log("=== main() starting ===")
    try:
        asyncio.run(run())
        _log("=== main() asyncio.run() completed ===")
    except KeyboardInterrupt:
        _log("=== main() KeyboardInterrupt ===")
    except Exception as e:
        _log(f"=== main() EXCEPTION: {type(e).__name__}: {e} ===")
        _log(f"  Traceback:\n{traceback.format_exc()}")
        sys.exit(1)
    finally:
        _log("=== main() finally block ===")


if __name__ == "__main__":
    main()
