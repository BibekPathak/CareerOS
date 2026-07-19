"use client"

import { useEffect, useState } from "react"
import { useParams } from "next/navigation"
import { useSession } from "next-auth/react"
import { api } from "@/lib/api-client"
import type { Person, OutreachMessage, OutreachIntelligence } from "@/types/api"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { Skeleton } from "@/components/ui/skeleton"
import { Progress } from "@/components/ui/progress"
import { cn } from "@/lib/utils"
import {
  User, Star, MessageSquare, Copy, CheckCircle2,
  ExternalLink, Sparkles, AlertTriangle
} from "lucide-react"

export default function PersonDetailPage() {
  const params = useParams()
  const { data: session } = useSession()
  const companyId = params.id as string
  const personId = params.personId as string
  const userId = session?.user?.id || "00000000-0000-0000-0000-000000000001"

  const [person, setPerson] = useState<Person | null>(null)
  const [intel, setIntel] = useState<OutreachIntelligence | null>(null)
  const [messages, setMessages] = useState<OutreachMessage[]>([])
  const [loading, setLoading] = useState(true)
  const [generating, setGenerating] = useState(false)
  const [copiedId, setCopiedId] = useState<string | null>(null)

  useEffect(() => {
    Promise.all([
      api.getPerson(companyId, personId),
      api.getOutreachIntelligence(personId).catch(() => null),
      api.getMessages(personId).catch<OutreachMessage[]>(() => []),
    ]).then(([p, i, m]) => {
      setPerson(p)
      setIntel(i)
      setMessages(m)
    }).catch(() => {}).finally(() => setLoading(false))
  }, [companyId, personId])

  const handleGenerate = async () => {
    setGenerating(true)
    try {
      const result = await api.generateOutreach(userId, personId, companyId)
      setMessages(result.messages)
      if (result.intelligence) setIntel(result.intelligence)
    } catch {}
    setGenerating(false)
  }

  const copyMessage = async (id: string, content: string) => {
    await navigator.clipboard.writeText(content)
    setCopiedId(id)
    setTimeout(() => setCopiedId(null), 2000)
  }

  if (loading) return <div className="space-y-6"><Skeleton className="h-48 rounded-lg" /><Skeleton className="h-64 rounded-lg" /></div>
  if (!person) return <div className="space-y-6"><h1 className="text-2xl font-bold">Person not found</h1></div>

  const score = person.score ?? 0
  const stars = Math.round(score / 20)

  return (
    <div className="grid gap-6 lg:grid-cols-5">
      {/* Left: Person Card */}
      <div className="lg:col-span-2 space-y-4">
        <Card>
          <CardContent className="p-6 space-y-4">
            <div className="flex items-center gap-3">
              <div className="flex h-12 w-12 items-center justify-center rounded-full bg-primary/10">
                <User className="h-6 w-6 text-primary" />
              </div>
              <div>
                <h2 className="text-lg font-semibold">{person.name}</h2>
                <p className="text-sm text-muted-foreground">{person.role || "Unknown role"}</p>
              </div>
            </div>

            <div className="flex items-center gap-1">
              {Array.from({ length: 5 }).map((_, i) => (
                <Star key={i} className={cn("h-4 w-4", i < stars ? "text-amber-400 fill-amber-400" : "text-muted")} />
              ))}
              <span className="text-sm font-medium ml-1">{Math.round(score)}/100</span>
            </div>

            {person.summary && <p className="text-sm text-muted-foreground">{person.summary}</p>}

            {person.public_profile_url && (
              <a href={person.public_profile_url} target="_blank" rel="noopener noreferrer"
                className="flex items-center gap-1.5 text-sm text-primary hover:underline">
                <ExternalLink className="h-3.5 w-3.5" /> View Profile
              </a>
            )}

            <div className="space-y-3 pt-2 border-t">
              {person.score != null && (
                <div className="space-y-1">
                  <div className="flex justify-between text-xs">
                    <span className="text-muted-foreground">Influence</span>
                    <span className="font-medium">{Math.round(score)}%</span>
                  </div>
                  <Progress value={score} className="h-1.5" />
                </div>
              )}
            </div>
          </CardContent>
        </Card>

        {intel && (
          <Card>
            <CardHeader className="pb-2">
              <CardTitle className="text-sm flex items-center gap-1.5">
                <Sparkles className="h-3.5 w-3.5 text-primary" /> Intelligence
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-3">
              {intel.referral_readiness && (
                <div className="flex items-center justify-between text-sm">
                  <span className="text-muted-foreground">Referral Readiness</span>
                  <Badge variant={
                    intel.referral_readiness === "ready" ? "success" :
                    intel.referral_readiness === "warm" ? "warning" : "secondary"
                  } className="text-xs">{intel.referral_readiness}</Badge>
                </div>
              )}
              {intel.response_approach && (
                <div className="flex items-center justify-between text-sm">
                  <span className="text-muted-foreground">Approach</span>
                  <Badge variant="outline" className="text-xs">{intel.response_approach}</Badge>
                </div>
              )}
              {intel.optimal_send_time && (
                <div className="flex items-center justify-between text-sm">
                  <span className="text-muted-foreground">Best Time</span>
                  <span className="font-medium text-xs">{intel.optimal_send_time}</span>
                </div>
              )}
            </CardContent>
          </Card>
        )}
      </div>

      {/* Right: Outreach Panel */}
      <div className="lg:col-span-3 space-y-4">
        {intel && intel.best_conversation_starters.length > 0 && (
          <Card>
            <CardHeader className="pb-2">
              <CardTitle className="text-sm">Conversation Strategy</CardTitle>
            </CardHeader>
            <CardContent className="space-y-3">
              <div>
                <p className="text-xs font-medium text-emerald-400 mb-1">Start with:</p>
                <ul className="space-y-1">
                  {intel.best_conversation_starters.map((s, i) => (
                    <li key={i} className="text-sm text-muted-foreground">💬 {s}</li>
                  ))}
                </ul>
              </div>
              {intel.topics_to_avoid.length > 0 && (
                <div>
                  <p className="text-xs font-medium text-red-400 mb-1">Avoid:</p>
                  <ul className="space-y-1">
                    {intel.topics_to_avoid.map((a, i) => (
                      <li key={i} className="text-sm text-muted-foreground flex items-center gap-1">
                        <AlertTriangle className="h-3 w-3 text-red-400" /> {a}
                      </li>
                    ))}
                  </ul>
                </div>
              )}
            </CardContent>
          </Card>
        )}

        <div className="flex items-center justify-between">
          <h3 className="text-sm font-medium">Messages</h3>
          <Button size="sm" onClick={handleGenerate} disabled={generating} className="gap-1.5">
            <MessageSquare className="h-3.5 w-3.5" />
            {generating ? "Generating..." : "Generate Messages"}
          </Button>
        </div>

        {messages.length > 0 ? (
          <Tabs defaultValue={messages[0]?.message_type || "connection_request"}>
            <TabsList className="flex-wrap h-auto">
              {messages.map((msg) => (
                <TabsTrigger key={msg.id} value={msg.message_type} className="text-xs capitalize">
                  {msg.message_type.replace(/_/g, " ")}
                </TabsTrigger>
              ))}
            </TabsList>
            {messages.map((msg) => (
              <TabsContent key={msg.id} value={msg.message_type}>
                <Card>
                  <CardContent className="p-4">
                    <p className="text-sm whitespace-pre-wrap">{msg.content}</p>
                    <div className="flex items-center gap-2 mt-3">
                      <Button
                        variant="outline"
                        size="sm"
                        className="gap-1.5"
                        onClick={() => copyMessage(msg.id, msg.content)}
                      >
                        {copiedId === msg.id ? (
                          <><CheckCircle2 className="h-3.5 w-3.5 text-emerald-400" /> Copied</>
                        ) : (
                          <><Copy className="h-3.5 w-3.5" /> Copy</>
                        )}
                      </Button>
                      <Badge variant="outline" className="text-[10px]">{msg.status}</Badge>
                    </div>
                  </CardContent>
                </Card>
              </TabsContent>
            ))}
          </Tabs>
        ) : (
          <Card>
            <CardContent className="py-8 text-center">
              <MessageSquare className="mx-auto h-6 w-6 text-muted-foreground" />
              <p className="text-sm text-muted-foreground mt-2">No messages yet</p>
              <p className="text-xs text-muted-foreground mt-1">Click "Generate Messages" to create personalized outreach</p>
            </CardContent>
          </Card>
        )}

        {intel?.person_interests && intel.person_interests.length > 0 && (
          <Card>
            <CardHeader className="pb-2">
              <CardTitle className="text-sm">Shared Interests</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="flex flex-wrap gap-1.5">
                {intel.person_interests.map((interest, i) => (
                  <Badge key={i} variant="secondary" className="text-xs">{interest}</Badge>
                ))}
              </div>
            </CardContent>
          </Card>
        )}
      </div>
    </div>
  )
}
