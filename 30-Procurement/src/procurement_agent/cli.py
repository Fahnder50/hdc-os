import argparse
import json
import os
from pathlib import Path

from procurement_watch.config import resolve_config
from shared.agent_runtime import AgentRuntime, Trigger
from shared.agent_runtime.scheduler import SchedulerTrigger

from .agent import ProcurementAgent
from .analyzers import DeterministicFallbackAnalysisProvider, OllamaLocalAnalysisProvider
from .config import load_agent_config


def main(argv=None):
    parser = argparse.ArgumentParser(prog="procurement-agent")
    parser.add_argument("trigger", choices=("manual", "scheduled"))
    args = parser.parse_args(argv)
    config = resolve_config()
    agent_config = load_agent_config(config.repository_root)
    root = Path(os.environ.get("HDC_AGENT_RUNTIME", Path(config.runtime_path) / "agents" / "procurement"))
    runtime = AgentRuntime(root / "logs")
    provider = OllamaLocalAnalysisProvider(agent_config.model, agent_config.endpoint, agent_config.timeout_seconds)
    fallback = DeterministicFallbackAnalysisProvider() if agent_config.deterministic_fallback else None
    agent = ProcurementAgent(config, root / "executive-summaries", provider, fallback)
    result = SchedulerTrigger(runtime).start(agent) if args.trigger == "scheduled" else runtime.execute(agent, Trigger.MANUAL)
    print(json.dumps(result, indent=2, ensure_ascii=False))
    return 0 if result["execution_result"] == "SUCCESS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
