import os
from typing import Any
from pydantic_ai import Agent
from pydantic_ai.messages import ModelMessage, UserPromptPart
from pydantic_graph import End
from pydantic_ai.models.openai import OpenAIModel
from pydantic_ai.providers.openai import OpenAIProvider

from create_agent_app.common.vibe_coding.utils import (
    generate_directory_tree,
)


class VibeCodingAgent:
    def __init__(self, template_path: str):
        agent = Agent(
            "google-gla:gemini-2.5-flash-preview-04-17",
            system_prompt=f"""
        You are a coding assistant specialized in building whole new websites from scratch.

        You will be given a basic React, TypeScript, Vite, Tailwind and Radix UI template and will work on top of that. Use the components from the "@/components/ui" folder.

        On the first user request for building the application, start by the src/index.css and tailwind.config.ts files to define the colors and general application style.
        Then, start building the website, you can call tools in sequence as much as you want.

        You will be given tools to read file, create file and update file to carry on your work.

        You CAN access local files by using the tools provided, but you CANNOT run the application, do NOT suggest the user that.

        <execution_flow>
        1. Call the read_file tool to understand the current files before updating them or creating new ones
        2. Start building the website, you can call tools in sequence as much as you want
        3. Ask the user for next steps
        </execution_flow>

        <files>
        After the user request, you will be given the second part of this system prompt, containing the file present on the project using the <files/> tag.
        </files>
        """,
            model_settings={
                "parallel_tool_calls": False,
                "temperature": 0.0,
                "max_tokens": 8192,
            },
        )

        @agent.tool_plain(
            docstring_format="google", require_parameter_descriptions=True
        )
        def read_file(path: str) -> str:
            """Reads the content of a file.

            Args:
                path (str): The path to the file to read. Required.

            Returns:
                str: The content of the file.
            """
            try:
                with open(os.path.join(self.template_path, path), "r") as f:
                    return f.read()
            except FileNotFoundError:
                return f"Error: File {path} not found (double check the file path)"

        @agent.tool_plain(
            docstring_format="google", require_parameter_descriptions=True
        )
        def update_file(path: str, content: str):
            """Updates the content of a file.

            Args:
                path (str): The path to the file to update. Required.
                content (str): The full file content to write. Required.
            """
            try:
                with open(os.path.join(self.template_path, path), "w") as f:
                    f.write(content)
            except FileNotFoundError:
                return f"Error: File {path} not found (double check the file path)"

            return "ok"

        @agent.tool_plain(
            docstring_format="google", require_parameter_descriptions=True
        )
        def create_file(path: str, content: str):
            """Creates a new file with the given content.

            Args:
                path (str): The path to the file to create. Required.
                content (str): The full file content to write. Required.
            """
            os.makedirs(
                os.path.dirname(os.path.join(self.template_path, path)), exist_ok=True
            )
            with open(os.path.join(self.template_path, path), "w") as f:
                f.write(content)

            return "ok"

        self.agent = agent
        self.history: list[ModelMessage] = []
        self.template_path = template_path

    async def call_agent(self, message: str, context: dict[str, Any]):
        tree = generate_directory_tree(self.template_path)

        user_prompt = f"""{message}

<files>
{tree}
</files>
"""

        async with self.agent.iter(
            user_prompt, message_history=self.history
        ) as agent_run:
            next_node = agent_run.next_node  # start with the first node
            nodes = [next_node]
            while not isinstance(next_node, End):
                next_node = await agent_run.next(next_node)
                nodes.append(next_node)

            if not agent_run.result:
                raise Exception("No result from agent")

            new_messages = agent_run.result.new_messages()
            for message_ in new_messages:
                for part in message_.parts:
                    if isinstance(part, UserPromptPart) and part.content == user_prompt:
                        part.content = message

            self.history += new_messages

            new_messages_openai_format = await OpenAIModel(
                "any", provider=OpenAIProvider(api_key="bogus")
            )._map_messages(new_messages)

        return {"messages": new_messages_openai_format}
