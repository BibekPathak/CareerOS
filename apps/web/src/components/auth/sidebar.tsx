"use client"

import Link from "next/link"
import { usePathname } from "next/navigation"
import { cn } from "@/lib/utils"
import {
  Target,
  FileText,
  Building2,
  Users,
  MessageSquare,
  Settings,
  ChevronLeft,
  ChevronRight,
} from "lucide-react"
import { useState } from "react"
import { Button } from "@/components/ui/button"

const navItems = [
  { href: "/dashboard", label: "Dashboard", icon: Target },
  { href: "/resume", label: "Resume", icon: FileText },
  { href: "/companies", label: "Companies", icon: Building2 },
  { href: "/goals", label: "Goals", icon: Users },
  { href: "/messages", label: "Messages", icon: MessageSquare },
  { href: "/settings", label: "Settings", icon: Settings },
]

export function Sidebar() {
  const pathname = usePathname()
  const [collapsed, setCollapsed] = useState(false)

  return (
    <aside
      className={cn(
        "flex flex-col border-r bg-card transition-all duration-200",
        collapsed ? "w-16" : "w-56"
      )}
    >
      <div className="flex h-14 items-center gap-2 border-b px-4">
        {!collapsed && <span className="font-bold text-primary">CareerOS</span>}
        <Button
          variant="ghost"
          size="icon"
          className="ml-auto h-6 w-6"
          onClick={() => setCollapsed(!collapsed)}
        >
          {collapsed ? <ChevronRight className="h-3 w-3" /> : <ChevronLeft className="h-3 w-3" />}
        </Button>
      </div>
      <nav className="flex-1 space-y-1 p-2">
        {navItems.map((item) => {
          const Icon = item.icon
          const active = pathname.startsWith(item.href)
          return (
            <Link
              key={item.href}
              href={item.href}
              className={cn(
                "flex items-center gap-3 rounded-md px-3 py-2 text-sm font-medium transition-colors",
                active
                  ? "bg-primary/10 text-primary"
                  : "text-muted-foreground hover:bg-accent hover:text-accent-foreground",
                collapsed && "justify-center px-2"
              )}
            >
              <Icon className="h-4 w-4 shrink-0" />
              {!collapsed && <span>{item.label}</span>}
            </Link>
          )
        })}
      </nav>
    </aside>
  )
}
