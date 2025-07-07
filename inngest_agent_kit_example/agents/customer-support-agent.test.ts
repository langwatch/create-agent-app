import scenario, { type AgentAdapter, AgentRole } from "@langwatch/scenario";
import { describe, expect, it } from "vitest";
import { customerSupportAgent } from "./customer-support-agent";
import { openai } from "@ai-sdk/openai";

const agent: AgentAdapter = {
  role: AgentRole.AGENT,
  call: async (input) => {
    const prompt = input.messages
      .map((m) => `${m.role === "user" ? "User" : "Assistant"}: ${m.content}`)
      .join("\n");

    const result = await customerSupportAgent.run(prompt);
    const lastMessage = result.output.at(-1);

    if (lastMessage?.type === "text") {
      return lastMessage.content.toString();
    }

    return JSON.stringify(lastMessage);
  },
};

describe("Customer Support Agent", () => {
  it("gets order status", async () => {
    const result = await scenario.run({
      name: "Customer Support Agent - Order Status",
      setId: "customer-support-agent",
      description: "User asks about the status of their last order",
      agents: [
        agent,
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
        agent,
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
