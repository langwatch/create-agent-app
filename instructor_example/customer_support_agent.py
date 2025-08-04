"""
Customer Support Agent using Instructor with Langwatch Integration

This example demonstrates how to create a customer support agent using Instructor
for structured outputs and Langwatch for observability.

References:
- https://github.com/jxnl/instructor
- https://langwatch.ai/
"""

import os
from typing import List, Literal, Dict, Any, Optional
from enum import Enum
import dotenv

dotenv.load_dotenv()

from create_agent_app.common.customer_support.mocked_apis import (
    DocumentResponse,
    OrderSummaryResponse,
    OrderStatusResponse,
    http_GET_company_policy,
    http_GET_customer_order_history,
    http_GET_order_status,
    http_GET_troubleshooting_guide,
)

import instructor
import openai
import langwatch
from pydantic import BaseModel, Field, field_validator


# Initialize Langwatch
langwatch.setup()

# Initialize OpenAI client
client = openai.OpenAI()

# Patch the client with Instructor for structured outputs
client = instructor.patch(client, mode=instructor.Mode.TOOLS)


class CustomerIntent(BaseModel):
    """Structured output for customer intent classification"""

    intent: Literal[
        "order_inquiry", "technical_support", "policy_question", "escalation", "general"
    ] = Field(description="The primary intent of the customer's message")
    confidence: float = Field(
        ge=0.0,
        le=1.0,
        description="Confidence score for the intent classification (0.0 to 1.0)",
    )
    requires_tool: bool = Field(
        description="Whether this intent requires using a tool to gather information"
    )


class ToolCall(BaseModel):
    """Structured output for tool calls"""

    tool_name: Literal[
        "get_customer_order_history",
        "get_order_status",
        "get_company_policy",
        "get_troubleshooting_guide",
        "escalate_to_human",
    ] = Field(description="The name of the tool to call")

    parameters: Dict[str, Any] = Field(
        default_factory=dict, description="Parameters to pass to the tool"
    )


class CustomerSupportResponse(BaseModel):
    """Structured output for customer support responses"""

    message: str = Field(description="The response message to the customer")
    intent: CustomerIntent = Field(description="The classified intent")
    tool_calls: List[ToolCall] = Field(
        default_factory=list, description="List of tools that need to be called"
    )
    should_escalate: bool = Field(
        default=False, description="Whether this issue should be escalated to a human"
    )


class EscalationRequest(BaseModel):
    """Structured output for escalation requests"""

    reason: str = Field(description="Reason for escalation")
    urgency: Literal["low", "medium", "high", "critical"] = Field(
        description="Urgency level of the escalation"
    )
    summary: str = Field(description="Summary of the issue and steps taken")


def get_customer_order_history() -> List[OrderSummaryResponse]:
    """Get the current customer order history"""
    return http_GET_customer_order_history()


def get_order_status(order_id: str) -> OrderStatusResponse:
    """Get the status of a specific order"""
    return http_GET_order_status(order_id)


def get_company_policy() -> DocumentResponse:
    """Get the company policy document"""
    return http_GET_company_policy()


def get_troubleshooting_guide(
    guide: Literal["internet", "mobile", "television", "ecommerce"],
) -> DocumentResponse:
    """Get troubleshooting guide for a specific service"""
    return http_GET_troubleshooting_guide(guide)


def escalate_to_human(reason: str, urgency: str, summary: str) -> Dict[str, str]:
    """Escalate the issue to a human agent"""
    return {
        "status": "escalated",
        "reason": reason,
        "urgency": urgency,
        "summary": summary,
        "message": "I'm escalating this to a human agent who will assist you shortly.",
    }


class CustomerSupportAgent:
    """Customer support agent using Instructor for structured outputs and Langfuse for observability"""

    def __init__(self):
        self.client = client

    def classify_intent(self, message: str) -> CustomerIntent:
        """Classify the customer's intent using structured output"""
        response = self.client.chat.completions.create(
            model="gpt-4o",
            response_model=CustomerIntent,
            messages=[
                {
                    "role": "system",
                    "content": """You are an intent classifier for a customer support system. 
                    Classify the customer's intent based on their message.""",
                },
                {
                    "role": "user",
                    "content": f"Classify the intent of this message: {message}",
                },
            ],
        )
        return response

    def generate_response(
        self,
        message: str,
        intent: CustomerIntent,
        tool_results: Optional[List[Dict]] = None,
    ) -> CustomerSupportResponse:
        """Generate a structured response based on intent and tool results"""

        # Build context from tool results
        context = ""
        if tool_results:
            context = "\n\nTool Results:\n" + "\n".join(
                [str(result) for result in tool_results]
            )

        response = self.client.chat.completions.create(
            model="gpt-4o",
            response_model=CustomerSupportResponse,
            messages=[
                {
                    "role": "system",
                    "content": """You are a customer support agent for XPTO Telecom. 
                    Generate helpful, accurate, and polite responses. Use tools when needed to gather information.
                    Always format responses clearly using markdown.""",
                },
                {
                    "role": "user",
                    "content": f"Customer message: {message}\nIntent: {intent.intent}\nConfidence: {intent.confidence}{context}",
                },
            ],
        )
        return response

    def execute_tools(self, tool_calls: List[ToolCall]) -> List[Dict]:
        """Execute the required tools and return results"""
        results = []

        for tool_call in tool_calls:
            try:
                if tool_call.tool_name == "get_customer_order_history":
                    result = get_customer_order_history()
                    results.append({"tool": tool_call.tool_name, "result": result})

                elif tool_call.tool_name == "get_order_status":
                    order_id = tool_call.parameters.get("order_id")
                    if order_id:
                        result = get_order_status(order_id)
                        results.append({"tool": tool_call.tool_name, "result": result})

                elif tool_call.tool_name == "get_company_policy":
                    result = get_company_policy()
                    results.append({"tool": tool_call.tool_name, "result": result})

                elif tool_call.tool_name == "get_troubleshooting_guide":
                    guide = tool_call.parameters.get("guide")
                    if guide:
                        result = get_troubleshooting_guide(guide)
                        results.append({"tool": tool_call.tool_name, "result": result})

                elif tool_call.tool_name == "escalate_to_human":
                    reason = tool_call.parameters.get(
                        "reason", "Customer requested escalation"
                    )
                    urgency = tool_call.parameters.get("urgency", "medium")
                    summary = tool_call.parameters.get(
                        "summary", "Issue requires human intervention"
                    )
                    result = escalate_to_human(reason, urgency, summary)
                    results.append({"tool": tool_call.tool_name, "result": result})

            except Exception as e:
                results.append({"tool": tool_call.tool_name, "error": str(e)})

        return results

    def run(self, message: str) -> str:
        """Main method to process customer messages"""

        # Step 1: Classify intent
        intent = self.classify_intent(message)

        # Step 2: Generate initial response with tool calls
        response = self.generate_response(message, intent)

        # Step 3: Execute tools if needed
        tool_results = []
        if response.tool_calls:
            tool_results = self.execute_tools(response.tool_calls)

            # Step 4: Generate final response with tool results
            response = self.generate_response(message, intent, tool_results)

        # Step 5: Score the interaction in Langfuse
        self.score_interaction(message, response, intent)

        # Step 6: Flush observations (Langwatch handles this automatically)
        pass

        return response.message

    def score_interaction(
        self, message: str, response: CustomerSupportResponse, intent: CustomerIntent
    ):
        """Score the interaction in Langwatch for monitoring"""
        try:
            # With Langwatch, scoring is handled automatically through the instrumentation
            # We can log additional metrics if needed
            print(f"Intent: {intent.intent} (confidence: {intent.confidence})")
            print(f"Tools used: {len(response.tool_calls)}")
            print(f"Should escalate: {response.should_escalate}")

        except Exception as e:
            print(f"Error scoring interaction: {e}")


def main():
    """Example usage of the customer support agent"""
    agent = CustomerSupportAgent()

    # Example interactions
    test_messages = [
        "I need help with my internet connection",
        "What's the status of my recent order?",
        "Can you tell me about your refund policy?",
        "I want to speak to a human agent",
    ]

    for message in test_messages:
        print(f"\nCustomer: {message}")
        response = agent.run(message)
        print(f"Agent: {response}")
        print("-" * 50)


if __name__ == "__main__":
    main()
