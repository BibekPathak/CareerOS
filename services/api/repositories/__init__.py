from collections.abc import Generator
from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from models.models import (
    User, Document, ResumeProfile, Company, CompanyProfile,
    Person, PersonProfile, Job, OutreachMessage, Interaction, Note, Embedding,
)


class UserRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_id(self, user_id) -> Optional[User]:
        return await self.session.get(User, user_id)

    async def get_by_auth_id(self, auth_id: str) -> Optional[User]:
        result = await self.session.execute(select(User).where(User.auth_provider_id == auth_id))
        return result.scalar_one_or_none()

    async def get_by_email(self, email: str) -> Optional[User]:
        result = await self.session.execute(select(User).where(User.email == email))
        return result.scalar_one_or_none()

    async def create(self, user: User) -> User:
        self.session.add(user)
        await self.session.flush()
        return user

    async def update(self, user: User) -> User:
        await self.session.merge(user)
        await self.session.flush()
        return user


class DocumentRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_id(self, doc_id) -> Optional[Document]:
        return await self.session.get(Document, doc_id)

    async def get_by_user(self, user_id) -> list[Document]:
        result = await self.session.execute(
            select(Document).where(Document.user_id == user_id).order_by(Document.created_at.desc())
        )
        return list(result.scalars().all())

    async def create(self, document: Document) -> Document:
        self.session.add(document)
        await self.session.flush()
        return document

    async def update(self, document: Document) -> Document:
        await self.session.merge(document)
        await self.session.flush()
        return document


class ResumeProfileRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_user(self, user_id) -> Optional[ResumeProfile]:
        result = await self.session.execute(
            select(ResumeProfile).where(ResumeProfile.user_id == user_id)
        )
        return result.scalar_one_or_none()

    async def create(self, profile: ResumeProfile) -> ResumeProfile:
        self.session.add(profile)
        await self.session.flush()
        return profile

    async def update(self, profile: ResumeProfile) -> ResumeProfile:
        await self.session.merge(profile)
        await self.session.flush()
        return profile

    async def upsert(self, profile: ResumeProfile) -> ResumeProfile:
        existing = await self.get_by_user(profile.user_id)
        if existing:
            profile.id = existing.id
            return await self.update(profile)
        return await self.create(profile)


class CompanyRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_id(self, company_id) -> Optional[Company]:
        return await self.session.get(Company, company_id)

    async def get_by_name(self, name: str) -> Optional[Company]:
        result = await self.session.execute(select(Company).where(Company.name.ilike(name)))
        return result.scalar_one_or_none()

    async def search(self, query: str, limit: int = 20) -> list[Company]:
        result = await self.session.execute(
            select(Company).where(Company.name.ilike(f"%{query}%")).limit(limit)
        )
        return list(result.scalars().all())

    async def create(self, company: Company) -> Company:
        self.session.add(company)
        await self.session.flush()
        return company

    async def update(self, company: Company) -> Company:
        await self.session.merge(company)
        await self.session.flush()
        return company


class CompanyProfileRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_company(self, company_id) -> Optional[CompanyProfile]:
        result = await self.session.execute(
            select(CompanyProfile).where(CompanyProfile.company_id == company_id)
        )
        return result.scalar_one_or_none()

    async def create(self, profile: CompanyProfile) -> CompanyProfile:
        self.session.add(profile)
        await self.session.flush()
        return profile

    async def update(self, profile: CompanyProfile) -> CompanyProfile:
        await self.session.merge(profile)
        await self.session.flush()
        return profile

    async def upsert(self, profile: CompanyProfile) -> CompanyProfile:
        existing = await self.get_by_company(profile.company_id)
        if existing:
            profile.id = existing.id
            return await self.update(profile)
        return await self.create(profile)


class PersonRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_id(self, person_id) -> Optional[Person]:
        return await self.session.get(Person, person_id)

    async def get_by_company(self, company_id) -> list[Person]:
        result = await self.session.execute(
            select(Person).where(Person.company_id == company_id)
        )
        return list(result.scalars().all())

    async def create(self, person: Person) -> Person:
        self.session.add(person)
        await self.session.flush()
        return person

    async def create_many(self, people: list[Person]) -> list[Person]:
        self.session.add_all(people)
        await self.session.flush()
        return people


class PersonProfileRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_person(self, person_id) -> Optional[PersonProfile]:
        result = await self.session.execute(
            select(PersonProfile).where(PersonProfile.person_id == person_id)
        )
        return result.scalar_one_or_none()

    async def create(self, profile: PersonProfile) -> PersonProfile:
        self.session.add(profile)
        await self.session.flush()
        return profile

    async def update(self, profile: PersonProfile) -> PersonProfile:
        await self.session.merge(profile)
        await self.session.flush()
        return profile

    async def upsert(self, profile: PersonProfile) -> PersonProfile:
        existing = await self.get_by_person(profile.person_id)
        if existing:
            profile.id = existing.id
            return await self.update(profile)
        return await self.create(profile)

    async def get_ranked_by_company(self, company_id) -> list[tuple[Person, PersonProfile]]:
        from sqlalchemy import select
        result = await self.session.execute(
            select(Person, PersonProfile)
            .join(PersonProfile, PersonProfile.person_id == Person.id)
            .where(Person.company_id == company_id)
            .order_by(PersonProfile.score.desc().nullslast())
        )
        return list(result.all())


class JobRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_company(self, company_id) -> list[Job]:
        result = await self.session.execute(
            select(Job).where(Job.company_id == company_id)
        )
        return list(result.scalars().all())

    async def create_many(self, jobs: list[Job]) -> list[Job]:
        self.session.add_all(jobs)
        await self.session.flush()
        return jobs


class OutreachMessageRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_person(self, person_id) -> list[OutreachMessage]:
        result = await self.session.execute(
            select(OutreachMessage).where(OutreachMessage.person_id == person_id)
        )
        return list(result.scalars().all())

    async def get_by_user(self, user_id) -> list[OutreachMessage]:
        result = await self.session.execute(
            select(OutreachMessage).where(OutreachMessage.user_id == user_id)
        )
        return list(result.scalars().all())

    async def create(self, message: OutreachMessage) -> OutreachMessage:
        self.session.add(message)
        await self.session.flush()
        return message

    async def create_many(self, messages: list[OutreachMessage]) -> list[OutreachMessage]:
        self.session.add_all(messages)
        await self.session.flush()
        return messages


class InteractionRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, interaction: Interaction) -> Interaction:
        self.session.add(interaction)
        await self.session.flush()
        return interaction


class NoteRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, note: Note) -> Note:
        self.session.add(note)
        await self.session.flush()
        return note


class EmbeddingRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, embedding: Embedding) -> Embedding:
        self.session.add(embedding)
        await self.session.flush()
        return embedding

    async def search_similar(self, query_embedding: list[float], resource_type: str, limit: int = 10) -> list[Embedding]:
        from sqlalchemy import text
        sql = text("""
            SELECT id, resource_type, resource_id, metadata, created_at, updated_at,
                   1 - (embedding <=> :query) AS similarity
            FROM embeddings
            WHERE resource_type = :resource_type
            ORDER BY embedding <=> :query
            LIMIT :limit
        """)
        result = await self.session.execute(sql, {
            "query": str(query_embedding),
            "resource_type": resource_type,
            "limit": limit,
        })
        return list(result.all())
