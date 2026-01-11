from fastapi import APIRouter, Depends
from app.core.security import verify_token
from app.models.schemas import JobCreate, JobResponse
from supabase import create_client
from app.core.config import settings
from typing import List

router = APIRouter()
supabase = create_client(settings.supabase_url, settings.supabase_service_role_key)


@router.get("/jobs", response_model=List[JobResponse])
def get_jobs():
    response = supabase.table("jobs").select("*").execute()
    return response.data


@router.post("/jobs", response_model=JobResponse)
def create_job(
    job: JobCreate,
    user_id: str = Depends(verify_token)
):
    data = job.dict()
    response = supabase.table("jobs").insert(data).execute()
    return response.data[0]