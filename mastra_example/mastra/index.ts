import { Mastra } from "@mastra/core/mastra";
import { PinoLogger } from "@mastra/loggers";
import { LibSQLStore } from "@mastra/libsql";

import { customerSupportAgent } from "./agents/customer-support-agent";
import { registerCopilotKit } from "@mastra/agui";

export const mastra = new Mastra({
  agents: { customerSupportAgent },
  storage: new LibSQLStore({
    url: ":memory:",
  }),
  logger: new PinoLogger({
    name: "Mastra",
    level: "info",
  }),
  server: {
    cors: {
      origin: "*",
      allowMethods: ["*"],
      allowHeaders: ["*"],
    },
    apiRoutes: [
      registerCopilotKit({
        path: "/copilotkit",
        resourceId: "customerSupportAgent",
      }),
    ],
  },
  telemetry: {
    serviceName: "customer-support-agent",
    enabled: true,
    sampling: {
      type: "always_on",
    },
    export: {
      type: "otlp",
      endpoint: "https://app.langwatch.ai/api/otel/v1/traces",
      headers: {
        "Authorization": `Bearer ${process.env.LANGWATCH_API_KEY}`,
      },
    }
  }
});
