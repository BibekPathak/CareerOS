// ============================================================
// CareerOS — API Type Definitions
// Matches all backend response schemas
// ============================================================

// --- Resume ---
export interface ResumeProfile {
  id: string
  skills: string[]
  projects: Project[]
  experience: Experience[]
  technologies: string[]
  seniority: string | null
  preferred_roles: string[]
  company_interests: string[]
  created_at: string
  updated_at: string
}

export interface Project {
  name: string
  description: string
  technologies: string[]
  url?: string | null
}

export interface Experience {
  company: string
  role: string
  duration: string
  description: string
  technologies: string[]
}

// --- Company ---
export interface Company {
  id: string
  name: string
  domain: string | null
  description: string | null
  created_at: string
}

export interface CompanyProfile {
  id: string
  company_id: string
  overview: string | null
  tech_stack: string[]
  products: Record<string, unknown>[]
  engineering_blog_url: string | null
  careers_page_url: string | null
  open_positions: Record<string, unknown>[]
  recent_news: Record<string, unknown>[]
  hiring_velocity: Record<string, unknown> | null
  backend_team_size: number | null
  languages_used: string[]
  hiring_manager_name: string | null
  recruiters: Record<string, unknown>[]
  interns: Record<string, unknown>[]
  ex_interns: Record<string, unknown>[]
  recent_promotions: Record<string, unknown>[]
  conference_talks: Record<string, unknown>[]
  interview_difficulty: string | null
  likely_interview_topics: string[]
  interesting_github_repos: Record<string, unknown>[]
  org_chart_summary: string | null
  created_at: string
}

export interface CompanyDetail {
  company: Company
  profile: CompanyProfile | null
  people_count: number
  jobs_count: number
}

// --- People ---
export interface Person {
  id: string
  name: string
  role: string | null
  public_profile_url: string | null
  source: string | null
  summary: string | null
  score: number | null
  explanation: string | null
}

// --- Jobs ---
export interface Job {
  id: string
  company_id: string
  title: string
  description: string | null
  url: string | null
  source: string | null
  skills: string[]
  created_at: string
}

export interface JobAnalysis {
  id: string
  required_skills: string[]
  nice_to_have_skills: string[]
  missing_skills: string[]
  resume_match_score: number | null
  strengths: string[]
  weaknesses: string[]
  people_to_contact: Record<string, unknown>[]
  projects_to_mention: string[]
  likely_interview_topics: string[]
  interview_difficulty: string | null
}

export interface JobDetail {
  job: Job
  analysis: JobAnalysis | null
}

// --- Outreach ---
export interface OutreachMessage {
  id: string
  message_type: string
  content: string
  status: string
  created_at: string
}

export interface OutreachIntelligence {
  id: string
  person_id: string
  best_conversation_starters: string[]
  topics_to_avoid: string[]
  person_interests: string[]
  response_approach: string | null
  optimal_send_time: string | null
  referral_readiness: string | null
}

// --- Graph ---
export interface OrgGraph {
  teams: OrgTeam[]
  relationships: OrgRelationship[]
  people: GraphPerson[]
}

export interface OrgTeam {
  id: string
  company_id: string
  name: string
  parent_team_id: string | null
  description: string | null
}

export interface OrgRelationship {
  id: string
  person_id: string
  related_person_id: string
  relationship_type: string
  team_name: string | null
  confidence: number
}

export interface GraphPerson {
  id: string
  name: string
  role: string | null
  team_id: string | null
  influence_score: number
  activity_score: number
  response_probability: number
  referral_probability: number
  expertise_areas: string[]
}

// --- Resume Match ---
export interface ResumeMatch {
  id: string
  overall_score: number
  skill_matches: SkillMatch[]
  strengths: string[]
  weaknesses: string[]
  mention_projects: string[]
  avoid_mentioning: string[]
  recommendation: string
}

export interface SkillMatch {
  skill: string
  status: "satisfied" | "partial" | "missing"
  importance: "required" | "nice_to_have"
  suggestion: string | null
}

// --- Memory / Timeline ---
export interface ConversationEvent {
  id: string
  person_id: string
  event_type: string
  event_data: Record<string, unknown> | null
  created_at: string
}

export interface FollowUpSuggestion {
  id: string
  person_id: string
  suggestion_type: string
  reasoning: string | null
  suggested_message: string | null
  urgency: string
  is_read: boolean
  created_at: string
}

export interface Timeline {
  events: ConversationEvent[]
  suggestions: FollowUpSuggestion[]
}

// --- Career Goals ---
export interface PlanStep {
  id: string
  phase: string
  action: string
  tool: string
  input: Record<string, unknown>
  output: Record<string, unknown> | null
  status: string
  reasoning: string
  deadline: string | null
}

export interface CareerGoal {
  id: string
  title: string
  target_company: string | null
  target_role: string | null
  deadline: string | null
  priority: string
  status: string
  plan: PlanStep[]
  current_step_index: number
  progress_metrics: Record<string, unknown> | null
  created_at: string
  updated_at: string
}

export interface GoalEvent {
  id: string
  goal_id: string
  event_type: string
  event_data: Record<string, unknown> | null
  created_at: string
}

// --- Daily / Mission ---
export interface DailyBrief {
  id: string
  date: string
  summary: string | null
  items: Record<string, unknown>[]
  is_read: boolean
  created_at: string
}

export interface MissionAction {
  type: string
  target: string
  detail: string
  deadline: string
  urgency: string
}

export interface GoalMission {
  goal_title: string
  actions: MissionAction[]
  focus: string
  progress: string
}

export interface TodaysMission {
  goals: GoalMission[]
  summary_stats: Record<string, unknown>
}

// --- Knowledge Graph ---
export interface KGEntity {
  id: string
  type: string
  name: string
  metadata: Record<string, unknown> | null
}

export interface KGNeighbor {
  entity: KGEntity
  edge: { type: string; weight: number }
}

export interface KGPath {
  path: KGPathHop[]
  length: number
  explanation: string | null
}

export interface KGPathHop {
  from: { id?: string; type?: string; name?: string }
  to: { id?: string; type?: string; name?: string }
  via: string
}

// --- Stats ---
export interface CareerStats {
  goals: { total: number; active: number; completed: number; paused: number }
  outreach: { total_messages: number; sent: number; drafts: number; unique_people_contacted: number }
  companies: { total_tracked: number }
  summary: string
}

// --- Extension ---
export interface ExtensionIntelligence {
  matchScore: number | null
  likelyInterviewer: boolean | null
  hiringManager: boolean | null
  recruiter: boolean | null
  conversationStarters: string[]
  topicsToAvoid: string[]
  sharedInterests: string[]
  bestProject: string | null
  suggestedMessage: string | null
  personId?: string
  companyId?: string
  note?: string
}
