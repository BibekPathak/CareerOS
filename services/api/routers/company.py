import uuid

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from core.database import get_db
from core.dependencies import (
    get_company_repo, get_company_profile_repo, get_person_repo, get_job_repo,
)
from models.models import Company, CompanyProfile
from schemas import CompanyResearchRequest, CompanyResponse, CompanyProfileResponse, CompanyDetailResponse
from packages.ai.agents.company_agent import research_company

router = APIRouter(prefix="/company", tags=["company"])


@router.post("/research")
async def research(
    req: CompanyResearchRequest,
    db: AsyncSession = Depends(get_db),
):
    company_repo = get_company_repo(db)
    existing = await company_repo.get_by_name(req.company_name)
    if existing:
        return CompanyDetailResponse(
            company=CompanyResponse.model_validate(existing),
            profile=await _get_profile(db, existing.id),
        )

    profile_data = await research_company(req.company_name)

    company = Company(name=req.company_name)
    company = await company_repo.create(company)

    company_profile = CompanyProfile(
        company_id=company.id,
        overview=profile_data.overview,
        tech_stack=profile_data.tech_stack,
        products=[p.model_dump() for p in profile_data.products],
        engineering_blog_url=profile_data.engineering_blog_url,
        careers_page_url=profile_data.careers_page_url,
        open_positions=[p.model_dump() for p in profile_data.open_positions],
        recent_news=[n.model_dump() for n in profile_data.recent_news],
    )
    profile_repo = get_company_profile_repo(db)
    await profile_repo.create(company_profile)

    return CompanyDetailResponse(
        company=CompanyResponse.model_validate(company),
        profile=CompanyProfileResponse.model_validate(company_profile),
    )


@router.get("/{company_id}", response_model=CompanyDetailResponse)
async def get_company(
    company_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
):
    company_repo = get_company_repo(db)
    company = await company_repo.get_by_id(company_id)
    if not company:
        raise HTTPException(status_code=404, detail="Company not found")

    people_repo = get_person_repo(db)
    jobs_repo = get_job_repo(db)
    people = await people_repo.get_by_company(company_id)
    jobs = await jobs_repo.get_by_company(company_id)

    return CompanyDetailResponse(
        company=CompanyResponse.model_validate(company),
        profile=await _get_profile(db, company_id),
        people_count=len(people),
        jobs_count=len(jobs),
    )


@router.get("/search/{query}")
async def search_companies(
    query: str,
    db: AsyncSession = Depends(get_db),
):
    company_repo = get_company_repo(db)
    companies = await company_repo.search(query)
    return [CompanyResponse.model_validate(c) for c in companies]


async def _get_profile(db: AsyncSession, company_id: uuid.UUID):
    profile_repo = get_company_profile_repo(db)
    profile = await profile_repo.get_by_company(company_id)
    return CompanyProfileResponse.model_validate(profile) if profile else None
