---
document: Generic Agent Runtime
version: 1.0
status: Accepted
owner: Project Owner
reviewed_by: Lead Architect
last_review: "2026-08-05"
work_order: WO-0043
last_updated: "2026-08-05"
---

# Generic Agent Runtime

## Zweck und Grenzen

Die generische Agent Runtime ist die fachneutrale Laufzeit für HDC-OS-Agenten. Sie kennt ausschließlich Agentenverträge, Trigger, Lifecycle, Logs und Ergebnisse. Procurement-Fachlogik, Scheduler-Fachlogik, Multi-Agent-Koordination, externe APIs, Cloud-Modelle und Selbstmodifikation gehören nicht zur Runtime.

## Verbindlicher Lifecycle

Der einzige zulässige Ablauf lautet `IDLE → TRIGGERED → COLLECT → ANALYZE → GENERATE_REPORT → WAIT_FOR_OWNER → COMPLETED`. Die Runtime prüft jede Transition. Ein fehlgeschlagener Lauf endet an der Fehlerstelle und wird mit genau einem Fehlerlog dokumentiert; ein fachliches Ergebnis wird in diesem Fall nicht vorgetäuscht.

## Verträge

Alle Agenten implementieren das Protokoll in `shared/agent_runtime/contracts.py`: Identität, Version, Owner, genau eine Verantwortung, unterstützte Trigger, Ein-/Ausgabevertrag, Zustand und Ergebnis sowie die drei fachlichen Phasen Collect, Analyze und Generate Report. Implementiert sind `MANUAL` und `SCHEDULED`; `EVENT` ist im Vertrag reserviert und wird von der Runtime abgewiesen.

Das generische `AnalysisProvider`-Interface erhält ausschließlich einen serialisierbaren Analysekontext. Repository-, Shell-, Git-, Datenbank-, Asset-, Connectivity- oder Runtime-Handles werden nicht übergeben. Dadurch bleibt das lokale Analysemodell austauschbar und read-only. Der reale Modellprovider verwendet Ollama ausschließlich über eine numerische Loopback-Adresse; HTTPS, Hostnamen, Cloud- und Nicht-Loopback-Endpunkte werden technisch abgewiesen. Provider und Modell stehen in `30-Procurement/config/agent.yaml`. Der bisherige regelbasierte Analyzer bleibt ausdrücklich als `DeterministicFallbackAnalysisProvider` erhalten. Seine Nutzung wird zusammen mit Provider und Modell im Agent Log ausgewiesen.

Jede Modellantwort wird vor der Berichtserzeugung gegen die eingecheckten Recommendation-Regeln und die vollständige Analysis-Struktur validiert. Der zusammengesetzte Bericht wird anschließend gegen `executive-summary.schema.json` einschließlich der referenzierten `recommendation.schema.json` validiert. Ungültige Antworten lösen je nach Konfiguration den ausgewiesenen Fallback oder einen kontrollierten Fehlerlauf aus.

## Procurement Agent v1

Der Procurement Agent startet unverändert `portfolio_watch`, sammelt Status, Preise, Angebote, Händler, technische Warnungen, Historie, vorherige Empfehlung, Zielpreis und aktuelle Bewertung. Fehler werden je Case klassifiziert und der restliche Lauf fortgesetzt. Anschließend erzeugt der lokale Analyzer eine Executive Summary und exakt eine erlaubte Empfehlung pro Case.

Der Agent erzeugt ausschließlich eine Executive Summary und sein Agent Log. Empfehlungen sind Informationen für den Project Owner; nur dieser darf akzeptieren, ablehnen oder verschieben. Der Agent bestellt nicht, gibt nichts frei und verändert weder Cases noch Regeln, Assets, Connectivity oder Infrastruktur. Persistente Änderungen des bestehenden Watch bleiben ausschließlich dessen bestehender Verantwortung zugeordnet.

## Scheduler

`SchedulerTrigger` besitzt nur `start(agent, payload)` und übersetzt dies in den Trigger `SCHEDULED`. Er enthält weder Bewertung noch Fachlogik oder Entscheidungen. `procurement-agent-scheduler install|status|disable|remove` verwaltet idempotent die reale Windows-Aufgabe. Der tägliche Zeitpunkt wird ausschließlich aus `scheduler.daily_at` in `agent.yaml` gelesen. `run-now` dient dem operativen End-to-End-Nachweis. Die Aufgabe startet `scripts/run-procurement-agent.ps1`, das den bestehenden Watch über `procurement-agent scheduled` ausführt.

Fehlerläufe durchlaufen weiterhin alle sieben Lifecycle-Zustände bis `COMPLETED`. Das Agent Log kennzeichnet sie mit `execution_result: FAILED` und der Phase in `failed_phase`; genau ein Log entsteht auch bei Fehlern.

## Artefakte

Die JSON-Schemas für Analysekontext, Executive Summary, Recommendation und Agent Log liegen unter `30-Procurement/schema`. Interaktive Laufartefakte verwenden `HDC_AGENT_RUNTIME` oder den konfigurierten Procurement-Runtimepfad. Die Windows-Aufgabe setzt `HDC_AGENT_RUNTIME` auf `%LOCALAPPDATA%\HDC-OS\agent-runtime\procurement`, sodass geplante Laufartefakte niemals im Repository entstehen.

## Erweiterbarkeit

Connectivity-, Monitoring-, Backup-, Maintenance- und Knowledge-Agenten können dasselbe fachneutrale Interface implementieren. Kein Agent darf den Zustand oder die interne Logik eines anderen Agenten verändern; Austausch ist ausschließlich über definierte Verträge zulässig.
