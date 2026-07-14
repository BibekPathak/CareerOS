import uuid

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from core.database import get_db
from core.dependencies import (
    get_job_repo, get_company_repo, get_resume_profile_repo,
    get_resume_match_repo,
)
from models.models import ResumeMatch
from schemas import ResumeMatchRequest, ResumeMatchResponse
from packages.ai.agents.resume_matching_agent import match_resume_to_job

router = APIRouter(prefix="/resume/match", tags=["resume"])


@router.post("/{job_id}")
async def match(
    job_id: uuid.UUID,
    user_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
):
    job_repo = get_job_repo(db)
    job = await job_repo.get_by_id(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    resume_repo = get_resume_profile_repo(db)
    resume = await resume_repo.get_by_user(user_id)
    if not resume:
        raise HTTPException(status_code=400, detail="Upload resume first")

    company_repo = get_company_repo(db)
    company = await company_repo.get_by_id(job.company_id)

    from packages.types.models import ResumeOutput, Project, Experience

    resume_input = ResumeOutput(
        skills=resume.skills,
        projects=[Project(**p) if isinstance(p, dict) else p for p in resume.projects],
        experience=[Experience(**e) if isinstance(e, dict) else e for e in resume.experience],
        technologies=resume.technologies,
        seniority=resume.seniority or "",
        preferred_roles=resume.preferred_roles,
        company_interests=resume.company_interests,
    )

    result = await match_resume_to_job(
        job_title=job.title,
        job_description=job.description or "",
        job_skills=job.skills,
        company_name=company.name if company else "Unknown",
        resume=resume_input,
    )

    match_repo = get_resume_match_repo(db)
    rm = ResumeMatch(
        user_id=user_id,
        job_id=job_id,
        overall_score=result.overall_score,
        skill_matches=[s.model_dump() for s in result.skill_matches],
        strengths=result.strengths,
        weaknesses=result.weaknesses,
        mention_projects=result.mention_projects,
        avoid_mentioning=result.avoid_mentioning,
        recommendation=result.recommendation,
    )
    await match_repo.upsert(rm)

    return ResumeMatchResponse(
        id=rm.id,
        overall_score=rm.overall_score or 0.0,
        skill_matches=rm.skill_matches,
        strengths=rm.strengths,
        weaknesses=rm.weaknesses,
        mention_projects=rm.mention_projects,
        avoid_mentioning=rm.avoid_mentioning,
        recommendation=rm.recommendation or "",
    )


@router.get("/{job_id}", response_model=ResumeMatchResponse | None)
async def get_match(
    job_id: uuid.UUID,
    user_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
):
    match_repo = get_resume_match_repo(db)
    rm = await match_repo.get_by_user_and_job(user_id, job_id)
    if not rm:
        raise HTTPException(status_code=404, detail="No match found. Run match first.")
    return ResumeMatchResponse(
        id=rm.id,
        overall_score=rm.overall_score or 0.0,
        skill_matches=rm.skill_matches,
        strengths=rm.strengths,
        weaknesses=rm.weaknesses,
        mention_projects=rm.mention_projects,
        avoid_mentioning=rm.avoid_mentioning,
        recommendation=rm.recommendation or "",
    )


@router.get("/list/{user_id}", response_model=list[ResumeMatchResponse])
async def list_matches(
    user_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
):
    match_repo = get_resume_match_repo(db)
    matches = await match_repo.get_by_user(user_id)
    return [
        ResumeMatchResponse(
            id=rm.id,
            overall_score=rm.overall_score or 0.0,
            skill_matches=rm.skill_matches,
            strengths=rm.strengths,
            weaknesses=rm.weaknesses,
            mention_projects=rm.mention_projects,
            avoid_mentioning=rm.avoid_mentioning,
            recommendation=rm.recommendation or "",
        )
        for rm in matches
    ]
