import uuid
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from core.database import get_db
from core.dependencies import (
    get_company_repo, get_company_profile_repo, get_person_repo,
    get_org_team_repo, get_org_relationship_repo,
)
from models.models import OrgTeam, OrgRelationship
from schemas import (
    OrgGraphResponse, OrgTeamResponse, OrgRelationshipResponse,
    PersonGraphResponse, PathResponse,
)
from packages.ai.agents.relationship_agent import build_relationship_graph

router = APIRouter(prefix="/graph", tags=["graph"])


@router.post("/build/{company_id}")
async def build_graph(
    company_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
):
    company_repo = get_company_repo(db)
    company = await company_repo.get_by_id(company_id)
    if not company:
        raise HTTPException(status_code=404, detail="Company not found")

    person_repo = get_person_repo(db)
    people = await person_repo.get_by_company(company_id)
    if not people:
        raise HTTPException(status_code=400, detail="No people found. Run people discovery first.")

    profile_repo = get_company_profile_repo(db)
    company_profile = await profile_repo.get_by_company(company_id)

    from packages.types.models import GraphPerson, CompanyIntelligence

    graph_people = [
        GraphPerson(
            name=p.name, role=p.role,
            expertise_areas=[],
        )
        for p in people
    ]

    ci = None
    if company_profile:
        ci = CompanyIntelligence(
            overview=company_profile.overview or "",
            tech_stack=company_profile.tech_stack,
            products=company_profile.products,
            engineering_blog_url=company_profile.engineering_blog_url,
            careers_page_url=company_profile.careers_page_url,
            open_positions=company_profile.open_positions,
            recent_news=company_profile.recent_news,
            hiring_velocity=company_profile.hiring_velocity,
            backend_team_size=company_profile.backend_team_size,
            languages_used=company_profile.languages_used,
            hiring_manager_name=company_profile.hiring_manager_name,
            recruiters=company_profile.recruiters,
            interns=company_profile.interns,
            ex_interns=company_profile.ex_interns,
            recent_promotions=company_profile.recent_promotions,
            conference_talks=company_profile.conference_talks,
            interview_difficulty=company_profile.interview_difficulty,
            likely_interview_topics=company_profile.likely_interview_topics,
            interesting_github_repos=company_profile.interesting_github_repos,
            org_chart_summary=company_profile.org_chart_summary,
        )

    graph = await build_relationship_graph(company.name, graph_people, ci)

    org_team_repo = get_org_team_repo(db)
    await org_team_repo.clear_company(company_id)

    name_to_id = {p.name: p.id for p in people}
    team_map = {}

    for t in graph.teams:
        team = OrgTeam(
            company_id=company_id,
            name=t.name,
            parent_team_id=None,
            description=t.description,
        )
        team = await org_team_repo.create(team)
        team_map[t.name] = team.id

    for p in graph.people:
        db_person_id = name_to_id.get(p.name)
        if db_person_id:
            team_id = team_map.get(p.team_name) if p.team_name else None
            await person_repo.update_graph_fields(
                db_person_id,
                team_id=team_id,
                influence_score=p.influence_score,
                activity_score=p.activity_score,
                response_probability=p.response_probability,
                referral_probability=p.referral_probability,
                expertise_areas=p.expertise_areas,
            )

    org_rel_repo = get_org_relationship_repo(db)
    await org_rel_repo.clear_company(company_id)
    relationships = []
    for r in graph.relationships:
        person_id = name_to_id.get(r.person_id)
        related_id = name_to_id.get(r.related_person_id)
        if person_id and related_id:
            relationships.append(OrgRelationship(
                company_id=company_id,
                person_id=person_id,
                related_person_id=related_id,
                relationship_type=r.relationship_type,
                team_name=r.team_name,
                confidence=r.confidence,
            ))
    if relationships:
        await org_rel_repo.create_many(relationships)

    return {"status": "built", "teams": len(graph.teams), "relationships": len(relationships), "people_with_graph": len([p for p in graph.people if p.name in name_to_id])}


@router.get("/{company_id}", response_model=OrgGraphResponse)
async def get_graph(
    company_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
):
    org_team_repo = get_org_team_repo(db)
    org_rel_repo = get_org_relationship_repo(db)
    person_repo = get_person_repo(db)

    teams = await org_team_repo.get_by_company(company_id)
    relationships = await org_rel_repo.get_by_company(company_id)
    people = await person_repo.get_by_company(company_id)

    return OrgGraphResponse(
        teams=[OrgTeamResponse.model_validate(t) for t in teams],
        relationships=[OrgRelationshipResponse.model_validate(r) for r in relationships],
        people=[
            PersonGraphResponse(
                id=p.id,
                name=p.name,
                role=p.role,
                team_id=p.team_id,
                influence_score=p.influence_score or 0.0,
                activity_score=p.activity_score or 0.0,
                response_probability=p.response_probability or 0.0,
                referral_probability=p.referral_probability or 0.0,
                expertise_areas=p.expertise_areas or [],
            )
            for p in people
        ],
    )


@router.get("/path/{company_id}", response_model=PathResponse)
async def find_path(
    company_id: uuid.UUID,
    from_person_id: uuid.UUID = Query(...),
    to_person_id: uuid.UUID = Query(...),
    db: AsyncSession = Depends(get_db),
):
    org_rel_repo = get_org_relationship_repo(db)
    path = await org_rel_repo.find_path(from_person_id, to_person_id)
    return PathResponse(
        path=[OrgRelationshipResponse.model_validate(r) for r in path],
        length=len(path),
    )


@router.get("/recommend-connector/{company_id}")
async def recommend_connector(
    company_id: uuid.UUID,
    target_person_id: uuid.UUID = Query(...),
    db: AsyncSession = Depends(get_db),
):
    org_rel_repo = get_org_relationship_repo(db)
    person_repo = get_person_repo(db)

    target = await person_repo.get_by_id(target_person_id)
    if not target:
        raise HTTPException(status_code=404, detail="Target person not found")

    relationships = await org_rel_repo.get_by_person(target_person_id)

    connector_ids = set()
    for r in relationships:
        if r.person_id != target_person_id:
            connector_ids.add(r.person_id)
        if r.related_person_id != target_person_id:
            connector_ids.add(r.related_person_id)

    connectors = []
    for cid in connector_ids:
        p = await person_repo.get_by_id(cid)
        if p:
            connectors.append({
                "id": str(p.id),
                "name": p.name,
                "role": p.role,
                "relationship": target.name,
                "influence_score": p.influence_score or 0.0,
            })

    connectors.sort(key=lambda c: c["influence_score"], reverse=True)
    return {"connectors": connectors}
