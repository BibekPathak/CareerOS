import uuid
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from core.database import get_db
from core.dependencies import (
    get_knowledge_graph_repo, get_company_repo, get_person_repo,
    get_company_profile_repo,
)
from models.models import KnowledgeGraphEntity, KnowledgeGraphEdge

router = APIRouter(prefix="/kg", tags=["knowledge_graph"])


class AddEntityRequest(BaseModel):
    type: str
    name: str


class AddEdgeRequest(BaseModel):
    source_id: uuid.UUID
    target_id: uuid.UUID
    relationship_type: str
    weight: float = 1.0
    metadata: Optional[dict] = None


@router.get("/entities")
async def find_entities(
    type: Optional[str] = None,
    name: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
):
    kg_repo = get_knowledge_graph_repo(db)
    entities = await kg_repo.find_entities(type, name)
    return [
        {"id": str(e.id), "type": e.type, "name": e.name, "metadata": e.metadata}
        for e in entities
    ]


@router.post("/entities")
async def add_entity(
    req: AddEntityRequest,
    db: AsyncSession = Depends(get_db),
):
    kg_repo = get_knowledge_graph_repo(db)
    entity = await kg_repo.get_or_create_entity(req.type, req.name)
    return {"id": str(entity.id), "type": entity.type, "name": entity.name}


@router.post("/edges")
async def add_edge(
    req: AddEdgeRequest,
    db: AsyncSession = Depends(get_db),
):
    kg_repo = get_knowledge_graph_repo(db)
    edge = KnowledgeGraphEdge(
        source_id=req.source_id,
        target_id=req.target_id,
        relationship_type=req.relationship_type,
        weight=req.weight,
        metadata=req.metadata,
    )
    await kg_repo.create_edge(edge)
    return {"status": "created"}


@router.get("/neighbors/{entity_id}")
async def get_neighbors(
    entity_id: uuid.UUID,
    relationship_type: Optional[str] = None,
    depth: int = Query(1, alias="depth"),
    db: AsyncSession = Depends(get_db),
):
    kg_repo = get_knowledge_graph_repo(db)
    neighbors = await kg_repo.get_neighbors(entity_id, relationship_type, depth)
    return {"entity_id": str(entity_id), "neighbors": neighbors, "count": len(neighbors)}


@router.get("/path")
async def find_path(
    from_type: str = Query(...),
    from_name: str = Query(...),
    to_type: str = Query(...),
    to_name: str = Query(...),
    max_depth: int = Query(4, alias="max_depth"),
    db: AsyncSession = Depends(get_db),
):
    kg_repo = get_knowledge_graph_repo(db)
    path = await kg_repo.find_path(from_type, from_name, to_type, to_name, max_depth)

    explanation = None
    if path:
        hops = [f"{p['from'].get('name', '?')} →({p['via']})→ {p['to'].get('name', '?')}" for p in path]
        explanation = " → ".join(hops)

    return {"path": path, "length": len(path), "explanation": explanation}


@router.post("/populate/{company_id}")
async def populate_from_company(
    company_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
):
    kg_repo = get_knowledge_graph_repo(db)
    company_repo = get_company_repo(db)
    person_repo = get_person_repo(db)
    profile_repo = get_company_profile_repo(db)

    company = await company_repo.get_by_id(company_id)
    if not company:
        raise HTTPException(404, "Company not found")

    company_entity = await kg_repo.get_or_create_entity("company", company.name, source_id=company.id)

    profile = await profile_repo.get_by_company(company_id)
    if profile:
        for tech in profile.tech_stack:
            tech_entity = await kg_repo.get_or_create_entity("technology", tech)
            await kg_repo.create_edge(KnowledgeGraphEdge(
                source_id=company_entity.id, target_id=tech_entity.id,
                relationship_type="uses_technology",
            ))

    people = await person_repo.get_by_company(company_id)
    for p in people:
        person_entity = await kg_repo.get_or_create_entity("person", p.name, source_id=p.id)
        await kg_repo.create_edge(KnowledgeGraphEdge(
            source_id=person_entity.id, target_id=company_entity.id,
            relationship_type="works_at",
        ))
        if p.expertise_areas:
            for area in p.expertise_areas:
                tech_entity = await kg_repo.get_or_create_entity("technology", area)
                await kg_repo.create_edge(KnowledgeGraphEdge(
                    source_id=person_entity.id, target_id=tech_entity.id,
                    relationship_type="knows",
                ))

    return {
        "company": company.name,
        "entities_created": 2 + len(profile.tech_stack if profile else []) + len(people) * (1 + sum(len(p.expertise_areas or []) for p in people)),
    }
