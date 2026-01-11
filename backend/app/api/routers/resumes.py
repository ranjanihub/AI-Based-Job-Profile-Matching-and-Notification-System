from fastapi import APIRouter, Depends, UploadFile, File, HTTPException, Request
from slowapi import Limiter
from slowapi.util import get_remote_address
from app.core.security import verify_token
from app.models.schemas import ResumeResponse
from supabase import create_client
from app.core.config import settings
import PyPDF2
import io
from app.services.preprocess import preprocess_text

router = APIRouter()
supabase = create_client(settings.supabase_url, settings.supabase_service_role_key)

limiter = Limiter(key_func=get_remote_address)


def extract_text_from_pdf(file: bytes) -> str:
    pdf_reader = PyPDF2.PdfReader(io.BytesIO(file))
    text = ""
    for page in pdf_reader.pages:
        text += page.extract_text()
    return text


@router.post("/resumes", response_model=ResumeResponse)
@limiter.limit("5/minute")
def upload_resume(
    request: Request,
    file: UploadFile = File(...),
    user_id: str = Depends(verify_token)
):
    if file.content_type != "application/pdf":
        raise HTTPException(status_code=400, detail="Only PDF files are allowed")
    if file.size > 10 * 1024 * 1024:  # 10MB
        raise HTTPException(status_code=400, detail="File too large")
    # ... rest of the code
    file_content = file.file.read()
    file_path = f"resumes/{user_id}/{file.filename}"
    supabase.storage.from_("resumes").upload(file_path, file_content)

    # Extract and preprocess text
    raw_text = extract_text_from_pdf(file_content)
    text_content = preprocess_text(raw_text)

    # Save to DB
    data = {
        "user_id": user_id,
        "filename": file.filename,
        "text_content": text_content
    }
    response = supabase.table("resumes").insert(data).execute()
    return response.data[0]