from pydantic import BaseModel


class ResumeInput(BaseModel):
    raw_text: str


class Project(BaseModel):
    name: str
    description: str
    technologies: list[str]
    url: str | None = None


class Experience(BaseModel):
    company: str
    role: str
    duration: str
    description: str
    technologies: list[str]


class ResumeOutput(BaseModel):
    skills: list[str]
    projects: list[Project]
    experience: list[Experience]
    technologies: list[str]
    seniority: str
    preferred_roles: list[str]
    company_interests: list[str]


class CompanyResearchInput(BaseModel):
    company_name: str


class Product(BaseModel):
    name: str
    description: str


class OpenPosition(BaseModel):
    title: str
    url: str | None = None


class NewsItem(BaseModel):
    title: str
    url: str | None = None
    summary: str


class HiringVelocity(BaseModel):
    rate: str
    roles_per_month: float | None = None
    team_growth_trend: str | None = None
    recent_hiring_signal: str | None = None


class Recruiter(BaseModel):
    name: str
    role: str
    profile_url: str | None = None
    focus_area: str | None = None


class Intern(BaseModel):
    name: str
    role: str
    duration: str | None = None
    source: str | None = None


class Promotion(BaseModel):
    person_name: str
    previous_role: str
    new_role: str
    date: str | None = None
    source: str | None = None


class ConferenceTalk(BaseModel):
    title: str
    conference: str
    speaker: str
    year: str | None = None
    url: str | None = None


class GitHubRepo(BaseModel):
    name: str
    description: str | None = None
    language: str | None = None
    stars: int | None = None
    url: str | None = None


class CompanyIntelligence(BaseModel):
    overview: str
    tech_stack: list[str]
    products: list[Product]
    engineering_blog_url: str | None = None
    careers_page_url: str | None = None
    open_positions: list[OpenPosition]
    recent_news: list[NewsItem]

    hiring_velocity: HiringVelocity | None = None
    backend_team_size: int | None = None
    languages_used: list[str] = []
    hiring_manager_name: str | None = None
    recruiters: list[Recruiter] = []
    interns: list[Intern] = []
    ex_interns: list[Intern] = []
    recent_promotions: list[Promotion] = []
    conference_talks: list[ConferenceTalk] = []
    interview_difficulty: str | None = None
    likely_interview_topics: list[str] = []
    interesting_github_repos: list[GitHubRepo] = []
    org_chart_summary: str | None = None


CompanyProfile = CompanyIntelligence


class PeopleDiscoveryInput(BaseModel):
    company_name: str
    company_domain: str | None = None


class Person(BaseModel):
    name: str
    role: str | None = None
    public_profile_url: str | None = None
    source: str
    summary: str


class PeopleDiscoveryOutput(BaseModel):
    people: list[Person]


class RankingInput(BaseModel):
    company_name: str
    resume: ResumeOutput
    people: list[Person]
    target_role: str | None = None


class RankedPerson(BaseModel):
    name: str
    score: float
    explanation: str
    hiring_influence_score: float
    technical_similarity_score: float
    team_relevance_score: float


class RankingOutput(BaseModel):
    ranked_people: list[RankedPerson]


class OutreachInput(BaseModel):
    resume: ResumeOutput
    target_person: RankedPerson
    person_summary: str
    company_name: str
    target_role: str | None = None


class MessageSet(BaseModel):
    connection_request: str
    dm: str
    referral_request: str
    follow_up: str
    thank_you: str


class OutreachOutput(BaseModel):
    messages: MessageSet


class RelationshipEdge(BaseModel):
    person_id: str
    related_person_id: str
    relationship_type: str
    team_name: str | None = None
    confidence: float = 0.5


class OrgTeamNode(BaseModel):
    id: str | None = None
    name: str
    parent_team_id: str | None = None
    description: str | None = None


class GraphPerson(BaseModel):
    id: str | None = None
    name: str
    role: str | None = None
    team_id: str | None = None
    influence_score: float = 0.0
    activity_score: float = 0.0
    response_probability: float = 0.0
    referral_probability: float = 0.0
    expertise_areas: list[str] = []


class OrgGraphInput(BaseModel):
    company_name: str
    people: list[GraphPerson]
    company_profile: CompanyIntelligence | None = None


class OrgGraphOutput(BaseModel):
    teams: list[OrgTeamNode]
    relationships: list[RelationshipEdge]
    people: list[GraphPerson]


class PersonToContact(BaseModel):
    name: str
    role: str | None = None
    reason: str


class JobAnalysisInput(BaseModel):
    job_title: str
    job_description: str
    company_name: str
    resume: ResumeOutput
    context: str | None = None


class JobAnalysisOutput(BaseModel):
    required_skills: list[str]
    nice_to_have_skills: list[str]
    missing_skills: list[str]
    resume_match_score: float
    strengths: list[str]
    weaknesses: list[str]
    people_to_contact: list[PersonToContact]
    projects_to_mention: list[str]
    likely_interview_topics: list[str]
    interview_difficulty: str


class SkillMatch(BaseModel):
    skill: str
    status: str
    importance: str
    suggestion: str | None = None


class ResumeMatchInput(BaseModel):
    job_title: str
    job_description: str
    job_skills: list[str]
    company_name: str
    resume: ResumeOutput


class ResumeMatchOutput(BaseModel):
    overall_score: float
    skill_matches: list[SkillMatch]
    strengths: list[str]
    weaknesses: list[str]
    mention_projects: list[str]
    avoid_mentioning: list[str]
    recommendation: str


class OutreachIntelligenceInput(BaseModel):
    person_name: str
    person_role: str | None = None
    person_summary: str
    expertise_areas: list[str] = []
    company_name: str
    resume: ResumeOutput


class OutreachIntelligenceOutput(BaseModel):
    best_conversation_starters: list[str]
    topics_to_avoid: list[str]
    person_interests: list[str]
    response_approach: str
    optimal_send_time: str
    referral_readiness: str


class ConversationEvent(BaseModel):
    person_id: str
    event_type: str
    event_data: dict | None = None


class TimelineEntry(BaseModel):
    event_type: str
    event_data: dict | None = None
    timestamp: str


class MemoryAnalysisInput(BaseModel):
    person_name: str
    timeline: list[TimelineEntry]
    recent_activity: str | None = None


class MemoryAnalysisOutput(BaseModel):
    should_follow_up: bool
    reasoning: str
    timing_suggestion: str
    suggested_message: str | None = None
    urgency: str


class FollowUpSuggestionOut(BaseModel):
    id: str | None = None
    person_name: str
    suggestion_type: str
    reasoning: str
    suggested_message: str | None = None
    urgency: str
    is_read: bool


class BriefItem(BaseModel):
    type: str
    title: str
    description: str
    person_name: str | None = None
    company_name: str | None = None
    url: str | None = None
    urgency: str = "medium"


class DailyBriefInput(BaseModel):
    user_id: str
    new_jobs: list[dict] = []
    recruiter_changes: list[dict] = []
    engagement_signals: list[dict] = []
    follow_ups_due: list[dict] = []
    company_news: list[dict] = []


class DailyBriefOutput(BaseModel):
    summary: str
    items: list[BriefItem]


class PlanStep(BaseModel):
    id: str
    phase: str
    action: str
    tool: str
    input: dict = {}
    output: dict | None = None
    status: str = "pending"
    reasoning: str = ""
    deadline: str | None = None


class CareerGoalInput(BaseModel):
    title: str
    target_company: str | None = None
    target_role: str | None = None
    deadline: str | None = None
    priority: str = "medium"
    context: str | None = None


class CareerPlanOutput(BaseModel):
    title: str
    plan: list[PlanStep]
    summary: str
    estimated_duration: str | None = None


class GoalCreateResponse(BaseModel):
    id: str
    title: str
    plan: list[PlanStep]
    summary: str


class KnowledgeEntity(BaseModel):
    id: str | None = None
    type: str
    name: str
    metadata: dict | None = None


class KnowledgeEdge(BaseModel):
    source_id: str
    target_id: str
    relationship_type: str
    weight: float = 1.0
    metadata: dict | None = None


class KnowledgeGraphQuery(BaseModel):
    entity_type: str | None = None
    entity_name: str | None = None
    relationship_type: str | None = None
    max_depth: int = 2


class KnowledgePath(BaseModel):
    path: list[dict]
    length: int
    explanation: str | None = None


__all__ = [
    "ResumeInput", "ResumeOutput", "Project", "Experience",
    "CompanyResearchInput", "CompanyIntelligence", "CompanyProfile",
    "Product", "OpenPosition", "NewsItem",
    "HiringVelocity", "Recruiter", "Intern", "Promotion",
    "ConferenceTalk", "GitHubRepo",
    "PeopleDiscoveryInput", "Person", "PeopleDiscoveryOutput",
    "RankingInput", "RankedPerson", "RankingOutput",
    "OutreachInput", "MessageSet", "OutreachOutput",
    "RelationshipEdge", "OrgTeamNode", "GraphPerson",
    "OrgGraphInput", "OrgGraphOutput",
    "PersonToContact", "JobAnalysisInput", "JobAnalysisOutput",
    "SkillMatch", "ResumeMatchInput", "ResumeMatchOutput",
    "OutreachIntelligenceInput", "OutreachIntelligenceOutput",
    "ConversationEvent", "TimelineEntry",
    "MemoryAnalysisInput", "MemoryAnalysisOutput", "FollowUpSuggestionOut",
    "BriefItem", "DailyBriefInput", "DailyBriefOutput",
    "PlanStep", "CareerGoalInput", "CareerPlanOutput", "GoalCreateResponse",
    "KnowledgeEntity", "KnowledgeEdge",
]
