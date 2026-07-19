"use client"

import { useEffect, useState } from "react"
import { useParams, useRouter } from "next/navigation"
import { useSession } from "next-auth/react"
import { api } from "@/lib/api-client"
import type { CareerGoal, GoalEvent } from "@/types/api"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { Progress } from "@/components/ui/progress"
import { Skeleton } from "@/components/ui/skeleton"
import { cn } from "@/lib/utils"
import {
  Target, ArrowLeft, Calendar, CheckCircle2, Circle,
  Clock, ChevronRight, PlayCircle, PauseCircle, Square
} from "lucide-react"
import Link from "next/link"

const phaseColors: Record<string, string> = {
  research: "bg-blue-500/20 text-blue-400",
  apply: "bg-emerald-500/20 text-emerald-400",
  network: "bg-violet-500/20 text-violet-400",
  prepare: "bg-amber-500/20 text-amber-400",
  interview: "bg-rose-500/20 text-rose-400",
}

export default function GoalDetailPage() {
  const params = useParams()
  const router = useRouter()
  const goalId = params.id as string
  const { data: session } = useSession()
  const userId = session?.user?.id || "00000000-0000-0000-0000-000000000001"

  const [goal, setGoal] = useState<CareerGoal | null>(null)
  const [events, setEvents] = useState<GoalEvent[]>([])
  const [loading, setLoading] = useState(true)

  const load = () => {
    Promise.all([
      api.getGoal(goalId),
      api.getGoalEvents(goalId).catch<GoalEvent[]>(() => []),
    ]).then(([g, e]) => { setGoal(g); setEvents(e) }).catch(() => {}).finally(() => setLoading(false))
  }

  useEffect(load, [goalId])

  const handleAdvance = async () => {
    await api.advanceGoal(goalId)
    load()
  }

  const handleStatusChange = async (status: string) => {
    await api.updateGoalStatus(goalId, status)
    load()
  }

  if (loading) return <div className="space-y-6"><Skeleton className="h-10 w-48" /><Skeleton className="h-64 rounded-lg" /></div>
  if (!goal) return <div className="space-y-6"><h1 className="text-2xl font-bold">Goal not found</h1></div>

  const progress = goal.plan?.length ? Math.round((goal.current_step_index / goal.plan.length) * 100) : 0
  const currentStep = goal.plan?.[goal.current_step_index]
  const completedSteps = goal.plan?.slice(0, goal.current_step_index) || []

  return (
    <div className="space-y-6 max-w-4xl">
      <Button variant="ghost" size="sm" asChild className="gap-1.5">
        <Link href="/goals"><ArrowLeft className="h-3.5 w-3.5" /> Back to Goals</Link>
      </Button>

      <div className="flex items-start justify-between">
        <div>
          <div className="flex items-center gap-2">
            <Target className="h-5 w-5 text-primary" />
            <h1 className="text-2xl font-bold">{goal.title}</h1>
            <Badge variant={
              goal.status === "active" ? "success" :
              goal.status === "paused" ? "warning" : "secondary"
            } className="capitalize">{goal.status}</Badge>
          </div>
          <div className="flex items-center gap-3 mt-1 text-sm text-muted-foreground">
            {goal.target_company && <span>{goal.target_company}</span>}
            {goal.target_role && <span>— {goal.target_role}</span>}
            {goal.deadline && (
              <span className="flex items-center gap-1">
                <Calendar className="h-3.5 w-3.5" />
                Due {new Date(goal.deadline).toLocaleDateString()}
              </span>
            )}
          </div>
        </div>
        <div className="flex gap-2">
          {goal.status === "active" && (
            <Button variant="outline" size="sm" onClick={() => handleStatusChange("paused")} className="gap-1.5">
              <PauseCircle className="h-3.5 w-3.5" /> Pause
            </Button>
          )}
          {goal.status === "paused" && (
            <Button variant="outline" size="sm" onClick={() => handleStatusChange("active")} className="gap-1.5">
              <PlayCircle className="h-3.5 w-3.5" /> Resume
            </Button>
          )}
          {goal.status !== "completed" && (
            <Button variant="outline" size="sm" onClick={() => handleStatusChange("completed")} className="gap-1.5">
              <CheckCircle2 className="h-3.5 w-3.5" /> Complete
            </Button>
          )}
        </div>
      </div>

      <div className="grid gap-6 lg:grid-cols-3">
        <div className="lg:col-span-2 space-y-4">
          <Card>
            <CardHeader className="pb-2">
              <CardTitle className="text-sm">Progress</CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <Progress value={progress} className="h-2.5" />
              <div className="flex items-center justify-between text-sm text-muted-foreground">
                <span>{goal.current_step_index} of {goal.plan?.length || 0} steps completed</span>
                <span className="font-medium">{progress}%</span>
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="pb-2">
              <CardTitle className="text-sm">Plan</CardTitle>
            </CardHeader>
            <CardContent>
              {goal.plan && goal.plan.length > 0 ? (
                <div className="space-y-1">
                  {goal.plan.map((step, i) => {
                    const isCompleted = i < goal.current_step_index
                    const isCurrent = i === goal.current_step_index
                    return (
                      <div key={step.id} className={cn(
                        "flex items-start gap-3 rounded-lg p-3 transition-colors",
                        isCurrent && "bg-primary/5 border border-primary/20",
                        isCompleted && "opacity-60"
                      )}>
                        <div className={cn(
                          "flex h-6 w-6 shrink-0 items-center justify-center rounded-full text-xs font-medium mt-0.5",
                          isCompleted && "bg-emerald-500/20 text-emerald-400",
                          isCurrent && "bg-primary/20 text-primary",
                          !isCompleted && !isCurrent && "bg-muted text-muted-foreground"
                        )}>
                          {isCompleted ? "✓" : i + 1}
                        </div>
                        <div className="flex-1 min-w-0">
                          <div className="flex items-center gap-2">
                            <span className={cn("text-sm font-medium", isCompleted && "line-through")}>{step.action}</span>
                            {step.phase && (
                              <span className={cn("text-[10px] px-1.5 py-0.5 rounded-full", phaseColors[step.phase] || "bg-muted text-muted-foreground")}>
                                {step.phase}
                              </span>
                            )}
                          </div>
                          {step.reasoning && (
                            <p className="text-xs text-muted-foreground mt-0.5">{step.reasoning}</p>
                          )}
                        </div>
                        {isCurrent && (
                          <Button size="sm" variant="outline" className="shrink-0 h-7 text-xs" onClick={handleAdvance}>
                            Complete Step
                          </Button>
                        )}
                      </div>
                    )
                  })}
                </div>
              ) : (
                <p className="text-sm text-muted-foreground py-4 text-center">No plan steps yet</p>
              )}
            </CardContent>
          </Card>
        </div>

        <div className="space-y-4">
          <Card>
            <CardHeader className="pb-2">
              <CardTitle className="text-sm">Details</CardTitle>
            </CardHeader>
            <CardContent className="space-y-2 text-sm">
              <div className="flex justify-between">
                <span className="text-muted-foreground">Priority</span>
                <Badge variant={goal.priority === "high" ? "warning" : "secondary"} className="text-[10px] capitalize">{goal.priority}</Badge>
              </div>
              <div className="flex justify-between">
                <span className="text-muted-foreground">Status</span>
                <Badge variant={goal.status === "active" ? "success" : "secondary"} className="text-[10px] capitalize">{goal.status}</Badge>
              </div>
              <div className="flex justify-between">
                <span className="text-muted-foreground">Steps</span>
                <span>{goal.current_step_index}/{goal.plan?.length || 0}</span>
              </div>
            </CardContent>
          </Card>

          {events.length > 0 && (
            <Card>
              <CardHeader className="pb-2">
                <CardTitle className="text-sm">Activity</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-2">
                  {events.slice(-5).reverse().map((event) => (
                    <div key={event.id} className="flex items-start gap-2 text-xs">
                      <ChevronRight className="h-3 w-3 mt-0.5 text-muted-foreground shrink-0" />
                      <div>
                        <p className="font-medium capitalize">{event.event_type.replace(/_/g, " ")}</p>
                        <p className="text-muted-foreground">{new Date(event.created_at).toLocaleDateString()}</p>
                      </div>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          )}
        </div>
      </div>
    </div>
  )
}
