import subprocess

class Render():
    def __init__(self, file: str, output_file: str):
        self.file_name = file_name
        self.output_path = output_path
        
    
    async def render_one_frame(self):
        command = ["blender", "-b", self.file_name, "-o", f"output/{self.output_file}.png", "-F", "PNG", "-f", "1"]
        result = subprocess.run(command, capture_output=True, text=True)
        
        if result.returncode == 0:
            return {"message": "Render started successfully", "output": result.stdout}
        else:
            return {"message": "Render failed", "error": result.stderr}