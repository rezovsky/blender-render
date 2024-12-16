import subprocess
from models.base import File

class Render():
    def __init__(self, file: File, output_file: str):
        self.file = file
        self.output_path = output_path
        self.resolution_preview_x = 320
        self.resolution_preview_y = 240
        self.samples = 16
        
    
    async def render_one_frame(self):
        command = [
            "blender", 
            "-b", self.file.path, 
            "-o", f"output/{self.file.output_name}.png", 
            "-F", "PNG", 
            "-f", "1"
            ]
        
        result = subprocess.run(command, capture_output=True, text=True)
        
        if result.returncode == 0:
            return {"message": "Render started successfully", "output": result.stdout}
        else:
            return {"message": "Render failed", "error": result.stderr}
    
    async def render_all_frames(self):
            command = [
                "blender", 
                "-b", self.file.path, 
                "-o", f"output/animation_{self.file.output_name}/{self.file.output_name}_#####.png",
                "-F", "PNG", 
                "-a" 
            ]
            
            result = subprocess.run(command, capture_output=True, text=True)
            
            if result.returncode == 0:
                return {"message": "Render started successfully", "output": result.stdout}
            else:
                return {"message": "Render failed", "error": result.stderr}
    
    
    async def render_preview(self):
        python_expr = (
            f"import bpy; "
            f"bpy.context.scene.render.resolution_x={self.resolution_x}; "
            f"bpy.context.scene.render.resolution_y={self.resolution_y}; "
            f"bpy.context.scene.cycles.samples={self.samples}"
        )
        
        command = [
            "blender", 
            "-b", self.file.path, 
            "-o", f"preview/{self.file.output_name}.png", 
            "-F", "PNG", 
            "-x", "1", 
            "-f", "1",
            "--python-expr", python_expr
        ]

        result = subprocess.run(command, capture_output=True, text=True)

        if result.returncode == 0:
            return {"message": "Render completed successfully", "output": result.stdout}
        else:
            return {"message": "Render failed", "error": result.stderr}