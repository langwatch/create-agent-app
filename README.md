# Create Agent App

![PRs Welcome](https://camo.githubusercontent.com/02856e08e249f91890ab08c5770b25afe81dcf939e840c4f66bbc2c901ddb39f/68747470733a2f2f696d672e736869656c64732e696f2f62616467652f5052732d77656c636f6d652d677265656e2e737667)

This repository contains the same agent examples written in several different frameworks, so you can compare them side by side and use it as a template for starting a new project.

## Running the examples

Clone this repo and navigate to any of the examples:

```bash
git clone https://github.com/langwatch/create-agent-app.git
cd create-agent-app
cd inspect_ai_example # or any other example
```

Install the dependencies:

```bash
uv sync --all-groups
```

Run the tests to see the agent in action:

```bash
uv run pytest -s tests/test_customer_support_agent.py
```

Or enter the debug mode to chat with the agent yourself:

```bash
uv run pytest -s tests/test_customer_support_agent.py --debug
```

## Frameworks

In alphabetical order:

- [Agno](https://github.com/agno-ai/agno)
- [DSPy](https://github.com/stanfordnlp/dspy)
- [Google ADK](https://github.com/google/adk-python)
- [InspectAI](https://github.com/UKGovernmentBEIS/inspect_ai)
- [LangGraph (Functional API)](https://langchain-ai.github.io/langgraph/concepts/functional_api/)
- [LangGraph (High-level API)](https://github.com/langchain-ai/langgraph)
- No Framework (just [litellm](https://github.com/BerriAI/litellm) and a loop)
- [Pydantic AI](https://github.com/pydantic/pydantic-ai)
- [smolagents](https://github.com/huggingface/smolagents)

Coming up soon:

- [ ] AutoGen
- [ ] Mastra

All examples are using the same `gemini-2.5-flash-preview-04-17` model from Google and pass the same [Scenario](https://github.com/langwatch/scenario) tests which uses the same model for verification.

Feel free to [open an issue](https://github.com/langwatch/create-agent-app/issues) and request others!

## Agent Examples

The goal is to have examples that cover all the LLM workflows and Agent examples listed on the [Building Effective Agents](https://www.anthropic.com/engineering/building-effective-agents) guide by Anthropic, as those are real practical examples of what's actually mostly being built with LLMs right now.

- Agent: Tools Loop
  - [x] Customer Support Agent
  - [ ] Coding Agent
  - [ ] Deep Search Agent (using MCP)
- Workflow: Prompt Chaining
  - [ ] Marketing Copy with Translation
  - [ ] Document Outline Writing
- Workflow: Routing
  - [ ] Customer Service Querying
  - [ ] Hard/easy question routing
- Workflow: Parallelization
  - [ ] Code Vulnerability Voting
  - [ ] Content Flagging Voting
- Workflow: Orchestrator-workers
  - [ ] Architect-Developer Code Changes
  - [ ] Multi-Source Searching
- Workflow: Evaluator-optimizer
  - [ ] Literaly Translation
  - [ ] Multi-Round Searching

## Looking for Contributions

I am looking for contributors to help me expand this repo, both for adding new examples and new frameworks.

**If you want to add a new framework example**, copy one of the existing ones (e.g. langgraph_highlevel_api_example) and adapt the as much use cases you can to the new framework. They just need to follow a couple rules:

- The example are made to be completely self-contained, and the code readable without jumping through hoops, so we copy and paste the prompts and the tests to each. The only code in the `common` package are those simulating external system connections and data that need to be replaced by the user's own system anyway.

- The examples should look as close to each other as possible, with the same features, changing only in the philosophical approach that each framework has. The examples are not meant to advertise features.

**If you want to add a new use case example**, pick one of the list and start with a framework that you are most familiar with, try to follow the same simplicity approach as the other examples, if it's a brand new use case, this will define how all the other framework examples will be written, so it's good to have in mind what valuable distinct complexities this use case will show. [Join our Discord](https://discord.gg/kT4PhDS2gH) if you want to debate the idea.

**If you have a request** [open an issue](https://github.com/langwatch/create-agent-app/issues) so contributors can help!

## License

MIT
