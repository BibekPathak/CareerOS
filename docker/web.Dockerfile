FROM node:20-alpine AS base

FROM base AS deps
WORKDIR /app
COPY apps/web/package.json apps/web/package-lock.json* ./
RUN npm ci

FROM base AS runner
WORKDIR /app
COPY --from=deps /app/node_modules ./node_modules
COPY apps/web/ .

ENV NEXT_TELEMETRY_DISABLED=1

EXPOSE 3000

CMD ["npm", "run", "dev"]
