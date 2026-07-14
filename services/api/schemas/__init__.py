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

    hiring_velocity: Optional[dict] = None
    backend_team_size: Optional[int] = None
    languages_used: list[str] = []
    hiring_manager_name: Optional[str] = None
    recruiters: list[dict] = []
    interns: list[dict] = []
    ex_interns: list[dict] = []
    recent_promotions: list[dict] = []
    conference_talks: list[dict] = []
    interview_difficulty: Optional[str] = None
    likely_interview_topics: list[str] = []
    interesting_github_repos: list[dict] = []
    org_chart_summary: Optional[str] = None

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


class PersonGraphResponse(BaseModel):
    id: uuid.UUID
    name: str
    role: Optional[str] = None
    team_id: Optional[uuid.UUID] = None
    influence_score: float = 0.0
    activity_score: float = 0.0
    response_probability: float = 0.0
    referral_probability: float = 0.0
    expertise_areas: list[str] = []

    model_config = {"from_attributes": True}


class OrgTeamResponse(BaseModel):
    id: uuid.UUID
    company_id: uuid.UUID
    name: str
    parent_team_id: Optional[uuid.UUID] = None
    description: Optional[str] = None

    model_config = {"from_attributes": True}


class OrgRelationshipResponse(BaseModel):
    id: uuid.UUID
    person_id: uuid.UUID
    related_person_id: uuid.UUID
    relationship_type: str
    team_name: Optional[str] = None
    confidence: float = 0.5

    model_config = {"from_attributes": True}


class OrgGraphResponse(BaseModel):
    teams: list[OrgTeamResponse]
    relationships: list[OrgRelationshipResponse]
    people: list[PersonGraphResponse]


class PathResponse(BaseModel):
    path: list[OrgRelationshipResponse]
    length: int


class JobResponse(BaseModel):
    id: uuid.UUID
    company_id: uuid.UUID
    title: str
    description: Optional[str] = None
    url: Optional[str] = None
    source: Optional[str] = None
    skills: list[str] = []
    created_at: datetime

    model_config = {"from_attributes": True}


class JobAnalysisResponse(BaseModel):
    id: uuid.UUID
    required_skills: list[str] = []
    nice_to_have_skills: list[str] = []
    missing_skills: list[str] = []
    resume_match_score: Optional[float] = None
    strengths: list[str] = []
    weaknesses: list[str] = []
    people_to_contact: list[dict] = []
    projects_to_mention: list[str] = []
    likely_interview_topics: list[str] = []
    interview_difficulty: Optional[str] = None

    model_config = {"from_attributes": True}


class JobDetailResponse(BaseModel):
    job: JobResponse
    analysis: Optional[JobAnalysisResponse] = None


class ResumeMatchRequest(BaseModel):
    pass


class ResumeMatchResponse(BaseModel):
    id: uuid.UUID
    overall_score: float = 0.0
    skill_matches: list[dict] = []
    strengths: list[str] = []
    weaknesses: list[str] = []
    mention_projects: list[str] = []
    avoid_mentioning: list[str] = []
    recommendation: str = ""

    model_config = {"from_attributes": True}


class OutreachIntelligenceResponse(BaseModel):
    id: uuid.UUID
    person_id: uuid.UUID
    best_conversation_starters: list[str] = []
    topics_to_avoid: list[str] = []
    person_interests: list[str] = []
    response_approach: Optional[str] = None
    optimal_send_time: Optional[str] = None
    referral_readiness: Optional[str] = None

    model_config = {"from_attributes": True}


class ConversationEventResponse(BaseModel):
    id: uuid.UUID
    person_id: uuid.UUID
    event_type: str
    event_data: Optional[dict] = None
    created_at: datetime

    model_config = {"from_attributes": True}


class FollowUpSuggestionResponse(BaseModel):
    id: uuid.UUID
    person_id: uuid.UUID
    suggestion_type: str
    reasoning: Optional[str] = None
    suggested_message: Optional[str] = None
    urgency: str = "medium"
    is_read: bool = False
    created_at: datetime

    model_config = {"from_attributes": True}


class TimelineResponse(BaseModel):
    events: list[ConversationEventResponse]
    suggestions: list[FollowUpSuggestionResponse]
