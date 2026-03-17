import base64
import glob
import os
import tempfile
import threading
from typing import Optional

from .base import ComputeBackend, Result, TextContent, ImageContent, ErrorContent

# Global singleton
_session: Optional[object] = None
_lock = threading.Lock()


def _find_mathematica_kernel() -> str:
    """Find WolframKernel path"""
    # Environment variable takes priority
    env_path = os.environ.get("MATHEMATICA_KERNEL_PATH")
    if env_path and os.path.exists(env_path):
        return env_path

    # Auto-find common paths
    patterns = [
        "/usr/local/Wolfram/Wolfram/*/Executables/WolframKernel",
        "/Applications/Mathematica.app/Contents/MacOS/WolframKernel",
        "C:/Program Files/Wolfram Research/Mathematica/*/WolframKernel.exe",
    ]
    for pattern in patterns:
        matches = glob.glob(pattern)
        if matches:
            return matches[0]

    return "/usr/local/Wolfram/Wolfram/14.3/Executables/WolframKernel"


class MathematicaBackend(ComputeBackend):
    name = "mathematica"
    description = "Wolfram Mathematica - symbolic and numeric computation, visualization"
    capabilities = ["symbolic", "numeric", "plot", "image", "audio"]

    KERNEL_PATH = _find_mathematica_kernel()

    @property
    def is_running(self) -> bool:
        return _session is not None

    @classmethod
    def is_available(cls) -> bool:
        return os.path.exists(cls.KERNEL_PATH)

    def start(self) -> bool:
        global _session
        with _lock:
            if _session is not None:
                return True

            try:
                from wolframclient.evaluation import WolframLanguageSession
                _session = WolframLanguageSession(kernel=self.KERNEL_PATH)
                _session.start()
                return True
            except Exception as e:
                print(f"Failed to start Mathematica: {e}", file=__import__("sys").stderr)
                return False

    def evaluate(self, code: str, timeout: float = 30.0) -> Result:
        if _session is None:
            return Result(success=False, content=[ErrorContent(message="Mathematica not started")])

        try:
            temp_file = tempfile.NamedTemporaryFile(suffix=".png", delete=False)
            temp_path = temp_file.name
            temp_file.close()

            wrapped_code = f'''
            With[{{result = ({code})}},
                Module[{{graphic = result, isImage = False}},
                    graphic = If[Head[result] === Legended, First[List @@ result], result];
                    isImage = MatchQ[Head[graphic], Graphics | Graphics3D | Image];
                    If[isImage,
                        Export["{temp_path}", graphic, "PNG"];
                        <|"type" -> "image", "path" -> "{temp_path}"|>,
                        <|"type" -> "text", "data" -> ToString[result]|>
                    ]
                ]
            ]
            '''
            result = _session.evaluate(wrapped_code)
            return self._process_result(result, temp_path)
        except Exception as e:
            return Result(success=False, content=[ErrorContent(message=str(e))])

    def _process_result(self, result, temp_path: str = "") -> Result:
        if result is None:
            return Result(success=True, content=[TextContent(text="Null")])

        try:
            if hasattr(result, 'get'):
                result_type = result.get('type', 'text')

                if result_type == 'image':
                    if os.path.exists(temp_path):
                        with open(temp_path, "rb") as f:
                            image_data = base64.b64encode(f.read()).decode("utf-8")
                        os.unlink(temp_path)
                        return Result(success=True, content=[ImageContent(data=image_data, mimeType="image/png")])
                    else:
                        return Result(success=False, content=[ErrorContent(message="Image file not created")])
                else:
                    data = result.get('data', '')
                    return Result(success=True, content=[TextContent(text=str(data))])
        except Exception as e:
            if temp_path and os.path.exists(temp_path):
                os.unlink(temp_path)
            return Result(success=False, content=[ErrorContent(message=str(e))])

        return Result(success=True, content=[TextContent(text=str(result))])

    def reset(self) -> None:
        global _session
        if _session:
            try:
                _session.evaluate("ClearAll[\"Global`*\"]")
            except:
                pass

    def stop(self) -> None:
        global _session
        with _lock:
            if _session is None:
                return

            try:
                _session.terminate()
            except:
                pass

            _session = None