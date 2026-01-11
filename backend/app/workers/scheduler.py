from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger
import asyncio
from app.services.vectorize import vectorizer
from app.services.match_score import compute_weighted_score
from app.api.routers.notifications import send_email
from supabase import create_client
from app.core.config import settings

supabase = create_client(settings.supabase_url, settings.supabase_service_role_key)

scheduler = AsyncIOScheduler()

async def periodic_match_rescore():
    # Get all resumes and jobs
    resumes = supabase.table("resumes").select("*").execute().data
    jobs = supabase.table("jobs").select("*").execute().data

    if not jobs:
        return

    # Fit vectorizer
    job_texts = [job['description'] for job in jobs]
    vectorizer.fit(job_texts)

    for resume in resumes:
        for job in jobs:
            scores = compute_weighted_score(
                resume['text_content'],
                job['description'],
                job['skills'],
                job.get('experience_years'),
                job.get('education_level'),
                5,  # Placeholder
                'bachelor'
            )
            if scores['overall'] >= 70:
                # Check if match already exists
                existing = supabase.table("matches").select("*").eq("user_id", resume['user_id']).eq("resume_id", resume['id']).eq("job_id", job['id']).execute()
                if not existing.data:
                    match_data = {
                        "user_id": resume['user_id'],
                        "resume_id": resume['id'],
                        "job_id": job['id'],
                        "score": scores['overall'],
                        "top_terms": []
                    }
                    supabase.table("matches").insert(match_data).execute()
                    # Notification
                    notification_data = {
                        "user_id": resume['user_id'],
                        "match_id": None,
                        "type": "in_app",
                        "sent_at": None,
                        "status": "pending"
                    }
                    supabase.table("notifications").insert(notification_data).execute()
                    # Email
                    send_email("user@example.com", "New Job Match!", f"You have a {scores['overall']}% match for {job['title']}")

def start_scheduler():
    scheduler.add_job(periodic_match_rescore, IntervalTrigger(hours=24))  # Daily
    scheduler.start()