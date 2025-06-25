import { openai } from "@ai-sdk/openai";
import scenario, { type AgentAdapter, AgentRole } from "@langwatch/scenario";
import { describe, it, expect } from "vitest";

import { customerSupportAgent as customerSupportAgentMastra } from "../agents/customer-support-agent";

const customerSupportAgent: AgentAdapter = {
  role: AgentRole.AGENT,
  call: async (input) => {
    const result = await customerSupportAgentMastra.generate(input.messages);
    return result.response.messages;
  },
};

describe("Customer Support Agent", () => {
  it("should call the getCustomerOrderHistor tool in the scenario", async () => {
    const result = await scenario.run({
      setId: "customer-support-agent",
      name: "checking the order status",
      description: `
       User is asking about order history.
      `,
      agents: [
        customerSupportAgent,
        scenario.userSimulatorAgent({ model: openai("gpt-4.1-mini") }),
      ],
      script: [
        scenario.user(),
        scenario.agent(),
        (state) => {
          expect(state.hasToolCall("getCustomerOrderHistory")).toBe(true);
        },
        scenario.succeed(),
      ],
    });
    expect(result.success).toBe(true);
  });
});
