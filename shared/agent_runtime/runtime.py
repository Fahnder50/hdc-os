from datetime import datetime, timezone
import json
from pathlib import Path
from time import perf_counter
from typing import Any, Mapping
import uuid

from .contracts import Agent, AgentResult, ExecutionTrace, LifecycleState, Trigger


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


class AgentRuntime:
    """Executes contracts and lifecycle only; it contains no domain logic."""

    def __init__(self, log_directory: Path):
        self.log_directory = Path(log_directory)

    def execute(self, agent: Agent, trigger: Trigger, payload: Mapping[str, Any] | None = None) -> Mapping[str, Any]:
        if trigger == Trigger.EVENT:
            raise ValueError("EVENT is reserved but not implemented")
        if trigger not in agent.supported_triggers:
            raise ValueError(f"Trigger {trigger} is not supported by {agent.agent_id}")
        trace = ExecutionTrace()
        started_at = _utc_now()
        started = perf_counter()
        exit_status = "FAILED"
        result = None
        report_path = None
        failure = None
        failed_phase = None
        try:
            self._advance(agent, trace, LifecycleState.TRIGGERED)
            self._advance(agent, trace, LifecycleState.COLLECT)
            context = agent.collect(trigger, dict(payload or {}))
            self._advance(agent, trace, LifecycleState.ANALYZE)
            analysis = agent.analyze(context)
            self._advance(agent, trace, LifecycleState.GENERATE_REPORT)
            result = agent.generate_report(context, analysis)
            report_path = agent.persist_report(result)
            agent.execution_result = result
            self._advance(agent, trace, LifecycleState.WAIT_FOR_OWNER)
            self._advance(agent, trace, LifecycleState.COMPLETED)
            exit_status = "COMPLETED_WITH_ERRORS" if result.errors else "SUCCESS"
        except Exception as error:
            failed_phase = agent.current_state.value
            failure = {"classification": error.__class__.__name__, "message": str(error)}
            result = AgentResult({}, 0, 0, (failure,), "FAILED", failed_phase)
            agent.execution_result = result
            for state in tuple(LifecycleState)[len(trace.states):]:
                self._advance(agent, trace, state)
        finally:
            ended_at = _utc_now()
            log = {
                "agent": agent.agent_id,
                "version": agent.version,
                "trigger": trigger.value,
                "started_at": started_at,
                "ended_at": ended_at,
                "duration_seconds": round(perf_counter() - started, 6),
                "processed_cases": result.case_count if result else 0,
                "recommendations": result.recommendation_count if result else 0,
                "result": report_path or failure,
                "exit_status": exit_status,
                "execution_result": result.status if result else "FAILED",
                "failed_phase": failed_phase,
                "lifecycle": [state.value for state in trace.states],
                "analysis": dict(getattr(agent, "execution_metadata", {})),
            }
            self._write_one_log(agent.agent_id, started_at, log)
        return log

    @staticmethod
    def _advance(agent: Agent, trace: ExecutionTrace, state: LifecycleState) -> None:
        trace.advance(state)
        agent.current_state = state

    def _write_one_log(self, agent_id: str, started_at: str, value: Mapping[str, Any]) -> None:
        self.log_directory.mkdir(parents=True, exist_ok=True)
        token = uuid.uuid4().hex[:8]
        filename = f"{started_at.replace(':', '').replace('+', '_')}-{token}-{agent_id}.json"
        (self.log_directory / filename).write_text(
            json.dumps(value, indent=2, ensure_ascii=False, default=str) + "\n", encoding="utf-8"
        )
