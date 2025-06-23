from typing import List
import pytest

import scenario
from customer_support_agent import agent
from pydantic_ai.messages import ModelMessage
from pydantic_graph import End
from pydantic_ai.models.openai import OpenAIModel
from pydantic_ai.providers.openai import OpenAIProvider

scenario.configure(
    default_model="openai/gpt-4.1-mini",
    cache_key="42",
)


class Agent(scenario.AgentAdapter):
    def __init__(self):
        # In-Memory History
        # Pydantic AI does not have a built-in memory mechanism yet: https://github.com/pydantic/pydantic-ai/issues/530
        self.history: dict[str, List[ModelMessage]] = {}

    async def call(self, input: scenario.AgentInput) -> scenario.AgentReturnTypes:
        if input.thread_id not in self.history:
            self.history[input.thread_id] = []

        user_message = input.last_new_user_message_str()
        async with agent.iter(
            user_message,
            message_history=self.history[input.thread_id],
        ) as agent_run:
            next_node = agent_run.next_node  # start with the first node
            nodes = [next_node]
            while not isinstance(next_node, End):
                next_node = await agent_run.next(next_node)
                nodes.append(next_node)

            if not agent_run.result:
                raise Exception("No result from agent")

            new_messages = agent_run.result.new_messages()
            self.history[input.thread_id] += new_messages

            new_messages_openai_format = await OpenAIModel(
                "any", provider=OpenAIProvider(api_key="bogus")
            )._map_messages(new_messages)

            return new_messages_openai_format


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
