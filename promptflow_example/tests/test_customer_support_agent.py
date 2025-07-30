from typing import List
import pytest
import langwatch

import scenario
from customer_support_agent import agent

langwatch.setup()

scenario.configure(
    default_model="openai/gpt-4.1-mini",
    cache_key="42",
)


class AgentAdapter(scenario.AgentAdapter):
    def __init__(self):
        self.agent = agent

    async def call(self, input: scenario.AgentInput) -> scenario.AgentReturnTypes:
        # Run the agent with the user message
        response = self.agent.chat(input.last_new_user_message_str())

        # Return the response directly as a string
        return response


# Test scenarios
@pytest.mark.asyncio
async def test_order_inquiry():
    """Test the agent's ability to handle order inquiries."""

    result = await scenario.run(
        name="Order Inquiry Test",
        description="Test the agent's ability to handle order inquiries",
        agents=[
            AgentAdapter(),
            scenario.UserSimulatorAgent(),
            scenario.JudgeAgent(
                criteria=[
                    "The agent should greet the customer politely",
                    "The agent should ask how they can help",
                    "The agent should be ready to assist with order-related questions",
                ]
            ),
        ],
        set_id="customer-support-tests",
    )

    assert result.success is True


@pytest.mark.asyncio
async def test_troubleshooting_assistance():
    """Test the agent's ability to provide troubleshooting assistance."""

    result = await scenario.run(
        name="Troubleshooting Assistance Test",
        description="Test the agent's ability to provide troubleshooting assistance",
        agents=[
            AgentAdapter(),
            scenario.UserSimulatorAgent(),
            scenario.JudgeAgent(
                criteria=[
                    "The agent should offer to help with technical issues",
                    "The agent should be able to access troubleshooting guides",
                    "The agent should provide helpful technical support",
                ]
            ),
        ],
        set_id="customer-support-tests",
    )

    assert result.success is True


@pytest.mark.asyncio
async def test_policy_information():
    """Test the agent's ability to provide policy information."""

    result = await scenario.run(
        name="Policy Information Test",
        description="Test the agent's ability to provide policy information",
        agents=[
            AgentAdapter(),
            scenario.UserSimulatorAgent(),
            scenario.JudgeAgent(
                criteria=[
                    "The agent should be able to access company policies",
                    "The agent should provide accurate policy information",
                    "The agent should explain policies clearly",
                ]
            ),
        ],
        set_id="customer-support-tests",
    )

    assert result.success is True


@pytest.mark.asyncio
async def test_escalation():
    """Test the agent's ability to escalate when needed."""

    result = await scenario.run(
        name="Escalation Test",
        description="Test the agent's ability to escalate when needed",
        agents=[
            AgentAdapter(),
            scenario.UserSimulatorAgent(),
            scenario.JudgeAgent(
                criteria=[
                    "The agent should recognize when escalation is needed",
                    "The agent should provide escalation options",
                    "The agent should summarize the issue before escalating",
                ]
            ),
        ],
        set_id="customer-support-tests",
    )

    assert result.success is True
