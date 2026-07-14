from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from core.database import get_db
from repositories import (
    UserRepository, DocumentRepository, ResumeProfileRepository,
    CompanyRepository, CompanyProfileRepository, PersonRepository,
    PersonProfileRepository, JobRepository, OutreachMessageRepository,
    InteractionRepository, NoteRepository, EmbeddingRepository,
    OrgTeamRepository, OrgRelationshipRepository,
    ResumeMatchRepository, OutreachIntelligenceRepository,
)


async def get_user_repo(session: AsyncSession = Depends(get_db)) -> UserRepository:
    return UserRepository(session)


async def get_document_repo(session: AsyncSession = Depends(get_db)) -> DocumentRepository:
    return DocumentRepository(session)


async def get_resume_profile_repo(session: AsyncSession = Depends(get_db)) -> ResumeProfileRepository:
    return ResumeProfileRepository(session)


async def get_company_repo(session: AsyncSession = Depends(get_db)) -> CompanyRepository:
    return CompanyRepository(session)


async def get_company_profile_repo(session: AsyncSession = Depends(get_db)) -> CompanyProfileRepository:
    return CompanyProfileRepository(session)


async def get_person_repo(session: AsyncSession = Depends(get_db)) -> PersonRepository:
    return PersonRepository(session)


async def get_person_profile_repo(session: AsyncSession = Depends(get_db)) -> PersonProfileRepository:
    return PersonProfileRepository(session)


async def get_job_repo(session: AsyncSession = Depends(get_db)) -> JobRepository:
    return JobRepository(session)


async def get_outreach_repo(session: AsyncSession = Depends(get_db)) -> OutreachMessageRepository:
    return OutreachMessageRepository(session)


async def get_interaction_repo(session: AsyncSession = Depends(get_db)) -> InteractionRepository:
    return InteractionRepository(session)


async def get_note_repo(session: AsyncSession = Depends(get_db)) -> NoteRepository:
    return NoteRepository(session)


async def get_embedding_repo(session: AsyncSession = Depends(get_db)) -> EmbeddingRepository:
    return EmbeddingRepository(session)


async def get_org_team_repo(session: AsyncSession = Depends(get_db)) -> OrgTeamRepository:
    return OrgTeamRepository(session)


async def get_org_relationship_repo(session: AsyncSession = Depends(get_db)) -> OrgRelationshipRepository:
    return OrgRelationshipRepository(session)


async def get_resume_match_repo(session: AsyncSession = Depends(get_db)) -> ResumeMatchRepository:
    return ResumeMatchRepository(session)


async def get_outreach_intelligence_repo(session: AsyncSession = Depends(get_db)) -> OutreachIntelligenceRepository:
    return OutreachIntelligenceRepository(session)
