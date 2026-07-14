import httpx

from packages.ai.base import BaseAgent, AgentContext
from packages.ai.client import get_openai_client
from packages.prompts.company import COMPANY_RESEARCH_SYSTEM_PROMPT
from packages.types.models import (
    CompanyResearchInput, CompanyIntelligence, HiringVelocity, Recruiter,
    Intern, Promotion, ConferenceTalk, GitHubRepo,
)


async def _fetch_url(url: str, max_length: int = 8000) -> str | None:
    try:
        async with httpx.AsyncClient(timeout=10.0, follow_redirects=True) as client:
            resp = await client.get(url, headers={"User-Agent": "CareerOS/1.0"})
            resp.raise_for_status()
            return resp.text[:max_length]
    except Exception:
        return None


class CompanyResearchAgent(BaseAgent[CompanyResearchInput, CompanyIntelligence]):
    async def run(self, inputs: CompanyResearchInput) -> CompanyIntelligence:
        context_parts = []
        domain = f"{inputs.company_name.lower().replace(' ', '')}.com"
        org_name = inputs.company_name.lower().replace(' ', '')

        homepage = await _fetch_url(f"https://{domain}")
        if homepage:
            context_parts.append(f"--- Homepage ({domain}) ---\n{homepage[:4000]}")

        careers = await _fetch_url(f"https://{domain}/careers")
        if careers:
            context_parts.append(f"--- Careers page ---\n{careers[:4000]}")

        blog = await _fetch_url(f"https://{domain}/blog")
        if not blog:
            blog = await _fetch_url(f"https://engineering.{domain}")
        if blog:
            context_parts.append(f"--- Blog ---\n{blog[:3000]}")

        team = await _fetch_url(f"https://{domain}/team")
        if team:
            context_parts.append(f"--- Team page ---\n{team[:4000]}")

        about = await _fetch_url(f"https://{domain}/about")
        if about:
            context_parts.append(f"--- About page ---\n{about[:3000]}")

        jobs_page = await _fetch_url(f"https://{domain}/jobs")
        if jobs_page:
            context_parts.append(f"--- Jobs page ---\n{jobs_page[:4000]}")

        github_org = await _fetch_url(f"https://api.github.com/orgs/{org_name}", max_length=6000)
        if github_org:
            context_parts.append(f"--- GitHub org ---\n{github_org}")

        github_repos = await _fetch_url(
            f"https://api.github.com/orgs/{org_name}/repos?sort=stars&per_page=10",
            max_length=8000,
        )
        if github_repos:
            context_parts.append(f"--- GitHub repos ---\n{github_repos}")

        crunchbase = await _fetch_url(f"https://www.crunchbase.com/organization/{org_name}", max_length=3000)
        if crunchbase:
            context_parts.append(f"--- Crunchbase ---\n{crunchbase[:2000]}")

        web_context = "\n\n".join(context_parts) if context_parts else "No public web pages found."
        user_prompt = (
            f"Research the company '{inputs.company_name}' (domain: {domain}).\n\n"
            f"Public web content:\n{web_context}\n\n"
            f"Return a structured company intelligence profile with all available fields."
        )

        return await self._llm_call(
            system_prompt=COMPANY_RESEARCH_SYSTEM_PROMPT,
            user_prompt=user_prompt,
            response_model=CompanyIntelligence,
        )


async def research_company(company_name: str, api_key: str | None = None) -> CompanyIntelligence:
    client = get_openai_client(api_key)
    agent = CompanyResearchAgent(AgentContext(openai_client=client))
    return await agent.run(CompanyResearchInput(company_name=company_name))
