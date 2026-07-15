import uuid
from datetime import date

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from core.database import get_db
from core.dependencies import (
    get_daily_brief_repo, get_job_repo, get_company_repo,
    get_follow_up_repo, get_person_repo, get_company_profile_repo,
)
from models.models import DailyBrief
from schemas import DailyBriefResponse, DailyBriefGenerateResponse
from packages.ai.agents.daily_agent import generate_daily_brief

router = APIRouter(prefix="/daily", tags=["daily"])


@router.get("/today/{user_id}", response_model=DailyBriefResponse | None)
async def get_today_brief(
    user_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
):
    brief_repo = get_daily_brief_repo(db)
    brief = await brief_repo.get_today(user_id)
    if not brief:
        return None
    return DailyBriefResponse(
        id=brief.id,
        date=brief.date,
        summary=brief.summary,
        items=brief.items,
        is_read=brief.is_read,
        created_at=brief.created_at,
    )


@router.post("/generate/{user_id}", response_model=DailyBriefGenerateResponse)
async def generate_brief(
    user_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
):
    brief_repo = get_daily_brief_repo(db)
    existing = await brief_repo.get_today(user_id)
    if existing:
        return DailyBriefGenerateResponse(
            brief=DailyBriefResponse(
                id=existing.id,
                date=existing.date,
                summary=existing.summary,
                items=existing.items,
                is_read=existing.is_read,
                created_at=existing.created_at,
            ),
            generated=False,
        )

    company_repo = get_company_repo(db)
    companies = await company_repo.search("", limit=20)

    new_jobs = []
    company_news = []
    for c in companies:
        job_repo = get_job_repo(db)
        jobs = await job_repo.get_by_company(c.id)
        if jobs:
            new_jobs.append({
                "title": f"{len(jobs)} open positions at {c.name}",
                "description": ", ".join(j.title for j in jobs[:5]),
                "urgency": "medium",
            })
        profile_repo = get_company_profile_repo(db)
        profile = await profile_repo.get_by_company(c.id)
        if profile and profile.recent_news:
            for news in profile.recent_news[:2]:
                company_news.append({
                    "title": f"{c.name}: {news.get('title', 'Update')}",
                    "description": news.get("summary", ""),
                    "urgency": "low",
                })

    follow_up_repo = get_follow_up_repo(db)
    suggestions = await follow_up_repo.get_by_user(user_id)
    follow_ups_due = []
    for s in suggestions:
        if not s.is_read:
            person_repo = get_person_repo(db)
            person = await person_repo.get_by_id(s.person_id)
            follow_ups_due.append({
                "title": f"Follow up with {person.name if person else 'someone'}",
                "description": s.reasoning or "",
                "urgency": s.urgency,
            })

    result = await generate_daily_brief(
        new_jobs=new_jobs,
        company_news=company_news,
        follow_ups_due=follow_ups_due,
    )

    brief = DailyBrief(
        user_id=user_id,
        date=date.today(),
        summary=result.summary,
        items=[i.model_dump() for i in result.items],
    )
    await brief_repo.upsert(brief)

    return DailyBriefGenerateResponse(
        brief=DailyBriefResponse(
            id=brief.id,
            date=brief.date,
            summary=brief.summary,
            items=brief.items,
            is_read=brief.is_read,
            created_at=brief.created_at,
        ),
        generated=True,
    )


@router.get("/history/{user_id}", response_model=list[DailyBriefResponse])
async def brief_history(
    user_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
):
    brief_repo = get_daily_brief_repo(db)
    briefs = await brief_repo.get_recent(user_id)
    return [
        DailyBriefResponse(
            id=b.id,
            date=b.date,
            summary=b.summary,
            items=b.items,
            is_read=b.is_read,
            created_at=b.created_at,
        )
        for b in briefs
    ]


@router.post("/{brief_id}/read")
async def mark_read(
    brief_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
):
    brief_repo = get_daily_brief_repo(db)
    await brief_repo.mark_read(brief_id)
    return {"status": "read"}
