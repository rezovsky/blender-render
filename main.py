from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
import subprocess
import os
from modules.files import Files
from modules.render import Render

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
    files = Files("blend_files")
    return await files.find_files()

@app.get("/render/")
async def render_scene():
    render = Render("blend_files/scene.blend", "scene")
    return await render.render_one_frame()
