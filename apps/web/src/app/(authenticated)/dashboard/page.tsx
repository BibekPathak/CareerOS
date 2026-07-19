"use client"

import { useSession } from "next-auth/react"
import { useEffect, useState } from "react"
import { api } from "@/lib/api-client"
import type { TodaysMission, CareerStats, CareerGoal } from "@/types/api"
import { MissionCard } from "@/components/dashboard/mission-card"
import { StatsWidget } from "@/components/dashboard/stats-widget"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { Skeleton } from "@/components/ui/skeleton"
import { Plus, User, ArrowRight, Calendar, Target, Building2, FileText } from "lucide-react"
import Link from "next/link"

function Greeting() {
  const hour = new Date().getHours()
  let timeOfDay = "evening"
  if (hour < 12) timeOfDay = "morning"
  else if (hour < 17) timeOfDay = "afternoon"

  const { data: session } = useSession()
  const name = session?.user?.name?.split(" ")[0] || "there"

  return (
    <div>
      <h1 className="text-3xl font-bold tracking-tight">Good {timeOfDay}, {name}</h1>
      <p className="text-muted-foreground mt-1">Here's your career intelligence for today</p>
    </div>
  )
}

function LoadingSkeleton() {
  return (
    <div className="space-y-6">
      <div>
        <Skeleton className="h-9 w-72" />
        <Skeleton className="h-5 w-96 mt-2" />
      </div>
      <div className="grid gap-6 lg:grid-cols-3">
        <div className="lg:col-span-2 space-y-4">
          <Skeleton className="h-64 w-full rounded-lg" />
        </div>
        <div className="space-y-4">
          <div className="grid grid-cols-2 gap-3">
            <Skeleton className="h-24 rounded-lg" />
            <Skeleton className="h-24 rounded-lg" />
            <Skeleton className="h-24 rounded-lg" />
            <Skeleton className="h-24 rounded-lg" />
          </div>
        </div>
      </div>
    </div>
  )
}

export default function DashboardPage() {
  const { data: session } = useSession()
  const userId = session?.user?.id || "00000000-0000-0000-0000-000000000001"
  const [mission, setMission] = useState<TodaysMission | null>(null)
  const [stats, setStats] = useState<CareerStats | null>(null)
  const [goals, setGoals] = useState<CareerGoal[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    async function load() {
      try {
        const [missionData, statsData, goalsData] = await Promise.all([
          api.generateMission(userId).catch(() => null),
          api.getStats(userId).catch(() => null),
          api.getGoals(userId, true).catch<CareerGoal[]>(() => []),
        ])
        setMission(missionData)
        setStats(statsData)
        setGoals(goalsData)
      } catch (err) {
        setError(err instanceof Error ? err.message : "Failed to load dashboard")
      } finally {
        setLoading(false)
      }
    }
    load()
  }, [userId])

  if (loading) return <LoadingSkeleton />
  if (error) {
    return (
      <div className="space-y-6">
        <Greeting />
        <Card>
          <CardContent className="py-12 text-center">
            <p className="text-muted-foreground">Unable to load dashboard data.</p>
            <p className="text-sm text-muted-foreground mt-1">Make sure the backend is running at {process.env.NEXT_PUBLIC_API_URL}</p>
            <Button variant="outline" className="mt-4" onClick={() => window.location.reload()}>
              Retry
            </Button>
          </CardContent>
        </Card>
      </div>
    )
  }

  const activeGoal = goals[0]
  const activeMission = mission?.goals?.[0]

  return (
    <div className="space-y-6">
      <Greeting />

      {!goals.length && !mission ? (
        <Card>
          <CardContent className="py-12 text-center space-y-4">
            <div className="mx-auto flex h-12 w-12 items-center justify-center rounded-full bg-primary/10">
              <Target className="h-6 w-6 text-primary" />
            </div>
            <div>
              <h2 className="text-lg font-semibold">No active goals yet</h2>
              <p className="text-sm text-muted-foreground mt-1">
                Create your first career goal and CareerOS will build a plan for you
              </p>
            </div>
            <Button asChild>
              <Link href="/goals/create">
                <Plus className="mr-1.5 h-4 w-4" /> Create Goal
              </Link>
            </Button>
          </CardContent>
        </Card>
      ) : null}

      {activeGoal && activeMission ? (
        <div className="grid gap-6 lg:grid-cols-3">
          <div className="lg:col-span-2 space-y-4">
            <MissionCard mission={activeMission} goal={activeGoal} />

            {activeGoal.plan && activeGoal.plan.length > 0 && (
              <Card>
                <CardHeader>
                  <CardTitle className="text-sm font-medium">Plan Progress</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="space-y-2">
                    {activeGoal.plan.slice(0, 5).map((step, i) => (
                      <div
                        key={step.id}
                        className="flex items-center gap-3 text-sm"
                      >
                        <div className={`flex h-6 w-6 shrink-0 items-center justify-center rounded-full text-xs font-medium ${
                          i < activeGoal.current_step_index
                            ? "bg-emerald-500/20 text-emerald-400"
                            : i === activeGoal.current_step_index
                            ? "bg-primary/20 text-primary"
                            : "bg-muted text-muted-foreground"
                        }`}>
                          {i < activeGoal.current_step_index ? "✓" : i + 1}
                        </div>
                        <span className={i < activeGoal.current_step_index ? "text-muted-foreground line-through" : ""}>
                          {step.action}
                        </span>
                        <Badge variant="outline" className="ml-auto text-[10px]">{step.phase}</Badge>
                      </div>
                    ))}
                  </div>
                </CardContent>
              </Card>
            )}
          </div>

          <div className="space-y-4">
            {stats && <StatsWidget stats={stats} />}

            <Card>
              <CardHeader className="pb-3">
                <CardTitle className="text-sm font-medium">Quick Actions</CardTitle>
              </CardHeader>
              <CardContent className="space-y-2">
                <Button variant="outline" size="sm" className="w-full justify-start" asChild>
                  <Link href="/companies">
                    <Building2 className="mr-2 h-4 w-4" /> Browse Companies
                  </Link>
                </Button>
                <Button variant="outline" size="sm" className="w-full justify-start" asChild>
                  <Link href="/resume">
                    <FileText className="mr-2 h-4 w-4" /> View Resume
                  </Link>
                </Button>
                <Button variant="outline" size="sm" className="w-full justify-start" asChild>
                  <Link href="/goals">
                    <Target className="mr-2 h-4 w-4" /> All Goals
                  </Link>
                </Button>
              </CardContent>
            </Card>
          </div>
        </div>
      ) : goals.length > 0 ? (
        <div className="grid gap-6 lg:grid-cols-3">
          <div className="lg:col-span-2 space-y-4">
            {goals.map((goal) => (
              <Card key={goal.id}>
                <CardHeader>
                  <div className="flex items-center justify-between">
                    <CardTitle className="text-base">{goal.title}</CardTitle>
                    <Button variant="ghost" size="sm" asChild>
                      <Link href={`/goals/${goal.id}`}>
                        <ArrowRight className="h-4 w-4" />
                      </Link>
                    </Button>
                  </div>
                </CardHeader>
                <CardContent className="space-y-2">
                  {goal.target_company && (
                    <p className="text-sm text-muted-foreground">{goal.target_company}</p>
                  )}
                  {goal.deadline && (
                    <div className="flex items-center gap-1.5 text-sm text-muted-foreground">
                      <Calendar className="h-3.5 w-3.5" />
                      Due {new Date(goal.deadline).toLocaleDateString()}
                    </div>
                  )}
                </CardContent>
              </Card>
            ))}
          </div>
          <div className="space-y-4">
            {stats && <StatsWidget stats={stats} />}
          </div>
        </div>
      ) : null}
    </div>
  )
}

