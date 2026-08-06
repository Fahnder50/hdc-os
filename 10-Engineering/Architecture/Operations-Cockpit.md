---
document: Operations Cockpit
version: 1.0
status: Accepted
owner: Project Owner
reviewed_by: Lead Architect
last_review: "2026-08-05"
work_order: WO-0044
last_updated: "2026-08-05"
classification: Historical
---

# Operations Cockpit

## Zweck

Das Operations Cockpit ist die einzige menschenorientierte Gesamtsicht auf HDC-OS. Es zeigt einen aktuellen Snapshot und ein Daily Briefing für den Project Owner, besitzt keine Fachlogik, trifft keine Entscheidungen und verändert keine Domänendaten.

## Architekturgrenze

Domäneneigene Producer veröffentlichen ihren Zustand als Dashboard Contract. Procurement und Agent Runtime veröffentlichen ihre Contracts aus `procurement_agent.dashboard_contracts`; Deployment und Assets aus `operations_dashboard.contracts`. Nur diese Producer kennen ihre Primärquellen. Die Cockpit-Runtime unter `Dashboard/src/operations_cockpit` importiert keine Procurement-, Deployment-, Asset- oder Agentmodule und liest ausschließlich JSON-Dateien im Contract-Verzeichnis.

Jeder Contract besitzt exakt die acht Pflichtfelder `domain`, `health`, `summary`, `status`, `last_update`, `requires_action`, `recommendations` und `links`. Ausschließlich `details` ist optional. Es enthält darstellbare, domänenspezifische Zusatzwerte und wird vom Cockpit ohne Interpretation als Key/Value-Liste ausgegeben. Neue Domänen können denselben Vertrag implementieren, ohne Aggregator oder Renderer strukturell zu ändern.

## Aggregation und Gesamtzustand

Der Aggregator führt ausschließlich generische Operationen aus: Contracts laden, den höchsten bereits von den Domänen gelieferten Health-Wert als `Overall Health` wählen, seit dem letzten Build strukturell geänderte Domain-Snapshots für `Today's Summary` markieren und aktuelle Recommendations aus Contracts mit `requires_action: true` zusammenführen. Zulässige Health-Werte sind `HEALTHY`, `WARNING` und `CRITICAL`.

Der interne vorherige Snapshot liegt in `Dashboard/.state.json` und ist kein Ausgabeformat. Contract-Dateien und State sind per `.gitignore` von der Wissensbasis getrennt.

## Darstellung und Einstieg

`Dashboard/refresh-dashboard.ps1` ist der einzige Refresh-Einstieg. Er lässt zunächst die Domänen ihre Contracts veröffentlichen und ruft anschließend die fachneutrale Runtime auf. Diese überschreibt ausschließlich `Dashboard/Latest.md` und `Dashboard/Latest.html`; Datumsdateien entstehen nicht. Beide Ansichten werden aus demselben Aggregationsmodell erzeugt und enthalten Overall Health, Today's Summary, Procurement, Deployment, Assets, Agents und Recommended Actions.

Der Project Owner öffnet mit einem Klick eine der beiden `Latest`-Dateien. Runtime-Verzeichnisse, JSON-Contracts und Agent Logs müssen nicht manuell gelesen werden.

## Automatischer Refresh

Gemäß WO-0046 besitzt ausschließlich die generische Agent Runtime die Refresh-Entscheidung. Nach `execution_result: SUCCESS` fordert sie vom Agenten dessen Dashboard Contracts an, schreibt diese über den generischen Contract Sink und ruft genau einmal den injizierten Cockpit Refresher auf. Fehlgeschlagene Agentläufe erzeugen weder Contracts noch Refresh.

Markdown und HTML werden zunächst vollständig in temporäre Dateien gerendert und anschließend als Paar ersetzt. Schlägt Staging oder Replacement fehl, werden bestehende Views wiederhergestellt und der Fehler in `.refresh.log` sowie `.refresh-status.json` dokumentiert. Das letzte erfolgreiche Cockpit bleibt erhalten. Jede erfolgreiche Darstellung zeigt Last Refresh, Refresh Result und Refresh Duration; das Schema liegt unter `Dashboard/schema/refresh-status.schema.json`.

## Bewusste Grenzen

Nicht implementiert sind Live-Monitoring, Connectivity-, Firewall- oder Sensordaten, Netzwerkgraphen, Webserver, REST APIs, Authentifizierung, Interaktion, Benachrichtigungen, KI-Auswertung und automatische Entscheidungen. Connectivity, Monitoring, Backup, Security, Temperature und Network Topology können später ausschließlich als weitere Contract-Producer ergänzt werden.
