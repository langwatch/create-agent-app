import { CopilotKit } from "@copilotkit/react-core";
import { CopilotChat } from "@copilotkit/react-ui";
import "@copilotkit/react-ui/styles.css";

function App() {
  return (
    <CopilotKit
      runtimeUrl="http://localhost:4111/copilotkit"
      agent="customerSupportAgent"
    >
      <CustomerSupportChat />
    </CopilotKit>
  );
}

function CustomerSupportChat() {
  return (
    <CopilotChat
      labels={{
        title: "Your Assistant",
        initial: "Hi! 👋 How can I assist you today?",
      }}
    />
  );
}

export default App;
