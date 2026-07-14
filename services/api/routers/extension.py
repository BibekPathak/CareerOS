import uuid
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from core.database import get_db
from core.dependencies import (
    get_company_repo, get_person_repo, get_person_profile_repo,
    get_resume_profile_repo, get_outreach_intelligence_repo,
)
from packages.ai.agents.outreach_intelligence_agent import generate_outreach_intelligence

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
            "thingsToMention": [],
            "sharedInterests": [],
            "suggestedMessage": None,
            "note": "Company not found in CareerOS. Research it first.",
        }

    person_repo = get_person_repo(db)
    people = await person_repo.get_by_company(company.id)
    person = next((p for p in people if p.name.lower() == req.person_name.lower()), None)
    if not person:
        return {
            "matchScore": None,
            "thingsToMention": [],
            "sharedInterests": [],
            "suggestedMessage": None,
            "note": "Person not found in CareerOS for this company.",
            "companyId": str(company.id),
        }

    profile_repo = get_person_profile_repo(db)
    person_profile = await profile_repo.get_by_person(person.id)

    things_to_mention = []
    shared_interests = []
    suggested_message = None
    match_score = None

    if person_profile and person_profile.ranking_factors:
        match_score = person_profile.score

    oi_repo = get_outreach_intelligence_repo(db)
    oi = await oi_repo.get_by_person(person.id)
    if oi:
        shared_interests = oi.person_interests
        if oi.best_conversation_starters:
            things_to_mention = oi.best_conversation_starters

    return {
        "matchScore": match_score,
        "thingsToMention": things_to_mention,
        "sharedInterests": shared_interests,
        "suggestedMessage": suggested_message,
        "personId": str(person.id),
        "companyId": str(company.id),
    }
