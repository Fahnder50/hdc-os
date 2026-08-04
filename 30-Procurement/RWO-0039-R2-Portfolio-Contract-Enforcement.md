---
document: RWO-0039-R2-Portfolio-Contract-Enforcement.md
version: 1.0
status: Accepted
owner: Project Owner
reviewed_by: Lead Architect
last_review: "2026-08-04"
last_updated: "2026-08-04"
work_order: RWO-0039-R2
related_work_order: WO-0039
classification: Workspace
---

# RWO-0039-R2 – Portfolio Contract Enforcement for Completed Procurement

## Durchgesetzter Vertrag

Der Portfolio Runner selektiert vor jedem Aufruf der Watch Engine ausschließlich
die vier aktiven Lifecycle-Zustände. `PURCHASED` und `CANCELLED` werden in einer
separaten, rein informativen `Completed Procurement`-Liste geführt und niemals
an Live Watch, Foundation Watch, Evaluation, Recommendation, Journal Writer
oder Report Writer übergeben.

## Portfolio Summary

`Active Procurement` enthält ausschließlich aktive Cases und Kennzahlen für:

- `ACTIVE`,
- `WATCHING`,
- `QUALIFYING`,
- `READY_FOR_REVIEW`,
- `BUY_CANDIDATE`.

`Completed Procurement` enthält separat:

- Anzahl,
- Case-ID,
- Abschlussstatus,
- fachliches Abschlussdatum, sofern vorhanden.

Die Zusammenstellung der abgeschlossenen Cases liest ausschließlich persistente
Case- und Abschlussmetadaten. Sie löst keine Statusberechnung aus.

## Freeze-Vertrag

Der Wechsel nach `PURCHASED` oder `CANCELLED` erzeugt genau den letzten
Journal-Eintrag mit Engine-Status `CLOSED` und dokumentiert das Abschlussdatum.
Danach sind Case und Journal endgültig eingefroren.

Ein bereits vorhandener historischer HTML-Report eines abgeschlossenen Cases
wird auch bei manueller Reportabfrage nicht neu geschrieben. Fehlt ein
historischer Report, darf er einmalig aus ausschließlich vorhandenen Daten
erzeugt werden. Portfolio- und Watch-Läufe schreiben ihn niemals.

Manuelle Status-, History- und Reportabfragen bleiben lesend möglich. Sie
erzeugen keine Angebote, Beobachtungen, Bewertungen, Watch Runs,
Journal-Einträge oder Empfehlungen.

## Nicht geändert

Lifecycle-Status, Transition Contract, CLI-Kommandos, Reportformat, Scheduler,
Datenbankmodell, Asset Lifecycle, Operations, Infrastructure und Connectivity
Model bleiben unverändert.

Die Änderungen liegen uncommitted zur Review vor.
