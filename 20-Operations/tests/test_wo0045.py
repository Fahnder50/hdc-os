from copy import deepcopy
from pathlib import Path

import pytest
import yaml

from shared.scheduler_lifecycle.manager import SchedulerLifecycleManager
from shared.scheduler_lifecycle import cli
from shared.scheduler_lifecycle import registry as registry_module
from shared.scheduler_lifecycle.registry import configuration_hash, load_registry, persist_dynamic_state


ROOT = Path(__file__).resolve().parents[2]


class FakePlatform:
    def __init__(self):
        self.tasks = {}
        self.apply_count = 0

    def expected(self, definition):
        return {"name": definition["name"], "at": definition["schedule"]["at"], "enabled": definition["runtime"]["enabled"], "wake_to_run": definition["schedule"]["wake_to_run"]}

    def inspect(self, definition):
        value = self.tasks.get(definition["scheduler_id"])
        return deepcopy(value) if value else None

    def apply(self, definition):
        self.tasks[definition["scheduler_id"]] = self.expected(definition)
        self.apply_count += 1

    def remove(self, definition):
        self.tasks.pop(definition["scheduler_id"], None)


def _definition():
    return deepcopy(load_registry(ROOT / "20-Operations" / "config" / "schedulers.yaml")[0])


def _registry_root(tmp_path, state="INSTALLED", verified="2026-01-01T00:00:00+00:00"):
    target = tmp_path / "20-Operations" / "config" / "schedulers.yaml"
    target.parent.mkdir(parents=True)
    document = yaml.safe_load((ROOT / "20-Operations" / "config" / "schedulers.yaml").read_text(encoding="utf-8"))
    document["schedulers"][0]["installation_state"] = state
    document["schedulers"][0]["last_verification"] = verified
    target.write_text(yaml.safe_dump(document, sort_keys=False), encoding="utf-8")
    return tmp_path, target


def _execute(monkeypatch, root, platform, command):
    monkeypatch.setattr(cli, "WindowsTaskScheduler", lambda unused_root: platform)
    monkeypatch.setattr(cli, "write_dashboard_contract", lambda *args: None)
    return cli.execute(command, root, "procurement-agent-daily")


def test_registry_contains_exactly_one_owned_procurement_scheduler():
    entries = load_registry(ROOT / "20-Operations" / "config" / "schedulers.yaml")
    assert len(entries) == 1
    assert entries[0]["scheduler_id"] == "procurement-agent-daily"
    assert entries[0]["configuration_hash"] == configuration_hash(entries[0])


def test_install_is_idempotent_and_verifies_healthy():
    platform = FakePlatform()
    manager = SchedulerLifecycleManager(platform)
    first = manager.install(_definition())
    second = manager.install(_definition())
    assert len(platform.tasks) == 1
    assert first["installation_state"] == second["installation_state"] == "HEALTHY"


def test_verification_detects_drift_and_repair_restores_only_configuration():
    platform = FakePlatform()
    manager = SchedulerLifecycleManager(platform)
    definition = _definition()
    manager.install(definition)
    platform.tasks[definition["scheduler_id"]]["wake_to_run"] = False
    drift = manager.verify(definition)
    assert drift["installation_state"] == "DRIFT"
    assert drift["drift"] == ["wake_to_run"]
    repaired = manager.repair(definition)
    assert repaired["before"]["installation_state"] == "DRIFT"
    assert repaired["after"]["installation_state"] == "HEALTHY"


def test_update_and_remove_cover_full_lifecycle():
    platform = FakePlatform()
    manager = SchedulerLifecycleManager(platform)
    definition = _definition()
    manager.install(definition)
    definition["schedule"]["at"] = "08:30"
    assert manager.update(definition)["actual"]["at"] == "08:30"
    assert manager.remove(definition)["installation_state"] == "NOT_INSTALLED"


def test_verify_persists_healthy_state_and_new_timestamp(monkeypatch, tmp_path):
    root, registry = _registry_root(tmp_path)
    platform = FakePlatform()
    before = deepcopy(load_registry(registry)[0])
    before_static_lines = [line for line in registry.read_text(encoding="utf-8").splitlines() if not any(f"{field}:" in line for field in registry_module.DYNAMIC_FIELDS)]
    platform.apply(before)
    _execute(monkeypatch, root, platform, "verify")
    persisted = load_registry(registry)[0]
    assert persisted["installation_state"] == "HEALTHY"
    assert persisted["last_verification"] != "2026-01-01T00:00:00+00:00"
    assert persisted["configuration_hash"] == configuration_hash(persisted)
    for key in set(before) - {"configuration_hash", "installation_state", "last_verification"}:
        assert persisted[key] == before[key]
    after_static_lines = [line for line in registry.read_text(encoding="utf-8").splitlines() if not any(f"{field}:" in line for field in registry_module.DYNAMIC_FIELDS)]
    assert after_static_lines == before_static_lines


@pytest.mark.parametrize("command", ["install", "update", "status"])
def test_all_other_operations_persist_their_verified_state(monkeypatch, tmp_path, command):
    root, registry = _registry_root(tmp_path)
    platform = FakePlatform()
    if command == "status":
        platform.apply(load_registry(registry)[0])
    _execute(monkeypatch, root, platform, command)
    persisted = load_registry(registry)[0]
    assert persisted["installation_state"] == "HEALTHY"
    assert persisted["last_verification"] != "2026-01-01T00:00:00+00:00"
    assert persisted["configuration_hash"] == configuration_hash(persisted)


def test_verify_persists_external_drift(monkeypatch, tmp_path):
    root, registry = _registry_root(tmp_path)
    platform = FakePlatform()
    definition = load_registry(registry)[0]
    platform.apply(definition)
    platform.tasks[definition["scheduler_id"]]["wake_to_run"] = False
    _execute(monkeypatch, root, platform, "verify")
    assert load_registry(registry)[0]["installation_state"] == "DRIFT"


def test_repair_documents_both_states_and_persists_final_state(monkeypatch, tmp_path):
    root, registry = _registry_root(tmp_path, state="DRIFT")
    platform = FakePlatform()
    definition = load_registry(registry)[0]
    platform.apply(definition)
    platform.tasks[definition["scheduler_id"]]["wake_to_run"] = False
    result = _execute(monkeypatch, root, platform, "repair")[0]
    assert result["before"]["installation_state"] == "DRIFT"
    assert result["after"]["installation_state"] == "HEALTHY"
    assert load_registry(registry)[0]["installation_state"] == "HEALTHY"


def test_remove_persists_not_installed_and_keeps_registry_entry(monkeypatch, tmp_path):
    root, registry = _registry_root(tmp_path, state="HEALTHY")
    platform = FakePlatform()
    platform.apply(load_registry(registry)[0])
    _execute(monkeypatch, root, platform, "remove")
    entries = load_registry(registry)
    assert len(entries) == 1
    assert entries[0]["scheduler_id"] == "procurement-agent-daily"
    assert entries[0]["installation_state"] == "NOT_INSTALLED"


def test_atomic_persistence_failure_preserves_existing_registry(monkeypatch, tmp_path):
    unused_root, registry = _registry_root(tmp_path)
    original = registry.read_bytes()
    status = {"installation_state": "HEALTHY", "last_verification": "2026-08-06T12:00:00+00:00"}

    def fail_replace(source, destination):
        raise OSError("simulated replace failure")

    monkeypatch.setattr(registry_module.os, "replace", fail_replace)
    with pytest.raises(OSError, match="simulated replace failure"):
        persist_dynamic_state(registry, "procurement-agent-daily", status)
    assert registry.read_bytes() == original
    assert not list(registry.parent.glob(".schedulers.yaml.*.tmp"))
