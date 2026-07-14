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
        hiring_velocity=profile_data.hiring_velocity.model_dump() if profile_data.hiring_velocity else None,
        backend_team_size=profile_data.backend_team_size,
        languages_used=profile_data.languages_used,
        hiring_manager_name=profile_data.hiring_manager_name,
        recruiters=[r.model_dump() for r in profile_data.recruiters],
        interns=[i.model_dump() for i in profile_data.interns],
        ex_interns=[e.model_dump() for e in profile_data.ex_interns],
        recent_promotions=[p.model_dump() for p in profile_data.recent_promotions],
        conference_talks=[t.model_dump() for t in profile_data.conference_talks],
        interview_difficulty=profile_data.interview_difficulty,
        likely_interview_topics=profile_data.likely_interview_topics,
        interesting_github_repos=[r.model_dump() for r in profile_data.interesting_github_repos],
        org_chart_summary=profile_data.org_chart_summary,
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


@router.post("/{company_id}/intelligence")
async def run_intelligence(
    company_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
):
    company_repo = get_company_repo(db)
    company = await company_repo.get_by_id(company_id)
    if not company:
        raise HTTPException(status_code=404, detail="Company not found")

    profile_data = await research_company(company.name)

    profile_repo = get_company_profile_repo(db)
    existing = await profile_repo.get_by_company(company_id)
    if existing:
        existing.overview = profile_data.overview
        existing.tech_stack = profile_data.tech_stack
        existing.products = [p.model_dump() for p in profile_data.products]
        existing.engineering_blog_url = profile_data.engineering_blog_url
        existing.careers_page_url = profile_data.careers_page_url
        existing.open_positions = [p.model_dump() for p in profile_data.open_positions]
        existing.recent_news = [n.model_dump() for n in profile_data.recent_news]
        existing.hiring_velocity = profile_data.hiring_velocity.model_dump() if profile_data.hiring_velocity else None
        existing.backend_team_size = profile_data.backend_team_size
        existing.languages_used = profile_data.languages_used
        existing.hiring_manager_name = profile_data.hiring_manager_name
        existing.recruiters = [r.model_dump() for r in profile_data.recruiters]
        existing.interns = [i.model_dump() for i in profile_data.interns]
        existing.ex_interns = [e.model_dump() for e in profile_data.ex_interns]
        existing.recent_promotions = [p.model_dump() for p in profile_data.recent_promotions]
        existing.conference_talks = [t.model_dump() for t in profile_data.conference_talks]
        existing.interview_difficulty = profile_data.interview_difficulty
        existing.likely_interview_topics = profile_data.likely_interview_topics
        existing.interesting_github_repos = [r.model_dump() for r in profile_data.interesting_github_repos]
        existing.org_chart_summary = profile_data.org_chart_summary
        await profile_repo.update(existing)
        profile = existing
    else:
        company_profile = CompanyProfile(
            company_id=company.id,
            overview=profile_data.overview,
            tech_stack=profile_data.tech_stack,
            products=[p.model_dump() for p in profile_data.products],
            engineering_blog_url=profile_data.engineering_blog_url,
            careers_page_url=profile_data.careers_page_url,
            open_positions=[p.model_dump() for p in profile_data.open_positions],
            recent_news=[n.model_dump() for n in profile_data.recent_news],
            hiring_velocity=profile_data.hiring_velocity.model_dump() if profile_data.hiring_velocity else None,
            backend_team_size=profile_data.backend_team_size,
            languages_used=profile_data.languages_used,
            hiring_manager_name=profile_data.hiring_manager_name,
            recruiters=[r.model_dump() for r in profile_data.recruiters],
            interns=[i.model_dump() for i in profile_data.interns],
            ex_interns=[e.model_dump() for e in profile_data.ex_interns],
            recent_promotions=[p.model_dump() for p in profile_data.recent_promotions],
            conference_talks=[t.model_dump() for t in profile_data.conference_talks],
            interview_difficulty=profile_data.interview_difficulty,
            likely_interview_topics=profile_data.likely_interview_topics,
            interesting_github_repos=[r.model_dump() for r in profile_data.interesting_github_repos],
            org_chart_summary=profile_data.org_chart_summary,
        )
        await profile_repo.create(company_profile)
        profile = company_profile

    return CompanyProfileResponse.model_validate(profile)


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
