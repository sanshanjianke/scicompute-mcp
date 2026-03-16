import os
from typing import Optional

from .backends.base import ComputeBackend, Result, ErrorContent
from .backends.mathematica import MathematicaBackend
from .backends.octave import OctaveBackend


class BackendManager:
    def __init__(self):
        self._backends: dict[str, ComputeBackend] = {}
        self._priority: list[str] = []
        
        self._register_default_backends()
        self._load_priority()
    
    def _register_default_backends(self):
        self._backends["mathematica"] = MathematicaBackend()
        self._backends["octave"] = OctaveBackend()
    
    def _load_priority(self):
        env_priority = os.environ.get("SCICOMPUTE_PRIORITY", "")
        if env_priority:
            self._priority = [p.strip() for p in env_priority.split(",")]
        else:
            self._priority = ["mathematica", "octave"]
    
    def list_available(self) -> list[dict]:
        result = []
        for name, backend in self._backends.items():
            if backend.is_available():
                result.append({
                    "name": backend.name,
                    "description": backend.description,
                    "capabilities": backend.capabilities,
                })
        return result
    
    def get_backend(self, name: str) -> Optional[ComputeBackend]:
        return self._backends.get(name)
    
    def select_backend(self, name: Optional[str] = None) -> tuple[Optional[ComputeBackend], str]:
        if name:
            backend = self._backends.get(name)
            if backend and backend.is_available():
                return backend, name
            return None, f"Backend '{name}' not available"
        
        for backend_name in self._priority:
            backend = self._backends.get(backend_name)
            if backend and backend.is_available():
                return backend, backend_name
        
        return None, "No available backends"
    
    def compute(self, code: str, backend: Optional[str] = None, timeout: float = 30.0) -> Result:
        selected, msg = self.select_backend(backend)
        if not selected:
            available = [b["name"] for b in self.list_available()]
            return Result(
                success=False,
                content=[ErrorContent(message=f"{msg}. Available: {available}")]
            )
        
        if not selected._started:
            if not selected.start():
                return Result(
                    success=False,
                    content=[ErrorContent(message=f"Failed to start {selected.name}")]
                )
        
        return selected.evaluate(code, timeout)
    
    def reset(self, backend: Optional[str] = None) -> dict:
        if backend:
            b = self._backends.get(backend)
            if b:
                b.reset()
                return {"success": True, "message": f"Reset {backend}"}
            return {"success": False, "message": f"Backend '{backend}' not found"}
        
        for b in self._backends.values():
            if b._started:
                b.reset()
        return {"success": True, "message": "Reset all backends"}
    
    def stop_all(self) -> None:
        for b in self._backends.values():
            if b._started:
                try:
                    b.stop()
                except Exception:
                    pass
    
    def stop(self, backend: Optional[str] = None) -> dict:
        if backend:
            b = self._backends.get(backend)
            if b:
                if b._started:
                    b.stop()
                    return {"success": True, "message": f"Stopped {backend}"}
                return {"success": True, "message": f"{backend} not running"}
            return {"success": False, "message": f"Backend '{backend}' not found"}
        
        self.stop_all()
        return {"success": True, "message": "Stopped all backends"}
    
    def doc(self, symbol: str, backend: Optional[str] = None) -> Result:
        selected, msg = self.select_backend(backend)
        if not selected:
            available = [b["name"] for b in self.list_available()]
            return Result(
                success=False,
                content=[ErrorContent(message=f"{msg}. Available: {available}")]
            )
        
        if not selected._started:
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
        else:
            return Result(
                success=False,
                content=[ErrorContent(message=f"doc not supported for backend: {selected.name}")]
            )
        
        return selected.evaluate(doc_code)