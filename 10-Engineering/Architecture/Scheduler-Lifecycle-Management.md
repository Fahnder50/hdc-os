---
document: Scheduler Lifecycle Management
version: 1.0
status: Review
owner: Project Owner
work_order: WO-0045
last_updated: "2026-08-06"
classification: Historical
---

# Scheduler Lifecycle Management

## Ownership und Registry

HDC-OS verwaltet alle eigenen Scheduler ausschließlich über `hdc-scheduler`. Die einzige Sollquelle ist `20-Operations/config/schedulers.yaml`. Jeder Eintrag enthält Identität, Version, Owner, Trigger, Schedule, Runtime, einen SHA-256-Konfigurationshash sowie die dynamischen Registry-Felder Installation State und Last Verification. Manuelle Änderungen über Windows gehören nicht zum Betriebsmodell und werden als Drift erkannt.

Zulässige Zustände sind ausschließlich `NOT_INSTALLED`, `INSTALLED`, `HEALTHY`, `DRIFT` und `BROKEN`. Der Manager veröffentlicht den Scheduler Health als Dashboard Contract für das Operations Cockpit.

## Lifecycle

Die Befehle `install`, `update`, `verify`, `status`, `repair` und `remove` gelten wahlweise für alle Registry-Einträge oder eine Scheduler-ID. Installation und Update wenden den vollständigen Sollzustand idempotent an. Verification vergleicht Vorhandensein, Enabled, Trigger, Uhrzeit, Benutzer, Logon Type, Aktion, StartWhenAvailable, WakeToRun und Energieoptionen. Jede Abweichung ist Drift. Repair wendet ausschließlich die Scheduler-Konfiguration erneut an; Agent, Runtime und Domänen bleiben unverändert. Remove adressiert ausschließlich den Namen aus einem registrierten HDC-OS-Eintrag.

## Plattformgrenze

`SchedulerPlatform` ist das generische Interface. `WindowsTaskScheduler` ist die einzige implementierte Plattform und delegiert Betriebssystemoperationen an `windows_task.ps1`. Linux, Cron, Container, Services und Daemons sind nicht implementiert.

## Procurement Scheduler

`procurement-agent-daily` ist vollständig migriert. Der Sollzustand aktiviert Nachholen verpasster Starts und WakeToRun, erlaubt Starts auf Batterie, beendet den Lauf bei einem Wechsel auf Batterie nicht, verwendet den aktuellen interaktiven Benutzer und startet ausschließlich den bestehenden PowerShell-Wrapper. Damit ist der zuvor diagnostizierte, vom Windows Scheduler abgelehnte 07:00-Start deterministisch reparierbar.
