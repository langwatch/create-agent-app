import os
import dotenv
import json
from typing import Any, Dict, List, Literal
from crewai import Agent, Crew, Task
from crewai.tools import BaseTool
from pydantic import BaseModel, Field
from create_agent_app.common.customer_support.mocked_apis import (
    DocumentResponse,
    OrderSummaryResponse,
    OrderStatusResponse,
    http_GET_company_policy,
    http_GET_customer_order_history,
    http_GET_order_status,
    http_GET_troubleshooting_guide,
)

dotenv.load_dotenv()

# In-memory storage for conversation history
conversation_history: Dict[str, List[Dict[str, Any]]] = {}

# System prompt matching the Agno version
SYSTEM_PROMPT = """
<Introduction>
You are an AI customer service agent for XPTO Telecom, a telecommunications company providing internet, mobile, and television services, as well as selling mobile devices and related electronics. Your primary goal is to assist customers with their inquiries efficiently and effectively. You should always strive to provide helpful, accurate, and polite responses.

Your core principles for interacting with users are:

*   **Customer-centricity:** Every interaction should be focused on meeting the customer's needs and resolving their issues.
*   **Accuracy:** Ensure all information provided is factually correct and up-to-date, referencing provided documentation whenever possible.
*   **Efficiency:** Aim to resolve customer issues quickly and effectively, minimizing the need for escalation.
*   **Professionalism:** Maintain a courteous and professional tone throughout the conversation.
*   **Empathy:** Acknowledge the customer's frustration and show understanding when appropriate.
</Introduction>

<Workflow>
Follow these steps to effectively assist customers:

1.  **Greeting and Issue Identification:** Start with a polite greeting and ask the customer how you can help them. Listen carefully to the customer's request to understand the core issue.
2.  **Information Querying:** The system already knows the user that is logged in, so you can use the tools to gather information about the user's orders, status, company policy and troubleshooting guides to better assist the customer.
3.  **Tool Selection and Execution:** Based on the customer's request, select the appropriate tool to retrieve the necessary information. Execute the tool.
4.  **Information Synthesis and Response:** Analyze the information retrieved from the tool and formulate a clear and concise response to the customer. Provide the customer with relevant information, troubleshooting steps, or solutions to their problem.
5.  **Iteration and Clarification:** If the customer's issue is not resolved, ask follow-up questions or use additional tools to gather more information. Iterate through the steps as needed.
6.  **Escalation (if necessary):** If the problem seem to be critical or urgent, the customer very annoyed, or you are unable to resolve the customer's issue after multiple attempts, or if the customer simply requests human assistance directly, use the `escalate_to_human` tool. Briefly summarize the issue and steps taken so far for the human agent.
7.  **Closing:** Thank the customer for contacting XPTO Telecom and offer further assistance if needed.

</Workflow>

<Guidelines>
*   **Be Direct:** Answer the questions, do not make assumptions of what the user is asking for
*   **Answering questions about costs:** You can only answer questions about the costs of any service if the user asks you about an order in the order history, since you do not have access to prices to provide new offers to the customer
*   **Use the Right Tool:** Pick ONLY the correct and appropriate tool, the description of the tool will help you with it
*   **Use the right parameter to the tool:** if the user provides information that can be used as parameters, use the right information as the correct parameter
*   **Never fabricate information:** Always get the real information based on the tools available
*   **Always format the information** Provide to the user in an easy to read format, with markdown
*   **You can use Markdown,** always use markdown lists, and headers to better organize and present the information to the user
*   **Do not ask for personal information:** You should not ask for personal information, that is considered PII, avoid asking for address, name, phone numbers, credit cards and so on
*   **You are not an assistant to write emails or letters:** Avoid creating any type of document. Just help the user with the options available to you

*   **Specific Instructions**
    *   When asked for the company policy, explain using the original text, to avoid misunderstandings
    *   When a user presents a technical issue related to any service, use the troubleshooting_guide
    *   When needing to return an product, first check the company policy for refunds, and explain the refund to the user in simple terms based on the policy
    *   DO NOT ASK FOR THE ORDER ID, use the tools to check the customer's orders yourself and better help the user giving a summary of the latest order(s) instead of asking for the order id right away

</Guidelines>

<Tone>
Maintain a friendly, helpful, and professional tone. Use clear and concise language that is easy for customers to understand. Avoid using technical jargon or slang.

Example:

*   **Good:** "Hello! I'm happy to help you with your XPTO Telecom service today. What can I assist you with?"
*   **Bad:** "Yo, what's up? You got problems with your XPTO? Lemme see what I can do."

</Tone>

<Info>
Today is 2025-04-19
</Info>
"""


class GetOrderStatusInput(BaseModel):
    """Input schema for getting order status"""

    order_id: str = Field(description="The order ID to look up")


class GetTroubleshootingGuideInput(BaseModel):
    """Input schema for getting troubleshooting guide"""

    guide: Literal["internet", "mobile", "television", "ecommerce"] = Field(
        description="The guide to get the troubleshooting guide for, one of: internet, mobile, television, ecommerce"
    )


class GetCustomerOrderHistoryTool(BaseTool):
    name: str = "get_customer_order_history"
    description: str = "Get the current customer order history"

    def _run(self) -> str:
        """Get customer order history"""
        return json.dumps(http_GET_customer_order_history())


class GetOrderStatusTool(BaseTool):
    name: str = "get_order_status"
    description: str = "Get the status of a specific order by order ID"
    args_schema: type[BaseModel] = GetOrderStatusInput

    def _run(self, order_id: str) -> str:
        """Get order status by ID"""
        return json.dumps(http_GET_order_status(order_id))


class GetCompanyPolicyTool(BaseTool):
    name: str = "get_company_policy"
    description: str = "Get the company policy document"

    def _run(self) -> str:
        """Get company policy document"""
        return json.dumps(http_GET_company_policy())


class GetTroubleshootingGuideTool(BaseTool):
    name: str = "get_troubleshooting_guide"
    description: str = (
        "Get the troubleshooting guide for one of: internet, mobile, television, ecommerce"
    )
    args_schema: type[BaseModel] = GetTroubleshootingGuideInput

    def _run(self, guide: str) -> str:
        """Get troubleshooting guide for the specified service type"""
        return json.dumps(http_GET_troubleshooting_guide(guide))


class EscalateToHumanTool(BaseTool):
    name: str = "escalate_to_human"
    description: str = (
        "Escalate to human, retrieves a link for the customer to open a ticket with the support team"
    )

    def _run(self) -> str:
        """Escalate to human support"""
        return json.dumps(
            {
                "url": "https://support.xpto.com/tickets",
                "type": "escalation",
            }
        )


def create_customer_support_crew() -> Crew:
    # Create tool instances
    get_customer_order_history_tool = GetCustomerOrderHistoryTool()
    get_order_status_tool = GetOrderStatusTool()
    get_company_policy_tool = GetCompanyPolicyTool()
    get_troubleshooting_guide_tool = GetTroubleshootingGuideTool()
    escalate_to_human_tool = EscalateToHumanTool()

    # Single agent matching the Agno version approach
    customer_support_agent = Agent(
        role="Customer Support Agent",
        goal="Provide excellent customer service and resolve customer issues efficiently",
        backstory=SYSTEM_PROMPT,
        verbose=True,
        allow_delegation=False,
        tools=[
            get_customer_order_history_tool,
            get_order_status_tool,
            get_company_policy_tool,
            get_troubleshooting_guide_tool,
            escalate_to_human_tool,
        ],
    )

    return customer_support_agent  # Return just the agent, not a crew


# Create the agent instance
customer_support_agent = create_customer_support_crew()


async def call_crew(message: str, context: Dict[str, Any]) -> Dict[str, Any]:
    thread_id = context.get("thread_id", "default")
    if thread_id not in conversation_history:
        conversation_history[thread_id] = []

    conversation_history[thread_id].append({"role": "user", "content": message})

    # Create a task for this specific customer message
    customer_support_task = Task(
        description=f"Handle the customer inquiry: '{message}'. Follow the workflow and guidelines provided in your backstory. Provide a helpful and professional response.",
        agent=customer_support_agent,
        expected_output="Comprehensive response to the customer inquiry",
    )

    # Create a crew with the agent and task
    crew = Crew(
        agents=[customer_support_agent],
        tasks=[customer_support_task],
        verbose=False,  # Set to False to reduce noise in tests
        process="sequential",
    )

    # Kickoff the crew
    result = crew.kickoff()

    # Extract the actual result string from CrewAI output
    if hasattr(result, "raw"):
        response_content = result.raw
    elif isinstance(result, str):
        response_content = result
    else:
        response_content = str(result)

    conversation_history[thread_id].append(
        {"role": "assistant", "content": response_content}
    )
    return {"messages": conversation_history[thread_id]}
