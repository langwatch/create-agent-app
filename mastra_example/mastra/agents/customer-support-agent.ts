import { createGoogleGenerativeAI } from "@ai-sdk/google";
import opentelemetry from '@opentelemetry/api';
import { Agent } from "@mastra/core/agent";
import { LibSQLStore } from "@mastra/libsql";
import { Memory } from "@mastra/memory";
import {
  httpGETOrderStatus,
  httpGETCompanyPolicy,
  httpGETTroubleshootingGuide,
  httpGETCustomerOrderHistory,
} from "@langwatch/create-agent-app";
import { createTool } from "@mastra/core";
import { z } from "zod";
import { getPrompt } from "./prompts";


export const getCustomerOrderHistory = createTool({
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

export const getOrderStatus = createTool({
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

export const getCompanyPolicy = createTool({
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

export const getTroubleshootingGuide = createTool({
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

export const escalateToHuman = createTool({
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
  instructions: async () => {
    const response = await getPrompt("prompt_Zh3Sto74tKjjlrzH-L2y_");

    return response.prompt;
  },
  model: createGoogleGenerativeAI({ apiKey: process.env.GEMINI_API_KEY }).chat(
    "gemini-2.5-flash-preview-04-17"
  ),
  tools: {
    getCustomerOrderHistory,
    getOrderStatus,
    getCompanyPolicy,
    getTroubleshootingGuide,
    escalateToHuman,
  },
  memory: new Memory({
    storage: new LibSQLStore({
      url: "file:../mastra.db", // path is relative to the .mastra/output directory
    }),
  }),
});
