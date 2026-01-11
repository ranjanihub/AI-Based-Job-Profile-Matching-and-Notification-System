from fastapi import APIRouter, Depends, HTTPException
from app.core.security import verify_token
from app.models.schemas import MatchCreate, MatchResponse
from supabase import create_client
from app.core.config import settings
from app.services.vectorize import vectorizer
from app.services.match_score import compute_weighted_score
from app.api.routers.notifications import send_email
from app.core.logging import logger
from typing import List

router = APIRouter()
supabase = create_client(settings.supabase_url, settings.supabase_service_role_key)


@router.post("/matches", response_model=List[MatchResponse])
def compute_matches(
    match: MatchCreate,
    user_id: str = Depends(verify_token)
):
    # Get resume
    resume_response = supabase.table("resumes").select("*").eq("id", str(match.resume_id)).eq("user_id", user_id).execute()
    if not resume_response.data:
        raise HTTPException(status_code=404, detail="Resume not found")
    resume = resume_response.data[0]

    # Get all jobs
    jobs_response = supabase.table("jobs").select("*").execute()
    jobs = jobs_response.data

    # Fit vectorizer on job descriptions if not fitted
    if not hasattr(vectorizer.vectorizer, 'vocabulary_'):
        job_texts = [job['description'] for job in jobs]
        vectorizer.fit(job_texts)

    matches = []
    for job in jobs:
        scores = compute_weighted_score(
            resume['text_content'],
            job['description'],
            job['skills'],
            job.get('experience_years'),
            job.get('education_level'),
            # Assume resume has these fields, or extract from text (simplified)
            resume_experience_years=5,  # Placeholder
            resume_education_level='bachelor'  # Placeholder
        )
        logger.info(f"Match score for user {user_id} job {job['id']}: {scores['overall']}")
        if scores['overall'] >= 70:  # Threshold
            match_data = {
                "user_id": user_id,
                "resume_id": str(match.resume_id),
                "job_id": str(job['id']),
                "score": scores['overall'],
                "top_terms": []  # Placeholder
            }
            supabase.table("matches").insert(match_data).execute()
            # Create notification
            notification_data = {
                "user_id": user_id,
                "match_id": None,  # Would need to get the inserted match ID
                "type": "in_app",
                "sent_at": None,
                "status": "pending"
            }
            supabase.table("notifications").insert(notification_data).execute()
            # Send email
            user_email = "user@example.com"  # In real app, get from auth
            send_email(user_email, "New Job Match!", f"You have a {scores['overall']}% match for {job['title']}")
            matches.append({
                "id": None,
                "job": job,
                "score": scores['overall'],
                "top_terms": [],
                "created_at": None
            })

    return matches