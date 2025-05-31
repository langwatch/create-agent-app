import {
  useCopilotAction,
  type CatchAllFrontendAction,
} from "@copilotkit/react-core";
import { CopilotChat } from "@copilotkit/react-ui";
import "@copilotkit/react-ui/styles.css";
import { useState } from "react";

function App() {
  const [todos, setTodos] = useState<string[]>([]);

  useCopilotAction({
    name: "addTodoItem",
    description: "Add a new todo item to the list",
    parameters: [
      {
        name: "todoText",
        type: "string",
        description: "The text of the todo item to add",
        required: true,
      },
    ],
    handler: async ({ todoText }) => {
      setTodos([...todos, todoText]);
    },
    render: ({ status, args }) => {
      const { todoText } = args;

      if (status === "inProgress") {
        return <div className="text-yellow-500">Adding todo...</div>;
      } else {
        return (
          <div
            style={{
              backgroundColor: "lightgreen",
              padding: "10px",
              borderRadius: "5px",
              border: "1px solid lightgreen",
            }}
          >
            Todo added: {todoText}
          </div>
        );
      }
    },
  });

  useCopilotAction({
    name: "*",
    render: ({ name, status, args, result }) => {
      if (name === "weatherTool") {
        const { location } = args;
        const { temperature } = result ?? {};

        if (status === "inProgress") {
          return <div className="text-yellow-500">Getting weather...</div>;
        }
        return (
          <div
            style={{
              backgroundColor: "lightblue",
              padding: "10px",
              borderRadius: "5px",
              border: "1px solid lightblue",
              color: "black",
            }}
          >
            Weather for {location} is {temperature}°C
          </div>
        );
      }

      return null;
    },
  } as CatchAllFrontendAction);

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
