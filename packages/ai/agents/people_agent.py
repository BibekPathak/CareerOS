import httpx

from packages.ai.base import BaseAgent, AgentContext
from packages.ai.client import get_openai_client
from packages.prompts.people import PEOPLE_DISCOVERY_SYSTEM_PROMPT
from packages.types.models import PeopleDiscoveryInput, PeopleDiscoveryOutput, Person


class PeopleDiscoveryAgent(BaseAgent[PeopleDiscoveryInput, PeopleDiscoveryOutput]):
    async def run(self, inputs: PeopleDiscoveryInput) -> PeopleDiscoveryOutput:
        context_parts = []
        domain = inputs.company_domain or f"{inputs.company_name.lower().replace(' ', '')}.com"

        team_page = await self._fetch_url(f"https://{domain}/team")
        if team_page:
            context_parts.append(f"--- Team page ({domain}/team) ---\n{team_page[:4000]}")

        about_page = await self._fetch_url(f"https://{domain}/about")
        if about_page:
            context_parts.append(f"--- About page ---\n{about_page[:4000]}")

        github_url = f"github.com/{inputs.company_name.lower().replace(' ', '')}"
        github_page = await self._fetch_url(f"https://{github_url}/orgs/{inputs.company_name.lower().replace(' ', '')}/people")
        if github_page:
            context_parts.append(f"--- GitHub org ---\n{github_page[:4000]}")

        web_context = "\n\n".join(context_parts) if context_parts else "No team pages found."
        user_prompt = (
            f"Find people working at '{inputs.company_name}' (domain: {domain}).\n\n"
            f"Public web content:\n{web_context}\n\n"
            f"Return a list of people with their roles and public profiles."
        )

        return await self._llm_call(
            system_prompt=PEOPLE_DISCOVERY_SYSTEM_PROMPT,
            user_prompt=user_prompt,
            response_model=PeopleDiscoveryOutput,
        )

    async def _fetch_url(self, url: str) -> str | None:
        try:
            async with httpx.AsyncClient(timeout=10.0, follow_redirects=True) as client:
                resp = await client.get(url, headers={"User-Agent": "CareerOS/1.0"})
                resp.raise_for_status()
                return resp.text
        except Exception:
            return None


async def discover_people(company_name: str, domain: str | None = None, api_key: str | None = None) -> list[Person]:
    client = get_openai_client(api_key)
    agent = PeopleDiscoveryAgent(AgentContext(openai_client=client))
    result = await agent.run(PeopleDiscoveryInput(company_name=company_name, company_domain=domain))
    return result.people
