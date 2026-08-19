import os
import logging
from datetime import datetime, timezone
from fastapi import APIRouter, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse

from core.config import settings
from services.document_service import get_document_service

router = APIRouter()
logger = logging.getLogger(__name__)

MAX_FILE_SIZE = settings.max_file_size


@router.post("/upload")
async def upload_paper(file: UploadFile = File(...)):
    if not file.filename.lower().endswith('.pdf'):
        raise HTTPException(status_code=400, detail="Only PDF files are supported")

    content = await file.read()
    if len(content) > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=413,
            detail=f"File too large. Maximum size is {MAX_FILE_SIZE // (1024*1024)}MB"
        )

    os.makedirs(settings.upload_dir, exist_ok=True)
    import uuid
    file_id = str(uuid.uuid4())
    file_path = os.path.join(settings.upload_dir, f"{file_id}.pdf")

    try:
        with open(file_path, "wb") as f:
            f.write(content)

        doc_service = get_document_service()
        result = await doc_service.process_upload(file_path, file.filename)

        result["file_id"] = file_id

        return JSONResponse(content=result)

    except ValueError as e:
        if os.path.exists(file_path):
            os.remove(file_path)
        raise HTTPException(status_code=422, detail=str(e))
    except Exception as e:
        logger.error(f"Upload processing failed: {e}")
        if os.path.exists(file_path):
            os.remove(file_path)
        raise HTTPException(status_code=500, detail="Error processing PDF")


@router.get("/upload/{file_id}")
async def get_upload_status(file_id: str):
    file_path = os.path.join(settings.upload_dir, f"{file_id}.pdf")
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="File not found")
    return {"file_id": file_id, "status": "processed"}
