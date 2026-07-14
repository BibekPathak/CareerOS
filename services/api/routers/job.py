import uuid
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from core.database import get_db
from core.dependencies import (
    get_job_repo, get_company_repo, get_company_profile_repo,
    get_resume_profile_repo,
)
from schemas import JobResponse, JobAnalysisResponse, JobDetailResponse
from packages.ai.agents.job_agent import analyze_job

router = APIRouter(prefix="/job", tags=["job"])


class JobAnalyzeRequest(BaseModel):
    user_id: uuid.UUID
    job_id: uuid.UUID
    context: Optional[str] = None


@router.post("/{job_id}/analyze")
async def analyze(
    job_id: uuid.UUID,
    user_id: uuid.UUID,
    context: Optional[str] = None,
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

    analysis = await analyze_job(
        job_title=job.title,
        job_description=job.description or "",
        company_name=company.name if company else "Unknown",
        resume=resume_input,
        context=context,
    )

    updated = await job_repo.update_analysis(
        job_id,
        required_skills=analysis.required_skills,
        nice_to_have_skills=analysis.nice_to_have_skills,
        missing_skills=analysis.missing_skills,
        resume_match_score=analysis.resume_match_score,
        strengths=analysis.strengths,
        weaknesses=analysis.weaknesses,
        people_to_contact=[p.model_dump() for p in analysis.people_to_contact],
        projects_to_mention=analysis.projects_to_mention,
        likely_interview_topics=analysis.likely_interview_topics,
        interview_difficulty=analysis.interview_difficulty,
    )

    return JobDetailResponse(
        job=JobResponse.model_validate(job),
        analysis=JobAnalysisResponse.model_validate(updated) if updated else None,
    )


@router.get("/{job_id}", response_model=JobDetailResponse)
async def get_job(
    job_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
):
    job_repo = get_job_repo(db)
    job = await job_repo.get_by_id(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    return JobDetailResponse(
        job=JobResponse.model_validate(job),
        analysis=JobAnalysisResponse.model_validate(job) if job.resume_match_score is not None else None,
    )


@router.get("/company/{company_id}", response_model=list[JobResponse])
async def list_company_jobs(
    company_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
):
    job_repo = get_job_repo(db)
    jobs = await job_repo.get_by_company(company_id)
    return [JobResponse.model_validate(j) for j in jobs]
