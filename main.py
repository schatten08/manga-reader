from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
import os
import re
import json

app = FastAPI(title="Manga Reader API")

PROGRESS_FILE = "read_progress.json"

class ProgressData(BaseModel):
    volume: str
    page: int

@app.get("/api/progress")
async def get_progress():
    if os.path.exists(PROGRESS_FILE):
        try:
            with open(PROGRESS_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except:
            pass
    return {"volume": None, "page": 1}

@app.post("/api/progress")
async def save_progress(data: ProgressData):
    try:
        with open(PROGRESS_FILE, "w", encoding="utf-8") as f:
            json.dump({"volume": data.volume, "page": data.page}, f)
        return {"status": "ok"}
    except Exception as e:
        return {"error": str(e)}

# Путь к вашей папке с мангой
MANGA_FOLDER = r"C:\Users\andrei_trokol\OneDrive - EPAM\OnePiece"

# Отдаем статические файлы (HTML, CSS, JS) из папки static
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/")
async def root():
    # При заходе на главную страницу отдаем наш index.html
    return FileResponse("static/index.html")

@app.get("/api/manga")
async def get_manga_list():
    # Отдаем список PDF файлов
    if not os.path.exists(MANGA_FOLDER):
        return {"error": "Папка не найдена"}
    files = [f for f in os.listdir(MANGA_FOLDER) if f.endswith(".pdf")]
    
    # Естественная сортировка (чтобы 2 шло перед 100)
    def alphanum_key(s):
        return [int(text) if text.isdigit() else text.lower() for text in re.split(r'(\d+)', s)]
        
    files.sort(key=alphanum_key)
    return {"files": files}

@app.get("/api/manga/{filename}")
async def get_manga_file(filename: str):
    # Отдаем сам PDF файл браузеру!
    file_path = os.path.join(MANGA_FOLDER, filename)
    if os.path.exists(file_path):
        return FileResponse(file_path, media_type="application/pdf")
    return {"error": "Файл не найден"}
