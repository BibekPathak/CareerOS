"use client"

import { useEffect, useState, useCallback } from "react"
import { useParams } from "next/navigation"
import { api } from "@/lib/api-client"
import type { CompanyDetail, Person } from "@/types/api"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { Button } from "@/components/ui/button"
import { Skeleton } from "@/components/ui/skeleton"
import {
  Building2, Globe, Users, Briefcase, GraduationCap,
  ExternalLink, Beaker, ScrollText, RefreshCw, GitBranch,
} from "lucide-react"
import Link from "next/link"
import { cn } from "@/lib/utils"

export default function CompanyDetailPage() {
  const params = useParams()
  const companyId = params.id as string
  const [detail, setDetail] = useState<CompanyDetail | null>(null)
  const [people, setPeople] = useState<Person[]>([])
  const [loading, setLoading] = useState(true)
  const [researching, setResearching] = useState(false)

  const load = useCallback(async () => {
    setLoading(true)
    try {
      const [d, p] = await Promise.all([
        api.getCompany(companyId),
        api.getPeople(companyId).catch<Person[]>(() => []),
      ])
      setDetail(d)
      setPeople(p)
    } catch {}
    setLoading(false)
  }, [companyId])

  useEffect(() => { load() }, [load])

  const handleResearch = async () => {
    setResearching(true)
    try {
      const d = await api.researchCompany(detail?.company.name || "")
      setDetail(d)
      const p = await api.getPeople(companyId).catch<Person[]>(() => [])
      setPeople(p)
    } catch {}
    setResearching(false)
  }

  if (loading) {
    return (
      <div className="space-y-6">
        <Skeleton className="h-10 w-64" />
        <Skeleton className="h-8 w-96" />
        <Skeleton className="h-64 w-full rounded-lg" />
      </div>
    )
  }

  if (!detail) {
    return (
      <div className="space-y-6">
        <h1 className="text-3xl font-bold tracking-tight">Company not found</h1>
        <p className="text-muted-foreground">The company you're looking for doesn't exist or hasn't been researched yet.</p>
        <Button asChild><Link href="/companies">Back to Companies</Link></Button>
      </div>
    )
  }

  const { company, profile } = detail
  const hasProfile = !!profile

  return (
    <div className="space-y-6">
      <div className="flex items-start justify-between">
        <div className="flex items-center gap-3">
          <div className="flex h-12 w-12 items-center justify-center rounded-xl bg-primary/10">
            <Building2 className="h-6 w-6 text-primary" />
          </div>
          <div>
            <h1 className="text-2xl font-bold">{company.name}</h1>
            <div className="flex items-center gap-2 mt-0.5">
              {company.domain && (
                <span className="text-sm text-muted-foreground">{company.domain}</span>
              )}
              {hasProfile && profile?.interview_difficulty && (
                <Badge variant="outline" className="text-xs">{profile.interview_difficulty}</Badge>
              )}
            </div>
          </div>
        </div>
        <Button
          variant="outline"
          size="sm"
          onClick={handleResearch}
          disabled={researching}
          className="gap-1.5"
        >
          <RefreshCw className={cn("h-3.5 w-3.5", researching && "animate-spin")} />
          {researching ? "Researching..." : "Research"}
        </Button>
      </div>

      {hasProfile && profile && (
        <Tabs defaultValue="overview">
          <TabsList>
            <TabsTrigger value="overview">Overview</TabsTrigger>
            <TabsTrigger value="people">People ({people.length})</TabsTrigger>
            <TabsTrigger value="jobs">Jobs ({detail.jobs_count})</TabsTrigger>
            <TabsTrigger value="interview">Interview</TabsTrigger>
          </TabsList>

          <TabsContent value="overview" className="space-y-4 mt-4">
            {profile.overview && (
              <Card>
                <CardHeader><CardTitle className="text-sm">Overview</CardTitle></CardHeader>
                <CardContent><p className="text-sm text-muted-foreground">{profile.overview}</p></CardContent>
              </Card>
            )}

            <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
              {profile.tech_stack.length > 0 && (
                <Card>
                  <CardHeader className="pb-2"><CardTitle className="text-xs flex items-center gap-1.5"><Beaker className="h-3.5 w-3.5" /> Tech Stack</CardTitle></CardHeader>
                  <CardContent><div className="flex flex-wrap gap-1">{profile.tech_stack.map((t) => <Badge key={t} variant="secondary" className="text-[10px]">{t}</Badge>)}</div></CardContent>
                </Card>
              )}
              {profile.languages_used.length > 0 && (
                <Card>
                  <CardHeader className="pb-2"><CardTitle className="text-xs flex items-center gap-1.5"><ScrollText className="h-3.5 w-3.5" /> Languages</CardTitle></CardHeader>
                  <CardContent><div className="flex flex-wrap gap-1">{profile.languages_used.map((l) => <Badge key={l} variant="outline" className="text-[10px]">{l}</Badge>)}</div></CardContent>
                </Card>
              )}
              {profile.hiring_velocity && (
                <Card>
                  <CardHeader className="pb-2"><CardTitle className="text-xs flex items-center gap-1.5"><GraduationCap className="h-3.5 w-3.5" /> Hiring Velocity</CardTitle></CardHeader>
                  <CardContent>{
                    (() => {
                      const hv = profile.hiring_velocity as any
                      const rate = hv?.rate || "Unknown"
                      return (
                        <Badge variant={rate === "high" ? "success" : rate === "medium" ? "warning" : "secondary"} className="text-xs">{rate}</Badge>
                      )
                    })()
                  }</CardContent>
                </Card>
              )}
              {profile.backend_team_size && (
                <Card>
                  <CardHeader className="pb-2"><CardTitle className="text-xs">Backend Team Size</CardTitle></CardHeader>
                  <CardContent><p className="text-2xl font-bold">{profile.backend_team_size}</p></CardContent>
                </Card>
              )}
              {profile.recruiters && profile.recruiters.length > 0 && (
                <Card>
                  <CardHeader className="pb-2"><CardTitle className="text-xs">Recruiters</CardTitle></CardHeader>
                  <CardContent>
                    <div className="space-y-1">
                      {profile.recruiters.slice(0, 3).map((r: any, i: number) => (
                        <p key={i} className="text-xs text-muted-foreground">{r.name} — {r.role}</p>
                      ))}
                    </div>
                  </CardContent>
                </Card>
              )}
              {profile.hiring_manager_name && (
                <Card>
                  <CardHeader className="pb-2"><CardTitle className="text-xs">Hiring Manager</CardTitle></CardHeader>
                  <CardContent><p className="text-sm font-medium">{profile.hiring_manager_name}</p></CardContent>
                </Card>
              )}
            </div>

            {profile.recent_news && profile.recent_news.length > 0 && (
              <Card>
                <CardHeader><CardTitle className="text-sm">Recent News</CardTitle></CardHeader>
                <CardContent>
                  <div className="space-y-2">
                    {profile.recent_news.slice(0, 3).map((news: any, i: number) => (
                      <div key={i} className="flex items-start gap-2">
                        <ExternalLink className="h-3.5 w-3.5 mt-0.5 text-muted-foreground shrink-0" />
                        <div>
                          <p className="text-sm font-medium">{news.title}</p>
                          {news.summary && <p className="text-xs text-muted-foreground">{news.summary}</p>}
                        </div>
                      </div>
                    ))}
                  </div>
                </CardContent>
              </Card>
            )}
          </TabsContent>

          <TabsContent value="people" className="space-y-4 mt-4">
            <div className="flex items-center justify-between">
              <p className="text-sm text-muted-foreground">{people.length} people found</p>
              <Button variant="outline" size="sm" onClick={async () => {
                await api.discoverPeople(companyId)
                const p = await api.getPeople(companyId).catch<Person[]>(() => [])
                setPeople(p)
              }} className="gap-1.5">
                <Users className="h-3.5 w-3.5" /> Discover
              </Button>
            </div>
            <div className="grid gap-3 sm:grid-cols-2">
              {people.map((person) => (
                <Link key={person.id} href={`/companies/${companyId}/people/${person.id}`}>
                  <Card className="h-full transition-colors hover:border-primary/30">
                    <CardContent className="p-4">
                      <div className="flex items-start justify-between">
                        <div>
                          <p className="font-medium text-sm">{person.name}</p>
                          <p className="text-xs text-muted-foreground">{person.role || "Unknown role"}</p>
                        </div>
                        {person.score != null && (
                          <Badge variant={person.score >= 70 ? "success" : person.score >= 40 ? "warning" : "secondary"}>
                            {Math.round(person.score)}
                          </Badge>
                        )}
                      </div>
                      {person.summary && (
                        <p className="text-xs text-muted-foreground mt-2 line-clamp-2">{person.summary}</p>
                      )}
                    </CardContent>
                  </Card>
                </Link>
              ))}
            </div>
          </TabsContent>

          <TabsContent value="jobs" className="space-y-4 mt-4">
            <JobList companyId={companyId} companyName={company.name} />
          </TabsContent>

          <TabsContent value="interview" className="space-y-4 mt-4">
            {profile.likely_interview_topics && profile.likely_interview_topics.length > 0 && (
              <Card>
                <CardHeader><CardTitle className="text-sm">Likely Interview Topics</CardTitle></CardHeader>
                <CardContent>
                  <div className="flex flex-wrap gap-1.5">
                    {profile.likely_interview_topics.map((topic) => (
                      <Badge key={topic} variant="secondary">{topic}</Badge>
                    ))}
                  </div>
                </CardContent>
              </Card>
            )}
            {profile.interesting_github_repos && profile.interesting_github_repos.length > 0 && (
              <Card>
                <CardHeader><CardTitle className="text-sm flex items-center gap-1.5"><GitBranch className="h-3.5 w-3.5" /> GitHub Repos</CardTitle></CardHeader>
                <CardContent>
                  <div className="space-y-2">
                    {profile.interesting_github_repos.slice(0, 5).map((repo: any, i: number) => (
                      <div key={i} className="flex items-center justify-between">
                        <div>
                          <p className="text-sm font-medium">{repo.name}</p>
                          <p className="text-xs text-muted-foreground">{repo.description || ""}</p>
                        </div>
                        <div className="flex items-center gap-2 text-xs text-muted-foreground">
                          {repo.language && <span>{repo.language}</span>}
                          {repo.stars != null && <span>★ {repo.stars}</span>}
                        </div>
                      </div>
                    ))}
                  </div>
                </CardContent>
              </Card>
            )}
            {profile.conference_talks && profile.conference_talks.length > 0 && (
              <Card>
                <CardHeader><CardTitle className="text-sm">Conference Talks</CardTitle></CardHeader>
                <CardContent>
                  <div className="space-y-2">
                    {profile.conference_talks.slice(0, 3).map((talk: any, i: number) => (
                      <div key={i} className="text-sm">
                        <p className="font-medium">{talk.title}</p>
                        <p className="text-xs text-muted-foreground">{talk.conference} — {talk.speaker}</p>
                      </div>
                    ))}
                  </div>
                </CardContent>
              </Card>
            )}
          </TabsContent>
        </Tabs>
      )}

      {!hasProfile && (
        <Card>
          <CardContent className="py-12 text-center space-y-4">
            <Beaker className="mx-auto h-8 w-8 text-muted-foreground" />
            <p className="text-sm text-muted-foreground">This company hasn't been researched yet</p>
            <Button onClick={handleResearch} disabled={researching}>
              <RefreshCw className={cn("mr-1.5 h-4 w-4", researching && "animate-spin")} />
              Research {company.name}
            </Button>
          </CardContent>
        </Card>
      )}
    </div>
  )
}

function JobList({ companyId, companyName }: { companyId: string; companyName: string }) {
  const [jobs, setJobs] = useState<any[]>([])
  const [loading, setLoading] = useState(true)
  useEffect(() => {
    api.getJobs(companyId).then(setJobs).catch(() => {}).finally(() => setLoading(false))
  }, [companyId])

  if (loading) return <Skeleton className="h-32 rounded-lg" />
  if (!jobs.length) return (
    <Card><CardContent className="py-8 text-center"><p className="text-sm text-muted-foreground">No jobs found</p></CardContent></Card>
  )
  return (
    <div className="grid gap-3 sm:grid-cols-2">
      {jobs.map((job: any) => (
        <Link key={job.id} href={`/resume/match/${job.id}`}>
          <Card className="h-full transition-colors hover:border-primary/30">
            <CardContent className="p-4">
              <div className="flex items-start justify-between">
                <div>
                  <p className="font-medium text-sm">{job.title}</p>
                  <p className="text-xs text-muted-foreground">{companyName}</p>
                </div>
                <Briefcase className="h-4 w-4 text-muted-foreground shrink-0" />
              </div>
              {job.skills && job.skills.length > 0 && (
                <div className="flex flex-wrap gap-1 mt-2">
                  {job.skills.slice(0, 5).map((s: string) => (
                    <Badge key={s} variant="outline" className="text-[10px]">{s}</Badge>
                  ))}
                </div>
              )}
            </CardContent>
          </Card>
        </Link>
      ))}
    </div>
  )
}
