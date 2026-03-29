import base64
import glob
import os
import shutil
import sys
import tempfile
import threading
from typing import Optional

from .base import ComputeBackend, Result, TextContent, ImageContent, ErrorContent

# Global singleton
_session: Optional[object] = None
_lock = threading.Lock()


def _find_matlab_path() -> Optional[str]:
    """Find MATLAB executable path"""
    # Environment variable takes priority
    env_path = os.environ.get("MATLAB_PATH")
    if env_path and os.path.exists(env_path):
        return env_path

    # Check if matlab command is in PATH
    matlab_cmd = shutil.which("matlab")
    if matlab_cmd:
        return matlab_cmd

    # Auto-find common installation paths
    patterns = [
        "/usr/local/MATLAB/R*/bin/matlab",
        "/Applications/MATLAB_R*.app/bin/matlab",
        "C:/Program Files/MATLAB/R*/bin/matlab.exe",
        "C:/Program Files (x86)/MATLAB/R*/bin/matlab.exe",
    ]
    for pattern in patterns:
        matches = glob.glob(pattern)
        if matches:
            return matches[0]

    return None


def _check_python_version() -> bool:
    """MATLAB Engine requires Python 3.9, 3.10, or 3.11"""
    version = sys.version_info
    return version.major == 3 and version.minor in (9, 10, 11)


class MatlabBackend(ComputeBackend):
    name = "matlab"
    description = "MATLAB - Numerical computing, visualization, and programming"
    capabilities = ["numeric", "plot", "image"]

    MATLAB_PATH = _find_matlab_path()

    @property
    def is_running(self) -> bool:
        return _session is not None

    @classmethod
    def is_available(cls) -> bool:
        """Check if MATLAB is available."""
        # Check Python version first
        if not _check_python_version():
            return False
        try:
            import matlab.engine
            return True
        except ImportError:
            return False

    def start(self) -> bool:
        global _session
        with _lock:
            if _session is not None:
                return True

            # Check Python version
            if not _check_python_version():
                version = ".".join(map(str, sys.version_info[:2]))
                print(f"MATLAB Engine requires Python 3.9, 3.10, or 3.11, but current version is {version}",
                      file=__import__("sys").stderr)
                return False

            try:
                import matlab.engine
                # Start MATLAB engine without GUI
                _session = matlab.engine.start_matlab()
                # Set default figure visibility to off
                _session.set(0, 'DefaultFigureVisible', 'off', nargout=0)
                return True
            except Exception as e:
                print(f"Failed to start MATLAB: {e}", file=__import__("sys").stderr)
                return False

    def evaluate(self, code: str, timeout: float = 30.0) -> Result:
        if _session is None:
            return Result(success=False, content=[ErrorContent(message="MATLAB not started")])

        temp_path = ""
        temp_file = None
        try:
            # Create temp file for potential plot output
            temp_file = tempfile.NamedTemporaryFile(suffix=".png", delete=False)
            temp_path = temp_file.name
            temp_file.close()

            # Wrap code to handle graphics - use a script approach
            wrapper_script = f"""
set(0, 'DefaultFigureVisible', 'off');
close all;

plot_generated = false;
result_str = '';

try
    {code}
    % Check if any figures were created
    figs = get(0, 'Children');
    if ~isempty(figs)
        fig = figs(1);
        print(fig, '{temp_path}', '-dpng', '-r150');
        close all;
        plot_generated = true;
    end
catch ME
    result_str = ME.message;
end

% Return result structure
result = struct('plot_generated', plot_generated, 'message', result_str);
"""
            # Execute code - result is a struct with fields
            try:
                result_struct = _session.eval(wrapper_script, nargout=1)
                plot_generated = result_struct['plot_generated']
                message = result_struct.get('message', '')
            except:
                # Fallback if struct doesn't work as expected
                _session.eval(wrapper_script, nargout=0)
                plot_generated = True  # Assume plot was generated
                message = ''

            # Check if plot was generated and file exists
            if os.path.exists(temp_path) and os.path.getsize(temp_path) > 100:
                with open(temp_path, "rb") as f:
                    image_data = base64.b64encode(f.read()).decode("utf-8")
                os.unlink(temp_path)
                return Result(success=True, content=[ImageContent(data=image_data, mimeType="image/png")])

            # No plot
            if message:
                return Result(success=False, content=[ErrorContent(message=message)])

            return Result(success=True, content=[TextContent(text="(no output)")])

        except Exception as e:
            if temp_file and os.path.exists(temp_path):
                os.unlink(temp_path)
            return Result(success=False, content=[ErrorContent(message=str(e))])

    def reset(self) -> None:
        global _session
        if _session:
            try:
                _session.eval("clear all; close all;", nargout=0)
            except:
                pass

    def stop(self) -> None:
        global _session
        with _lock:
            if _session is None:
                return

            try:
                _session.quit()
            except:
                pass

            _session = None
