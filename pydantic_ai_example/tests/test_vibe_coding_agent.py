import pytest

from vibe_coding_agent import VibeCodingAgent
import scenario
from create_agent_app.common.vibe_coding.utils import clone_template
from pydantic_graph import End
from pydantic_ai.models.openai import OpenAIModel
from pydantic_ai.providers.openai import OpenAIProvider

scenario.configure(
    default_model="openai/gpt-4.1-mini",
    cache_key="42",
)


class Agent(scenario.AgentAdapter):
    def __init__(self, template_path: str):
        self.agent = VibeCodingAgent(template_path)

    async def call(self, input: scenario.AgentInput) -> scenario.AgentReturnTypes:
        new_messages = await self.agent.call(input.last_new_user_message_str())

        new_messages_openai_format = await OpenAIModel(
            "any", provider=OpenAIProvider(api_key="bogus")
        )._map_messages(new_messages)

        return new_messages_openai_format


@pytest.mark.agent_test
@pytest.mark.asyncio
async def test_vibe_coding():
    template_path = clone_template()
    print(f"\n-> Vibe coding template path: {template_path}\n")

    result = await scenario.run(
        name="user wants to create a new landing page for their dog walking startup",
        description="""
            User wants to create a new landing page for their dog walking startup.

            They send the first message to generate the landing page, then a single follow up request to extend it.
        """,
        agents=[
            Agent(template_path),
            scenario.UserSimulatorAgent(),
            scenario.JudgeAgent(
                criteria=[
                    "agent reads the files before go and making changes",
                    "agent modified the index.css file",
                    "agent modified the Index.tsx file",
                    "agent created a comprehensive landing page",
                    "agent extended the landing page with a new section",
                    "agent DOES NOT say it can't read the file",
                    "agent DOES NOT produce incomplete code or is too lazy to finish",
                ],
            ),
        ],
    )

    print(f"\n-> Done, check the results at: {template_path}\n")

    assert result.success
