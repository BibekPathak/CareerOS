import Link from "next/link"

export default function Home() {
  return (
    <div className="flex min-h-screen flex-col items-center justify-center p-8">
      <div className="text-center space-y-6 max-w-lg">
        <h1 className="text-4xl font-bold tracking-tight">
          CareerOS
        </h1>
        <p className="text-lg text-muted-foreground">
          AI-powered career intelligence platform
        </p>
        <div className="flex justify-center gap-4">
          <Link
            href="/auth/signin"
            className="inline-flex items-center justify-center rounded-md bg-primary px-6 py-3 text-sm font-medium text-primary-foreground hover:bg-primary/90"
          >
            Get Started
          </Link>
          <Link
            href="/dashboard"
            className="inline-flex items-center justify-center rounded-md border border-input bg-background px-6 py-3 text-sm font-medium hover:bg-accent"
          >
            Dashboard
          </Link>
        </div>
      </div>
    </div>
  )
}
