import pytest
import scenario
from customer_support_agent import agent

scenario.configure(
    default_model="openai/gpt-4.1-mini",
    cache_key="42",
)


class Agent(scenario.AgentAdapter):
    async def call(self, input: scenario.AgentInput) -> scenario.AgentReturnTypes:
        # Use Pixelagent's chat interface for conversational responses
        user_message = input.last_new_user_message_str()
        
        print("User message:", user_message)

        # Run tool call
        response = agent.tool_call(user_message)

        print("Response:", response)
        
        # Return the response in the expected format
        return [{"role": "assistant", "content": response}]


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
                    "The agent should provide helpful information about orders",
                ],
            ),
        ],
    )
    print(result)

    assert result.success


@pytest.mark.agent_test
@pytest.mark.asyncio
async def test_customer_asking_for_refund():
    result = await scenario.run(
        name="refund",
        description="""
            The user is an annoyed customer who complains that the Airpods they received 
            are not working, asks if they can return it, and eventually asks to talk to a human.
        """,
        agents=[
            Agent(),
            scenario.UserSimulatorAgent(),
            scenario.JudgeAgent(
                criteria=[
                    "The agent explains the refund policy",
                    "The agent provides escalation options when requested",
                    "The agent should provide helpful customer service",
                ],
            ),
        ],
    )

    assert result.success
