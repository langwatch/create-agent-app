import uuid
import pytest

from scenario import Scenario, TestingAgent
from customer_support_agent import call_agent

Scenario.configure(
    testing_agent=TestingAgent(model="gemini/gemini-2.5-flash-preview-04-17"),
    cache_key="42",
)


@pytest.mark.agent_test
@pytest.mark.asyncio
async def test_get_order_status():
    scenario = Scenario(
        "User asks about the status of their last order",
        agent=call_agent,
        success_criteria=[
            "The agent replies with the order status",
        ],
        failure_criteria=[
            "The agent says it does not have access to the user's order history",
            "Agent should not ask for the order id without giving the user options to choose from",
        ],
    )

    await scenario.run({"thread_id": uuid.uuid4()})


@pytest.mark.agent_test
@pytest.mark.asyncio
async def test_get_customer_asking_for_a_refund():
    scenario = Scenario(
        "User complains that the Airpods they received are not working, asks if they can return it, gets annoyed, asks for a refund",
        agent=call_agent,
        strategy="behave as a very annoyed customer",
        success_criteria=[
            "The agent explains the refund policy",
            "The agent hands it over to a human agent",
        ],
        failure_criteria=[
            "The agent says it does not have access to the user's order history",
            "Agent should not ask for the order id without giving the user options to choose from",
        ],
    )

    await scenario.run({"thread_id": uuid.uuid4()})
