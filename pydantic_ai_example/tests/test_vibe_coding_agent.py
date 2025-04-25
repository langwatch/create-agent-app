import pytest

from vibe_coding_agent import VibeCodingAgent
from scenario import Scenario, TestingAgent
from create_agent_app.common.vibe_coding.utils import clone_template

Scenario.configure(
    testing_agent=TestingAgent(model="gemini/gemini-2.5-flash-preview-04-17")
)


@pytest.mark.agent_test
@pytest.mark.asyncio
async def test_vibe_coding():
    template_path = clone_template()
    print(f"\n-> Vibe coding template path: {template_path}\n")

    vibe_coding_agent = VibeCodingAgent(template_path)

    scenario = Scenario(
        "user wants to create a new landing page for their dog walking startup",
        agent=vibe_coding_agent.call_agent,
        strategy="send the first message to generate the landing page, then a single follow up request to extend it, then give your final verdict",
        success_criteria=[
            "agent reads the files before go and making changes",
            "agent modified the index.css file",
            "agent modified the Index.tsx file",
            "agent created a comprehensive landing page",
            "agent extended the landing page with a new section",
        ],
        failure_criteria=[
            "agent says it can't read the file",
            "agent produces incomplete code or is too lazy to finish",
        ],
        max_turns=5,
    )

    result = await scenario.run()

    print(f"\n-> Done, check the results at: {template_path}\n")

    assert result.success
