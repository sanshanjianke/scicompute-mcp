import os
import sys
import traceback
from typing import Optional, Type
from datetime import datetime

from .backends.base import ComputeBackend, Result, ErrorContent
from .backends.mathematica import MathematicaBackend
from .backends.octave import OctaveBackend
from .backends.maxima import MaximaBackend
from .backends.py_scientific import PyScientificBackend
from .backends.r import RBackend
from .backends.sage import SageBackend
from .backends.matlab import MatlabBackend


from .backends.julia import JuliaBackend

LOG_FILE = "/tmp/scicompute_mcp.log"

def _log(msg):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]
    log_line = f"[{timestamp}] [BACKEND MANAGER] {msg}\n"
    with open(LOG_FILE, "a") as f:
        f.write(log_line)
        f.flush()


class BackendManager:
    def __init__(self):
        _log("=== BackendManager.__init__() START ===")
        self._backend_classes: dict[str, Type[ComputeBackend]] = {}
        self._priority: list[str] = []

        self._register_backend_classes()
        self._load_priority()
        _log(f"=== BackendManager.__init__() DONE - registered {len(self._backend_classes)} backends ===")

    def _register_backend_classes(self):
        self._backend_classes["mathematica"] = MathematicaBackend
        self._backend_classes["octave"] = OctaveBackend
        # maxima is reserved but disabled by default; uncomment to enable
        # self._backend_classes["maxima"] = MaximaBackend
        self._backend_classes["py_scientific"] = PyScientificBackend
        self._backend_classes["r"] = RBackend
        self._backend_classes["sage"] = SageBackend
        self._backend_classes["matlab"] = MatlabBackend
        self._backend_classes["julia"] = JuliaBackend
        _log(f"_register_backend_classes() registered: {list(self._backend_classes.keys())}")

    def _load_priority(self):
        env_priority = os.environ.get("SCICOMPUTE_PRIORITY", "")
        if env_priority:
            self._priority = [p.strip() for p in env_priority.split(",")]
            _log(f"_load_priority() from env: {self._priority}")
        else:
            self._priority = ["mathematica", "sage", "julia", "py_scientific", "r", "octave", "matlab"]
            _log(f"_load_priority() default: {self._priority}")

    def list_available(self) -> list[dict]:
        result = []
        for name, backend_cls in self._backend_classes.items():
            if backend_cls.is_available():
                result.append({
                    "name": backend_cls.name,
                    "description": backend_cls.description,
                    "capabilities": backend_cls.capabilities,
                })
        return result

    def select_backend(self, name: Optional[str] = None) -> tuple[Optional[ComputeBackend], str]:
        if name:
            backend_cls = self._backend_classes.get(name)
            if backend_cls and backend_cls.is_available():
                return backend_cls(), name
            return None, f"Backend '{name}' not available"

        for backend_name in self._priority:
            backend_cls = self._backend_classes.get(backend_name)
            if backend_cls and backend_cls.is_available():
                return backend_cls(), backend_name

        return None, "No available backends"

    def compute(self, code: str, backend: Optional[str] = None, timeout: float = 30.0) -> Result:
        _log(f"=== compute() START ===")
        _log(f"  backend requested: {backend}")
        _log(f"  code length: {len(code)}")
        _log(f"  code preview: {code[:100]}{'...' if len(code) > 100 else ''}")
        _log(f"  timeout: {timeout}")
        
        try:
            selected, msg = self.select_backend(backend)
            if not selected:
                available = [b["name"] for b in self.list_available()]
                _log(f"  ERROR: No backend selected - {msg}")
                _log(f"  Available backends: {available}")
                return Result(
                    success=False,
                    content=[ErrorContent(message=f"{msg}. Available: {available}")]
                )

            _log(f"  Selected backend: {selected.name}")
            
            _log(f"  Calling backend.start()...")
            if not selected.start():
                _log(f"  ERROR: Failed to start backend {selected.name}")
                return Result(
                    success=False,
                    content=[ErrorContent(message=f"Failed to start {selected.name}")]
                )
            _log(f"  Backend started successfully")

            _log(f"  Calling backend.evaluate()...")
            result = selected.evaluate(code, timeout)
            _log(f"  evaluate() returned: success={result.success}, content_count={len(result.content)}")
            if result.content:
                for i, c in enumerate(result.content):
                    _log(f"    content[{i}]: type={c.type}")
            _log(f"=== compute() END (success) ===")
            return result
            
        except Exception as e:
            _log(f"=== compute() UNEXPECTED EXCEPTION ===")
            _log(f"  Exception type: {type(e).__name__}")
            _log(f"  Exception message: {e}")
            _log(f"  Traceback:\n{traceback.format_exc()}")
            return Result(
                success=False,
                content=[ErrorContent(message=f"Internal error: {type(e).__name__}: {e}")]
            )

    def stop(self, backend: Optional[str] = None) -> dict:
        """Stop backend and clear all state.

        No arguments: Returns list of running backends, does NOT stop any.
        With backend name: Stops the specified backend.
        With "ALL": Stops all running backends.
        """
        # Get list of running backends
        running = []
        for name, backend_cls in self._backend_classes.items():
            if backend_cls.is_available():
                instance = backend_cls()
                if hasattr(instance, 'is_running') and instance.is_running:
                    running.append(name)

        # No argument: return running backends list
        if backend is None:
            if running:
                return {
                    "success": True,
                    "action": "list",
                    "running_backends": running,
                    "message": f"Running backends: {running}. Use stop('ALL') to stop all. Use stop('backend_name') to stop a specific backend."
                }
            else:
                return {
                    "success": True,
                    "action": "list",
                    "running_backends": [],
                    "message": "No running backends."
                }

        # With "ALL": stop all backends
        if backend.upper() == "ALL":
            stopped = []
            for name in running:
                backend_cls = self._backend_classes.get(name)
                if backend_cls:
                    instance = backend_cls()
                    instance.stop()
                    stopped.append(name)
            return {
                "success": True,
                "action": "stop_all",
                "stopped": stopped,
                "message": f"Stopped all backends: {stopped}"
            }

        # With specific backend name: stop that backend
        backend_cls = self._backend_classes.get(backend)
        if backend_cls:
            if backend not in running:
                return {
                    "success": True,
                    "action": "stop",
                    "stopped": [],
                    "message": f"Backend '{backend}' is not running, no need to stop."
                }
            instance = backend_cls()
            instance.stop()
            return {
                "success": True,
                "action": "stop",
                "stopped": [backend],
                "message": f"Stopped backend: {backend}"
            }
        return {"success": False, "message": f"Backend '{backend}' not found. Available: {list(self._backend_classes.keys())}"}

    def doc(self, symbol: str, backend: Optional[str] = None) -> Result:
        selected, msg = self.select_backend(backend)
        if not selected:
            available = [b["name"] for b in self.list_available()]
            return Result(
                success=False,
                content=[ErrorContent(message=f"{msg}. Available: {available}")]
            )

        if not selected.start():
            return Result(
                success=False,
                content=[ErrorContent(message=f"Failed to start {selected.name}")]
            )

        if selected.name == "mathematica":
            doc_code = f'''Module[{{usage, opts, attrs, result}},
                result = Quiet[Check[
                    usage = ToString[Information[{symbol}, "Usage"], OutputForm];
                    opts = ToString[Options[{symbol}], OutputForm];
                    attrs = ToString[Attributes[{symbol}], OutputForm];
                    If[usage === "Null" || StringQ[usage] === False,
                        "Symbol '{symbol}' not found or has no documentation.",
                        "=== {symbol} ===" <> "\\n\\n" <>
                        "USAGE:\\n" <> usage <> "\\n\\n" <>
                        "ATTRIBUTES: " <> attrs <> "\\n\\n" <>
                        "OPTIONS:\\n" <> opts
                    ],
                    "Symbol '{symbol}' not found."
                ]];
                result
            ]'''
        elif selected.name == "octave":
            doc_code = f'ans = help("{symbol}"); disp(ans)'
        elif selected.name == "maxima":
            doc_code = f'? {symbol}'
        elif selected.name == "py_scientific":
            doc_code = f'import inspect; print(inspect.getdoc({symbol}))'
        elif selected.name == "r":
            doc_code = f'?{symbol}'
        elif selected.name == "sage":
            doc_code = f'{symbol}?'
        elif selected.name == "matlab":
            doc_code = f'help {symbol}'
        elif selected.name == "julia":
            doc_code = f'@doc {symbol}'
        else:
            return Result(
                success=False,
                content=[ErrorContent(message=f"doc not supported for backend: {selected.name}")]
            )

        return selected.evaluate(doc_code)