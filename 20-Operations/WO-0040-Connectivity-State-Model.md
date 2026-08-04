---
document: WO-0040-Connectivity-State-Model.md
version: 1.0
status: Accepted
owner: Project Owner
reviewed_by: Lead Architect
last_review: "2026-08-04"
last_updated: "2026-08-04"
work_order: WO-0040
classification: Deployment-relevant Architecture Baseline
---

# WO-0040 – Connectivity State Model & Offline Operation Baseline

## Ergebnis

Der verbindliche Architekturvertrag ist im
[Connectivity State Model](Connectivity-State-Model.md) dokumentiert.

Er definiert:

- exakt fünf eindeutige Gesamtzustände,
- getrennte Evidenzebenen für Power, Gateway, WAN Transport, Internet
  Reachability und DNS,
- providerneutrale Anwendung für einzelne, parallele und zukünftige WAN-Pfade,
- vollständige erlaubte Zustandsübergänge einschließlich zwingendem
  `RECOVERING` zwischen bestätigtem Ausfall und stabiler Wiederherstellung,
- sechs Connectivity-Ereignisse einschließlich `CONNECTIVITY_RECOVERING` und
  dem ausschließlich bei `RECOVERING → ONLINE` zulässigen
  `CONNECTIVITY_RECOVERED`,
- alleinige Eigentümerschaft des Connectivity State Providers,
- getrennte Rollen für Ermittler, State Provider und Consumer,
- deklarierbare Service-Reaktionen und Mindestverhalten je Zustand,
- Offline Operation und spätere Datenintegritätsanforderungen,
- Procurement Watch als späteren Consumer ohne Codeänderung.

## Nicht implementiert

Es wurden keine Probes, Integrationen, Scheduler, Hintergrunddienste,
Datenbanken, APIs, CLIs, Queues, Benachrichtigungen, Schwellenwerte oder
Änderungen bestehender Services implementiert.

Die Änderungen liegen uncommitted zur Review vor.
