/**
 * XPTO Telecom Customer Support Cloudflare Worker
 * This worker implements the agent functionality using JavaScript with zero dependencies
 */

// Types are just for documentation since we're using plain JS
/**
 * @typedef {Object} OrderSummaryResponse
 * @property {string} order_id - The ID of the order
 * @property {string[]} items - List of items in the order
 * @property {number} total_amount - Total amount of the order
 * @property {string} order_date - Date of the order
 */

/**
 * @typedef {Object} OrderStatusResponse
 * @property {string} order_id - The ID of the order
 * @property {'pending'|'shipped'|'delivered'|'cancelled'} status - Status of the order
 */

/**
 * @typedef {Object} DocumentResponse
 * @property {string} document_id - The ID of the document
 * @property {string} document_name - Name of the document
 * @property {string} document_content - Content of the document
 */

/**
 * @typedef {Object} Message
 * @property {'user'|'assistant'|'system'|'tool'} role - Role of the message
 * @property {string} content - Content of the message
 * @property {string} [tool_call_id] - ID of the tool call this message is responding to
 * @property {Array<ToolCall>} [tool_calls] - Tool calls in this message
 */

/**
 * @typedef {Object} ToolCall
 * @property {string} id - ID of the tool call
 * @property {Object} function - Function details
 * @property {string} function.name - Name of the function
 * @property {string} function.arguments - Arguments for the function
 */

const SYSTEM_PROMPT = `
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
6.  **Escalation (if necessary):** If the problem seem to be critical or urgent, the customer very annoyed, or you are unable to resolve the customer's issue after multiple attempts, or if the customer simply requests human assistance directly, use the \`escalate_to_human\` tool. Briefly summarize the issue and steps taken so far for the human agent.
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
`;

// Mock data for testing
const MOCK_CUSTOMER_ORDER_HISTORY = [
  {
    order_id: "9127412",
    items: ["iPhone 14 Pro"],
    total_amount: 959,
    order_date: "2024-02-05",
  },
  {
    order_id: "3451323",
    items: ["Airpods Pro"],
    total_amount: 299,
    order_date: "2024-01-15",
  },
];

// In-memory history for conversations
const history = {};

/**
 * Get the customer order history
 * @returns {Promise<OrderSummaryResponse[]>} The customer order history
 */
async function get_customer_order_history() {
  // In a real implementation, this would fetch from an API
  return MOCK_CUSTOMER_ORDER_HISTORY;
}

/**
 * Get the status of a specific order
 * @param {string} order_id The ID of the order to get the status of
 * @returns {Promise<OrderStatusResponse>} The status of the order
 */
async function get_order_status(order_id) {
  // Validate the order exists
  if (!["9127412", "3451323"].includes(order_id)) {
    throw new Error("Order not found");
  }

  // Simulate API delay
  await new Promise((resolve) => setTimeout(resolve, 100));

  // Generate a random status for testing
  const statuses = ["pending", "shipped", "delivered", "cancelled"];
  const randomStatus = statuses[Math.floor(Math.random() * statuses.length)];

  return {
    order_id: order_id,
    status: randomStatus,
  };
}

/**
 * Get the company policy document
 * @param {Env} env - Environment containing ASSETS binding
 * @returns {Promise<DocumentResponse>} The company policy document
 */
async function get_company_policy(env) {
  // Simulate API delay
  await new Promise((resolve) => setTimeout(resolve, 100));

  // Fetch from ASSETS
  const response = await env.ASSETS.fetch("http://internal/company_policy.md");
  const document_content = await response.text();

  return {
    document_id: "company_policy",
    document_name: "Company Policy",
    document_content: document_content,
  };
}

/**
 * Get a troubleshooting guide
 * @param {string} guide The guide to get (one of "internet", "mobile", "television", "ecommerce")
 * @param {Env} env - Environment containing ASSETS binding
 * @returns {Promise<DocumentResponse>} The troubleshooting guide document
 */
async function get_troubleshooting_guide(guide, env) {
  // Validate the guide type
  if (!["internet", "mobile", "television", "ecommerce"].includes(guide)) {
    throw new Error(
      "Invalid guide type. Must be one of: internet, mobile, television, ecommerce",
    );
  }

  // Simulate API delay
  await new Promise((resolve) => setTimeout(resolve, 100));

  // Fetch from ASSETS
  const response = await env.ASSETS.fetch(
    `http://internal/troubleshooting_${guide}.md`,
  );
  const document_content = await response.text();
  console.log({ document_content });
  return {
    document_id: `troubleshooting_${guide}`,
    document_name: `Troubleshooting ${guide}`,
    document_content: document_content,
  };
}

/**
 * Escalate to human support
 * @returns {Promise<Object>} Escalation details
 */
async function escalate_to_human() {
  return {
    url: "https://support.xpto.com/tickets",
    type: "escalation",
  };
}

/**
 * Map tool name to the actual function
 * @param {string} toolName - Name of the tool to call
 * @param {Env} env - Environment containing ASSETS binding
 * @returns {Function} The tool function
 */
function getToolFunction(toolName, env) {
  const toolsMap = {
    get_customer_order_history: get_customer_order_history,
    get_order_status: get_order_status,
    get_company_policy: () => get_company_policy(env),
    get_troubleshooting_guide: (guide) => get_troubleshooting_guide(guide, env),
    escalate_to_human: escalate_to_human,
  };

  return toolsMap[toolName];
}

/**
 * Convert functions to OpenAI compatible tool schemas
 * @returns {Array<Object>} Array of tool definitions
 */
function getToolDefinitions() {
  return [
    {
      type: "function",
      function: {
        name: "get_customer_order_history",
        description: "Get the current customer order history",
        parameters: {
          type: "object",
          properties: {},
          required: [],
        },
      },
    },
    {
      type: "function",
      function: {
        name: "get_order_status",
        description: "Get the status of a specific order",
        parameters: {
          type: "object",
          properties: {
            order_id: {
              type: "string",
              description: "The ID of the order to get the status of",
            },
          },
          required: ["order_id"],
        },
      },
    },
    {
      type: "function",
      function: {
        name: "get_company_policy",
        description: "Get the company policy",
        parameters: {
          type: "object",
          properties: {},
          required: [],
        },
      },
    },
    {
      type: "function",
      function: {
        name: "get_troubleshooting_guide",
        description: "Get the troubleshooting guide",
        parameters: {
          type: "object",
          properties: {
            guide: {
              type: "string",
              enum: ["internet", "mobile", "television", "ecommerce"],
              description: "The guide to get the troubleshooting guide for",
            },
          },
          required: ["guide"],
        },
      },
    },
    {
      type: "function",
      function: {
        name: "escalate_to_human",
        description:
          "Escalate to human, retrieves a link for the customer to open a ticket with the support team",
        parameters: {
          type: "object",
          properties: {},
          required: [],
        },
      },
    },
  ];
}

/**
 * Call an LLM API with the appropriate prompt
 * @param {Array<Message>} messages - The messages to send
 * @param {Array<Object>} tools - The tools definitions
 * @returns {Promise<Object>} - The LLM response
 */
async function callLLM(messages, tools, OPENAI_API_KEY) {
  // Replace this with your preferred LLM API
  // This example uses the OpenAI-compatible format which is common across many providers
  const response = await fetch("https://api.openai.com/v1/chat/completions", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      Authorization: `Bearer ${OPENAI_API_KEY}`,
    },
    body: JSON.stringify({
      model: "gpt-4-turbo", // Replace with your preferred model
      messages: messages,
      tools: tools,
    }),
  });

  return await response.json();
}

/**
 * Process a customer message and handle the conversation
 * @param {string} message - The customer's message
 * @param {string} threadId - Unique identifier for the conversation
 * @param {Env} env - Environment containing ASSETS binding
 * @returns {Promise<Object>} - The response object
 */
async function callAgent(message, threadId, env, OPENAI_API_KEY) {
  // Initialize history for this thread if it doesn't exist
  if (!history[threadId]) {
    history[threadId] = [];
  }

  // Add user message to history
  history[threadId].push({
    role: "user",
    content: message,
  });

  const newMessages = [];
  const tools = getToolDefinitions();

  // Initial messages includes system prompt and conversation history
  const initialMessages = [
    { role: "system", content: SYSTEM_PROMPT },
    ...history[threadId],
  ];

  let currentMessages = initialMessages;
  let shouldContinue = true;

  while (shouldContinue) {
    // Call the LLM
    const response = await callLLM(currentMessages, tools, OPENAI_API_KEY);
    const assistantMessage = response.choices?.[0]?.message;
    console.log({ response });
    // Add the assistant message to new messages
    newMessages.push(assistantMessage);

    // Check if there are tool calls to handle
    if (assistantMessage.tool_calls && assistantMessage.tool_calls.length > 0) {
      for (const toolCall of assistantMessage.tool_calls) {
        const toolName = toolCall.function.name;
        const toolArgs = JSON.parse(toolCall.function.arguments);

        try {
          // Get and execute the appropriate tool function
          const toolFunction = getToolFunction(toolName, env);
          if (!toolFunction) {
            throw new Error(`Tool ${toolName} not found`);
          }

          const toolResponse = await toolFunction(...Object.values(toolArgs));

          // Add tool response to new messages
          newMessages.push({
            role: "tool",
            tool_call_id: toolCall.id,
            content: JSON.stringify(toolResponse),
          });
        } catch (error) {
          // Handle tool execution errors
          newMessages.push({
            role: "tool",
            tool_call_id: toolCall.id,
            content: JSON.stringify({ error: error.message }),
          });
        }
      }

      // Update messages for next iteration
      currentMessages = [...initialMessages, ...newMessages];
    } else {
      // No more tool calls, we're done
      shouldContinue = false;
    }
  }

  // Update conversation history
  history[threadId] = [...history[threadId], ...newMessages];

  // Return the new messages
  return {
    messages: newMessages,
  };
}

// Main worker entry point
export default {
  /**
   * Fetch handler for Cloudflare Worker
   * @param {Request} request - The incoming request
   * @param {Env} env - Environment variables and bindings
   * @param {Object} ctx - Execution context
   * @returns {Promise<Response>} - The response
   */
  async fetch(request, env, ctx) {
    // Only handle POST requests
    if (request.method !== "POST") {
      return new Response(JSON.stringify({ error: "Method not allowed" }), {
        status: 405,
        headers: { "Content-Type": "application/json" },
      });
    }

    try {
      // Parse the request body
      const requestData = await request.json();
      const { message, thread_id } = requestData;
      console.log({ message, thread_id });
      if (!message || !thread_id) {
        return new Response(
          JSON.stringify({ error: "Missing required fields" }),
          {
            status: 400,
            headers: { "Content-Type": "application/json" },
          },
        );
      }

      // Call the agent to process the message
      const result = await callAgent(
        message,
        thread_id,
        env,
        env.OPENAI_API_KEY,
      );

      // Return the response
      return new Response(JSON.stringify(result), {
        status: 200,
        headers: { "Content-Type": "application/json" },
      });
    } catch (error) {
      // Handle errors
      return new Response(JSON.stringify({ error: error.message }), {
        status: 500,
        headers: { "Content-Type": "application/json" },
      });
    }
  },
};

/**
 * Environment interface definition (for documentation)
 * @typedef {Object} Env
 * @property {Object} ASSETS - Asset binding for accessing static files
 * @property {string} OPENAI_API_KEY - API key for OpenAI or compatible LLM service
 */
