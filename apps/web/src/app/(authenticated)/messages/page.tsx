"use client"

import { useEffect, useState } from "react"
import { useSession } from "next-auth/react"
import { api } from "@/lib/api-client"
import type { OutreachMessage } from "@/types/api"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { Skeleton } from "@/components/ui/skeleton"
import { MessageSquare, Copy, CheckCircle2, Search, User, Calendar, Filter } from "lucide-react"
import { Input } from "@/components/ui/input"
import { cn } from "@/lib/utils"

// Since we don't have a bulk messages endpoint, this page shows what's available
// via the person-specific getMessages endpoint. For now, show a searchable interface.
export default function MessagesPage() {
  const { data: session } = useSession()
  const userId = session?.user?.id || "00000000-0000-0000-0000-000000000001"
  const [search, setSearch] = useState("")
  const [loading] = useState(false)
  const [copiedId, setCopiedId] = useState<string | null>(null)

  const copyMessage = async (id: string, content: string) => {
    await navigator.clipboard.writeText(content)
    setCopiedId(id)
    setTimeout(() => setCopiedId(null), 2000)
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold tracking-tight">Messages</h1>
        <p className="text-muted-foreground mt-1">View and manage your generated outreach messages</p>
      </div>

      <Card>
        <CardContent className="py-12 text-center space-y-4">
          <MessageSquare className="mx-auto h-8 w-8 text-muted-foreground" />
          <div>
            <p className="text-sm text-muted-foreground">View messages by person</p>
            <p className="text-xs text-muted-foreground mt-1">
              Navigate to a person's page to see their generated messages, or use the Companies page to find people.
            </p>
          </div>
          <div className="flex justify-center gap-3">
            <Button variant="outline" asChild>
              <a href="/companies">Browse Companies</a>
            </Button>
            <Button asChild>
              <a href="/goals">View Goals</a>
            </Button>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}
