---
document: ADR-M2.2-Procurement-Foundation.md
version: 1.0
status: Accepted
owner: Project Owner
reviewed_by: Lead Architect
last_review: "2026-07-20"
classification: Workspace
---

# ADR-M2.2: Procurement Foundation

## Kontext

M2.2 überführt den bisherigen, chatgestützten Procurement Watch in ein eigenständig ausführbares und lokal reproduzierbares HDC-OS-Subsystem. Die akzeptierten Erkenntnisse aus `30-Procurement/Procurement.md` bleiben dabei gültig: Händlerregeln und Preisgrenzen sind Arbeitswerte, die Drei-Ampel-Regel bleibt maßgeblich, und der Project Owner trifft die finale Kaufentscheidung.

## Entscheidungen

### AD-M2.2-001: Procurement Cases sind fachlicher Ausgangspunkt

Procurement Cases bilden den fachlichen Ausgangspunkt. Produkte sind Kandidaten innerhalb eines Cases und nicht der primäre Prozessanker.

### AD-M2.2-002: Chats sind keine operative Datenhaltung

Chats und KI-Systeme sind optionale Benutzeroberflächen und Entscheidungsassistenten. Der Watcher muss ohne ChatGPT, Cloud-KI oder ein vollständiges HDC-OS betrieben werden können. Dauerhaft relevantes Wissen gehört in das Repository oder in lokale operative Speicher.

### AD-M2.2-003: SQLite als lokaler operativer Speicher

SQLite wird als lokaler operativer Datenspeicher eingesetzt. Schema, Migrationen, Regeln und Code werden versioniert; die produktive Datenbank, Preisbeobachtungen, Watch-Läufe, Logs und Reports bleiben außerhalb von Git. Die Zeitstrategie ist UTC.

### AD-M2.2-004: Eigenständiges Softwarepaket mit CLI und HTML-Report

Der Procurement Watch wird als eigenständig ausführbares Softwarepaket implementiert. CLI und lokaler HTML-Report bilden die erste Benutzeroberfläche und bleiben später als Diagnose- und Notfallwerkzeuge erhalten.

### AD-M2.2-005: Gesamter Lebenszyklus als fachlicher Rahmen

Der fachliche Rahmen berücksichtigt:

```text
Need
  → Procurement Case
  → Evaluation
  → Purchase Decision
  → Ordered
  → Received
  → Asset Handover
```

Bestellung, Inventarisierung und Monitoring werden in M2.2 nicht umgesetzt. `PurchaseDecision` bedeutet menschliche Freigabe oder Ablehnung; `AssetHandover` markiert nur die spätere Übergabegrenze.

### AD-M2.2-006: PriceObservations sind unveränderlich

Eine `PriceObservation` wird nach dem Anlegen niemals geändert oder überschrieben. Beobachtungen werden ausschließlich per `INSERT` erzeugt. Korrekturen oder neue Erkenntnisse erzeugen eine neue Beobachtung; die bisherige Historie bleibt vollständig erhalten. Die Datenbank schützt diese Eigenschaft zusätzlich gegen `UPDATE` und `DELETE`.

Damit bleiben Preisdiagramme, Trendanalysen, Auditierung, Reproduzierbarkeit, Debugging und spätere Machine-Learning-Auswertungen auf einer vollständigen Zeitreihe möglich.

## Konsequenzen

- Der Watch kann unabhängig und lokal getestet, betrieben und diagnostiziert werden.
- Angebots- und Beobachtungshistorien sind reproduzierbar speicherbar.
- Repository-Daten und lokale Laufzeitdaten müssen technisch und organisatorisch getrennt bleiben.
- Folgende Work Orders bauen auf diesen Verträgen auf: WO-0016 Runtime Foundation, WO-0017 PC-0001 Vertical Slice und WO-0018 Automation, Reporting & Operational Readiness.
- Jede Folge-Work-Order benötigt Review und ausdrückliche Freigabe vor Beginn.

## Nicht entschieden

Diese ADR legt keine konkrete Händlerquelle, Produktwahl, technische USV-Auslegung, Benachrichtigung, Scheduler-Aufgabe oder automatische Bestellung fest. Offene Detailfragen bleiben als spätere Review- oder Engineering-Arbeit erhalten.

## Referenzen

- [Procurement-Bestand](../../30-Procurement/Procurement.md)
- [Procurement-Architektur](../../30-Procurement/architecture/Procurement-Architecture.md)
- [Procurement-Datenmodell](../../30-Procurement/architecture/Data-Model.md)
- [Procurement-Ausführungsmodell](../../30-Procurement/architecture/Execution-Model.md)
- [Governance](../Governance.md)
