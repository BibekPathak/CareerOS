"use client"

import { useEffect, useState } from "react"
import { useParams } from "next/navigation"
import { useSession } from "next-auth/react"
import { api } from "@/lib/api-client"
import type { JobDetail, ResumeMatch } from "@/types/api"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { Progress } from "@/components/ui/progress"
import { Skeleton } from "@/components/ui/skeleton"
import { cn } from "@/lib/utils"
import {
  Briefcase, CheckCircle2, XCircle, AlertCircle,
  Lightbulb, Sparkles, ThumbsUp, ThumbsDown, BrainCircuit
} from "lucide-react"

export default function ResumeMatchPage() {
  const params = useParams()
  const jobId = params.jobId as string
  const { data: session } = useSession()
  const userId = session?.user?.id || "00000000-0000-0000-0000-000000000001"

  const [jobDetail, setJobDetail] = useState<JobDetail | null>(null)
  const [match, setMatch] = useState<ResumeMatch | null>(null)
  const [loading, setLoading] = useState(true)
  const [matching, setMatching] = useState(false)

  useEffect(() => {
    api.getJob(jobId).then(setJobDetail).catch(() => {}).finally(() => setLoading(false))
    api.getMatch(jobId, userId).then(setMatch).catch(() => {})
  }, [jobId, userId])

  const handleMatch = async () => {
    setMatching(true)
    try {
      const result = await api.matchResume(jobId, userId)
      setMatch(result)
    } catch {}
    setMatching(false)
  }

  if (loading) return <div className="space-y-6"><Skeleton className="h-32 rounded-lg" /><Skeleton className="h-64 rounded-lg" /></div>
  if (!jobDetail) return <div className="space-y-6"><h1 className="text-2xl font-bold">Job not found</h1></div>

  const { job, analysis } = jobDetail
  const hasMatch = !!match

  return (
    <div className="space-y-6">
      <div className="flex items-start justify-between">
        <div>
          <h1 className="text-2xl font-bold">{job.title}</h1>
          <p className="text-muted-foreground">{jobDetail.job.company_id ? "At company" : ""}</p>
        </div>
        <Button size="sm" onClick={handleMatch} disabled={matching} className="gap-1.5">
          <BrainCircuit className="h-4 w-4" />
          {matching ? "Matching..." : "Match Resume"}
        </Button>
      </div>

      {job.description && (
        <Card>
          <CardHeader className="pb-2"><CardTitle className="text-sm">Job Description</CardTitle></CardHeader>
          <CardContent>
            <p className="text-sm text-muted-foreground whitespace-pre-wrap line-clamp-6">{job.description}</p>
          </CardContent>
        </Card>
      )}

      {hasMatch ? (
        <>
          <Card>
            <CardContent className="p-6">
              <div className="flex items-center gap-6">
                <div className="relative flex h-24 w-24 items-center justify-center">
                  <svg className="h-24 w-24 -rotate-90" viewBox="0 0 100 100">
                    <circle cx="50" cy="50" r="45" fill="none" stroke="hsl(var(--secondary))" strokeWidth="8" />
                    <circle cx="50" cy="50" r="45" fill="none" stroke="hsl(var(--primary))" strokeWidth="8"
                      strokeDasharray={`${2 * Math.PI * 45}`}
                      strokeDashoffset={`${2 * Math.PI * 45 * (1 - (match.overall_score / 100))}`}
                      strokeLinecap="round"
                    />
                  </svg>
                  <span className="absolute text-2xl font-bold">{Math.round(match.overall_score)}%</span>
                </div>
                <div className="space-y-1">
                  <h3 className="font-semibold">Overall Match</h3>
                  <p className="text-sm text-muted-foreground">
                    {match.overall_score >= 80 ? "Strong fit — you're well qualified for this role" :
                     match.overall_score >= 60 ? "Good fit — some gaps to address" :
                     match.overall_score >= 40 ? "Moderate fit — several areas to work on" :
                     "Weak fit — significant gaps"}
                  </p>
                </div>
              </div>
            </CardContent>
          </Card>

          <div className="grid gap-4 sm:grid-cols-2">
            {match.skill_matches.length > 0 && (
              <Card>
                <CardHeader className="pb-2"><CardTitle className="text-sm flex items-center gap-1.5"><CheckCircle2 className="h-3.5 w-3.5 text-emerald-400" /> Skills</CardTitle></CardHeader>
                <CardContent className="space-y-2">
                  {match.skill_matches.map((sm: any, i: number) => (
                    <div key={i} className="flex items-center gap-2 text-sm">
                      {sm.status === "satisfied" ? <CheckCircle2 className="h-3.5 w-3.5 text-emerald-400 shrink-0" /> :
                       sm.status === "partial" ? <AlertCircle className="h-3.5 w-3.5 text-amber-400 shrink-0" /> :
                       <XCircle className="h-3.5 w-3.5 text-red-400 shrink-0" />}
                      <span className={cn(sm.status === "missing" && "text-red-400")}>{sm.skill}</span>
                      {sm.importance === "required" && <Badge variant="outline" className="text-[10px] ml-auto">Required</Badge>}
                    </div>
                  ))}
                </CardContent>
              </Card>
            )}

            <div className="space-y-4">
              {match.strengths.length > 0 && (
                <Card>
                  <CardHeader className="pb-2"><CardTitle className="text-sm flex items-center gap-1.5"><ThumbsUp className="h-3.5 w-3.5 text-emerald-400" /> Strengths</CardTitle></CardHeader>
                  <CardContent>
                    <ul className="space-y-1">
                      {match.strengths.map((s, i) => (
                        <li key={i} className="text-sm text-muted-foreground flex items-center gap-1.5">
                          <CheckCircle2 className="h-3 w-3 text-emerald-400 shrink-0" /> {s}
                        </li>
                      ))}
                    </ul>
                  </CardContent>
                </Card>
              )}

              {match.weaknesses.length > 0 && (
                <Card>
                  <CardHeader className="pb-2"><CardTitle className="text-sm flex items-center gap-1.5"><ThumbsDown className="h-3.5 w-3.5 text-red-400" /> Weaknesses</CardTitle></CardHeader>
                  <CardContent>
                    <ul className="space-y-1">
                      {match.weaknesses.map((w, i) => (
                        <li key={i} className="text-sm text-muted-foreground flex items-center gap-1.5">
                          <XCircle className="h-3 w-3 text-red-400 shrink-0" /> {w}
                        </li>
                      ))}
                    </ul>
                  </CardContent>
                </Card>
              )}
            </div>
          </div>

          <div className="grid gap-4 sm:grid-cols-2">
            {match.mention_projects.length > 0 && (
              <Card>
                <CardHeader className="pb-2"><CardTitle className="text-sm flex items-center gap-1.5"><Lightbulb className="h-3.5 w-3.5 text-amber-400" /> Mention These Projects</CardTitle></CardHeader>
                <CardContent>
                  <ul className="space-y-1">
                    {match.mention_projects.map((p, i) => (
                      <li key={i} className="text-sm text-muted-foreground">✦ {p}</li>
                    ))}
                  </ul>
                </CardContent>
              </Card>
            )}

            {match.avoid_mentioning.length > 0 && (
              <Card>
                <CardHeader className="pb-2"><CardTitle className="text-sm flex items-center gap-1.5"><Sparkles className="h-3.5 w-3.5 text-red-400" /> Avoid Mentioning</CardTitle></CardHeader>
                <CardContent>
                  <ul className="space-y-1">
                    {match.avoid_mentioning.map((a, i) => (
                      <li key={i} className="text-sm text-muted-foreground flex items-center gap-1.5">
                        <XCircle className="h-3 w-3 text-red-400 shrink-0" /> {a}
                      </li>
                    ))}
                  </ul>
                </CardContent>
              </Card>
            )}
          </div>

          {match.recommendation && (
            <Card>
              <CardHeader className="pb-2"><CardTitle className="text-sm">Recommendation</CardTitle></CardHeader>
              <CardContent>
                <p className="text-sm text-muted-foreground">{match.recommendation}</p>
              </CardContent>
            </Card>
          )}
        </>
      ) : (
        <Card>
          <CardContent className="py-12 text-center space-y-4">
            <BrainCircuit className="mx-auto h-8 w-8 text-muted-foreground" />
            <p className="text-sm text-muted-foreground">Run resume matching to see how your skills compare against this job</p>
          </CardContent>
        </Card>
      )}
    </div>
  )
}
