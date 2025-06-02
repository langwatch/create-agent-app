import { createServer } from "@inngest/agent-kit/server";
import { customerSupportAgent } from "./agents/customer-support-agent";

const server = createServer({
  agents: [customerSupportAgent],
});
server.listen(3000, () => console.log(`AgentKit server running!`));
