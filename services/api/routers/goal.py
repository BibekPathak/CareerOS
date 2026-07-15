import uuid
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from core.database import get_db
from core.dependencies import (
    get_career_goal_repo, get_goal_event_repo, get_resume_profile_repo,
)
from models.models import CareerGoal, GoalEvent
from schemas import (
    CareerGoalResponse, GoalEventResponse, GoalCreateResponse, PlanStepResponse,
)
from packages.ai.agents.planner_agent import create_career_plan

router = APIRouter(prefix="/goal", tags=["goal"])


class CreateGoalRequest(BaseModel):
    user_id: uuid.UUID
    title: str
    target_company: Optional[str] = None
    target_role: Optional[str] = None
    deadline: Optional[str] = None
    priority: str = "medium"
    context: Optional[str] = None


@router.post("/create", response_model=GoalCreateResponse)
async def create_goal(
    req: CreateGoalRequest,
    db: AsyncSession = Depends(get_db),
):
    plan = await create_career_plan(
        title=req.title,
        target_company=req.target_company,
        target_role=req.target_role,
        deadline=req.deadline,
        priority=req.priority,
        context=req.context,
    )

    goal = CareerGoal(
        user_id=req.user_id,
        title=plan.title,
        target_company=req.target_company,
        target_role=req.target_role,
        priority=req.priority,
        status="active",
        plan=[s.model_dump() for s in plan.plan],
        current_step_index=0,
        context_snapshot={"context": req.context} if req.context else {},
    )
    if req.deadline:
        from datetime import datetime
        try:
            goal.deadline = datetime.strptime(req.deadline, "%Y-%m-%d").date()
        except ValueError:
            pass

    goal_repo = get_career_goal_repo(db)
    goal = await goal_repo.create(goal)

    event_repo = get_goal_event_repo(db)
    await event_repo.create(GoalEvent(
        goal_id=goal.id,
        event_type="goal_created",
        event_data={"title": plan.title},
    ))

    return GoalCreateResponse(
        goal=_goal_to_response(goal),
        plan_summary=plan.summary,
    )


@router.get("/{goal_id}", response_model=CareerGoalResponse)
async def get_goal(
    goal_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
):
    goal_repo = get_career_goal_repo(db)
    goal = await goal_repo.get_by_id(goal_id)
    if not goal:
        raise HTTPException(status_code=404, detail="Goal not found")
    return _goal_to_response(goal)


@router.get("/user/{user_id}", response_model=list[CareerGoalResponse])
async def list_goals(
    user_id: uuid.UUID,
    active_only: bool = False,
    db: AsyncSession = Depends(get_db),
):
    goal_repo = get_career_goal_repo(db)
    if active_only:
        goals = await goal_repo.get_active_by_user(user_id)
    else:
        goals = await goal_repo.get_by_user(user_id)
    return [_goal_to_response(g) for g in goals]


@router.post("/{goal_id}/advance")
async def advance_goal(
    goal_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
):
    goal_repo = get_career_goal_repo(db)
    goal = await goal_repo.get_by_id(goal_id)
    if not goal:
        raise HTTPException(status_code=404, detail="Goal not found")

    plan = goal.plan or []
    next_idx = goal.current_step_index
    if next_idx < len(plan):
        plan[next_idx]["status"] = "completed"
        goal.plan = plan
        goal.current_step_index = next_idx + 1
        await goal_repo.update(goal)

        event_repo = get_goal_event_repo(db)
        await event_repo.create(GoalEvent(
            goal_id=goal.id,
            event_type="step_completed",
            event_data=plan[next_idx],
        ))

    return _goal_to_response(goal)


@router.post("/{goal_id}/status")
async def update_goal_status(
    goal_id: uuid.UUID,
    status: str,
    db: AsyncSession = Depends(get_db),
):
    goal_repo = get_career_goal_repo(db)
    goal = await goal_repo.get_by_id(goal_id)
    if not goal:
        raise HTTPException(status_code=404, detail="Goal not found")

    goal.status = status
    await goal_repo.update(goal)

    event_repo = get_goal_event_repo(db)
    await event_repo.create(GoalEvent(
        goal_id=goal.id,
        event_type=f"goal_{status}",
    ))

    return _goal_to_response(goal)


@router.get("/{goal_id}/events", response_model=list[GoalEventResponse])
async def get_goal_events(
    goal_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
):
    event_repo = get_goal_event_repo(db)
    events = await event_repo.get_by_goal(goal_id)
    return [
        GoalEventResponse(
            id=e.id,
            goal_id=e.goal_id,
            event_type=e.event_type,
            event_data=e.event_data,
            created_at=e.created_at,
        )
        for e in events
    ]


def _goal_to_response(goal: CareerGoal) -> CareerGoalResponse:
    return CareerGoalResponse(
        id=goal.id,
        title=goal.title,
        target_company=goal.target_company,
        target_role=goal.target_role,
        deadline=goal.deadline,
        priority=goal.priority,
        status=goal.status,
        plan=[PlanStepResponse(**s) for s in (goal.plan or [])],
        current_step_index=goal.current_step_index,
        progress_metrics=goal.progress_metrics,
        created_at=goal.created_at,
        updated_at=goal.updated_at,
    )
