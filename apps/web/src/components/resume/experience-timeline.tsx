"use client"

import { Badge } from "@/components/ui/badge"
import type { Experience } from "@/types/api"

interface ExperienceTimelineProps {
  experience: Experience[]
}

export function ExperienceTimeline({ experience }: ExperienceTimelineProps) {
  if (!experience.length) return null

  return (
    <div className="space-y-3">
      <h3 className="text-sm font-medium text-muted-foreground uppercase tracking-wider">Experience</h3>
      <div className="space-y-4">
        {experience.map((exp, i) => (
          <div key={i} className="relative pl-6 border-l border-border">
            <div className="absolute left-0 top-1.5 h-3 w-3 -translate-x-1/2 rounded-full border-2 border-primary bg-background" />
            <div className="space-y-1.5">
              <div className="flex items-center gap-2 flex-wrap">
                <h4 className="text-sm font-semibold">{exp.role}</h4>
                <span className="text-xs text-muted-foreground">at {exp.company}</span>
              </div>
              <p className="text-xs text-muted-foreground">{exp.duration}</p>
              <p className="text-xs text-muted-foreground line-clamp-2">{exp.description}</p>
              {exp.technologies.length > 0 && (
                <div className="flex flex-wrap gap-1 pt-1">
                  {exp.technologies.map((tech) => (
                    <Badge key={tech} variant="outline" className="text-[10px]">
                      {tech}
                    </Badge>
                  ))}
                </div>
              )}
            </div>
          </div>
        ))}
      </div>
    </div>
  )
}
