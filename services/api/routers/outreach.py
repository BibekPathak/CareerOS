import uuid
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from core.database import get_db
from core.dependencies import (
    get_person_repo, get_person_profile_repo, get_resume_profile_repo,
    get_company_repo, get_outreach_repo,
)
from models.models import OutreachMessage, MessageType, MessageStatus
from schemas import OutreachMessageResponse
from packages.ai.agents.outreach_agent import generate_outreach

router = APIRouter(prefix="/outreach", tags=["outreach"])


class GenerateRequest(BaseModel):
    user_id: uuid.UUID
    person_id: uuid.UUID
    company_id: uuid.UUID
    target_role: Optional[str] = None


@router.post("/generate")
async def generate(
    req: GenerateRequest,
    db: AsyncSession = Depends(get_db),
):
    person_repo = get_person_repo(db)
    person = await person_repo.get_by_id(req.person_id)
    if not person:
        raise HTTPException(status_code=404, detail="Person not found")

    profile_repo = get_person_profile_repo(db)
    person_profile = await profile_repo.get_by_person(req.person_id)
    if not person_profile:
        raise HTTPException(status_code=400, detail="Person has no ranking profile. Run ranking first.")

    resume_repo = get_resume_profile_repo(db)
    resume = await resume_repo.get_by_user(req.user_id)
    if not resume:
        raise HTTPException(status_code=400, detail="Upload resume first")

    company_repo = get_company_repo(db)
    company = await company_repo.get_by_id(req.company_id)
    if not company:
        raise HTTPException(status_code=404, detail="Company not found")

    from packages.types.models import ResumeOutput, RankedPerson, Project, Experience

    resume_input = ResumeOutput(
        skills=resume.skills,
        projects=[Project(**p) if isinstance(p, dict) else p for p in resume.projects],
        experience=[Experience(**e) if isinstance(e, dict) else e for e in resume.experience],
        technologies=resume.technologies,
        seniority=resume.seniority or "",
        preferred_roles=resume.preferred_roles,
        company_interests=resume.company_interests,
    )
    ranked_person = RankedPerson(
        name=person.name,
        score=person_profile.score or 0,
        explanation=person_profile.explanation or "",
        hiring_influence_score=(person_profile.ranking_factors or {}).get("hiring_influence", 0),
        technical_similarity_score=(person_profile.ranking_factors or {}).get("technical_similarity", 0),
        team_relevance_score=(person_profile.ranking_factors or {}).get("team_relevance", 0),
    )

    result = await generate_outreach(
        resume=resume_input,
        target_person=ranked_person,
        person_summary=person.summary or "",
        company_name=company.name,
        target_role=req.target_role,
    )

    outreach_repo = get_outreach_repo(db)
    type_map = {
        "connection_request": MessageType.CONNECTION_REQUEST,
        "dm": MessageType.DM,
        "referral_request": MessageType.REFERRAL_REQUEST,
        "follow_up": MessageType.FOLLOW_UP,
        "thank_you": MessageType.THANK_YOU,
    }

    messages = []
    for msg_type_str, content in result.messages.model_dump().items():
        msg = OutreachMessage(
            user_id=req.user_id,
            person_id=req.person_id,
            message_type=type_map[msg_type_str],
            content=content,
            status=MessageStatus.DRAFT,
        )
        messages.append(msg)

    saved = await outreach_repo.create_many(messages)
    return {
        "messages": [
            OutreachMessageResponse(
                id=m.id,
                message_type=m.message_type.value,
                content=m.content,
                status=m.status.value,
                created_at=m.created_at,
            )
            for m in saved
        ]
    }


@router.get("/{person_id}", response_model=list[OutreachMessageResponse])
async def get_messages(
    person_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
):
    outreach_repo = get_outreach_repo(db)
    messages = await outreach_repo.get_by_person(person_id)
    return [
        OutreachMessageResponse(
            id=m.id,
            message_type=m.message_type.value,
            content=m.content,
            status=m.status.value,
            created_at=m.created_at,
        )
        for m in messages
    ]
