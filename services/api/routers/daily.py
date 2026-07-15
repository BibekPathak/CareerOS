import uuid
from datetime import date
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from core.database import get_db
from core.dependencies import (
    get_daily_brief_repo, get_job_repo, get_company_repo,
    get_follow_up_repo, get_person_repo, get_company_profile_repo,
    get_career_goal_repo,
)
from models.models import DailyBrief
from schemas import DailyBriefResponse, DailyBriefGenerateResponse
from packages.ai.agents.daily_agent import generate_daily_brief
from packages.ai.agents.mission_agent import generate_todays_mission

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


class MissionResponse(BaseModel):
    goals: list[dict]
    summary_stats: dict = {}


@router.post("/mission/{user_id}")
async def generate_mission(
    user_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
):
    goal_repo = get_career_goal_repo(db)
    goals = await goal_repo.get_active_by_user(user_id)

    goals_data = []
    for g in goals:
        plan = g.plan or []
        next_step = plan[g.current_step_index] if g.current_step_index < len(plan) else None
        goals_data.append({
            "title": g.title,
            "company": g.target_company or "",
            "role": g.target_role or "",
            "deadline": str(g.deadline) if g.deadline else "",
            "priority": g.priority,
            "next_step": next_step.get("action", "") if next_step else "",
            "progress": f"Step {g.current_step_index + 1} of {len(plan)}" if plan else "No plan yet",
        })

    follow_up_repo = get_follow_up_repo(db)
    suggestions = await follow_up_repo.get_by_user(user_id)
    follow_ups = []
    for s in suggestions:
        if not s.is_read and s.urgency in ("high", "medium"):
            person_repo = get_person_repo(db)
            person = await person_repo.get_by_id(s.person_id)
            follow_ups.append({
                "title": f"Follow up with {person.name if person else 'someone'}",
                "description": s.reasoning or "",
                "urgency": s.urgency,
            })

    people = await get_person_repo(db).get_by_user(user_id) if hasattr(get_person_repo(db), 'get_by_user') else []
    stats = {
        "Active goals": len(goals),
        "Follow-ups due": len(follow_ups),
    }

    result = await generate_todays_mission(
        goals=goals_data,
        follow_ups=follow_ups,
        recent_activity=[],
        stats=stats,
    )

    return MissionResponse(
        goals=[g.model_dump() for g in result.goals],
        summary_stats=result.summary_stats,
    )

