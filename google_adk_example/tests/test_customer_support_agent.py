from typing import List
import pytest


import scenario
from customer_support_agent import agent
from google.adk.sessions import InMemorySessionService
from google.adk.runners import Runner
from google.genai.types import Content, Part
import google.adk.models.lite_llm as litellm


scenario.configure(
    default_model="openai/gpt-4.1-mini",
    cache_key="42",
)


class Agent(scenario.AgentAdapter):
    def __init__(self):
        self.session_service = InMemorySessionService()

        self.runner = Runner(
            agent=agent,
            app_name="customer_support_agent",
            session_service=self.session_service,
        )

    async def call(self, input: scenario.AgentInput) -> scenario.AgentReturnTypes:
        session = await self.session_service.get_session(
            app_name="customer_support_agent",
            user_id="user_1",
            session_id=input.thread_id,
        )
        if not session:
            session = await self.session_service.create_session(
                app_name="customer_support_agent",
                user_id="user_1",
                session_id=input.thread_id,
            )

        user_message = Content(
            role="user", parts=[Part(text=input.last_new_user_message_str())]
        )
        contents: List[Content] = []
        async for event in self.runner.run_async(
            user_id="user_1", session_id=input.thread_id, new_message=user_message
        ):
            contents += [event.content] if event.content else []

        messages_openai_format = [
            litellm._content_to_message_param(content) for content in contents
        ]
        return messages_openai_format  # type: ignore


@pytest.mark.agent_test
@pytest.mark.asyncio
async def test_get_order_status():
    result = await scenario.run(
        name="order status",
        description="""
            User asks about the status of their last order.
        """,
        agents=[
            Agent(),
            scenario.UserSimulatorAgent(),
            scenario.JudgeAgent(
                criteria=[
                    "The agent replies with the order status",
                    "The agent should NOT say it has no access to the user's order history",
                    "The agent should NOT ask for the order id without first giving the user a list of options to choose from",
                ],
            ),
        ],
    )

    assert result.success


@pytest.mark.agent_test
@pytest.mark.asyncio
async def test_get_customer_asking_for_a_refund():
    result = await scenario.run(
        name="refund",
        description="""
            The user is a very annoyed customer, they complain that the Airpods they received are not working,
            asks if they can return it, gets annoyed, asks for a refund and eventually to talk to a human.
        """,
        agents=[
            Agent(),
            scenario.UserSimulatorAgent(),
            scenario.JudgeAgent(
                criteria=[
                    "The agent explains the refund policy",
                    "The agent hands it over to a human agent",
                    "The agent should NOT say it doesn't have access to the user's order history",
                    "The agent should NOT ask for the order id without first giving the user a list of options to choose from",
                ],
            ),
        ],
    )

    assert result.success
