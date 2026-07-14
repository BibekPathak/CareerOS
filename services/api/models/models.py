import uuid
from datetime import date
from typing import Optional

from sqlalchemy import String, Text, Date, Float, Enum as SAEnum
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from . import Base, TimestampMixin, UUIDMixin
import enum


class DocumentType(str, enum.Enum):
    RESUME = "resume"
    PORTFOLIO = "portfolio"


class DocumentStatus(str, enum.Enum):
    PENDING = "pending"
    PROCESSED = "processed"
    FAILED = "failed"


class User(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "users"

    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    name: Mapped[Optional[str]] = mapped_column(String(255))
    auth_provider_id: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    avatar_url: Mapped[Optional[str]] = mapped_column(Text)

    documents: Mapped[list["Document"]] = relationship(back_populates="user", cascade="all, delete-orphan")
    resume_profiles: Mapped[list["ResumeProfile"]] = relationship(back_populates="user", cascade="all, delete-orphan")
    outreach_messages: Mapped[list["OutreachMessage"]] = relationship(back_populates="user", cascade="all, delete-orphan")
    interactions: Mapped[list["Interaction"]] = relationship(back_populates="user", cascade="all, delete-orphan")
    notes: Mapped[list["Note"]] = relationship(back_populates="user", cascade="all, delete-orphan")


class Document(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "documents"

    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False)
    type: Mapped[DocumentType] = mapped_column(SAEnum(DocumentType), nullable=False)
    file_path: Mapped[str] = mapped_column(String(500), nullable=False)
    status: Mapped[DocumentStatus] = mapped_column(SAEnum(DocumentStatus), default=DocumentStatus.PENDING, nullable=False)
    metadata: Mapped[Optional[dict]] = mapped_column(JSONB)

    user: Mapped["User"] = relationship(back_populates="documents", foreign_keys=[user_id])


class ResumeProfile(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "resume_profiles"

    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), unique=True, nullable=False)
    skills: Mapped[list[str]] = mapped_column(JSONB, default=list)
    projects: Mapped[list[dict]] = mapped_column(JSONB, default=list)
    experience: Mapped[list[dict]] = mapped_column(JSONB, default=list)
    technologies: Mapped[list[str]] = mapped_column(JSONB, default=list)
    seniority: Mapped[Optional[str]] = mapped_column(String(100))
    preferred_roles: Mapped[list[str]] = mapped_column(JSONB, default=list)
    company_interests: Mapped[list[str]] = mapped_column(JSONB, default=list)
    raw_text: Mapped[Optional[str]] = mapped_column(Text)

    user: Mapped["User"] = relationship(back_populates="resume_profiles", foreign_keys=[user_id])


class Company(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "companies"

    name: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    domain: Mapped[Optional[str]] = mapped_column(String(255))
    description: Mapped[Optional[str]] = mapped_column(Text)
    metadata: Mapped[Optional[dict]] = mapped_column(JSONB)

    profiles: Mapped[list["CompanyProfile"]] = relationship(back_populates="company", cascade="all, delete-orphan")
    people: Mapped[list["Person"]] = relationship(back_populates="company", cascade="all, delete-orphan")
    jobs: Mapped[list["Job"]] = relationship(back_populates="company", cascade="all, delete-orphan")


class CompanyProfile(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "company_profiles"

    company_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), unique=True, nullable=False)
    overview: Mapped[Optional[str]] = mapped_column(Text)
    tech_stack: Mapped[list[str]] = mapped_column(JSONB, default=list)
    products: Mapped[list[dict]] = mapped_column(JSONB, default=list)
    engineering_blog_url: Mapped[Optional[str]] = mapped_column(String(500))
    careers_page_url: Mapped[Optional[str]] = mapped_column(String(500))
    open_positions: Mapped[list[dict]] = mapped_column(JSONB, default=list)
    recent_news: Mapped[list[dict]] = mapped_column(JSONB, default=list)

    hiring_velocity: Mapped[Optional[dict]] = mapped_column(JSONB)
    backend_team_size: Mapped[Optional[int]]
    languages_used: Mapped[list[str]] = mapped_column(JSONB, default=list)
    hiring_manager_name: Mapped[Optional[str]] = mapped_column(String(255))
    recruiters: Mapped[list[dict]] = mapped_column(JSONB, default=list)
    interns: Mapped[list[dict]] = mapped_column(JSONB, default=list)
    ex_interns: Mapped[list[dict]] = mapped_column(JSONB, default=list)
    recent_promotions: Mapped[list[dict]] = mapped_column(JSONB, default=list)
    conference_talks: Mapped[list[dict]] = mapped_column(JSONB, default=list)
    interview_difficulty: Mapped[Optional[str]] = mapped_column(String(100))
    likely_interview_topics: Mapped[list[str]] = mapped_column(JSONB, default=list)
    interesting_github_repos: Mapped[list[dict]] = mapped_column(JSONB, default=list)
    org_chart_summary: Mapped[Optional[str]] = mapped_column(Text)

    company: Mapped["Company"] = relationship(back_populates="profiles", foreign_keys=[company_id])


class Person(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "people"

    company_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    role: Mapped[Optional[str]] = mapped_column(String(255))
    public_profile_url: Mapped[Optional[str]] = mapped_column(String(500))
    source: Mapped[Optional[str]] = mapped_column(String(100))
    summary: Mapped[Optional[str]] = mapped_column(Text)
    metadata: Mapped[Optional[dict]] = mapped_column(JSONB)

    team_id: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True))
    influence_score: Mapped[Optional[float]] = mapped_column(Float, default=0.0)
    response_probability: Mapped[Optional[float]] = mapped_column(Float, default=0.0)
    referral_probability: Mapped[Optional[float]] = mapped_column(Float, default=0.0)
    activity_score: Mapped[Optional[float]] = mapped_column(Float, default=0.0)
    expertise_areas: Mapped[list[str]] = mapped_column(JSONB, default=list)

    company: Mapped["Company"] = relationship(back_populates="people", foreign_keys=[company_id])
    profiles: Mapped[list["PersonProfile"]] = relationship(back_populates="person", cascade="all, delete-orphan")
    outreach_messages: Mapped[list["OutreachMessage"]] = relationship(back_populates="person", cascade="all, delete-orphan")
    interactions: Mapped[list["Interaction"]] = relationship(back_populates="person")


class PersonProfile(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "person_profiles"

    person_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), unique=True, nullable=False)
    embedding = None  # Added via pgvector DDL
    ranking_factors: Mapped[Optional[dict]] = mapped_column(JSONB)
    score: Mapped[Optional[float]]
    explanation: Mapped[Optional[str]] = mapped_column(Text)

    person: Mapped["Person"] = relationship(back_populates="profiles", foreign_keys=[person_id])


class Job(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "jobs"

    company_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text)
    url: Mapped[Optional[str]] = mapped_column(String(500))
    source: Mapped[Optional[str]] = mapped_column(String(100))
    skills: Mapped[list[str]] = mapped_column(JSONB, default=list)
    metadata: Mapped[Optional[dict]] = mapped_column(JSONB)

    required_skills: Mapped[list[str]] = mapped_column(JSONB, default=list)
    nice_to_have_skills: Mapped[list[str]] = mapped_column(JSONB, default=list)
    missing_skills: Mapped[list[str]] = mapped_column(JSONB, default=list)
    resume_match_score: Mapped[Optional[float]] = mapped_column(Float)
    strengths: Mapped[list[str]] = mapped_column(JSONB, default=list)
    weaknesses: Mapped[list[str]] = mapped_column(JSONB, default=list)
    people_to_contact: Mapped[list[dict]] = mapped_column(JSONB, default=list)
    projects_to_mention: Mapped[list[str]] = mapped_column(JSONB, default=list)
    likely_interview_topics: Mapped[list[str]] = mapped_column(JSONB, default=list)
    interview_difficulty: Mapped[Optional[str]] = mapped_column(String(50))

    company: Mapped["Company"] = relationship(back_populates="jobs", foreign_keys=[company_id])


class RelationshipType(str, enum.Enum):
    REPORTS_TO = "reports_to"
    WORKS_WITH = "works_with"
    SAME_TEAM = "same_team"
    SAME_PROJECT = "same_project"
    MENTORS = "mentors"
    PEER = "peer"
    MANAGER = "manager"
    INTERN = "intern"
    RECRUITER = "recruiter"
    HIRING_MANAGER = "hiring_manager"


class OrgTeam(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "org_teams"

    company_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    parent_team_id: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True))
    description: Mapped[Optional[str]] = mapped_column(Text)
    metadata: Mapped[Optional[dict]] = mapped_column(JSONB)


class OrgRelationship(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "org_relationships"

    company_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False)
    person_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False)
    related_person_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False)
    relationship_type: Mapped[RelationshipType] = mapped_column(SAEnum(RelationshipType), nullable=False)
    team_name: Mapped[Optional[str]] = mapped_column(String(255))
    confidence: Mapped[Optional[float]] = mapped_column(Float, default=0.5)
    metadata: Mapped[Optional[dict]] = mapped_column(JSONB)


class MessageType(str, enum.Enum):
    CONNECTION_REQUEST = "connection_request"
    DM = "dm"
    REFERRAL_REQUEST = "referral_request"
    FOLLOW_UP = "follow_up"
    THANK_YOU = "thank_you"


class MessageStatus(str, enum.Enum):
    DRAFT = "draft"
    REVIEWED = "reviewed"
    SENT = "sent"
    ARCHIVED = "archived"


class OutreachMessage(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "outreach_messages"

    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False)
    person_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False)
    job_id: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True))
    message_type: Mapped[MessageType] = mapped_column(SAEnum(MessageType), nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    status: Mapped[MessageStatus] = mapped_column(SAEnum(MessageStatus), default=MessageStatus.DRAFT)

    user: Mapped["User"] = relationship(back_populates="outreach_messages", foreign_keys=[user_id])
    person: Mapped["Person"] = relationship(back_populates="outreach_messages", foreign_keys=[person_id])


class InteractionAction(str, enum.Enum):
    VIEWED = "viewed"
    SAVED = "saved"
    COPIED = "copied"
    SENT = "sent"
    BOOKMARKED = "bookmarked"


class Interaction(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "interactions"

    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False)
    person_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False)
    action: Mapped[InteractionAction] = mapped_column(SAEnum(InteractionAction), nullable=False)
    notes: Mapped[Optional[str]] = mapped_column(Text)

    user: Mapped["User"] = relationship(back_populates="interactions", foreign_keys=[user_id])
    person: Mapped["Person"] = relationship(back_populates="interactions", foreign_keys=[person_id])


class Note(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "notes"

    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False)
    person_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)

    user: Mapped["User"] = relationship(back_populates="notes", foreign_keys=[user_id])


class Embedding(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "embeddings"

    resource_type: Mapped[str] = mapped_column(String(100), nullable=False)
    resource_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False)
    embedding = None
    metadata: Mapped[Optional[dict]] = mapped_column(JSONB)


class ResumeMatch(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "resume_matches"

    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False)
    job_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False)
    overall_score: Mapped[Optional[float]] = mapped_column(Float)
    skill_matches: Mapped[list[dict]] = mapped_column(JSONB, default=list)
    strengths: Mapped[list[str]] = mapped_column(JSONB, default=list)
    weaknesses: Mapped[list[str]] = mapped_column(JSONB, default=list)
    mention_projects: Mapped[list[str]] = mapped_column(JSONB, default=list)
    avoid_mentioning: Mapped[list[str]] = mapped_column(JSONB, default=list)
    recommendation: Mapped[Optional[str]] = mapped_column(Text)
