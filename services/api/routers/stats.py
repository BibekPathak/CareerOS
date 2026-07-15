import uuid

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from core.database import get_db
from core.dependencies import (
    get_career_goal_repo, get_person_repo, get_outreach_repo,
    get_interaction_repo,
)

router = APIRouter(prefix="/stats", tags=["stats"])


@router.get("/career/{user_id}")
async def career_stats(
    user_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
):
    goal_repo = get_career_goal_repo(db)
    goals = await goal_repo.get_by_user(user_id)
    active_goals = [g for g in goals if g.status == "active"]

    outreach_repo = get_outreach_repo(db)
    messages = await outreach_repo.get_by_user(user_id)
    sent = [m for m in messages if m.status.value == "sent"]
    total_outreach = len(messages)

    interaction_repo = get_interaction_repo(db)
    total_interactions = 0

    person_repo = get_person_repo(db)

    companies_tracked = set()
    people_contacted = set()
    for m in messages:
        people_contacted.add(str(m.person_id))

    from models.models import Company
    from sqlalchemy import select, func
    result = await db.execute(select(func.count(Company.id)))
    total_companies = result.scalar() or 0

    return {
        "goals": {
            "total": len(goals),
            "active": len(active_goals),
            "completed": len([g for g in goals if g.status == "completed"]),
            "paused": len([g for g in goals if g.status == "paused"]),
        },
        "outreach": {
            "total_messages": total_outreach,
            "sent": len(sent),
            "drafts": len([m for m in messages if m.status.value == "draft"]),
            "unique_people_contacted": len(people_contacted),
        },
        "companies": {
            "total_tracked": total_companies,
        },
        "summary": (
            f"You have {len(active_goals)} active career goals, "
            f"contacted {len(people_contacted)} people, "
            f"and generated {total_outreach} messages."
        ),
    }
