import json
from typing import Any, List, Literal
import dotenv

dotenv.load_dotenv()

from create_agent_app.common.cutomer_support.mocked_apis import (
    DocumentResponse,
    OrderSummaryResponse,
    OrderStatusResponse,
    http_GET_company_policy,
    http_GET_customer_order_history,
    http_GET_order_status,
    http_GET_troubleshooting_guide,
)
import litellm
from litellm import Choices, Message, cast
from litellm.types.utils import ModelResponse
from function_schema import get_function_schema


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


def get_customer_order_history() -> List[OrderSummaryResponse]:
    """
    Get the current customer order history

    Returns:
        The customer order history
    """
    return http_GET_customer_order_history()


def get_order_status(order_id: str) -> OrderStatusResponse:
    """
    Get the status of a specific order

    Args:
        order_id: The ID of the order to get the status of

    Returns:
        The status of the order
    """
    return http_GET_order_status(order_id)


def get_company_policy() -> DocumentResponse:
    """
    Get the company policy

    Returns:
        The company policy document
    """
    return http_GET_company_policy()


def get_troubleshooting_guide(
    guide: Literal["internet", "mobile", "television", "ecommerce"],
) -> DocumentResponse:
    """
    Get the troubleshooting guide

    Args:
        guide: The guide to get the troubleshooting guide for, one of "internet", "mobile", "television", "ecommerce"

    Returns:
        The troubleshooting guide document
    """
    return http_GET_troubleshooting_guide(guide)


def escalate_to_human() -> dict[str, str]:
    """
    Escalate to human, retrieves a link for the customer to open a ticket with the support team

    Returns:
        A link for the customer to open a ticket with the support team
    """
    return {
        "url": "https://support.xpto.com/tickets",
        "type": "escalation",
    }


# In-memory history
history: dict[str, List[Message]] = {}

tools = [
    get_customer_order_history,
    get_order_status,
    get_company_policy,
    get_troubleshooting_guide,
    escalate_to_human,
]


def call_agent(message: str, context: dict[str, Any]) -> dict[str, Any]:
    thread_id = context["thread_id"]
    if thread_id not in history:
        history[thread_id] = []
    history[thread_id].append(
        Message(
            role="user",  # type: ignore
            content=message,
        )
    )

    new_messages: List[Message] = []

    while True:
        response = cast(
            ModelResponse,
            litellm.completion(
                model="gemini/gemini-2.5-flash-preview-04-17",
                messages=(
                    [{"role": "system", "content": SYSTEM_PROMPT}]
                    + history[thread_id]
                    + new_messages
                ),
                tools=[get_function_schema(tool) for tool in tools],
            ),
        )
        message_ = cast(Message, cast(Choices, response.choices[0]).message)
        new_messages.append(message_)

        if message_.tool_calls:
            tools_by_name = {tool.__name__: tool for tool in tools}
            for tool_call in message_.tool_calls:
                tool_call_name = tool_call.function.name
                tool_call_args = json.loads(tool_call.function.arguments)
                if tool_call_name in tools_by_name:
                    tool_call_function = tools_by_name[tool_call_name]
                    tool_call_function_response = tool_call_function(**tool_call_args)
                    new_messages.append(
                        Message(
                            role="tool",  # type: ignore
                            tool_call_id=tool_call.id,
                            content=json.dumps(tool_call_function_response),
                        )
                    )
                else:
                    raise ValueError(f"Tool {tool_call_name} not found")
        else:
            break

    history[thread_id] += new_messages

    return {
        "messages": new_messages,
    }
