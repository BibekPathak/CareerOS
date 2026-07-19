"use client"

import type { CareerStats } from "@/types/api"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Target, MessageSquare, Building2, Trophy } from "lucide-react"

interface StatsWidgetProps {
  stats: CareerStats
}

const statCards = [
  {
    key: "active_goals" as const,
    icon: Target,
    label: "Active Goals",
    color: "text-emerald-400",
    bg: "bg-emerald-500/10",
  },
  {
    key: "people_contacted" as const,
    icon: MessageSquare,
    label: "People Contacted",
    color: "text-blue-400",
    bg: "bg-blue-500/10",
  },
  {
    key: "total_tracked" as const,
    icon: Building2,
    label: "Companies",
    color: "text-violet-400",
    bg: "bg-violet-500/10",
  },
  {
    key: "sent" as const,
    icon: Trophy,
    label: "Messages Sent",
    color: "text-amber-400",
    bg: "bg-amber-500/10",
  },
] as const

export function StatsWidget({ stats }: StatsWidgetProps) {
  const values: Record<string, number> = {
    active_goals: stats.goals.active,
    people_contacted: stats.outreach.unique_people_contacted,
    total_tracked: stats.companies.total_tracked,
    sent: stats.outreach.sent,
  }

  return (
    <div className="grid grid-cols-2 gap-3">
      {statCards.map(({ key, icon: Icon, label, color, bg }) => (
        <Card key={key} className={bg}>
          <CardHeader className="p-3 pb-1">
            <div className="flex items-center gap-2">
              <Icon className={cn("h-4 w-4", color)} />
              <CardTitle className="text-xs font-medium text-muted-foreground">{label}</CardTitle>
            </div>
          </CardHeader>
          <CardContent className="p-3 pt-1">
            <p className={cn("text-2xl font-bold", color)}>{values[key] ?? 0}</p>
          </CardContent>
        </Card>
      ))}
    </div>
  )
}

import { cn } from "@/lib/utils"
