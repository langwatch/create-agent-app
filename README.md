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
# Python Agent
uv sync --all-groups

# TypeScript Agent
npm install
```

Run the tests to see the agent in action:

```bash
# Python Agent
uv run pytest -s tests/test_customer_support_agent.py

# TypeScript Agent
npm test
```

Or enter the debug mode to chat with the agent yourself:

```bash
# Python Agent
uv run pytest -s tests/test_customer_support_agent.py --debug

# TypeScript Agent
npm run dev
```

## Frameworks

In alphabetical order:

### <img src="./create_agent_app/priv/python.svg" alt="Python" width="16" height="16"> Python

| Framework                                                                                        | Customer Support Agent                                                                                                                                                           | Vibe Coding Agent                                                                                                   |
| ------------------------------------------------------------------------------------------------ | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------- |
| [Agno](https://github.com/agno-agi/agno)                                                         | [Code](./agno_example/customer_support_agent.py) \| [Test](./agno_example/tests/test_customer_support_agent.py) \| [Trace](https://app.langwatch.ai/share/9vfPREIjTux0hc8aEiVbQ) |                                                                                                                     |
| [DSPy](https://github.com/stanfordnlp/dspy)                                                      | [Code](./dspy_example/customer_support_agent.py) \| [Test](./dspy_example/tests/test_customer_support_agent.py)                                                                  |                                                                                                                     |
| [Google ADK](https://github.com/google/adk-python)                                               | [Code](./google_adk_example/customer_support_agent.py) \| [Test](./google_adk_example/tests/test_customer_support_agent.py)                                                      |                                                                                                                     |
| [InspectAI](https://github.com/UKGovernmentBEIS/inspect_ai)                                      | [Code](./inspect_ai_example/customer_support_agent.py) \| [Test](./inspect_ai_example/tests/test_customer_support_agent.py)                                                      |                                                                                                                     |
| [LangGraph (High-level API)](https://github.com/langchain-ai/langgraph)                          | [Code](./langgraph_highlevel_api_example/customer_support_agent.py) \| [Test](./langgraph_highlevel_api_example/tests/test_customer_support_agent.py)                            |                                                                                                                     |
| [Letta](https://github.com/letta-ai/letta)                                                       | [Code](./letta_example/customer_support_agent.py)                                                                                                                                |                                                                                                                     |
| No Framework ([litellm](https://github.com/BerriAI/litellm), function_schema utility and a loop) | [Code](./no_framework_example/customer_support_agent.py) \| [Test](./no_framework_example/tests/test_customer_support_agent.py)                                                  |                                                                                                                     |
| [Pixelagent](https://github.com/pixeltable/pixelagent)                                           | [Code](./pixelagent_example/customer_support_agent.py) \| [Test](./pixelagent_example/tests/test_customer_support_agent.py)                                                       |                                                                                                                     |
| [Pydantic AI](https://github.com/pydantic/pydantic-ai)                                           | [Code](./pydantic_ai_example/customer_support_agent.py) \| [Test](./pydantic_ai_example/tests/test_customer_support_agent.py)                                                    | [Code](./pydantic_ai_example/vibe_coding_agent.py) \| [Test](./pydantic_ai_example/tests/test_vibe_coding_agent.py) |
| [smolagents](https://github.com/huggingface/smolagents)                                          | [Code](./smolagents_example/customer_support_agent.py) \| [Test](./smolagents_example/tests/test_customer_support_agent.py)                                                      |                                                                                                                     |

### <img src="./create_agent_app/priv/typescript.svg" alt="TypeScript" width="16" height="16"> TypeScript

| Framework                                                   | Customer Support Agent                                                                                                                                                                                                                               | Vibe Coding Agent |
| ----------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ----------------- |
| [Ax](https://github.com/ax-llm/ax)                          | [Code](./ax_example/src/customer-support-agent.ts) \| [Test](./ax_example/src/customer-support-agent.test.ts)                                                                                                                                        |                   |
| [Inngest AgentKit](https://github.com/inngest/agent-kit)    | [Code](./inngest_agent_kit_example/agents/customer-support-agent.ts) \| [Test](./inngest_agent_kit_example/agents/customer-support-agent.test.ts)                                                                                                    |                   |
| [LangGraph.js](https://github.com/langchain-ai/langgraphjs) | [Code](./langgraph_js_example/agents/customer-support-agent.ts) \| [Test](./langgraph_js_example/agents/customer-support-agent.test.ts) \| [UI](./langgraph_js_example/src/App.tsx) \| [Trace](https://app.langwatch.ai/share/ddcuQ7JTgEa7qrIaxGVJe) |                   |
| [Mastra](https://github.com/mastra-ai/mastra)               | [Code](./mastra_example/mastra/agents/customer-support-agent.ts) \| [Test](./mastra_example/mastra/agents/customer-support-agent.test.ts) \| [UI](./mastra_example/src/App.tsx) \| [Trace](https://app.langwatch.ai/share/z1qJYZcmVQH3NrxmGNEMf)     |                   |
| Pure JavaScript, zero dependencies (Cloudflare Workers)     | [Code](./cloudflare_worker_example_no_dependencies/index.js)                                                                                                                                                                                         |                   |

Coming up soon (help wanted!):

- [ ] CrewAI
- [ ] AutoGen
- [ ] Atomic Agents
- [ ] OpenAI Agent SDK

All examples are using the same `gemini-2.5-flash-preview-04-17` model from Google and pass the same [Scenario](https://github.com/langwatch/scenario) tests which uses the same model for verification.

Feel free to [open an issue](https://github.com/langwatch/create-agent-app/issues) and request others!

## Agent Examples

The goal is to have examples that cover all the LLM workflows and Agent examples listed on the [Building Effective Agents](https://www.anthropic.com/engineering/building-effective-agents) guide by Anthropic, as those are real practical examples of what's actually mostly being built with LLMs right now.

- Agent: Tools Loop
  - [x] Customer Support Agent (all frameworks)
  - [x] Vibe Coding Agent (implemented in: pydantic ai, others pending)
  - [ ] Deep Search MCP Agent
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
