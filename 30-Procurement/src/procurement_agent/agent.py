from dataclasses import dataclass, field
from datetime import datetime, timezone
import json
from pathlib import Path
from typing import Any, Mapping

from shared.agent_runtime import AgentResult, AnalysisProvider, LifecycleState, Trigger
from procurement_watch.services import case_report_data, case_status, history_for_case, offers_for_case, portfolio_watch

from .analyzers import ANALYSIS_SCHEMA, DeterministicFallbackAnalysisProvider, SchemaValidationError, validate_schema


RECOMMENDATIONS = {"KEEP_WATCHING", "REQUEST_REVIEW", "BUY_CANDIDATE", "NO_ACTION"}
INFORMATION_STATUSES = {"INFORMATION", "RECOMMENDATION", "ACTION_REQUIRED"}


@dataclass
class ProcurementAgent:
    config: Any
    report_directory: Path
    analysis_provider: AnalysisProvider = field(default_factory=DeterministicFallbackAnalysisProvider)
    fallback_provider: AnalysisProvider | None = None
    schemas_directory: Path | None = None
    agent_id: str = "procurement-agent"
    name: str = "Procurement Agent"
    version: str = "1.0.0"
    owner: str = "Project Owner"
    responsibility: str = "Run Procurement Watch, analyze its results, and inform the Project Owner."
    supported_triggers: frozenset[Trigger] = frozenset({Trigger.MANUAL, Trigger.SCHEDULED})
    input_contract: Mapping[str, Any] = field(default_factory=lambda: {"trigger": ["MANUAL", "SCHEDULED"]})
    output_contract: Mapping[str, Any] = field(default_factory=lambda: {"artifacts": ["executive_summary", "agent_log"]})
    current_state: LifecycleState = LifecycleState.IDLE
    execution_result: AgentResult | None = None
    execution_metadata: Mapping[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        if not self.execution_metadata:
            self.execution_metadata = self._provider_metadata(self.analysis_provider, False)

    def collect(self, trigger: Trigger, payload: Mapping[str, Any]) -> Mapping[str, Any]:
        watch = portfolio_watch(self.config)
        cases = []
        case_errors = []
        for watched in watch["cases"]:
            case_id = watched["case_id"]
            try:
                status = case_status(self.config, case_id)
                offers = offers_for_case(self.config, case_id)
                history = history_for_case(self.config, case_id)
                journal = case_report_data(self.config, case_id).get("journal", [])
                cases.append(self._context_case(status, offers, history, journal, watched))
            except Exception as error:
                classified = {"case_id": case_id, "classification": error.__class__.__name__, "message": str(error)}
                case_errors.append(classified)
                cases.append(self._failed_context_case(watched, classified))
        return {
            "schema_version": "1.0",
            "generated_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
            "trigger": trigger.value,
            "watch_result": watch,
            "cases": cases,
            "case_errors": case_errors + [
                {"case_id": item["case_id"], "classification": "WATCH_ERROR", "message": item.get("error", "Watch failed")}
                for item in watch["cases"] if item.get("error")
            ],
        }

    @staticmethod
    def _context_case(status, offers, history, journal, watched):
        latest_journal = journal[0] if journal else {}
        previous = journal[1].get("summary", {}) if len(journal) > 1 else {}
        current_offer_ids = {item.get("offer_id") for item in offers}
        previous_offer_ids = {item.get("offer_id") for item in previous.get("offers", [])}
        current_vendors = {item.get("vendor_name") for item in offers if item.get("vendor_name")}
        previous_vendors = {item.get("vendor") for item in previous.get("offers", []) if item.get("vendor")}
        changes = {
            "new_offers": sorted(current_offer_ids - previous_offer_ids),
            "removed_offers": sorted(previous_offer_ids - current_offer_ids),
            "new_vendors": sorted(current_vendors - previous_vendors),
            "technical_changes": status.get("warnings", []),
            "watch_changes": latest_journal.get("changes", {}),
        }
        changes = {key: value for key, value in changes.items() if value and value != {"first_run": False, "price_changes": [], "delivery_changes": [], "new_offers": [], "new_events": []}}
        return {
            "case_id": status["case_id"],
            "case_status": status.get("case_status"),
            "price_development": history,
            "offers": offers,
            "changes": changes,
            "previous_recommendation": previous.get("recommendation_status"),
            "target_price": status.get("budget_target"),
            "current_evaluation": status.get("recommendation_status", watched.get("status", "UNKNOWN")),
        }

    @staticmethod
    def _failed_context_case(watched, error):
        return {"case_id": watched["case_id"], "case_status": "UNKNOWN", "price_development": [], "offers": [], "changes": {}, "previous_recommendation": None, "target_price": None, "current_evaluation": "BLOCKED", "error": error}

    def analyze(self, context: Mapping[str, Any]) -> Mapping[str, Any]:
        # The provider receives this value only; no config, repository, DB or runtime handle crosses the boundary.
        isolated_context = json.loads(json.dumps(context, default=str))
        fallback_used = False
        provider_error = None
        provider = self.analysis_provider
        schemas = self.schemas_directory or Path(self.config.repository_root) / "30-Procurement" / "schema"
        try:
            analysis = provider.analyze(isolated_context)
            self._validate_analysis(analysis, schemas, isolated_context)
        except Exception as error:
            if self.fallback_provider is None:
                self.execution_metadata = self._provider_metadata(provider, False, error)
                raise
            provider_error = error
            provider = self.fallback_provider
            fallback_used = True
            analysis = provider.analyze(isolated_context)
            self._validate_analysis(analysis, schemas, isolated_context)
        self.execution_metadata = self._provider_metadata(provider, fallback_used, provider_error)
        return analysis

    @staticmethod
    def _validate_analysis(analysis, schemas, context):
        validate_schema(analysis, ANALYSIS_SCHEMA, schemas)
        recommendation_schema = json.loads((schemas / "recommendation.schema.json").read_text(encoding="utf-8"))
        for recommendation in analysis["recommendations"]:
            validate_schema(recommendation, recommendation_schema, schemas)
        expected_ids = {case["case_id"] for case in context["cases"]}
        actual_ids = [item["case_id"] for item in analysis["recommendations"]]
        if len(actual_ids) != len(expected_ids) or set(actual_ids) != expected_ids:
            raise SchemaValidationError("Model response must contain exactly one recommendation per context case")

    @staticmethod
    def _provider_metadata(provider, fallback_used, provider_error=None):
        return {
            "provider": getattr(provider, "provider_name", provider.__class__.__name__),
            "model": getattr(provider, "model", "unknown"),
            "fallback_used": fallback_used,
            "provider_error": str(provider_error) if provider_error else None,
        }

    def generate_report(self, context: Mapping[str, Any], analysis: Mapping[str, Any]) -> AgentResult:
        recommendations = list(analysis.get("recommendations", []))
        expected_ids = {case["case_id"] for case in context["cases"]}
        actual_ids = [item.get("case_id") for item in recommendations]
        if len(actual_ids) != len(expected_ids) or set(actual_ids) != expected_ids:
            raise ValueError("Analysis must provide exactly one recommendation per procurement case")
        if any(item.get("recommendation") not in RECOMMENDATIONS for item in recommendations):
            raise ValueError("Analysis returned a forbidden recommendation")
        if any(item.get("information_status") not in INFORMATION_STATUSES for item in recommendations):
            raise ValueError("Analysis returned a forbidden information status")
        report = {
            "schema_version": "1.0",
            "agent": {"agent_id": self.agent_id, "name": self.name, "version": self.version, "owner": self.owner},
            "approval": {"decision_authority": "Project Owner", "agent_may_decide": False, "owner_options": ["ACCEPT", "REJECT", "DEFER"]},
            "executive_summary": {key: analysis.get(key, []) for key in ("summary", "important_changes", "critical_developments", "unchanged_cases", "risks", "open_points")},
            "recommendations": recommendations,
            "case_errors": context["case_errors"],
        }
        schemas = self.schemas_directory or Path(self.config.repository_root) / "30-Procurement" / "schema"
        report_schema = json.loads((schemas / "executive-summary.schema.json").read_text(encoding="utf-8"))
        validate_schema(report, report_schema, schemas)
        return AgentResult(report, len(context["cases"]), len(recommendations), tuple(context["case_errors"]))

    def persist_report(self, result: AgentResult) -> str:
        self.report_directory.mkdir(parents=True, exist_ok=True)
        stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
        destination = self.report_directory / f"{stamp}-executive-summary.json"
        destination.write_text(json.dumps(result.report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        return str(destination)
