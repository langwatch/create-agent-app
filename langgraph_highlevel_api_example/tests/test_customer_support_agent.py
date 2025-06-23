from typing import List
import pytest

import scenario
from customer_support_agent import agent
from langchain_core.messages import (
    BaseMessage,
    HumanMessage,
    convert_to_openai_messages,
)

scenario.configure(
    default_model="openai/gpt-4.1-mini",
    cache_key="42",
)


class Agent(scenario.AgentAdapter):
    async def call(self, input: scenario.AgentInput) -> scenario.AgentReturnTypes:
        result: List[BaseMessage] = []
        for task in agent.stream(
            {
                "messages": [
                    HumanMessage(content=input.last_new_user_message_str()),
                ]
            },
            {
                "configurable": {
                    "thread_id": input.thread_id,
                }
            },
        ):
            for _, task_result in task.items():
                result += task_result["messages"]

        return convert_to_openai_messages(result)  # type: ignore


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
