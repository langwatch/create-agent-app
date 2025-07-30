from typing import List
import pytest
import langwatch

import scenario
from customer_support_agent import agent
from openinference.instrumentation.smolagents import SmolagentsInstrumentor

langwatch.setup(instrumentors=[SmolagentsInstrumentor()])

scenario.configure(
    default_model="openai/gpt-4.1-mini",
    cache_key="42",
)


class AgentAdapter(scenario.AgentAdapter):
    def __init__(self):
        self.agent = agent

    async def call(self, input: scenario.AgentInput) -> scenario.AgentReturnTypes:
        # Run the agent with the user message
        result = self.agent.run(input.last_new_user_message_str(), reset=False)

        # Convert the result to the expected format
        # smolagents returns a string, so we wrap it in a message format
        return [{"role": "assistant", "content": str(result)}]


@pytest.mark.agent_test
@pytest.mark.asyncio
async def test_get_order_status():
    result = await scenario.run(
        name="order status",
        description="""
            User asks about the status of their last order.
        """,
        agents=[
            AgentAdapter(),
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
            AgentAdapter(),
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
