import os
import aiofiles
from fastapi import APIRouter, HTTPException, UploadFile, File, Depends
from fastapi.responses import FileResponse
from app.services.auth import get_current_admin

router = APIRouter(prefix="/api/pdf", tags=["pdf"])

UPLOAD_DIR = "/uploads"


@router.get("")
async def list_pdfs():
    files = []
    if os.path.isdir(UPLOAD_DIR):
        files = [f for f in os.listdir(UPLOAD_DIR) if f.endswith(".pdf")]
    return [{"name": f, "url": f"/api/pdf/{f}"} for f in sorted(files)]


@router.get("/{filename}")
async def download_pdf(filename: str):
    if not filename.endswith(".pdf") or "/" in filename or ".." in filename:
        raise HTTPException(status_code=400, detail="Invalid filename")
    path = os.path.join(UPLOAD_DIR, filename)
    if not os.path.exists(path):
        raise HTTPException(status_code=404, detail="File not found")
    return FileResponse(path, media_type="application/pdf", filename=filename)


@router.post("", status_code=201)
async def upload_pdf(file: UploadFile = File(...), _: str = Depends(get_current_admin)):
    if not file.filename.endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files allowed")
    safe_name = os.path.basename(file.filename)
    os.makedirs(UPLOAD_DIR, exist_ok=True)
    path = os.path.join(UPLOAD_DIR, safe_name)
    async with aiofiles.open(path, "wb") as f:
        content = await file.read()
        await f.write(content)
    return {"name": safe_name, "url": f"/api/pdf/{safe_name}"}


@router.delete("/{filename}", status_code=204)
async def delete_pdf(filename: str, _: str = Depends(get_current_admin)):
    if not filename.endswith(".pdf") or "/" in filename or ".." in filename:
        raise HTTPException(status_code=400, detail="Invalid filename")
    path = os.path.join(UPLOAD_DIR, filename)
    if not os.path.exists(path):
        raise HTTPException(status_code=404, detail="File not found")
    os.remove(path)
