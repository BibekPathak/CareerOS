"use client"

import { useEffect, useState } from "react"
import { useSession } from "next-auth/react"
import { api } from "@/lib/api-client"
import type { ResumeProfile } from "@/types/api"
import { ResumeUploader } from "@/components/resume/resume-uploader"
import { SkillsSection } from "@/components/resume/skills-section"
import { ProjectsSection } from "@/components/resume/projects-section"
import { ExperienceTimeline } from "@/components/resume/experience-timeline"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Skeleton } from "@/components/ui/skeleton"
import { FileText, Wrench, Briefcase, Lightbulb, Layers } from "lucide-react"

export default function ResumePage() {
  const { data: session } = useSession()
  const userId = session?.user?.id || "00000000-0000-0000-0000-000000000001"
  const [profile, setProfile] = useState<ResumeProfile | null>(null)
  const [loading, setLoading] = useState(true)
  const [hasUploaded, setHasUploaded] = useState(false)

  useEffect(() => {
    api.getResume(userId)
      .then(setProfile)
      .catch(() => {})
      .finally(() => setLoading(false))
  }, [userId, hasUploaded])

  const handleUploadComplete = () => setHasUploaded((p) => !p)

  if (loading) {
    return (
      <div className="space-y-6">
        <div>
          <Skeleton className="h-9 w-48" />
          <Skeleton className="h-5 w-72 mt-2" />
        </div>
        <Skeleton className="h-40 w-full rounded-lg" />
        <div className="grid gap-6 lg:grid-cols-2">
          <Skeleton className="h-48 rounded-lg" />
          <Skeleton className="h-48 rounded-lg" />
        </div>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold tracking-tight">Resume</h1>
        <p className="text-muted-foreground mt-1">Upload and manage your resume</p>
      </div>

      <ResumeUploader onUploadComplete={handleUploadComplete} />

      {profile ? (
        <div className="grid gap-6 lg:grid-cols-3">
          <div className="lg:col-span-2 space-y-6">
            <Card>
              <CardHeader>
                <CardTitle className="text-base flex items-center gap-2">
                  <Wrench className="h-4 w-4 text-primary" />
                  Skills & Technologies
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <SkillsSection skills={profile.skills} />
                {profile.technologies.length > 0 && (
                  <div className="space-y-2">
                    <h3 className="text-sm font-medium text-muted-foreground uppercase tracking-wider">Technologies</h3>
                    <div className="flex flex-wrap gap-1.5">
                      {profile.technologies.map((t) => (
                        <Badge key={t} variant="outline" className="text-xs">
                          {t}
                        </Badge>
                      ))}
                    </div>
                  </div>
                )}
              </CardContent>
            </Card>

            <ProjectsSection projects={profile.projects} />
            <ExperienceTimeline experience={profile.experience} />
          </div>

          <div className="space-y-4">
            {profile.seniority && (
              <Card>
                <CardHeader className="pb-2">
                  <CardTitle className="text-sm flex items-center gap-2">
                    <Lightbulb className="h-4 w-4 text-primary" />
                    Seniority
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <Badge variant="secondary" className="text-sm">{profile.seniority}</Badge>
                </CardContent>
              </Card>
            )}

            {profile.preferred_roles.length > 0 && (
              <Card>
                <CardHeader className="pb-2">
                  <CardTitle className="text-sm flex items-center gap-2">
                    <Briefcase className="h-4 w-4 text-primary" />
                    Preferred Roles
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="space-y-1">
                    {profile.preferred_roles.map((role) => (
                      <p key={role} className="text-sm">{role}</p>
                    ))}
                  </div>
                </CardContent>
              </Card>
            )}

            {profile.company_interests.length > 0 && (
              <Card>
                <CardHeader className="pb-2">
                  <CardTitle className="text-sm flex items-center gap-2">
                    <Layers className="h-4 w-4 text-primary" />
                    Company Interests
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="flex flex-wrap gap-1.5">
                    {profile.company_interests.map((c) => (
                      <Badge key={c} variant="outline">{c}</Badge>
                    ))}
                  </div>
                </CardContent>
              </Card>
            )}
          </div>
        </div>
      ) : (
        <Card>
          <CardContent className="py-12 text-center">
            <FileText className="mx-auto h-8 w-8 text-muted-foreground" />
            <p className="mt-3 text-sm text-muted-foreground">Upload your resume to see your structured profile</p>
          </CardContent>
        </Card>
      )}
    </div>
  )
}
