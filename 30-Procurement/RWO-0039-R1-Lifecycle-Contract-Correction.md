---
document: RWO-0039-R1-Lifecycle-Contract-Correction.md
version: 1.0
status: Accepted
owner: Project Owner
reviewed_by: Lead Architect
last_review: "2026-08-04"
last_updated: "2026-08-04"
work_order: RWO-0039-R1
related_work_order: WO-0039
classification: Workspace
---

# RWO-0039-R1 – Finalize Generic Procurement Lifecycle Contract

## Korrekturergebnis

Der Lifecycle-Vertrag besitzt exakt sechs persistierbare Status. `CLOSED` wurde
aus Validierung, Import- und Migrationsvertrag entfernt und wird ausschließlich
als abgeleitete Runtime-Archivansicht erzeugt.

`transition_case_status` ist die zentrale Transition Engine. Import und
persistente Runtime-Wechsel verwenden diese eine Prüffunktion. Vorwärtsschritte,
Abschluss durch `PURCHASED` sowie Abbruch durch `CANCELLED` sind explizit
erlaubt; alle übrigen Wechsel werden technisch blockiert.

Der Procurement Core importiert nur eine optionale, domänenneutrale
`external_reference`. Er kennt keine Asset-, Operations-, Infrastructure- oder
Acceptance-Semantik.

## Regression

Die Review-Regression deckt ab:

- sechs persistente Status und Ablehnung von `CLOSED`,
- alle erlaubten und geforderten verbotenen Übergänge,
- endgültige Unveränderlichkeit abgeschlossener Cases,
- Schwimmbrillen-Workflow bis `CANCELLED` ohne Operations-Komponenten,
- Router-USV-Workflow bis `PURCHASED` mit ausschließlich externer Referenz,
- Portfolio-, Report-, Journal- und Runtime-Verhalten.

Die Änderungen bleiben uncommitted zur erneuten Review.
