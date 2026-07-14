from packages.ai.base import BaseAgent, AgentContext
from packages.ai.client import get_openai_client
from packages.prompts.relationship import (
    RELATIONSHIP_GRAPH_SYSTEM_PROMPT,
    RELATIONSHIP_GRAPH_USER_PROMPT_TEMPLATE,
)
from packages.types.models import OrgGraphInput, OrgGraphOutput


class RelationshipGraphAgent(BaseAgent[OrgGraphInput, OrgGraphOutput]):
    async def run(self, inputs: OrgGraphInput) -> OrgGraphOutput:
        people_str = "\n".join(
            f"- {p.name} ({p.role or 'Unknown role'})"
            f"{' | expertise: ' + ', '.join(p.expertise_areas) if p.expertise_areas else ''}"
            for p in inputs.people
        )

        company_context = ""
        if inputs.company_profile:
            profile = inputs.company_profile
            parts = []
            if profile.org_chart_summary:
                parts.append(f"Org chart summary: {profile.org_chart_summary}")
            if profile.tech_stack:
                parts.append(f"Tech stack: {', '.join(profile.tech_stack)}")
            if profile.hiring_manager_name:
                parts.append(f"Hiring manager: {profile.hiring_manager_name}")
            if profile.recruiters:
                recruiters_str = "; ".join(f"{r.get('name', '?')} ({r.get('role', '?')})" for r in profile.recruiters)
                parts.append(f"Recruiters: {recruiters_str}")
            if profile.overview:
                parts.append(f"Overview: {profile.overview[:500]}")
            if parts:
                company_context = "\n\nCompany context:\n" + "\n".join(parts)

        user_prompt = RELATIONSHIP_GRAPH_USER_PROMPT_TEMPLATE.format(
            company_name=inputs.company_name,
            people_str=people_str,
            company_context=company_context,
        )

        return await self._llm_call(
            system_prompt=RELATIONSHIP_GRAPH_SYSTEM_PROMPT,
            user_prompt=user_prompt,
            response_model=OrgGraphOutput,
        )


async def build_relationship_graph(
    company_name: str,
    people: list["GraphPerson"],
    company_profile: "CompanyIntelligence | None" = None,
    api_key: str | None = None,
) -> OrgGraphOutput:
    from packages.types.models import GraphPerson, CompanyIntelligence

    client = get_openai_client(api_key)
    agent = RelationshipGraphAgent(AgentContext(openai_client=client))
    return await agent.run(OrgGraphInput(
        company_name=company_name,
        people=people,
        company_profile=company_profile,
    ))
