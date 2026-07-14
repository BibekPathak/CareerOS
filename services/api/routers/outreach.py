import uuid
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from core.database import get_db
from core.dependencies import (
    get_person_repo, get_person_profile_repo, get_resume_profile_repo,
    get_company_repo, get_outreach_repo, get_outreach_intelligence_repo,
)
from models.models import OutreachMessage, MessageType, MessageStatus, OutreachIntelligence
from schemas import OutreachMessageResponse, OutreachIntelligenceResponse
from packages.ai.agents.outreach_agent import generate_outreach
from packages.ai.agents.outreach_intelligence_agent import generate_outreach_intelligence

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

    oi_repo = get_outreach_intelligence_repo(db)
    existing_intel = await oi_repo.get_by_person(req.person_id)

    if not existing_intel:
        intel = await generate_outreach_intelligence(
            person_name=person.name,
            person_role=person.role,
            person_summary=person.summary or "",
            expertise_areas=person.expertise_areas or [],
            company_name=company.name,
            resume=resume_input,
        )
        oi = OutreachIntelligence(
            user_id=req.user_id,
            person_id=req.person_id,
            best_conversation_starters=intel.best_conversation_starters,
            topics_to_avoid=intel.topics_to_avoid,
            person_interests=intel.person_interests,
            response_approach=intel.response_approach,
            optimal_send_time=intel.optimal_send_time,
            referral_readiness=intel.referral_readiness,
        )
        await oi_repo.upsert(oi)
    else:
        intel = None
        oi = existing_intel

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
        ],
        "intelligence": OutreachIntelligenceResponse.model_validate(oi) if oi else None,
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


@router.get("/intelligence/{person_id}", response_model=OutreachIntelligenceResponse)
async def get_intelligence(
    person_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
):
    oi_repo = get_outreach_intelligence_repo(db)
    oi = await oi_repo.get_by_person(person_id)
    if not oi:
        raise HTTPException(status_code=404, detail="No intelligence found. Run outreach generate first.")
    return OutreachIntelligenceResponse.model_validate(oi)

