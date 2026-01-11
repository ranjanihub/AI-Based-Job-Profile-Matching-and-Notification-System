from pydantic import BaseModel
from typing import List, Optional
from uuid import UUID


class ResumeCreate(BaseModel):
    filename: str
    text_content: str


class ResumeResponse(BaseModel):
    id: UUID
    user_id: UUID
    filename: str
    created_at: str


class JobCreate(BaseModel):
    title: str
    description: str
    skills: List[str]
    experience_years: Optional[int]
    education_level: Optional[str]
    location: Optional[str]


class JobResponse(BaseModel):
    id: UUID
    title: str
    description: str
    skills: List[str]
    experience_years: Optional[int]
    education_level: Optional[str]
    location: Optional[str]
    created_at: str


from pydantic import BaseModel
from typing import List, Optional
from uuid import UUID


class ResumeCreate(BaseModel):
    filename: str
    text_content: str


class ResumeResponse(BaseModel):
    id: UUID
    user_id: UUID
    filename: str
    created_at: str


class JobCreate(BaseModel):
    title: str
    description: str
    skills: List[str]
    experience_years: Optional[int]
    education_level: Optional[str]
    location: Optional[str]


class JobResponse(BaseModel):
    id: UUID
    title: str
    description: str
    skills: List[str]
    experience_years: Optional[int]
    education_level: Optional[str]
    location: Optional[str]
    created_at: str


class MatchCreate(BaseModel):
    resume_id: UUID


class MatchResponse(BaseModel):
    id: UUID
    job: JobResponse
    score: float
    top_terms: List[str]
    created_at: str