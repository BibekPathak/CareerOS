import uuid
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from core.database import get_db
from core.dependencies import (
    get_person_repo, get_conversation_memory_repo, get_follow_up_repo,
)
from models.models import ConversationMemory, FollowUpSuggestion
from schemas import (
    ConversationEventResponse, FollowUpSuggestionResponse, TimelineResponse,
)
from packages.ai.agents.memory_agent import analyze_memory

router = APIRouter(prefix="/memory", tags=["memory"])


class LogEventRequest(BaseModel):
    user_id: uuid.UUID
    person_id: uuid.UUID
    event_type: str
    event_data: Optional[dict] = None


@router.post("/event")
async def log_event(
    req: LogEventRequest,
    db: AsyncSession = Depends(get_db),
):
    event = ConversationMemory(
        user_id=req.user_id,
        person_id=req.person_id,
        event_type=req.event_type,
        event_data=req.event_data,
    )
    memory_repo = get_conversation_memory_repo(db)
    event = await memory_repo.create(event)
    return ConversationEventResponse(
        id=event.id,
        person_id=event.person_id,
        event_type=event.event_type.value,
        event_data=event.event_data,
        created_at=event.created_at,
    )


@router.get("/timeline/{person_id}", response_model=TimelineResponse)
async def get_timeline(
    person_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
):
    memory_repo = get_conversation_memory_repo(db)
    events = await memory_repo.get_by_person(person_id)

    follow_up_repo = get_follow_up_repo(db)
    suggestions = await follow_up_repo.get_by_person(person_id)

    return TimelineResponse(
        events=[
            ConversationEventResponse(
                id=e.id,
                person_id=e.person_id,
                event_type=e.event_type.value,
                event_data=e.event_data,
                created_at=e.created_at,
            )
            for e in events
        ],
        suggestions=[
            FollowUpSuggestionResponse(
                id=s.id,
                person_id=s.person_id,
                suggestion_type=s.suggestion_type,
                reasoning=s.reasoning,
                suggested_message=s.suggested_message,
                urgency=s.urgency,
                is_read=s.is_read,
                created_at=s.created_at,
            )
            for s in suggestions
        ],
    )


@router.post("/analyze/{person_id}")
async def analyze_person_memory(
    person_id: uuid.UUID,
    user_id: uuid.UUID,
    recent_activity: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
):
    person_repo = get_person_repo(db)
    person = await person_repo.get_by_id(person_id)
    if not person:
        raise HTTPException(status_code=404, detail="Person not found")

    memory_repo = get_conversation_memory_repo(db)
    events = await memory_repo.get_by_person(person_id)

    from packages.types.models import TimelineEntry

    timeline = [
        TimelineEntry(
            event_type=e.event_type.value,
            event_data=e.event_data,
            timestamp=e.created_at.isoformat(),
        )
        for e in events
    ]

    result = await analyze_memory(
        person_name=person.name,
        timeline=timeline,
        recent_activity=recent_activity,
    )

    follow_up_repo = get_follow_up_repo(db)
    if result.should_follow_up:
        suggestion = FollowUpSuggestion(
            user_id=user_id,
            person_id=person_id,
            suggestion_type="follow_up",
            reasoning=result.reasoning,
            suggested_message=result.suggested_message,
            urgency=result.urgency,
        )
        await follow_up_repo.create(suggestion)

    return {
        "should_follow_up": result.should_follow_up,
        "reasoning": result.reasoning,
        "timing_suggestion": result.timing_suggestion,
        "suggested_message": result.suggested_message,
        "urgency": result.urgency,
    }


@router.get("/suggestions/{user_id}", response_model=list[FollowUpSuggestionResponse])
async def list_suggestions(
    user_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
):
    follow_up_repo = get_follow_up_repo(db)
    suggestions = await follow_up_repo.get_by_user(user_id)
    return [
        FollowUpSuggestionResponse(
            id=s.id,
            person_id=s.person_id,
            suggestion_type=s.suggestion_type,
            reasoning=s.reasoning,
            suggested_message=s.suggested_message,
            urgency=s.urgency,
            is_read=s.is_read,
            created_at=s.created_at,
        )
        for s in suggestions
    ]


@router.post("/suggestions/{suggestion_id}/read")
async def mark_suggestion_read(
    suggestion_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
):
    follow_up_repo = get_follow_up_repo(db)
    await follow_up_repo.mark_read(suggestion_id)
    return {"status": "read"}
