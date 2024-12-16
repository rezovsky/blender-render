from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
import subprocess
import os

app = FastAPI()

origins = [
    "http://localhost:8765"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

css_directory = os.path.join(os.getcwd(), "web", "dist", "css")
app.mount("/css", StaticFiles(directory=css_directory), name="css")
js_directory = os.path.join(os.getcwd(), "web", "dist", "js")
app.mount("/js", StaticFiles(directory=js_directory), name="js")
static_directory = os.path.join(os.getcwd(), "web", "dist")


@app.get("/", response_class=HTMLResponse)
async def read_root():
    html_file_path = os.path.join(static_directory, "index.html")
    if os.path.exists(html_file_path):
        with open(html_file_path, "r", encoding="utf-8") as file:
            content = file.read()
        return HTMLResponse(content=content)
    return HTMLResponse(content="Index file not found.", status_code=404)

@app.get("/find_files")
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
