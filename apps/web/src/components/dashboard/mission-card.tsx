"use client"

import type { CareerGoal, GoalMission, MissionAction } from "@/types/api"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { GoalProgressBar } from "./goal-progress"
import { ActionItem } from "./action-item"
import { Target, ArrowRight, Copy } from "lucide-react"
import { useState } from "react"

interface MissionCardProps {
  mission: GoalMission
  goal: CareerGoal
}

export function MissionCard({ mission, goal }: MissionCardProps) {
  const [checkedActions, setCheckedActions] = useState<Set<number>>(new Set())
  const progress = goal.current_step_index > 0 && goal.plan?.length
    ? Math.round((goal.current_step_index / goal.plan.length) * 100)
    : 0

  const toggleAction = (index: number) => {
    setCheckedActions((prev) => {
      const next = new Set(prev)
      if (next.has(index)) next.delete(index)
      else next.add(index)
      return next
    })
  }

  return (
    <Card className="border-primary/20">
      <CardHeader className="pb-3">
        <div className="flex items-start justify-between">
          <div className="flex items-center gap-2">
            <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-primary/10">
              <Target className="h-4 w-4 text-primary" />
            </div>
            <div>
              <CardTitle className="text-lg">{mission.goal_title}</CardTitle>
              <p className="text-sm text-muted-foreground mt-0.5">
                {goal.target_company && `${goal.target_company} — `}
                Step {Math.min(goal.current_step_index + 1, goal.plan?.length || 1)} of {goal.plan?.length || 1}
              </p>
            </div>
          </div>
          <Button variant="outline" size="sm" asChild>
            <a href={`/goals/${goal.id}`}>
              Open Goal <ArrowRight className="ml-1 h-3 w-3" />
            </a>
          </Button>
        </div>
      </CardHeader>
      <CardContent className="space-y-4">
        <GoalProgressBar percent={progress} label="Progress" />

        <div className="space-y-2">
          <h4 className="text-sm font-medium text-muted-foreground">Today's Actions</h4>
          {mission.actions.map((action, i) => (
            <ActionItem
              key={i}
              action={action}
              checked={checkedActions.has(i)}
              onToggle={() => toggleAction(i)}
            />
          ))}
        </div>

        {mission.focus && (
          <div className="rounded-lg border border-primary/10 bg-primary/5 p-3">
            <p className="text-xs font-medium text-primary mb-1">🎯 Today's Focus</p>
            <p className="text-sm">{mission.focus}</p>
          </div>
        )}

        <div className="flex gap-2">
          <Button variant="secondary" size="sm" className="gap-1.5">
            <Copy className="h-3.5 w-3.5" /> Copy Plan
          </Button>
        </div>
      </CardContent>
    </Card>
  )
}
