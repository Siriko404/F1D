from counsel_harness.agents import build_agents
from counsel_harness.secrets import SecretValue


class FakeModel:
    def __init__(self, **kwargs):
        self.kwargs = kwargs


class FakeAgent:
    def __init__(self, **kwargs):
        self.kwargs = kwargs
        self.id = kwargs["id"]
        self.session_id = kwargs["session_id"]
        self.tools = kwargs["tools"]


def test_builds_five_independent_deepseek_agents_with_only_two_tools(run_config):
    agents = build_agents(
        run_config,
        SecretValue("sk-test-key"),
        db=object(),
        model_factory=FakeModel,
        agent_factory=FakeAgent,
    )

    assert set(agents) == set(run_config.experts)
    assert len({agent.session_id for agent in agents.values()}) == 5
    for slug, agent in agents.items():
        assert agent.id == f"defense-counsel-{slug}"
        assert [tool.__name__ for tool in agent.tools] == ["bash", "web_search"]
        assert agent.kwargs["tool_call_limit"] == 60
        assert agent.kwargs["retries"] == 0
        assert agent.kwargs["telemetry"] is False
        assert agent.kwargs["checkpoint"] == "tools"
        assert agent.kwargs["model"].kwargs["id"] == "deepseek-v4-pro"
        assert agent.kwargs["model"].kwargs["api_key"] == "sk-test-key"
        assert agent.kwargs["model"].kwargs["reasoning_effort"] == "max"


def test_tools_are_bound_to_each_experts_private_policy(run_config):
    agents = build_agents(
        run_config,
        SecretValue("sk-test-key"),
        db=object(),
        model_factory=FakeModel,
        agent_factory=FakeAgent,
    )

    quant_bash = agents["quantitative-results"].tools[0]
    visual_bash = agents["visualization-standards"].tools[0]

    assert "quantitative-results" in quant_bash.__doc__
    assert "visualization-standards" in visual_bash.__doc__
    assert quant_bash is not visual_bash

