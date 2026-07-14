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


__all__ = [
    "ResumeInput", "ResumeOutput", "Project", "Experience",
    "CompanyResearchInput", "CompanyIntelligence", "CompanyProfile",
    "Product", "OpenPosition", "NewsItem",
    "HiringVelocity", "Recruiter", "Intern", "Promotion",
    "ConferenceTalk", "GitHubRepo",
    "PeopleDiscoveryInput", "Person", "PeopleDiscoveryOutput",
    "RankingInput", "RankedPerson", "RankingOutput",
    "OutreachInput", "MessageSet", "OutreachOutput",
]
