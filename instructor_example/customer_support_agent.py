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

# Initialize OpenAI client and patch with Instructor (following official docs)
client = instructor.from_openai(openai.OpenAI())


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

    @field_validator("confidence")
    def validate_confidence(cls, v):
        if v < 0.0 or v > 1.0:
            raise ValueError("Confidence must be between 0.0 and 1.0")
        return v


class CustomerSupportResponse(BaseModel):
    """Structured output for customer support responses"""

    message: str = Field(description="The response message to the customer")
    intent: CustomerIntent = Field(description="The classified intent")
    should_escalate: bool = Field(
        default=False, description="Whether this issue should be escalated to a human"
    )


class CustomerSupportAgent:
    """Customer support agent using Instructor's full capabilities"""

    def __init__(self):
        self.client = client

    def classify_intent(self, message: str) -> CustomerIntent:
        """Classify customer intent using Instructor's structured output"""
        return self.client.chat.completions.create(
            model="gpt-4o",
            response_model=CustomerIntent,
            messages=[
                {
                    "role": "system",
                    "content": "You are an intent classifier for a customer support system. Classify the customer's intent based on their message.",
                },
                {
                    "role": "user",
                    "content": f"Classify the intent of this message: {message}",
                },
            ],
        )

    def get_customer_order_history(self) -> List[OrderSummaryResponse]:
        """Get customer order history - Instructor will call this automatically"""
        return http_GET_customer_order_history()

    def get_order_status(self, order_id: str) -> OrderStatusResponse:
        """Get order status - Instructor will call this automatically"""
        return http_GET_order_status(order_id)

    def get_company_policy(self) -> DocumentResponse:
        """Get company policy - Instructor will call this automatically"""
        return http_GET_company_policy()

    def get_troubleshooting_guide(
        self, guide: Literal["internet", "mobile", "television", "ecommerce"]
    ) -> DocumentResponse:
        """Get troubleshooting guide - Instructor will call this automatically"""
        return http_GET_troubleshooting_guide(guide)

    def escalate_to_human(
        self, reason: str = "Customer requested escalation"
    ) -> Dict[str, str]:
        """Escalate to human - Instructor will call this automatically"""
        return {
            "status": "escalated",
            "reason": reason,
            "message": "I'm escalating this to a human agent who will assist you shortly.",
        }

    def run(self, message: str) -> str:
        """Main method using Instructor's automatic tool calling"""

        # Step 1: Classify intent
        intent = self.classify_intent(message)

        # Step 2: Generate response with automatic tool calling
        # Instructor will automatically call the appropriate tools based on the response
        response = self.client.chat.completions.create(
            model="gpt-4o",
            response_model=CustomerSupportResponse,
            messages=[
                {
                    "role": "system",
                    "content": """You are a customer support agent for XPTO Telecom. 
                    Generate helpful, accurate, and polite responses. 
                    Use the available tools when needed to gather information.
                    Always format responses clearly using markdown.
                    
                    Available tools:
                    - get_customer_order_history(): Get customer's order history
                    - get_order_status(order_id): Get status of a specific order
                    - get_company_policy(): Get company policy document
                    - get_troubleshooting_guide(guide): Get troubleshooting guide for internet/mobile/television/ecommerce
                    - escalate_to_human(reason): Escalate to human agent
                    """,
                },
                {
                    "role": "user",
                    "content": f"Customer message: {message}\nIntent: {intent.intent} (confidence: {intent.confidence})",
                },
            ],
        )

        # Log the interaction
        print(f"Intent: {intent.intent} (confidence: {intent.confidence})")
        print(f"Should escalate: {response.should_escalate}")

        return response.message


def main():
    """Example usage of the Instructor customer support agent"""
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
