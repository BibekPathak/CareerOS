from collections.abc import Generator
from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from models.models import (
    User, Document, ResumeProfile, Company, CompanyProfile,
    Person, PersonProfile, Job, OutreachMessage, Interaction, Note, Embedding,
    OrgTeam, OrgRelationship, ResumeMatch, OutreachIntelligence,
    ConversationMemory, FollowUpSuggestion, DailyBrief,
    CareerGoal, GoalEvent,
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

    async def update_graph_fields(self, person_id, **kwargs) -> Person | None:
        person = await self.session.get(Person, person_id)
        if not person:
            return None
        for key, value in kwargs.items():
            if hasattr(person, key):
                setattr(person, key, value)
        await self.session.flush()
        return person


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
from sqlalchemy import select, delete as sa_delete
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

    async def get_by_id(self, job_id) -> Optional[Job]:
        return await self.session.get(Job, job_id)

    async def update(self, job: Job) -> Job:
        await self.session.merge(job)
        await self.session.flush()
        return job

    async def update_analysis(self, job_id, **kwargs) -> Job | None:
        job = await self.session.get(Job, job_id)
        if not job:
            return None
        for key, value in kwargs.items():
            if hasattr(job, key):
                setattr(job, key, value)
        await self.session.flush()
        return job


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


class OrgTeamRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_company(self, company_id) -> list[OrgTeam]:
        result = await self.session.execute(
            select(OrgTeam).where(OrgTeam.company_id == company_id)
        )
        return list(result.scalars().all())

    async def get_by_name(self, company_id, name: str) -> Optional[OrgTeam]:
        result = await self.session.execute(
            select(OrgTeam).where(OrgTeam.company_id == company_id, OrgTeam.name == name)
        )
        return result.scalar_one_or_none()

    async def create(self, team: OrgTeam) -> OrgTeam:
        self.session.add(team)
        await self.session.flush()
        return team

    async def create_many(self, teams: list[OrgTeam]) -> list[OrgTeam]:
        self.session.add_all(teams)
        await self.session.flush()
        return teams

    async def clear_company(self, company_id):
        await self.session.execute(
            sa_delete(OrgTeam).where(OrgTeam.company_id == company_id)
        )
        await self.session.flush()


class OrgRelationshipRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_company(self, company_id) -> list[OrgRelationship]:
        result = await self.session.execute(
            select(OrgRelationship).where(OrgRelationship.company_id == company_id)
        )
        return list(result.scalars().all())

    async def get_by_person(self, person_id) -> list[OrgRelationship]:
        result = await self.session.execute(
            select(OrgRelationship).where(
                (OrgRelationship.person_id == person_id) |
                (OrgRelationship.related_person_id == person_id)
            )
        )
        return list(result.scalars().all())

    async def create_many(self, relationships: list[OrgRelationship]) -> list[OrgRelationship]:
        self.session.add_all(relationships)
        await self.session.flush()
        return relationships

    async def find_path(self, from_person_id, to_person_id, max_depth: int = 4) -> list[OrgRelationship]:
        from sqlalchemy import text
        sql = text("""
            WITH RECURSIVE path AS (
                SELECT person_id, related_person_id, 1 AS depth,
                       ARRAY[person_id, related_person_id] AS visited
                FROM org_relationships
                WHERE person_id = :from_id
                UNION
                SELECT r.person_id, r.related_person_id, p.depth + 1,
                       p.visited || r.related_person_id
                FROM org_relationships r
                JOIN path p ON r.person_id = p.related_person_id
                WHERE p.depth < :max_depth
                AND NOT r.related_person_id = ANY(p.visited)
            )
            SELECT * FROM path
            WHERE related_person_id = :to_id
            ORDER BY depth
            LIMIT 1
        """)
        result = await self.session.execute(sql, {
            "from_id": from_person_id,
            "to_id": to_person_id,
            "max_depth": max_depth,
        })
        rows = result.all()
        if not rows:
            return []
        visited = rows[0].visited
        rels = await self.session.execute(
            select(OrgRelationship).where(
                OrgRelationship.person_id.in_(visited),
                OrgRelationship.related_person_id.in_(visited),
            )
        )
        return list(rels.scalars().all())

    async def clear_company(self, company_id):
        await self.session.execute(
            sa_delete(OrgRelationship).where(OrgRelationship.company_id == company_id)
        )
        await self.session.flush()


class ResumeMatchRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_user_and_job(self, user_id, job_id) -> Optional[ResumeMatch]:
        result = await self.session.execute(
            select(ResumeMatch).where(
                ResumeMatch.user_id == user_id,
                ResumeMatch.job_id == job_id,
            )
        )
        return result.scalar_one_or_none()

    async def get_by_user(self, user_id) -> list[ResumeMatch]:
        result = await self.session.execute(
            select(ResumeMatch).where(ResumeMatch.user_id == user_id)
        )
        return list(result.scalars().all())

    async def create(self, match: ResumeMatch) -> ResumeMatch:
        self.session.add(match)
        await self.session.flush()
        return match

    async def upsert(self, match: ResumeMatch) -> ResumeMatch:
        existing = await self.get_by_user_and_job(match.user_id, match.job_id)
        if existing:
            match.id = existing.id
            await self.session.merge(match)
            await self.session.flush()
            return match
        return await self.create(match)


class OutreachIntelligenceRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_person(self, person_id) -> Optional[OutreachIntelligence]:
        result = await self.session.execute(
            select(OutreachIntelligence).where(OutreachIntelligence.person_id == person_id)
        )
        return result.scalar_one_or_none()

    async def upsert(self, oi: OutreachIntelligence) -> OutreachIntelligence:
        existing = await self.get_by_person(oi.person_id)
        if existing:
            oi.id = existing.id
            await self.session.merge(oi)
            await self.session.flush()
            return oi
        self.session.add(oi)
        await self.session.flush()
        return oi


class ConversationMemoryRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_person(self, person_id) -> list[ConversationMemory]:
        result = await self.session.execute(
            select(ConversationMemory)
            .where(ConversationMemory.person_id == person_id)
            .order_by(ConversationMemory.created_at.asc())
        )
        return list(result.scalars().all())

    async def create(self, event: ConversationMemory) -> ConversationMemory:
        self.session.add(event)
        await self.session.flush()
        return event


class FollowUpSuggestionRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_user(self, user_id) -> list[FollowUpSuggestion]:
        result = await self.session.execute(
            select(FollowUpSuggestion)
            .where(FollowUpSuggestion.user_id == user_id)
            .order_by(FollowUpSuggestion.created_at.desc())
        )
        return list(result.scalars().all())

    async def get_by_person(self, person_id) -> list[FollowUpSuggestion]:
        result = await self.session.execute(
            select(FollowUpSuggestion)
            .where(FollowUpSuggestion.person_id == person_id)
            .order_by(FollowUpSuggestion.created_at.desc())
        )
        return list(result.scalars().all())

    async def create(self, suggestion: FollowUpSuggestion) -> FollowUpSuggestion:
        self.session.add(suggestion)
        await self.session.flush()
        return suggestion

    async def mark_read(self, suggestion_id) -> None:
        sug = await self.session.get(FollowUpSuggestion, suggestion_id)
        if sug:
            sug.is_read = True
            await self.session.flush()


class DailyBriefRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_today(self, user_id) -> Optional[DailyBrief]:
        from datetime import date
        result = await self.session.execute(
            select(DailyBrief).where(
                DailyBrief.user_id == user_id,
                DailyBrief.date == date.today(),
            )
        )
        return result.scalar_one_or_none()

    async def get_recent(self, user_id, limit: int = 7) -> list[DailyBrief]:
        result = await self.session.execute(
            select(DailyBrief)
            .where(DailyBrief.user_id == user_id)
            .order_by(DailyBrief.date.desc())
            .limit(limit)
        )
        return list(result.scalars().all())

    async def upsert(self, brief: DailyBrief) -> DailyBrief:
        existing = await self.get_today(brief.user_id)
        if existing:
            brief.id = existing.id
            await self.session.merge(brief)
            await self.session.flush()
            return brief
        self.session.add(brief)
        await self.session.flush()
        return brief

    async def mark_read(self, brief_id) -> None:
        brief = await self.session.get(DailyBrief, brief_id)
        if brief:
            brief.is_read = True
            await self.session.flush()


class CareerGoalRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_id(self, goal_id) -> Optional[CareerGoal]:
        return await self.session.get(CareerGoal, goal_id)

    async def get_active_by_user(self, user_id) -> list[CareerGoal]:
        result = await self.session.execute(
            select(CareerGoal)
            .where(CareerGoal.user_id == user_id, CareerGoal.status == "active")
            .order_by(CareerGoal.created_at.desc())
        )
        return list(result.scalars().all())

    async def get_by_user(self, user_id) -> list[CareerGoal]:
        result = await self.session.execute(
            select(CareerGoal)
            .where(CareerGoal.user_id == user_id)
            .order_by(CareerGoal.created_at.desc())
        )
        return list(result.scalars().all())

    async def create(self, goal: CareerGoal) -> CareerGoal:
        self.session.add(goal)
        await self.session.flush()
        return goal

    async def update(self, goal: CareerGoal) -> CareerGoal:
        await self.session.merge(goal)
        await self.session.flush()
        return goal


class GoalEventRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_goal(self, goal_id) -> list[GoalEvent]:
        result = await self.session.execute(
            select(GoalEvent)
            .where(GoalEvent.goal_id == goal_id)
            .order_by(GoalEvent.created_at.asc())
        )
        return list(result.scalars().all())

    async def create(self, event: GoalEvent) -> GoalEvent:
        self.session.add(event)
        await self.session.flush()
        return event
