---
document: WO-0039-Generic-Procurement-Lifecycle.md
version: 1.0
status: Accepted
owner: Project Owner
reviewed_by: Lead Architect
last_review: "2026-08-04"
last_updated: "2026-08-04"
work_order: WO-0039
classification: Workspace
---

# WO-0039 – Generic Procurement Lifecycle & Runtime Refinement

## Ergebnis

Der Procurement-Lifecycle ist generisch und vollständig von Asset Lifecycle,
Infrastructure Core und Operations entkoppelt. Die verbindliche Definition
steht in [Generic Procurement Lifecycle](architecture/Generic-Procurement-Lifecycle.md).

## Umgesetzte Deliverables

- zentraler Lifecycle-Vertrag mit vier aktiven, zwei abschließenden und einem
  archivierenden Zustand,
- konsistente Filter in Foundation Watch, Live Watch, Portfolio Watch,
  Portfolio Status, Journal-Backfill und manuellen Mutationen,
- schreibgeschützte Abschlussansicht ohne neue Markt- oder Kaufbewertung,
- separater Bereich `Completed Procurement` in der Portfolio-Ausgabe,
- widerspruchsfreie aktive und abgeschlossene Reports,
- generische optionale externe Übergabereferenz ohne Asset-Pflicht,
- Migration PC-0001 bis PC-0005 auf `lifecycle_version: 2`,
- Regressionstests für Lifecycle, Webzugriffe, Journal, Portfolio, Abschluss,
  Historie und Nicht-Asset-Fälle.

## Nicht geändert

Asset Lifecycle, Infrastructure Core, Assetdatensätze und Operations bleiben
unverändert. Es wurden keine neuen produktiven Procurement Cases angelegt.

## Reviewstatus

Die Änderungen liegen uncommitted zur Review vor.
