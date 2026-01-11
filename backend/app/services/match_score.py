from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
from app.services.vectorize import vectorizer

def compute_cosine_similarity(vec1, vec2) -> float:
    return cosine_similarity(vec1, vec2)[0][0]

def compute_weighted_score(
    resume_text: str,
    job_description: str,
    job_skills: list[str],
    job_experience_years: int = None,
    job_education_level: str = None,
    resume_experience_years: int = None,  # Assume extracted or provided
    resume_education_level: str = None
) -> dict:
    # Skills score (50%)
    resume_vec = vectorizer.transform(resume_text)
    job_vec = vectorizer.transform(job_description)
    skills_score = compute_cosine_similarity(resume_vec, job_vec) * 100

    # Experience score (30%) - simple match
    experience_score = 0
    if resume_experience_years and job_experience_years:
        if resume_experience_years >= job_experience_years:
            experience_score = 100
        else:
            experience_score = (resume_experience_years / job_experience_years) * 100

    # Education score (20%) - simple match
    education_score = 0
    education_levels = {'high school': 1, 'bachelor': 2, 'master': 3, 'phd': 4}
    if resume_education_level and job_education_level:
        resume_level = education_levels.get(resume_education_level.lower(), 0)
        job_level = education_levels.get(job_education_level.lower(), 0)
        if resume_level >= job_level:
            education_score = 100
        else:
            education_score = (resume_level / job_level) * 100 if job_level > 0 else 0

    overall_score = (skills_score * 0.5) + (experience_score * 0.3) + (education_score * 0.2)

    return {
        'overall': round(overall_score, 2),
        'skills': round(skills_score, 2),
        'experience': round(experience_score, 2),
        'education': round(education_score, 2)
    }