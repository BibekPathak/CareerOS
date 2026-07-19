export { auth as middleware } from "@/lib/auth"

export const config = {
  matcher: ["/dashboard/:path*", "/companies/:path*", "/goals/:path*", "/messages/:path*", "/resume/:path*", "/settings/:path*"],
}
