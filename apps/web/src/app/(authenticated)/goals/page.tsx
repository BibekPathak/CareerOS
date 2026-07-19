"use client"

import { useEffect, useState } from "react"
import { useSession } from "next-auth/react"
import { api } from "@/lib/api-client"
import type { CareerGoal } from "@/types/api"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { Progress } from "@/components/ui/progress"
import { Skeleton } from "@/components/ui/skeleton"
import { Target, Plus, ArrowRight, Calendar, CheckCircle2, PauseCircle, PlayCircle } from "lucide-react"
import Link from "next/link"

const statusColors: Record<string, "default" | "success" | "warning" | "secondary"> = {
  active: "success",
  paused: "warning",
  completed: "default",
  abandoned: "secondary",
}

export default function GoalsPage() {
  const { data: session } = useSession()
  const userId = session?.user?.id || "00000000-0000-0000-0000-000000000001"
  const [goals, setGoals] = useState<CareerGoal[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    api.getGoals(userId).then(setGoals).catch(() => {}).finally(() => setLoading(false))
  }, [userId])

  if (loading) return (
    <div className="space-y-6">
      <div><Skeleton className="h-9 w-36" /><Skeleton className="h-5 w-64 mt-2" /></div>
      <div className="grid gap-4 sm:grid-cols-2"><Skeleton className="h-40 rounded-lg" /><Skeleton className="h-40 rounded-lg" /></div>
    </div>
  )

  return (
    <div className="space-y-6">
      <div className="flex items-start justify-between">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Goals</h1>
          <p className="text-muted-foreground mt-1">Career goals and progress tracking</p>
        </div>
        <Button asChild>
          <Link href="/goals/create"><Plus className="mr-1.5 h-4 w-4" /> New Goal</Link>
        </Button>
      </div>

      {goals.length === 0 ? (
        <Card>
          <CardContent className="py-12 text-center space-y-4">
            <Target className="mx-auto h-8 w-8 text-muted-foreground" />
            <p className="text-sm text-muted-foreground">No career goals yet</p>
            <Button asChild><Link href="/goals/create"><Plus className="mr-1.5 h-4 w-4" /> Create Goal</Link></Button>
          </CardContent>
        </Card>
      ) : (
        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
          {goals.map((goal) => {
            const progress = goal.plan?.length ? Math.round((goal.current_step_index / goal.plan.length) * 100) : 0
            return (
              <Link key={goal.id} href={`/goals/${goal.id}`}>
                <Card className="h-full transition-colors hover:border-primary/30">
                  <CardHeader className="pb-2">
                    <div className="flex items-start justify-between">
                      <CardTitle className="text-sm">{goal.title}</CardTitle>
                      <Badge variant={statusColors[goal.status] || "secondary"} className="text-[10px] capitalize">{goal.status}</Badge>
                    </div>
                  </CardHeader>
                  <CardContent className="space-y-3">
                    {goal.target_company && <p className="text-xs text-muted-foreground">{goal.target_company}</p>}
                    <Progress value={progress} className="h-1.5" />
                    <div className="flex items-center justify-between text-xs text-muted-foreground">
                      <span>{goal.current_step_index} of {goal.plan?.length || 0} steps</span>
                      <ArrowRight className="h-3 w-3" />
                    </div>
                  </CardContent>
                </Card>
              </Link>
            )
          })}
        </div>
      )}
    </div>
  )
}
