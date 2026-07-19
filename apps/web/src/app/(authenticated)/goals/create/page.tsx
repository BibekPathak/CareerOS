"use client"

import { useState } from "react"
import { useRouter } from "next/navigation"
import { useSession } from "next-auth/react"
import { api } from "@/lib/api-client"
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Badge } from "@/components/ui/badge"
import { Target, Loader2, ArrowLeft } from "lucide-react"
import Link from "next/link"

export default function CreateGoalPage() {
  const router = useRouter()
  const { data: session } = useSession()
  const userId = session?.user?.id || "00000000-0000-0000-0000-000000000001"

  const [title, setTitle] = useState("")
  const [company, setCompany] = useState("")
  const [role, setRole] = useState("")
  const [deadline, setDeadline] = useState("")
  const [priority, setPriority] = useState("high")
  const [context, setContext] = useState("")
  const [submitting, setSubmitting] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!title.trim()) return
    setSubmitting(true)
    setError(null)
    try {
      const result = await api.createGoal({
        user_id: userId,
        title: title.trim(),
        target_company: company.trim() || undefined,
        target_role: role.trim() || undefined,
        deadline: deadline || undefined,
        priority,
        context: context.trim() || undefined,
      })
      router.push(`/goals/${result.goal.id}`)
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to create goal")
    } finally {
      setSubmitting(false)
    }
  }

  return (
    <div className="max-w-2xl mx-auto space-y-6">
      <Button variant="ghost" size="sm" asChild className="gap-1.5">
        <Link href="/goals"><ArrowLeft className="h-3.5 w-3.5" /> Back to Goals</Link>
      </Button>

      <div>
        <h1 className="text-3xl font-bold tracking-tight">New Career Goal</h1>
        <p className="text-muted-foreground mt-1">Define what you want to achieve and CareerOS will build a plan</p>
      </div>

      <form onSubmit={handleSubmit} className="space-y-4">
        <Card>
          <CardHeader>
            <CardTitle className="text-base">Goal Details</CardTitle>
            <CardDescription>What do you want to achieve?</CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="space-y-2">
              <label className="text-sm font-medium">Goal Title *</label>
              <Input
                placeholder="e.g. Backend Internship at AlphaGrep"
                value={title}
                onChange={(e) => setTitle(e.target.value)}
                required
              />
            </div>
            <div className="grid gap-4 sm:grid-cols-2">
              <div className="space-y-2">
                <label className="text-sm font-medium">Target Company</label>
                <Input
                  placeholder="e.g. AlphaGrep"
                  value={company}
                  onChange={(e) => setCompany(e.target.value)}
                />
              </div>
              <div className="space-y-2">
                <label className="text-sm font-medium">Target Role</label>
                <Input
                  placeholder="e.g. Backend Intern"
                  value={role}
                  onChange={(e) => setRole(e.target.value)}
                />
              </div>
            </div>
            <div className="grid gap-4 sm:grid-cols-2">
              <div className="space-y-2">
                <label className="text-sm font-medium">Deadline</label>
                <Input type="date" value={deadline} onChange={(e) => setDeadline(e.target.value)} />
              </div>
              <div className="space-y-2">
                <label className="text-sm font-medium">Priority</label>
                <div className="flex gap-2">
                  {["high", "medium", "low"].map((p) => (
                    <button
                      key={p}
                      type="button"
                      onClick={() => setPriority(p)}
                      className={`flex-1 rounded-md border px-3 py-2 text-sm font-medium transition-colors ${
                        priority === p
                          ? "border-primary bg-primary/10 text-primary"
                          : "border-input text-muted-foreground hover:bg-accent"
                      }`}
                    >
                      {p.charAt(0).toUpperCase() + p.slice(1)}
                    </button>
                  ))}
                </div>
              </div>
            </div>
            <div className="space-y-2">
              <label className="text-sm font-medium">Additional Context</label>
              <textarea
                className="flex min-h-[80px] w-full rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring"
                placeholder="Any additional context that will help CareerOS build a better plan..."
                value={context}
                onChange={(e) => setContext(e.target.value)}
              />
            </div>
          </CardContent>
        </Card>

        {error && (
          <Card className="border-red-500/50">
            <CardContent className="py-3"><p className="text-sm text-red-400">{error}</p></CardContent>
          </Card>
        )}

        <Button type="submit" className="w-full" disabled={submitting || !title.trim()}>
          {submitting ? <><Loader2 className="mr-1.5 h-4 w-4 animate-spin" /> Creating...</> : <>Create Goal</>}
        </Button>
      </form>
    </div>
  )
}
