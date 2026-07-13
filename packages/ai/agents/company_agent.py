import httpx

from packages.ai.base import BaseAgent, AgentContext
from packages.ai.client import get_openai_client
from packages.prompts.company import COMPANY_RESEARCH_SYSTEM_PROMPT
from packages.types.models import CompanyResearchInput, CompanyProfile


async def _fetch_url(url: str) -> str | None:
    try:
        async with httpx.AsyncClient(timeout=10.0, follow_redirects=True) as client:
            resp = await client.get(url, headers={"User-Agent": "CareerOS/1.0"})
            resp.raise_for_status()
            return resp.text[:8000]
    except Exception:
        return None


class CompanyResearchAgent(BaseAgent[CompanyResearchInput, CompanyProfile]):
    async def run(self, inputs: CompanyResearchInput) -> CompanyProfile:
        context_parts = []
        domain = f"{inputs.company_name.lower().replace(' ', '')}.com"

        homepage = await _fetch_url(f"https://{domain}")
        if homepage:
            context_parts.append(f"--- Homepage ({domain}) ---\n{homepage[:3000]}")

        careers = await _fetch_url(f"https://{domain}/careers")
        if careers:
            context_parts.append(f"--- Careers page ---\n{careers[:3000]}")

        blog = await _fetch_url(f"https://{domain}/blog")
        if not blog:
            blog = await _fetch_url(f"https://engineering.{domain}")
        if blog:
            context_parts.append(f"--- Blog ---\n{blog[:2000]}")

        web_context = "\n\n".join(context_parts) if context_parts else "No public web pages found."
        user_prompt = (
            f"Research the company '{inputs.company_name}' (domain: {domain}).\n\n"
            f"Public web content:\n{web_context}\n\n"
            f"Return a structured company profile."
        )

        return await self._llm_call(
            system_prompt=COMPANY_RESEARCH_SYSTEM_PROMPT,
            user_prompt=user_prompt,
            response_model=CompanyProfile,
        )


async def research_company(company_name: str, api_key: str | None = None) -> CompanyProfile:
    client = get_openai_client(api_key)
    agent = CompanyResearchAgent(AgentContext(openai_client=client))
    return await agent.run(CompanyResearchInput(company_name=company_name))
