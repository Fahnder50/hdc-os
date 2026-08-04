---
work_order: RWO-0039-R3
title: Runtime Database Upgrade & Legacy Case Migration
type: Procurement Review Work Order
status: Accepted
priority: High
sprint: Sprint 4 – First Deployment
related_work_order: WO-0039
date: 2026-08-04
reviewed_by: Lead Architect
last_review: 2026-08-04
---

# RWO-0039-R3 – Runtime Database Upgrade & Legacy Case Migration

## Ziel

Bestehende Runtime-Datenbanken werden beim regulären Start automatisch mit den im Repository bereits fachlich abgeschlossenen Procurement Cases abgeglichen. Dadurch gilt der mit WO-0039 definierte Lifecycle-Vertrag auch für Datenbanken, die vor seiner Einführung erstellt wurden.

## Verbindlicher Upgrade-Vertrag

- Das Repository ist während des Upgrades die führende Quelle für die Abschlusszustände `PURCHASED` und `CANCELLED`.
- Nur ein im Repository abgeschlossener, in der Runtime aber noch aktiver Case wird migriert.
- Die Migration läuft getrennt von der normalen Transition Engine. Sie erweitert weder deren erlaubte Übergänge noch den Lifecycle-Vertrag.
- Der Zielstatus entspricht exakt dem Abschlussstatus des Repository-Dokuments.
- Ein vorhandenes Abschlussdatum bleibt unverändert. Fehlt es, wird `closed_at`, `purchased_at` oder `cancelled_at` aus dem Repository übernommen; ersatzweise bleibt der vorhandene Runtime-Zeitbezug maßgeblich.
- Das Abschlussmerkmal `closed_flag: true` wird nur ergänzt, wenn es fehlt.
- Genau ein abschließender Journal-Eintrag mit dem Status `CLOSED` wird ergänzt, sofern noch keiner existiert.

## Schutz historischer Daten

Der Abgleich verändert ausschließlich fehlenden Abschlussstatus und fehlende Abschlussmetadaten. Insbesondere bleiben erhalten:

- Preisbeobachtungen und Angebote
- Händler und Produktzuordnungen
- Bewertungen und externe Referenzen
- bestehende Journal-Einträge
- Watch Runs und Portfolio-Historie
- erzeugte HTML-Reports einschließlich Inhalt und Zeitstempel

Historische Reports werden durch den Upgrade-Pfad weder neu erzeugt noch synchronisiert.

## Idempotenz

Der einmalige Abgleich wird bei der ersten Initialisierung mit RWO-0039-R3 geprüft und anschließend durch eine persistente Upgrade-Markierung abgeschlossen. Weitere Starts erzeugen keine zusätzlichen Statusänderungen, Metadaten oder Journal-Einträge. Neu angelegte Datenbanken erhalten die Markierung bei ihrer Erstellung; später regulär importierte aktive Cases werden daher nicht als Legacy-Bestand interpretiert.

## Portfolio-Wirkung

Nach dem Upgrade werden migrierte Cases vom bestehenden Portfolio-Vertrag als `Completed Procurement` behandelt. Sie gelangen nicht mehr an Watch Engine, Recommendation Engine, Report Generator oder Journal Writer. `PURCHASED` und `CANCELLED` besitzen dabei identische Sperrwirkung.

## Validierung

Die Regression deckt folgende Szenarien ab:

1. Legacy Case `QUALIFYING` im Runtime-Stand und `PURCHASED` im Repository.
2. Gemeinsames Portfolio mit `PURCHASED`, `CANCELLED`, `QUALIFYING` und `WATCHING`.
3. Wiederholter Upgrade-Lauf ohne weitere Änderungen.
4. Neue Datenbank ohne erforderliche Legacy-Migration.
5. Unveränderte historische Reports, Journale und Runtime-Daten.

## Nicht Bestandteil

Keine Änderung erfolgt an Lifecycle-Zuständen, normalen Transition-Regeln, CLI, Report-Funktionen, Asset Lifecycle, Operations, Infrastructure oder Connectivity.
