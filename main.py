from fastapi import FastAPI
import subprocess
import os

app = FastAPI()

@app.get("/find_files/")
async def find_files():
    folder_path = "blend_files"
    
    files = os.listdir(folder_path)
    
    blend_files = [file for file in files if file.endswith('.blend')]
    
    return {"files": blend_files}

@app.get("/render/")
async def render_scene():
    # Путь к сцене, которая будет рендериться
    scene_path = "/blend_files/panelka.blend"
    output_path = "blend_files/output/render_####.png"
    
    # Команда для рендеринга с использованием Blender
    command = [
        "blender", "-b", scene_path, "-o", output_path, "-F", "PNG", "-f", "1"
    ]
    
    # Запускаем процесс рендеринга
    result = subprocess.run(command, capture_output=True, text=True)
    
    if result.returncode == 0:
        return {"message": "Render started successfully", "output": result.stdout}
    else:
        return {"message": "Render failed", "error": result.stderr}
