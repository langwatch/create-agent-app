import uuid
import pytest
import scenario
from customer_support_crew import call_crew
from typing import Dict, Any
import dotenv

dotenv.load_dotenv()

scenario.configure(default_model="openai/gpt-4o-mini", cache_key="42")


class Agent(scenario.AgentAdapter):
    async def call(self, input: scenario.AgentInput) -> scenario.AgentReturnTypes:
        # Add the missing context parameter with thread_id
        context = {"thread_id": input.thread_id or str(uuid.uuid4())}
        result = await call_crew(input.last_new_user_message_str(), context)

        # Extract the assistant's response from the messages
        # The last message should be the assistant's response
        messages = result.get("messages", [])
        if messages:
            last_message = messages[-1]
            if last_message.get("role") == "assistant":
                return last_message.get("content", "")

        # Fallback if no assistant message found
        return "I apologize, but I encountered an issue processing your request."


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
