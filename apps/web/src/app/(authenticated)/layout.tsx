import { AuthProvider } from "@/components/auth/auth-provider"
import { Sidebar } from "@/components/auth/sidebar"
import { TopBar } from "@/components/auth/topbar"

export default function AuthenticatedLayout({ children }: { children: React.ReactNode }) {
  return (
    <AuthProvider>
      <div className="flex h-screen">
        <Sidebar />
        <div className="flex flex-1 flex-col overflow-hidden">
          <TopBar />
          <main className="flex-1 overflow-y-auto p-6">
            {children}
          </main>
        </div>
      </div>
    </AuthProvider>
  )
}
