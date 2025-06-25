import scenario, { type AgentAdapter, AgentRole } from "@langwatch/scenario";
import { describe, expect, it } from "vitest";
import { customerSupportAgent } from "../agents/customer-support-agent";
import { openai } from "@ai-sdk/openai";

const agent: AgentAdapter = {
  role: AgentRole.AGENT,
  call: async (input) => {
    const result = await customerSupportAgent.generate(input.messages);
    return result.text;
  },
};

describe("Customer Support Agent", () => {
  it("replies customer asking for a refund", async () => {
    const result = await scenario.run({
      name: "Customer Support Agent",
      setId: "customer-support-agent",
      description:
        "User complains that the Airpods they received are not working, asks if they can return it, gets annoyed, asks for a refund",
      agents: [
        agent,
        scenario.userSimulatorAgent({ model: openai("gpt-4.1-mini") }),
        scenario.judgeAgent({
          criteria: [
            "The agent explains the refund policy",
            "The agent hands it over to a human agent",
            "The agent should NOT say it doesn't have access to the user's order history",
            "The agent should NOT ask for the order id without first giving the user a list of options to choose from",
          ],
          model: openai("gpt-4.1-mini"),
        }),
      ],
    });

    expect(result.success).toBe(true);
  });
});
