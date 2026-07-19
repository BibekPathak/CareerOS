import NextAuth from "next-auth"
import GitHub from "next-auth/providers/github"
import Google from "next-auth/providers/google"

export const { auth, handlers: { GET, POST }, signIn, signOut } = NextAuth({
  providers: [
    GitHub({ clientId: process.env.AUTH_GITHUB_ID!, clientSecret: process.env.AUTH_GITHUB_SECRET! }),
    Google({ clientId: process.env.AUTH_GOOGLE_ID!, clientSecret: process.env.AUTH_GOOGLE_SECRET! }),
  ],
  pages: {
    signIn: "/auth/signin",
  },
  callbacks: {
    async session({ session, token }) {
      if (session.user && token.sub) {
        session.user.id = token.sub
      }
      return session
    },
  },
  trustHost: true,
})
