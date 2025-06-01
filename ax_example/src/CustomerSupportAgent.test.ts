import { Scenario, TestableAgent, Verdict } from "@langwatch/scenario-ts";
import { describe, expect, it } from "vitest";
import { customerSupportAgent } from "./CustomerSupportAgent";

describe("Customer Support Agent", () => {
  it("gets order status", async () => {
    try {
      const scenario = new Scenario({
        description: "User asks about the status of their last order",
        strategy: "",
        successCriteria: ["The agent replies with the order status"],
        failureCriteria: [
          "The agent says it does not have access to the user's order history",
          "Agent should not ask for the order id without giving the user options to choose from",
        ],
      });

      const agent = new CustomerSupportAgent();

      const result = await scenario.run({ agent, maxTurns: 10 });

      expect(result.verdict).toBe(Verdict.Success);
    } catch (error) {
      console.error(error.cause);
      throw error;
    }
  });

  it("replies customer asking for a refund", async () => {
    const scenario = new Scenario({
      description:
        "User complains that the Airpods they received are not working, asks if they can return it, gets annoyed, asks for a refund",
      strategy: "behave as a very annoyed customer",
      successCriteria: [
        "The agent explains the refund policy",
        "The agent hands it over to a human agent",
      ],
      failureCriteria: [
        "The agent says it does not have access to the user's order history",
        "Agent should not ask for the order id without giving the user options to choose from",
      ],
    });

    const agent = new CustomerSupportAgent();

    const result = await scenario.run({ agent, maxTurns: 10 });

    expect(result.verdict).toBe(Verdict.Success);
  });
});

class CustomerSupportAgent implements TestableAgent {
  async invoke(prompt: string) {
    const result = await customerSupportAgent.forward(null, {
      question: prompt,
    } as any);

    return { text: result.answer as string };
  }
}
