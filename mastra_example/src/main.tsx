import { StrictMode } from "react";
import { createRoot } from "react-dom/client";
import "./index.css";
import App from "./App.tsx";
import { CopilotKit } from "@copilotkit/react-core";

createRoot(document.getElementById("root")!).render(
  <StrictMode>
    <CopilotKit
      runtimeUrl="http://localhost:4111/copilotkit"
      agent="weatherAgent"
    >
      <App />
    </CopilotKit>
  </StrictMode>
);
