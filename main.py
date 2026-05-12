from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, RedirectResponse
from pydantic import BaseModel
import os
import re
import json
import boto3
from botocore.config import Config
from dotenv import load_dotenv

load_dotenv()

app = FastAPI(title="Manga Reader API")

B2_KEY_ID = os.environ.get("B2_KEY_ID")
B2_APPLICATION_KEY = os.environ.get("B2_APPLICATION_KEY")
B2_ENDPOINT = os.environ.get("B2_ENDPOINT")
B2_BUCKET_NAME = os.environ.get("B2_BUCKET_NAME")

# Инициализация клиента для Backblaze B2 через S3 API
s3 = boto3.client(
    's3',
    endpoint_url=B2_ENDPOINT,
    aws_access_key_id=B2_KEY_ID,
    aws_secret_access_key=B2_APPLICATION_KEY,
    config=Config(signature_version='s3v4')
)

PROGRESS_FILE_KEY = "read_progress.json"

class ProgressData(BaseModel):
    volume: str
    page: int

class UploadRequest(BaseModel):
    filename: str

@app.post("/api/upload-url")
async def get_upload_url(data: UploadRequest):
    try:
        # Генерируем временную ссылку (на 1 час) для ЗАГРУЗКИ файла напрямую в B2
        url = s3.generate_presigned_url(
            ClientMethod='put_object',
            Params={
                'Bucket': B2_BUCKET_NAME,
                'Key': data.filename,
                'ContentType': 'application/pdf'
            },
            ExpiresIn=3600
        )
        return {"url": url}
    except Exception as e:
        return {"error": str(e)}

@app.get("/api/progress")
async def get_progress():
    try:
        response = s3.get_object(Bucket=B2_BUCKET_NAME, Key=PROGRESS_FILE_KEY)
        content = response['Body'].read().decode('utf-8')
        return json.loads(content)
    except Exception:
        # Если файла в облаке еще нет (первый запуск)
        return {"volume": None, "page": 1}

@app.post("/api/progress")
async def save_progress(data: ProgressData):
    try:
        progress_data = json.dumps({"volume": data.volume, "page": data.page})
        s3.put_object(Bucket=B2_BUCKET_NAME, Key=PROGRESS_FILE_KEY, Body=progress_data)
        return {"status": "ok"}
    except Exception as e:
        return {"error": str(e)}

# Отдаем статические файлы (HTML, CSS, JS) из папки static
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/")
async def root():
    return FileResponse("static/index.html")

@app.get("/sw.js")
async def service_worker():
    return FileResponse("static/sw.js", media_type="application/javascript")

@app.get("/api/manga")
async def get_manga_list():
    try:
        # Получаем список файлов прямо из облака
        response = s3.list_objects_v2(Bucket=B2_BUCKET_NAME)
        files = [item['Key'] for item in response.get('Contents', []) if item['Key'].endswith('.pdf')]
        
        # Естественная сортировка (чтобы 2 шло перед 100)
        def alphanum_key(s):
            return [int(text) if text.isdigit() else text.lower() for text in re.split(r'(\d+)', s)]
            
        files.sort(key=alphanum_key)
        return {"files": files}
    except Exception as e:
        return {"error": str(e)}

@app.get("/api/manga/{filename}")
async def get_manga_file(filename: str):
    try:
        # Генерируем временную (на 2 часа) прямую ссылку на файл
        url = s3.generate_presigned_url(
            ClientMethod='get_object',
            Params={
                'Bucket': B2_BUCKET_NAME,
                'Key': filename
            },
            ExpiresIn=7200
        )
        # Отдаем ссылку в формате JSON
        return {"url": url}
    except Exception as e:
        return {"error": str(e)}
