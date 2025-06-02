import { defineConfig, type ViteDevServer } from "vite";
import react from "@vitejs/plugin-react-swc";
import tailwindcss from "@tailwindcss/vite";
import type { IncomingMessage, ServerResponse } from "node:http";
import {
  CopilotRuntime,
  ExperimentalEmptyAdapter,
  copilotRuntimeNodeHttpEndpoint,
  langGraphPlatformEndpoint,
} from "@copilotkit/runtime";

const copilotKitPlugin = () => ({
  name: "copilotkit-middleware",
  configureServer: (server: ViteDevServer) => {
    const serviceAdapter = new ExperimentalEmptyAdapter();

    server.middlewares.use(
      "/copilotkit",
      (req: IncomingMessage, res: ServerResponse) => {
        const runtime = new CopilotRuntime({
          remoteEndpoints: [
            langGraphPlatformEndpoint({
              deploymentUrl: "http://localhost:2024",
              agents: [
                {
                  name: "customerSupportAgent",
                  description: "Customer support agent for XPTO company",
                },
              ],
            }),
          ],
        });

        const handler = copilotRuntimeNodeHttpEndpoint({
          endpoint: "/copilotkit",
          runtime,
          serviceAdapter,
        });

        return handler(req, res);
      }
    );
  },
});

// https://vite.dev/config/
export default defineConfig({
  plugins: [react(), tailwindcss(), copilotKitPlugin()],
});
