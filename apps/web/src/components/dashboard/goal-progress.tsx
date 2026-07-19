"use client"

import { Progress } from "@/components/ui/progress"

interface GoalProgressBarProps {
  percent: number
  label: string
}

export function GoalProgressBar({ percent, label }: GoalProgressBarProps) {
  return (
    <div className="space-y-1.5">
      <div className="flex items-center justify-between text-sm">
        <span className="font-medium">{label}</span>
        <span className="text-muted-foreground">{Math.round(percent)}%</span>
      </div>
      <Progress value={percent} className="h-2.5" />
    </div>
  )
}
