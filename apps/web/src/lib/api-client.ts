// ============================================================
// CareerOS — Typed API Client
// ============================================================

import type {
  ResumeProfile,
  CompanyDetail,
  Company,
  Person,
  Job,
  JobDetail,
  OutreachMessage,
  OutreachIntelligence,
  OrgGraph,
  ResumeMatch,
  Timeline,
  CareerGoal,
  GoalEvent,
  DailyBrief,
  TodaysMission,
  CareerStats,
  KGEntity,
  KGNeighbor,
  KGPath,
  ExtensionIntelligence,
  ConversationEvent,
} from "@/types/api"

const BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api/v1"
const DEFAULT_USER = "00000000-0000-0000-0000-000000000001"

class ApiError extends Error {
  constructor(public status: number, message: string) {
    super(message)
    this.name = "ApiError"
  }
}

async function request<T>(path: string, options: RequestInit = {}): Promise<T> {
  const url = `${BASE_URL}${path}`
  const res = await fetch(url, {
    headers: { "Content-Type": "application/json", ...options.headers },
    ...options,
  })
  if (!res.ok) {
    const body = await res.text().catch(() => "")
    throw new ApiError(res.status, body || `API error: ${res.status}`)
  }
  return res.json()
}

function qs(params: Record<string, string | number | boolean | undefined>): string {
  const entries = Object.entries(params).filter(([, v]) => v !== undefined)
  if (!entries.length) return ""
  return "?" + entries.map(([k, v]) => `${k}=${encodeURIComponent(String(v))}`).join("&")
}

// Helper to get or create a consistent user ID for demo purposes
function uid(): string {
  if (typeof window !== "undefined") {
    try {
      const stored = sessionStorage.getItem("careeros_user_id")
      if (stored) return stored
    } catch {}
  }
  return DEFAULT_USER
}

export const api = {
  // ==================== Resume ====================
  async uploadResume(file: File): Promise<{ id: string; status: string; message: string }> {
    const formData = new FormData()
    formData.append("file", file)
    const url = `${BASE_URL}/resume/upload`
    const res = await fetch(url, { method: "POST", body: formData })
    if (!res.ok) throw new ApiError(res.status, await res.text())
    return res.json()
  },

  getResume: (userId?: string) =>
    request<ResumeProfile>(`/resume/${userId || uid()}`),

  // ==================== Company ====================
  researchCompany: (companyName: string) =>
    request<CompanyDetail>("/company/research", {
      method: "POST",
      body: JSON.stringify({ company_name: companyName }),
    }),

  getCompany: (id: string) =>
    request<CompanyDetail>(`/company/${id}`),

  getCompanyIntelligence: (id: string) =>
    request<CompanyDetail>(`/company/${id}/intelligence`, { method: "POST" }),

  searchCompanies: (query: string) =>
    request<Company[]>(`/company/search/${encodeURIComponent(query)}`),

  // ==================== People ====================
  discoverPeople: (companyId: string) =>
    request<{ discovered: number; new: number; total: number }>("/people/discover", {
      method: "POST",
      body: JSON.stringify({ company_id: companyId }),
    }),

  rankPeople: (companyId: string, userId?: string) =>
    request<{ ranked: Person[] }>("/people/rank", {
      method: "POST",
      body: JSON.stringify({ company_id: companyId, user_id: userId || uid() }),
    }),

  getPeople: (companyId: string) =>
    request<Person[]>(`/people/${companyId}`),

  getPerson: (companyId: string, personId: string) =>
    request<Person>(`/people/${companyId}/${personId}`),

  // ==================== Outreach ====================
  generateOutreach: (userId: string, personId: string, companyId: string, targetRole?: string) =>
    request<{ messages: OutreachMessage[]; intelligence: OutreachIntelligence | null }>(
      "/outreach/generate",
      {
        method: "POST",
        body: JSON.stringify({ user_id: userId, person_id: personId, company_id: companyId, target_role: targetRole }),
      }
    ),

  getMessages: (personId: string) =>
    request<OutreachMessage[]>(`/outreach/${personId}`),

  getOutreachIntelligence: (personId: string) =>
    request<OutreachIntelligence>(`/outreach/intelligence/${personId}`),

  // ==================== Graph ====================
  buildGraph: (companyId: string) =>
    request<{ status: string; teams: number; relationships: number; people_with_graph: number }>(
      `/graph/build/${companyId}`,
      { method: "POST" }
    ),

  getGraph: (companyId: string) =>
    request<OrgGraph>(`/graph/${companyId}`),

  findPath: (companyId: string, fromPersonId: string, toPersonId: string) =>
    request<{ path: unknown[]; length: number }>(
      `/graph/path/${companyId}${qs({ from_person_id: fromPersonId, to_person_id: toPersonId })}`
    ),

  recommendConnector: (companyId: string, targetPersonId: string) =>
    request<{ connectors: unknown[] }>(
      `/graph/recommend-connector/${companyId}${qs({ target_person_id: targetPersonId })}`
    ),

  // ==================== Jobs ====================
  getJobs: (companyId: string) =>
    request<Job[]>(`/job/company/${companyId}`),

  getJob: (jobId: string) =>
    request<JobDetail>(`/job/${jobId}`),

  analyzeJob: (jobId: string, userId?: string) =>
    request<JobDetail>(
      `/job/${jobId}/analyze${qs({ user_id: userId || uid() })}`,
      { method: "POST" }
    ),

  // ==================== Resume Match ====================
  matchResume: (jobId: string, userId?: string) =>
    request<ResumeMatch>(
      `/resume/match/${jobId}${qs({ user_id: userId || uid() })}`,
      { method: "POST" }
    ),

  getMatch: (jobId: string, userId?: string) =>
    request<ResumeMatch>(
      `/resume/match/${jobId}${qs({ user_id: userId || uid() })}`
    ),

  // ==================== Memory ====================
  logEvent: (userId: string, personId: string, eventType: string, eventData?: Record<string, unknown>) =>
    request<ConversationEvent>("/memory/event", {
      method: "POST",
      body: JSON.stringify({ user_id: userId, person_id: personId, event_type: eventType, event_data: eventData }),
    }),

  getTimeline: (personId: string) =>
    request<Timeline>(`/memory/timeline/${personId}`),

  analyzeMemory: (personId: string, userId: string, recentActivity?: string) =>
    request<{ should_follow_up: boolean; reasoning: string; timing_suggestion: string; suggested_message: string | null; urgency: string }>(
      `/memory/analyze/${personId}${qs({ user_id: userId, recent_activity: recentActivity })}`,
      { method: "POST" }
    ),

  // ==================== Goals ====================
  createGoal: (data: { user_id: string; title: string; target_company?: string; target_role?: string; deadline?: string; priority?: string; context?: string }) =>
    request<{ goal: CareerGoal; plan_summary: string }>("/goal/create", {
      method: "POST",
      body: JSON.stringify(data),
    }),

  getGoal: (id: string) =>
    request<CareerGoal>(`/goal/${id}`),

  getGoals: (userId: string, activeOnly?: boolean) =>
    request<CareerGoal[]>(`/goal/user/${userId}${qs({ active_only: activeOnly })}`),

  advanceGoal: (id: string) =>
    request<void>(`/goal/${id}/advance`, { method: "POST" }),

  updateGoalStatus: (id: string, status: string) =>
    request<void>(`/goal/${id}/status${qs({ status })}`, { method: "POST" }),

  getGoalEvents: (id: string) =>
    request<GoalEvent[]>(`/goal/${id}/events`),

  // ==================== Daily / Mission ====================
  getDailyBrief: (userId: string) =>
    request<DailyBrief | null>(`/daily/today/${userId}`),

  generateDailyBrief: (userId: string) =>
    request<{ brief: DailyBrief; generated: boolean }>(`/daily/generate/${userId}`, { method: "POST" }),

  generateMission: (userId: string) =>
    request<TodaysMission>(`/daily/mission/${userId}`, { method: "POST" }),

  // ==================== Stats ====================
  getStats: (userId: string) =>
    request<CareerStats>(`/stats/career/${userId}`),

  // ==================== Knowledge Graph ====================
  findKGEntities: (type?: string, name?: string) =>
    request<KGEntity[]>(`/kg/entities${qs({ type, name })}`),

  getKGNeighbors: (entityId: string, relationshipType?: string, depth?: number) =>
    request<{ entity_id: string; neighbors: KGNeighbor[]; count: number }>(
      `/kg/neighbors/${entityId}${qs({ relationship_type: relationshipType, depth })}`
    ),

  findKGPath: (fromType: string, fromName: string, toType: string, toName: string, maxDepth?: number) =>
    request<KGPath>(
      `/kg/path${qs({ from_type: fromType, from_name: fromName, to_type: toType, to_name: toName, max_depth: maxDepth })}`
    ),

  populateKG: (companyId: string) =>
    request<{ company: string; entities_created: number }>(`/kg/populate/${companyId}`, { method: "POST" }),

  // ==================== Extension ====================
  getExtensionIntelligence: (personName: string, companyName: string, personRole?: string, userId?: string) =>
    request<ExtensionIntelligence>("/extension/intelligence", {
      method: "POST",
      body: JSON.stringify({ person_name: personName, person_role: personRole, company_name: companyName, user_id: userId }),
    }),
}
