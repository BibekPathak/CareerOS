"use client"

import { useEffect, useState } from "react"
import { api } from "@/lib/api-client"
import type { Company } from "@/types/api"
import { Input } from "@/components/ui/input"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Skeleton } from "@/components/ui/skeleton"
import { Search, Building2, ArrowRight } from "lucide-react"
import Link from "next/link"
import { useDebounce } from "@/lib/hooks"

export default function CompaniesPage() {
  const [query, setQuery] = useState("")
  const [companies, setCompanies] = useState<Company[]>([])
  const [loading, setLoading] = useState(false)
  const debouncedQuery = useDebounce(query, 300)

  useEffect(() => {
    if (!debouncedQuery) {
      setCompanies([])
      return
    }
    setLoading(true)
    api.searchCompanies(debouncedQuery)
      .then(setCompanies)
      .catch(() => {})
      .finally(() => setLoading(false))
  }, [debouncedQuery])

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold tracking-tight">Companies</h1>
        <p className="text-muted-foreground mt-1">Research companies and discover opportunities</p>
      </div>

      <div className="relative">
        <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
        <Input
          placeholder="Search companies... (e.g. AlphaGrep, Jane Street, Optiver)"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          className="pl-9"
        />
      </div>

      {loading ? (
        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
          {Array.from({ length: 6 }).map((_, i) => (
            <Skeleton key={i} className="h-32 rounded-lg" />
          ))}
        </div>
      ) : companies.length > 0 ? (
        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
          {companies.map((company) => (
            <Link key={company.id} href={`/companies/${company.id}`}>
              <Card className="h-full transition-colors hover:border-primary/30">
                <CardHeader className="pb-2">
                  <div className="flex items-start justify-between">
                    <div className="flex items-center gap-2">
                      <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-primary/10">
                        <Building2 className="h-4 w-4 text-primary" />
                      </div>
                      <CardTitle className="text-sm">{company.name}</CardTitle>
                    </div>
                    <ArrowRight className="h-4 w-4 text-muted-foreground" />
                  </div>
                </CardHeader>
                <CardContent>
                  {company.domain && (
                    <p className="text-xs text-muted-foreground">{company.domain}</p>
                  )}
                  {company.description && (
                    <p className="text-xs text-muted-foreground mt-1 line-clamp-2">{company.description}</p>
                  )}
                </CardContent>
              </Card>
            </Link>
          ))}
        </div>
      ) : debouncedQuery ? (
        <Card>
          <CardContent className="py-12 text-center">
            <Building2 className="mx-auto h-8 w-8 text-muted-foreground" />
            <p className="mt-3 text-sm text-muted-foreground">No companies found for "{debouncedQuery}"</p>
            <p className="text-xs text-muted-foreground mt-1">Try researching the company first via the API</p>
          </CardContent>
        </Card>
      ) : (
        <Card>
          <CardContent className="py-12 text-center">
            <Building2 className="mx-auto h-8 w-8 text-muted-foreground" />
            <p className="mt-3 text-sm text-muted-foreground">Search for a company to get started</p>
          </CardContent>
        </Card>
      )}
    </div>
  )
}
