from fastapi import APIRouter, Depends
from app.core.security import verify_token
from supabase import create_client
from app.core.config import settings
from typing import List

router = APIRouter()
supabase = create_client(settings.supabase_url, settings.supabase_service_role_key)


@router.get("/notifications", response_model=List[dict])
def get_notifications(user_id: str = Depends(verify_token)):
    response = supabase.table("notifications").select("*").eq("user_id", user_id).order("created_at", desc=True).execute()
    return response.data


# Mock email send function
def send_email(to: str, subject: str, body: str):
    # In production, integrate with Resend or SendGrid
    print(f"Sending email to {to}: {subject} - {body}")
    return True