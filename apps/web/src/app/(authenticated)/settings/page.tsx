"use client"

import { useSession, signOut } from "next-auth/react"
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { Skeleton } from "@/components/ui/skeleton"
import { User, Mail, Shield, LogOut, Github } from "lucide-react"

export default function SettingsPage() {
  const { data: session, status } = useSession()
  const user = session?.user

  if (status === "loading") {
    return <div className="space-y-6"><Skeleton className="h-32 rounded-lg" /><Skeleton className="h-32 rounded-lg" /></div>
  }

  return (
    <div className="max-w-2xl space-y-6">
      <div>
        <h1 className="text-3xl font-bold tracking-tight">Settings</h1>
        <p className="text-muted-foreground mt-1">Manage your account and preferences</p>
      </div>

      <Card>
        <CardHeader>
          <CardTitle className="text-base flex items-center gap-2">
            <User className="h-4 w-4 text-primary" /> Profile
          </CardTitle>
          <CardDescription>Your account information</CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="flex items-center gap-3">
            {user?.image && (
              <img src={user.image} alt="" className="h-12 w-12 rounded-full" />
            )}
            <div>
              <p className="font-medium">{user?.name || "Unknown"}</p>
              <p className="text-sm text-muted-foreground">{user?.email || ""}</p>
            </div>
          </div>
          <div className="flex flex-wrap gap-2">
            {user?.email && (
              <Badge variant="outline" className="gap-1">
                <Mail className="h-3 w-3" /> {user.email}
              </Badge>
            )}
            <Badge variant="outline" className="gap-1">
              <Shield className="h-3 w-3" /> ID: {user?.id?.slice(0, 8)}...
            </Badge>
          </div>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle className="text-base flex items-center gap-2">
            <Github className="h-4 w-4 text-primary" /> Connected Accounts
          </CardTitle>
          <CardDescription>Authentication providers linked to your account</CardDescription>
        </CardHeader>
        <CardContent className="space-y-3">
          <div className="flex items-center justify-between rounded-lg border p-3">
            <div className="flex items-center gap-2">
              <Github className="h-4 w-4" />
              <span className="text-sm">GitHub</span>
            </div>
            <Badge variant="success" className="text-[10px]">Connected</Badge>
          </div>
          <div className="flex items-center justify-between rounded-lg border p-3">
            <div className="flex items-center gap-2">
              <svg className="h-4 w-4" viewBox="0 0 24 24"><path d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92a5.06 5.06 0 0 1-2.2 3.32v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.1z" fill="#4285F4"/><path d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z" fill="#34A853"/></svg>
              <span className="text-sm">Google</span>
            </div>
            <Badge variant="success" className="text-[10px]">Connected</Badge>
          </div>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle className="text-base">Danger Zone</CardTitle>
        </CardHeader>
        <CardContent>
          <Button variant="destructive" onClick={() => signOut({ redirectTo: "/auth/signin" })} className="gap-1.5">
            <LogOut className="h-4 w-4" /> Sign Out
          </Button>
        </CardContent>
      </Card>
    </div>
  )
}
