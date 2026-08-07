import argparse
import json
import os
from pathlib import Path

from procurement_watch.config import resolve_config
from shared.agent_runtime import AgentRuntime, Trigger
from shared.agent_runtime.scheduler import SchedulerTrigger
from shared.dashboard_contract import write_dashboard_contract
from operations_cockpit.runtime import CockpitRuntime
from shared.intelligence_layer import DecisionMemory, FeedbackMemory, IntelligenceLayer, IntelligenceMetrics, RepositoryKnowledgeRetriever, load_intelligence_config
from shared.intelligence_providers import provider_from_config

from .agent import ProcurementAgent
from .analyzers import DeterministicFallbackAnalysisProvider
from .config import load_agent_config


def main(argv=None):
    parser = argparse.ArgumentParser(prog="procurement-agent")
    parser.add_argument("trigger", choices=("manual", "scheduled"))
    args = parser.parse_args(argv)
    config = resolve_config()
    agent_config = load_agent_config(config.repository_root)
    intelligence_config = load_intelligence_config(config.repository_root)
    root = Path(os.environ.get("HDC_AGENT_RUNTIME", Path(config.runtime_path) / "agents" / "procurement"))
    dashboard = Path(config.repository_root) / "Dashboard"
    runtime = AgentRuntime(root / "logs", lambda contract: write_dashboard_contract(dashboard / "contracts", contract), lambda: CockpitRuntime(dashboard).build())
    provider = provider_from_config(intelligence_config.provider.value, intelligence_config.model, intelligence_config.endpoint, intelligence_config.timeout_seconds)
    fallback = DeterministicFallbackAnalysisProvider() if agent_config.deterministic_fallback else None
    intelligence_root = root / "intelligence"
    intelligence = IntelligenceLayer(
        provider,
        RepositoryKnowledgeRetriever(config.repository_root, root / "executive-summaries", Path(config.runtime_path) / "journals"),
        DecisionMemory(intelligence_root / "decision-memory.json"),
        IntelligenceMetrics(intelligence_root / "metrics.json"),
        feedback_memory=FeedbackMemory(intelligence_root / "feedback-memory.json"),
    )
    agent = ProcurementAgent(config, root / "executive-summaries", intelligence, fallback)
    result = SchedulerTrigger(runtime).start(agent) if args.trigger == "scheduled" else runtime.execute(agent, Trigger.MANUAL)
    print(json.dumps(result, indent=2, ensure_ascii=False))
    return 0 if result["execution_result"] == "SUCCESS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
