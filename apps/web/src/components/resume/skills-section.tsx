"use client"

import { Badge } from "@/components/ui/badge"

interface SkillsSectionProps {
  skills: string[]
}

export function SkillsSection({ skills }: SkillsSectionProps) {
  if (!skills.length) return null

  return (
    <div className="space-y-3">
      <h3 className="text-sm font-medium text-muted-foreground uppercase tracking-wider">Skills</h3>
      <div className="flex flex-wrap gap-1.5">
        {skills.map((skill) => (
          <Badge key={skill} variant="secondary" className="text-xs">
            {skill}
          </Badge>
        ))}
      </div>
    </div>
  )
}
