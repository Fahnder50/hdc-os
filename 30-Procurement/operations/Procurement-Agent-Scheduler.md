---
document: Procurement Agent Scheduler
version: 1.0
status: Accepted
owner: Project Owner
reviewed_by: Lead Architect
last_review: "2026-08-05"
work_order: RWO-0043-R1
last_updated: "2026-08-05"
---

# Procurement Agent Scheduler

## Konfiguration

Der tägliche Startzeitpunkt, Provider, Modell und Fallback werden ausschließlich in `30-Procurement/config/agent.yaml` gepflegt. Zulässiger Modellprovider ist ausschließlich `ollama` über eine numerische Loopback-Adresse.

## Verwaltung

Aus dem Repository-Root mit `PYTHONPATH=30-Procurement/src;.`:

```powershell
python -m procurement_agent.scheduler_cli install
python -m procurement_agent.scheduler_cli status
python -m procurement_agent.scheduler_cli disable
python -m procurement_agent.scheduler_cli remove
```

`install` verwendet Windows `schtasks /Create /F` und ist idempotent. `run-now` startet denselben registrierten Task für einen operativen Test. Der Task ruft `scripts/run-procurement-agent.ps1` auf. Geplante Agent Logs und Executive Summaries liegen außerhalb des Repositories unter `%LOCALAPPDATA%\HDC-OS\agent-runtime\procurement`.

## Scheduled-End-to-End-Nachweis vom 05.08.2026

Die Aufgabe `HDC-OS Procurement Agent` wurde real installiert und durch `run-now` über den Windows Task Scheduler gestartet. Der Scheduler meldete für den Lauf um 09:00:11 Ortszeit das Ergebnis `0` und den Folgestatus `Bereit`; der nächste konfigurierte Lauf ist der 06.08.2026 um 07:00 Uhr.

Der Lauf verwendete `trigger: SCHEDULED`, startete vier bestehende Watch-Läufe erfolgreich und erreichte den vollständigen Agent Lifecycle bis `COMPLETED`. Das lokale Modell `llama3.2:3b` wurde über Ollama auf `127.0.0.1` aufgerufen. Seine Antwort verletzte den Vertrag „exakt eine Empfehlung je Case“, weshalb der konfigurierte und im Log ausgewiesene `deterministic-fallback` kontrolliert übernahm. Ergebnis: vier bearbeitete Cases, vier beratende Empfehlungen, `execution_result: SUCCESS`, genau ein Agent Log und eine Executive Summary.

Ein vorausgehender Fehlernachweis bestätigte außerdem den kontrollierten Fehlervertrag: vollständiger Lifecycle bis `COMPLETED`, `execution_result: FAILED`, `failed_phase: GENERATE_REPORT` und genau ein Agent Log.
