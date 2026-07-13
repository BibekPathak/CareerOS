import uuid
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from core.database import get_db
from core.dependencies import (
    get_company_repo, get_person_repo, get_person_profile_repo, get_resume_profile_repo,
)
from models.models import Person, PersonProfile
from schemas import PersonResponse
from packages.ai.agents.people_agent import discover_people
from packages.ai.agents.ranking_agent import rank_people as run_ranking

router = APIRouter(prefix="/people", tags=["people"])


class DiscoverRequest(BaseModel):
    company_id: uuid.UUID
    company_name: Optional[str] = None


@router.post("/discover")
async def discover(
    req: DiscoverRequest,
    db: AsyncSession = Depends(get_db),
):
    company_repo = get_company_repo(db)
    company = await company_repo.get_by_id(req.company_id)
    if not company:
        raise HTTPException(status_code=404, detail="Company not found")

    name = req.company_name or company.name
    discovered = await discover_people(name, company.domain)

    person_repo = get_person_repo(db)
    existing = await person_repo.get_by_company(req.company_id)
    existing_names = {p.name for p in existing}

    new_people = []
    for p in discovered:
        if p.name not in existing_names:
            new_people.append(Person(
                company_id=req.company_id,
                name=p.name,
                role=p.role,
                public_profile_url=p.public_profile_url,
                source=p.source,
                summary=p.summary,
            ))
    if new_people:
        await person_repo.create_many(new_people)

    return {"discovered": len(discovered), "new": len(new_people), "total": len(existing) + len(new_people)}


class RankRequest(BaseModel):
    company_id: uuid.UUID
    user_id: uuid.UUID
    target_role: Optional[str] = None


@router.post("/rank")
async def rank(
    req: RankRequest,
    db: AsyncSession = Depends(get_db),
):
    resume_repo = get_resume_profile_repo(db)
    resume = await resume_repo.get_by_user(req.user_id)
    if not resume:
        raise HTTPException(status_code=400, detail="Upload resume first")

    person_repo = get_person_repo(db)
    people = await person_repo.get_by_company(req.company_id)
    if not people:
        raise HTTPException(status_code=400, detail="No people found. Run discover first.")

    company_repo = get_company_repo(db)
    company = await company_repo.get_by_id(req.company_id)
    if not company:
        raise HTTPException(status_code=404, detail="Company not found")

    from packages.types.models import ResumeOutput, Person as PersonModel, Experience, Project

    resume_input = ResumeOutput(
        skills=resume.skills,
        projects=[Project(**p) if isinstance(p, dict) else p for p in resume.projects],
        experience=[Experience(**e) if isinstance(e, dict) else e for e in resume.experience],
        technologies=resume.technologies,
        seniority=resume.seniority or "",
        preferred_roles=resume.preferred_roles,
        company_interests=resume.company_interests,
    )
    people_input = [
        PersonModel(name=p.name, role=p.role, source=p.source or "", summary=p.summary or "")
        for p in people
    ]

    ranking = await run_ranking(company.name, resume_input, people_input, req.target_role)

    profile_repo = get_person_profile_repo(db)
    results = []
    name_to_person = {p.name: p for p in people}
    for r in ranking.ranked_people:
        person = name_to_person.get(r.name)
        if person:
            await profile_repo.upsert(PersonProfile(
                person_id=person.id,
                ranking_factors={
                    "hiring_influence": r.hiring_influence_score,
                    "technical_similarity": r.technical_similarity_score,
                    "team_relevance": r.team_relevance_score,
                },
                score=r.score,
                explanation=r.explanation,
            ))
            results.append(PersonResponse(
                id=person.id,
                name=r.name,
                role=person.role,
                public_profile_url=person.public_profile_url,
                source=person.source,
                summary=person.summary,
                score=r.score,
                explanation=r.explanation,
            ))

    return {"ranked": results}


@router.get("/{company_id}", response_model=list[PersonResponse])
async def list_people(
    company_id: uuid.UUID,
    sort_by: str = Query("score", regex="^(score|name)$"),
    db: AsyncSession = Depends(get_db),
):
    profile_repo = get_person_profile_repo(db)
    ranked = await profile_repo.get_ranked_by_company(company_id)
    return [
        PersonResponse(
            id=person.id,
            name=person.name,
            role=person.role,
            public_profile_url=person.public_profile_url,
            source=person.source,
            summary=person.summary,
            score=profile.score,
            explanation=profile.explanation,
        )
        for person, profile in ranked
    ]


@router.get("/{company_id}/{person_id}", response_model=PersonResponse)
async def get_person(
    company_id: uuid.UUID,
    person_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
):
    person_repo = get_person_repo(db)
    person = await person_repo.get_by_id(person_id)
    if not person:
        raise HTTPException(status_code=404, detail="Person not found")

    profile_repo = get_person_profile_repo(db)
    profile = await profile_repo.get_by_person(person_id)

    return PersonResponse(
        id=person.id,
        name=person.name,
        role=person.role,
        public_profile_url=person.public_profile_url,
        source=person.source,
        summary=person.summary,
        score=profile.score if profile else None,
        explanation=profile.explanation if profile else None,
    )
