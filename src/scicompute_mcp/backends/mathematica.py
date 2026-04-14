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
            Module[{{evalData, graphic, isImage}},
                evalData = EvaluationData[{code}];
                
                (* Handle graphics *)
                graphic = evalData["Result"];
                If[Head[graphic] === Legended,
                    graphic = First[List @@ graphic];
                ];
                isImage = MatchQ[Head[graphic], Graphics | Graphics3D | Image | GraphicsComplex];
                
                If[isImage,
                    Export["{temp_path}", graphic, "PNG"];
                    {{{{"type", "image"}}}},
                    {{{{"type", "text"}}, 
                      {{"outputLog", evalData["OutputLog"]}},
                      {{"messages", evalData["MessagesText"]}},
                      {{"data", ToString[OutputForm[evalData["Result"]]]}}
                    }}
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
            # V3: Parse nested tuple/list format: {{"key", value}, ...} or (("key", value), ...)
            result_dict = {}
            
            if isinstance(result, (list, tuple)):
                for item in result:
                    if isinstance(item, (list, tuple)) and len(item) >= 2:
                        result_dict[item[0]] = item[1]
            
            if result_dict:
                result_type = result_dict.get('type', 'text')

                if result_type == 'image':
                    if temp_path and os.path.exists(temp_path):
                        with open(temp_path, "rb") as f:
                            image_data = base64.b64encode(f.read()).decode("utf-8")
                        os.unlink(temp_path)
                        return Result(success=True, content=[ImageContent(data=image_data, mimeType="image/png")])
                    else:
                        return Result(success=False, content=[ErrorContent(message="Image file not created")])
                else:
                    output_log = result_dict.get('outputLog', [])
                    messages = result_dict.get('messages', [])
                    data = result_dict.get('data', '')
                    
                    parts = []
                    
                    # Handle outputLog - may be tuple, list or empty
                    if output_log:
                        if isinstance(output_log, (list, tuple)):
                            log_text = '\n'.join(str(x) for x in output_log if x)
                            if log_text.strip():
                                parts.append(log_text)
                        elif str(output_log).strip():
                            parts.append(str(output_log))
                    
                    # Handle messages
                    if messages:
                        if isinstance(messages, (list, tuple)):
                            msg_text = '\n'.join(str(x) for x in messages if x)
                            if msg_text.strip():
                                parts.append(msg_text)
                        elif str(messages).strip():
                            parts.append(str(messages))
                    
                    # Handle data
                    if data and str(data).strip() and str(data) != 'Null':
                        parts.append(str(data))
                    
                    combined = '\n'.join(parts)
                    if combined.strip() == '':
                        combined = '(no output)'
                    return Result(success=True, content=[TextContent(text=combined.strip())])
                    
            elif hasattr(result, 'get'):
                # Fallback for dict-like objects
                result_type = result.get('type', 'text')
                if result_type == 'image':
                    if temp_path and os.path.exists(temp_path):
                        with open(temp_path, "rb") as f:
                            image_data = base64.b64encode(f.read()).decode("utf-8")
                        os.unlink(temp_path)
                        return Result(success=True, content=[ImageContent(data=image_data, mimeType="image/png")])
                
        except Exception as e:
            if temp_path and os.path.exists(temp_path):
                os.unlink(temp_path)
            return Result(success=False, content=[ErrorContent(message=str(e))])

        return Result(success=True, content=[TextContent(text=str(result))])

    def reset(self) -> None:
        global _session
        if _session:
            try:
                _session.evaluate('''
                    ClearAll["Global`*"];
                    Remove["Global`*"];
                    $ContextPath = DeleteCases[$ContextPath, "Global`"];
                    $Context = "Global`";
                    $ContextPath = Prepend[$ContextPath, "Global`"];
                ''')
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