"use client"

import { cn } from "@/lib/utils"
import { CheckCircle2, Circle, AlertCircle, Clock } from "lucide-react"
import type { MissionAction } from "@/types/api"

interface ActionItemProps {
  action: MissionAction
  checked?: boolean
  onToggle?: () => void
}

const urgencyColors = {
  high: "text-red-400",
  medium: "text-amber-400",
  low: "text-blue-400",
}

const typeIcons = {
  apply: "🚀",
  contact: "💬",
  learn: "📚",
  follow_up: "🔄",
  prepare: "🎯",
}

export function ActionItem({ action, checked = false, onToggle }: ActionItemProps) {
  const icon = typeIcons[action.type as keyof typeof typeIcons] || "•"
  const color = urgencyColors[action.urgency as keyof typeof urgencyColors] || urgencyColors.low

  return (
    <button
      onClick={onToggle}
      className={cn(
        "flex w-full items-center gap-3 rounded-lg border p-3 text-left text-sm transition-colors",
        checked
          ? "border-primary/20 bg-primary/5 opacity-60"
          : "border-border hover:border-primary/30 hover:bg-accent"
      )}
    >
      <span className="text-base">{checked ? "✅" : icon}</span>
      <div className="flex-1 min-w-0">
        <div className={cn("font-medium truncate", checked && "line-through")}>
          {action.detail}
        </div>
        <div className="flex items-center gap-2 mt-0.5">
          <span className="text-xs text-muted-foreground truncate">{action.target}</span>
          <span className={cn("text-xs font-medium", color)}>{action.deadline}</span>
        </div>
      </div>
      <span className={cn("h-2 w-2 rounded-full shrink-0", color.replace("text-", "bg-"))} />
    </button>
  )
}
