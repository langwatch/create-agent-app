import { createGoogleGenerativeAI } from "@ai-sdk/google";
import { Agent } from "@mastra/core/agent";
import { LibSQLStore } from "@mastra/libsql";
import { Memory } from "@mastra/memory";
import {
  httpGETCustomerOrderHistory,
  httpGETOrderStatus,
  httpGETCompanyPolicy,
  httpGETTroubleshootingGuide,
} from "@langwatch/create-agent-app";
import { createTool } from "@mastra/core";
import { z } from "zod";

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

export const getCustomerOrderHistoryTool = createTool({
  id: "get-customer-order-history",
  description: "Get the current customer order history",
  inputSchema: z.object({}),
  outputSchema: z.array(
    z.object({
      orderId: z.string(),
      items: z.array(z.string()),
      totalAmount: z.number(),
      orderDate: z.string(),
    })
  ),
  execute: async () => {
    return await httpGETCustomerOrderHistory();
  },
});

export const getOrderStatusTool = createTool({
  id: "get-order-status",
  description: "Get the status of a specific order",
  inputSchema: z.object({
    orderId: z.string().describe("The ID of the order to get the status of"),
  }),
  outputSchema: z.object({
    orderId: z.string(),
    status: z.enum(["pending", "shipped", "delivered", "cancelled"]),
  }),
  execute: async ({ context }) => {
    return await httpGETOrderStatus(context.orderId);
  },
});

export const getCompanyPolicyTool = createTool({
  id: "get-company-policy",
  description: "Get the company policy document",
  inputSchema: z.object({}),
  outputSchema: z.object({
    documentId: z.string(),
    documentName: z.string(),
    documentContent: z.string(),
  }),
  execute: async () => {
    return await httpGETCompanyPolicy();
  },
});

export const getTroubleshootingGuideTool = createTool({
  id: "get-troubleshooting-guide",
  description: "Get the troubleshooting guide for a specific topic",
  inputSchema: z.object({
    guide: z
      .enum(["internet", "mobile", "television", "ecommerce"])
      .describe("The guide to get the troubleshooting guide for"),
  }),
  outputSchema: z.object({
    documentId: z.string(),
    documentName: z.string(),
    documentContent: z.string(),
  }),
  execute: async ({ context }) => {
    return await httpGETTroubleshootingGuide(context.guide);
  },
});

export const escalateToHumanTool = createTool({
  id: "escalate-to-human",
  description:
    "Escalate to human support, retrieves a link for the customer to open a ticket",
  inputSchema: z.object({}),
  outputSchema: z.object({
    url: z.string(),
    type: z.literal("escalation"),
  }),
  execute: async () => {
    return {
      url: "https://support.xpto.com/tickets",
      type: "escalation" as const,
    };
  },
});

export const customerSupportAgent = new Agent({
  name: "Customer Support Agent",
  instructions: SYSTEM_PROMPT,
  model: createGoogleGenerativeAI({ apiKey: process.env.GEMINI_API_KEY }).chat(
    "gemini-2.5-flash-preview-04-17"
  ),
  tools: {
    getCustomerOrderHistoryTool,
    getOrderStatusTool,
    getCompanyPolicyTool,
    getTroubleshootingGuideTool,
    escalateToHumanTool,
  },
  memory: new Memory({
    storage: new LibSQLStore({
      url: "file:../mastra.db", // path is relative to the .mastra/output directory
    }),
  }),
});
