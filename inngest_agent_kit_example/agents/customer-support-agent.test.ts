import scenario, { type AgentAdapter, AgentRole } from "@langwatch/scenario";
import { describe, expect, it } from "vitest";
import { customerSupportAgent } from "./customer-support-agent";
import { openai } from "@ai-sdk/openai";
import { createState, Message } from "@inngest/agent-kit";

const createAgent = (): AgentAdapter => {
  const agentState = createState();

  return {
    role: AgentRole.AGENT,
    call: async (input) => {
      const latestMessage = input.messages.at(-1)?.content || "";
      const messageContent = typeof latestMessage === "string" ? latestMessage : JSON.stringify(latestMessage);

      let lastMessage: Message | undefined;
      while (!lastMessage || lastMessage?.type === "tool_call") {
        const result = await customerSupportAgent.run(messageContent, {
          state: agentState,
        });
        agentState.appendResult(result);
        lastMessage = result.output.at(-1);
      }
  
      if (lastMessage?.type === "text") {
        return lastMessage.content as string;
      }
      
      return JSON.stringify(lastMessage);
    },
  };
};

describe("Customer Support Agent", () => {
  it("gets order status", async () => {
    const result = await scenario.run({
      name: "Customer Support Agent - Order Status",
      setId: "customer-support-agent",
      description: "User asks about the status of their last order",
      agents: [
        createAgent(),
        scenario.userSimulatorAgent({
          model: openai("gpt-4.1"),
        }),
        scenario.judgeAgent({
          model: openai("gpt-4.1"),
          criteria: [
            "The agent replies with the order status",
            "The agent should NOT say it does not have access to the user's order history",
            "The agent should NOT ask for the order ID without providing the user with order options",
          ],
        }),
      ],
    });

    expect(result.success).toBe(true);
  });

  it("replies customer asking for a refund", async () => {
    const result = await scenario.run({
      name: "Customer Support Agent - Refund Request",
      setId: "customer-support-agent",
      description:
        "User complains that the Airpods they received are not working, asks if they can return it, gets annoyed, asks for a refund",
      agents: [
        createAgent(),
        scenario.userSimulatorAgent({
          model: openai("gpt-4.1"),
        }),
        scenario.judgeAgent({
          model: openai("gpt-4.1"),
          criteria: [
            "The agent explains the refund policy",
            "The agent hands it over to a human agent",
            "The agent should NOT say it does not have access to the user's order history",
            "The agent should NOT ask for the order ID without providing the user with order options",
          ],
        }),
      ],
    });

    expect(result.success).toBe(true);
  });
});
