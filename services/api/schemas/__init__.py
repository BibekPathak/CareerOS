import uuid
from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class UserResponse(BaseModel):
    id: uuid.UUID
    email: str
    name: Optional[str] = None
    created_at: datetime

    model_config = {"from_attributes": True}


class ResumeUploadResponse(BaseModel):
    id: uuid.UUID
    status: str
    message: str


class ResumeProfileResponse(BaseModel):
    id: uuid.UUID
    skills: list[str]
    projects: list[dict]
    experience: list[dict]
    technologies: list[str]
    seniority: Optional[str] = None
    preferred_roles: list[str]
    company_interests: list[str]
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class CompanyResponse(BaseModel):
    id: uuid.UUID
    name: str
    domain: Optional[str] = None
    description: Optional[str] = None
    created_at: datetime

    model_config = {"from_attributes": True}


class CompanyProfileResponse(BaseModel):
    id: uuid.UUID
    company_id: uuid.UUID
    overview: Optional[str] = None
    tech_stack: list[str]
    products: list[dict]
    engineering_blog_url: Optional[str] = None
    careers_page_url: Optional[str] = None
    open_positions: list[dict]
    recent_news: list[dict]
    created_at: datetime

    model_config = {"from_attributes": True}


class CompanyDetailResponse(BaseModel):
    company: CompanyResponse
    profile: Optional[CompanyProfileResponse] = None
    people_count: int = 0
    jobs_count: int = 0


class PersonResponse(BaseModel):
    id: uuid.UUID
    name: str
    role: Optional[str] = None
    public_profile_url: Optional[str] = None
    source: Optional[str] = None
    summary: Optional[str] = None
    score: Optional[float] = None
    explanation: Optional[str] = None

    model_config = {"from_attributes": True}


class OutreachGenerateRequest(BaseModel):
    person_id: uuid.UUID
    job_title: Optional[str] = None


class OutreachMessageResponse(BaseModel):
    id: uuid.UUID
    message_type: str
    content: str
    status: str
    created_at: datetime

    model_config = {"from_attributes": True}


class CompanySearchRequest(BaseModel):
    query: str


class CompanyResearchRequest(BaseModel):
    company_name: str
