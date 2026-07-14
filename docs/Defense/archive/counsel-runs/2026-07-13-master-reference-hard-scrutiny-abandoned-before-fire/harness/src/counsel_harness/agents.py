from __future__ import annotations

import json
from collections.abc import Callable

from .bash_proxy import BashProxy
from .config import RunConfig
from .journal_bridge import JournalBridge
from .policy import ExpertPolicy
from .secrets import SecretValue
from .web import RawDownloader, WebDiscovery


def build_agents(
    config: RunConfig,
    key: SecretValue,
    *,
    db=None,
    model_factory: Callable | None = None,
    agent_factory: Callable | None = None,
) -> dict[str, object]:
    if model_factory is None:
        from agno.models.deepseek import DeepSeek

        model_factory = DeepSeek
    if agent_factory is None:
        from agno.agent import Agent

        agent_factory = Agent
    if db is None:
        from agno.db.sqlite import SqliteDb

        db = SqliteDb(db_file=str(config.run_dir / "agentos.sqlite"))

    agents: dict[str, object] = {}
    for slug, expert in config.experts.items():
        policy = ExpertPolicy(config.run_dir, expert)
        downloader = RawDownloader(policy)
        journal = JournalBridge(policy)
        proxy = BashProxy(
            policy,
            downloader=downloader,
            append_entry=lambda entry, bridge=journal: bridge.append(entry).output,
        )
        discovery = WebDiscovery()

        def bash(command: str, *, _proxy=proxy) -> str:
            return _proxy.run(command)

        bash.__name__ = "bash"
        bash.__doc__ = (
            f"Policy-enforced Bash proxy for {slug}. Supports only the ratified bounded "
            "text, raw-download, and journal-append command grammar."
        )

        def web_search(query: str, max_results: int = 8, *, _discovery=discovery) -> str:
            return json.dumps(
                _discovery.search(query, max_results=max_results),
                ensure_ascii=False,
            )

        web_search.__name__ = "web_search"
        web_search.__doc__ = (
            f"Discovery-only public-web search for {slug}; results are not citable evidence."
        )

        model = model_factory(
            id="deepseek-v4-pro",
            api_key=key.get_secret_value(),
            reasoning_effort="max",
            use_thinking=True,
            temperature=0,
            max_tokens=8192,
            retries=0,
        )
        agents[slug] = agent_factory(
            id=f"defense-counsel-{slug}",
            name=f"Defense Counsel — {expert.aspect}",
            session_id=f"defense-counsel-{slug}-2026-07-13",
            user_id="sina-defense-counsel",
            model=model,
            db=db,
            tools=[bash, web_search],
            tool_call_limit=60,
            checkpoint="tools",
            retries=0,
            telemetry=False,
            store_events=True,
            store_tool_messages=True,
            store_history_messages=True,
            markdown=False,
        )
    return agents

