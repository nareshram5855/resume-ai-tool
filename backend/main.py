import uuid
import os
import glob as glob_mod
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse

from models import AnalyzeRequest, AnalyzeResponse, UploadResponse
from services.docx_parser import parse_resume
from services.jd_parser import parse_jd_text, parse_jd_url
from services.analyzer import analyze_resume_vs_jd
from services.summarizer import generate_summaries
from services.updater import update_resume

app = FastAPI(title="Resume Update App")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3001", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

UPLOAD_DIR = os.path.join(os.path.dirname(__file__), "uploads")
os.makedirs(UPLOAD_DIR, exist_ok=True)

# In-memory store for file metadata (use DB in production)
file_store: dict[str, dict] = {}


@app.get("/api/files")
async def list_files():
    """List all uploaded resumes."""
    files = []
    for file_id, data in file_store.items():
        files.append({
            "file_id": file_id,
            "filename": data["filename"],
        })
    return {"files": files}


@app.post("/api/upload", response_model=UploadResponse)
async def upload_resume(file: UploadFile = File(...)):
    if not file.filename.endswith(".docx"):
        raise HTTPException(status_code=400, detail="Only .docx files are supported")

    file_id = str(uuid.uuid4())
    # Save with original filename (prefix with ID to avoid collisions)
    safe_name = file.filename.replace("/", "_").replace("\\", "_")
    file_path = os.path.join(UPLOAD_DIR, f"{file_id}_{safe_name}")

    content = await file.read()
    with open(file_path, "wb") as f:
        f.write(content)

    resume_data = parse_resume(file_path)
    file_store[file_id] = {
        "original_path": file_path,
        "filename": file.filename,
        "resume_data": resume_data,
    }

    return UploadResponse(file_id=file_id, resume_data=resume_data, filename=file.filename)


@app.delete("/api/files/{file_id}")
async def delete_file(file_id: str):
    """Delete an uploaded resume and its updated version."""
    if file_id not in file_store:
        raise HTTPException(status_code=404, detail="File not found")

    stored = file_store[file_id]

    # Delete original file
    if os.path.exists(stored["original_path"]):
        os.remove(stored["original_path"])

    # Delete updated file if exists
    updated = stored.get("updated_path")
    if updated and os.path.exists(updated):
        os.remove(updated)

    del file_store[file_id]
    return {"message": "File deleted successfully"}


@app.post("/api/analyze", response_model=AnalyzeResponse)
async def analyze(request: AnalyzeRequest):
    if request.file_id not in file_store:
        raise HTTPException(status_code=404, detail="File not found. Please upload again.")

    if not request.jd_text and not request.jd_url:
        raise HTTPException(status_code=400, detail="Provide either jd_text or jd_url")

    # Get JD text
    if request.jd_url:
        jd_text = parse_jd_url(request.jd_url)
    else:
        jd_text = parse_jd_text(request.jd_text)

    stored = file_store[request.file_id]
    resume_data = stored["resume_data"]

    # Analyze gaps
    analysis = await analyze_resume_vs_jd(resume_data, jd_text)

    # Update the DOCX with gap points
    updated_path = update_resume(stored["original_path"], analysis)
    stored["updated_path"] = updated_path

    # Re-parse updated resume for summary generation
    updated_resume_data = parse_resume(updated_path)

    # Generate summaries from updated resume
    summaries = await generate_summaries(updated_resume_data, jd_text)

    return AnalyzeResponse(
        file_id=request.file_id,
        analysis=analysis,
        summaries=summaries,
    )


@app.get("/api/download/{file_id}")
async def download_resume(file_id: str):
    if file_id not in file_store:
        raise HTTPException(status_code=404, detail="File not found")

    stored = file_store[file_id]
    path = stored.get("updated_path", stored["original_path"])

    if not os.path.exists(path):
        raise HTTPException(status_code=404, detail="File not found on disk")

    return FileResponse(
        path,
        media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        filename=f"updated_{stored['filename']}",
    )
