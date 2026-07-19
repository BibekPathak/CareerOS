"use client"

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { ExternalLink } from "lucide-react"
import type { Project } from "@/types/api"

interface ProjectsSectionProps {
  projects: Project[]
}

export function ProjectsSection({ projects }: ProjectsSectionProps) {
  if (!projects.length) return null

  return (
    <div className="space-y-3">
      <h3 className="text-sm font-medium text-muted-foreground uppercase tracking-wider">Projects</h3>
      <div className="grid gap-3 sm:grid-cols-2">
        {projects.map((project, i) => (
          <Card key={i}>
            <CardHeader className="p-3 pb-1">
              <div className="flex items-start justify-between">
                <CardTitle className="text-sm font-medium">{project.name}</CardTitle>
                {project.url && (
                  <a
                    href={project.url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="text-muted-foreground hover:text-foreground"
                  >
                    <ExternalLink className="h-3.5 w-3.5" />
                  </a>
                )}
              </div>
            </CardHeader>
            <CardContent className="p-3 pt-1 space-y-2">
              <p className="text-xs text-muted-foreground line-clamp-2">{project.description}</p>
              <div className="flex flex-wrap gap-1">
                {project.technologies.map((tech) => (
                  <Badge key={tech} variant="outline" className="text-[10px]">
                    {tech}
                  </Badge>
                ))}
              </div>
            </CardContent>
          </Card>
        ))}
      </div>
    </div>
  )
}
