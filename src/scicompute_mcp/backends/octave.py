import base64
import os
import subprocess
import tempfile
import shutil
from typing import Optional

from .base import ComputeBackend, Result, TextContent, ImageContent, ErrorContent


class OctaveBackend(ComputeBackend):
    name = "octave"
    description = "GNU Octave - MATLAB-compatible numerical computation"
    capabilities = ["numeric", "plot"]
    
    def __init__(self):
        self._started = False
        self._octave_path: Optional[str] = None
    
    def is_available(self) -> bool:
        self._octave_path = shutil.which("octave")
        return self._octave_path is not None
    
    def start(self) -> bool:
        if self._started:
            return True
        
        if not self.is_available():
            return False
        
        self._started = True
        return True
    
    def evaluate(self, code: str, timeout: float = 30.0) -> Result:
        if not self._started:
            if not self.start():
                return Result(success=False, content=[ErrorContent(message="Octave not available")])
        
        temp_dir = tempfile.mkdtemp()
        plot_file = os.path.join(temp_dir, "plot.png")
        
        wrapped_code = f'''
graphics_toolkit('gnuplot');
set(0, 'DefaultFigureVisible', 'off');
set(0, 'DefaultFigurePaperPositionMode', 'auto');
set(0, 'DefaultFigurePaperSize', [8, 6]);

has_plot = false;
original_plot = @plot;
original_plot3 = @plot3;
original_surf = @surf;
original_mesh = @mesh;
original_contour = @contour;
original_imagesc = @imagesc;
original_histogram = @histogram;
original_bar = @bar;

function plot_wrap(varargin)
    global has_plot;
    has_plot = true;
    plot_result = original_plot(varargin{{:}});
    print("{plot_file}", "-dpng", "-r150");
endfunction

function plot3_wrap(varargin)
    global has_plot;
    has_plot = true;
    plot3_result = original_plot3(varargin{{:}});
    print("{plot_file}", "-dpng", "-r150");
endfunction

function surf_wrap(varargin)
    global has_plot;
    has_plot = true;
    surf_result = original_surf(varargin{{:}});
    print("{plot_file}", "-dpng", "-r150");
endfunction

function mesh_wrap(varargin)
    global has_plot;
    has_plot = true;
    mesh_result = original_mesh(varargin{{:}});
    print("{plot_file}", "-dpng", "-r150");
endfunction

function contour_wrap(varargin)
    global has_plot;
    has_plot = true;
    contour_result = original_contour(varargin{{:}});
    print("{plot_file}", "-dpng", "-r150");
endfunction

function imagesc_wrap(varargin)
    global has_plot;
    has_plot = true;
    imagesc_result = original_imagesc(varargin{{:}});
    print("{plot_file}", "-dpng", "-r150");
endfunction

function histogram_wrap(varargin)
    global has_plot;
    has_plot = true;
    histogram_result = original_histogram(varargin{{:}});
    print("{plot_file}", "-dpng", "-r150");
endfunction

function bar_wrap(varargin)
    global has_plot;
    has_plot = true;
    bar_result = original_bar(varargin{{:}});
    print("{plot_file}", "-dpng", "-r150");
endfunction

function handle_graphics = figure_wrap(varargin)
    global has_plot;
    handle_graphics = figure(varargin{{:}});
endfunction

plot = @plot_wrap;
plot3 = @plot3_wrap;
surf = @surf_wrap;
mesh = @mesh_wrap;
contour = @contour_wrap;
imagesc = @imagesc_wrap;
histogram = @histogram_wrap;
bar = @bar_wrap;
figure = @figure_wrap;

try
    result = {code};
    disp(result);
    if has_plot
        disp("__PLOT_GENERATED__");
    endif
catch err
    disp(err.message);
end_try_catch
'''
        
        try:
            octave_path = self._octave_path
            if octave_path is None:
                return Result(success=False, content=[ErrorContent(message="Octave path not found")])
            
            result = subprocess.run(
                [octave_path, "--quiet", "--no-gui", "--eval", wrapped_code],
                capture_output=True,
                text=True,
                timeout=timeout,
                cwd=temp_dir
            )
            
            output = result.stdout.strip()
            errors = result.stderr.strip()
            
            if "__PLOT_GENERATED__" in output and os.path.exists(plot_file):
                with open(plot_file, "rb") as f:
                    image_data = base64.b64encode(f.read()).decode("utf-8")
                
                output = output.replace("__PLOT_GENERATED__", "").strip()
                
                shutil.rmtree(temp_dir, ignore_errors=True)
                
                content = []
                if output:
                    content.append(TextContent(text=output))
                content.append(ImageContent(data=image_data, mimeType="image/png"))
                return Result(success=True, content=content)
            
            shutil.rmtree(temp_dir, ignore_errors=True)
            
            if result.returncode != 0 and errors:
                return Result(success=False, content=[ErrorContent(message=errors)])
            
            return Result(success=True, content=[TextContent(text=output if output else "(no output)")])
            
        except subprocess.TimeoutExpired:
            shutil.rmtree(temp_dir, ignore_errors=True)
            return Result(success=False, content=[ErrorContent(message=f"Execution timeout ({timeout}s)")])
        except Exception as e:
            shutil.rmtree(temp_dir, ignore_errors=True)
            return Result(success=False, content=[ErrorContent(message=str(e))])
    
    def reset(self) -> None:
        pass
    
    def stop(self) -> None:
        self._started = False