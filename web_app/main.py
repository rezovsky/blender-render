from fastapi import FastAPI
import subprocess
import os

app = FastAPI()

@app.get("/render/")
async def render_scene():
    # Путь к сцене, которая будет рендериться
    scene_path = "/workspace/panelka.blend"
    output_path = "/workspace/output/render_####.png"
    
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
