import uuid
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from core.database import get_db
from core.dependencies import (
    get_company_repo, get_person_repo, get_person_profile_repo,
    get_resume_profile_repo, get_outreach_intelligence_repo,
    get_career_goal_repo,
)

router = APIRouter(prefix="/extension", tags=["extension"])


class ProfileIntelligenceRequest(BaseModel):
    person_name: str
    person_role: Optional[str] = None
    company_name: str
    user_id: Optional[uuid.UUID] = None


@router.post("/intelligence")
async def profile_intelligence(
    req: ProfileIntelligenceRequest,
    db: AsyncSession = Depends(get_db),
):
    company_repo = get_company_repo(db)
    company = await company_repo.get_by_name(req.company_name)
    if not company:
        return {
            "matchScore": None,
            "likelyInterviewer": None,
            "hiringManager": None,
            "recruiter": None,
            "conversationStarters": [],
            "topicsToAvoid": [],
            "sharedInterests": [],
            "bestProject": None,
            "suggestedMessage": None,
            "note": "Company not found in CareerOS. Research it first.",
        }

    person_repo = get_person_repo(db)
    people = await person_repo.get_by_company(company.id)
    person = next((p for p in people if p.name.lower() == req.person_name.lower()), None)
    if not person:
        return {
            "matchScore": None,
            "likelyInterviewer": None,
            "hiringManager": None,
            "recruiter": None,
            "conversationStarters": [],
            "topicsToAvoid": [],
            "sharedInterests": [],
            "bestProject": None,
            "suggestedMessage": None,
            "note": "Person not found in CareerOS for this company.",
            "companyId": str(company.id),
        }

    profile_repo = get_person_profile_repo(db)
    person_profile = await profile_repo.get_by_person(person.id)

    match_score = person_profile.score if person_profile and person_profile.score else None
    role_lower = (req.person_role or "").lower()
    likely_interviewer = "recruiter" in role_lower or "talent" in role_lower or "hr" in role_lower
    hiring_manager = "manager" in role_lower or "lead" in role_lower or "head" in role_lower or "director" in role_lower or "vp" in role_lower
    is_recruiter = "recruiter" in role_lower or "talent" in role_lower or "sourcer" in role_lower or "hr" in role_lower

    conversation_starters = []
    topics_to_avoid = []
    shared_interests = []
    best_project = None

    oi_repo = get_outreach_intelligence_repo(db)
    oi = await oi_repo.get_by_person(person.id)
    if oi:
        conversation_starters = oi.best_conversation_starters
        topics_to_avoid = oi.topics_to_avoid
        shared_interests = oi.person_interests

    suggested_message = None
    if oi and oi.best_conversation_starters:
        starter = oi.best_conversation_starters[0]
        suggested_message = f"Hi {person.name}, {starter}"

    if person.expertise_areas and person.expertise_areas:
        best_project = person.expertise_areas[0]

    return {
        "matchScore": match_score,
        "likelyInterviewer": likely_interviewer,
        "hiringManager": hiring_manager,
        "recruiter": is_recruiter,
        "conversationStarters": conversation_starters,
        "topicsToAvoid": topics_to_avoid,
        "sharedInterests": shared_interests,
        "bestProject": best_project,
        "suggestedMessage": suggested_message,
        "personId": str(person.id),
        "companyId": str(company.id),
    }
