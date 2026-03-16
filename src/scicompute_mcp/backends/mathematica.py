import base64
import os
import tempfile
from typing import Optional

from .base import ComputeBackend, Result, TextContent, ImageContent, ErrorContent


class MathematicaBackend(ComputeBackend):
    name = "mathematica"
    description = "Wolfram Mathematica - symbolic and numeric computation, visualization"
    capabilities = ["symbolic", "numeric", "plot", "image", "audio"]
    
    KERNEL_PATH = "/usr/local/Wolfram/Wolfram/14.3/Executables/WolframKernel"
    
    def __init__(self):
        self._session = None
        self._started = False
    
    def is_available(self) -> bool:
        return os.path.exists(self.KERNEL_PATH)
    
    def start(self) -> bool:
        if self._started:
            return True
        
        try:
            from wolframclient.evaluation import WolframLanguageSession
            self._session = WolframLanguageSession(kernel=self.KERNEL_PATH)
            self._session.start()
            self._started = True
            return True
        except Exception as e:
            print(f"Failed to start Mathematica: {e}", file=__import__("sys").stderr)
            return False
    
    def evaluate(self, code: str, timeout: float = 30.0) -> Result:
        if not self._started or self._session is None:
            if not self.start():
                return Result(success=False, content=[ErrorContent(message="Mathematica kernel not started")])
        
        session = self._session
        if session is None:
            return Result(success=False, content=[ErrorContent(message="Mathematica kernel not started")])
        
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
            result = session.evaluate(wrapped_code)
            return self._process_result(result, temp_path)
        except Exception as e:
            return Result(success=False, content=[ErrorContent(message=str(e))])
    
    def reset(self) -> None:
        if self._session:
            try:
                self._session.evaluate("ClearAll[\"Global`*\"]")
            except:
                pass
    
    def stop(self) -> None:
        if self._session:
            try:
                self._session.terminate()
            except:
                pass
        self._session = None
        self._started = False
    
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