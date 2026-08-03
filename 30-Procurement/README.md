---
document: 30-Procurement/README.md
version: 1.4.4-baseline
status: Accepted
owner: Project Owner
reviewed_by: Lead Architect
last_review: "2026-08-03"
release_reference: knowledge-v1.4.4
last_updated: "2026-08-03"
classification: Workspace
---

# Procurement Watch Runtime

## Repository Baseline

`knowledge-v1.4.4` ist die aktuelle Releasebasis. Das Projekt befindet sich in
Sprint 4 – First Deployment. Procurement Foundation und der erste Übergang nach
Operations sind abgeschlossen; die Runtime unterstützt jetzt die verbleibenden
aktiven Cases PC-0002 bis PC-0005 auf dem Weg zum ersten Deployment.

## Betriebsstand

Die lokale Python-3.12-Runtime verarbeitet ausschließlich Cases mit Status
`WATCHING`. Seit WO-0036 ist PC-0001 `PURCHASED`: Es wird nicht mehr beobachtet,
erzeugt keine neue Kaufempfehlung und bleibt nur als vollständige Historie
erhalten. Aktiv sind PC-0002 bis PC-0005.

Der Watch speichert Beobachtungen, Bewertungen, Journals und Reports lokal. Er
bestellt niemals automatisch und leitet keinen Asset-Betriebsstatus ab.

## Einstieg

Installation aus dem Repository-Root:

```powershell
python -m pip install -e 30-Procurement
```

Initialisierung und Portfolio-Import:

```powershell
python -m procurement_watch db init
python -m procurement_watch import --all
python -m procurement_watch portfolio status
```

Aktiver täglicher Lauf:

```powershell
python -m procurement_watch watch live --all
```

Direkte Aufrufe abgeschlossener Cases, beispielsweise `watch live PC-0001`,
werden abgewiesen. Historische Abfragen bleiben möglich:

```powershell
python -m procurement_watch status PC-0001
python -m procurement_watch offers PC-0001
python -m procurement_watch history PC-0001
python -m procurement_watch report PC-0001
```

## Aktive Cases und Quellen

| Case | Runtime-Status | Quellen-/Entscheidungsstand |
|---|---|---|
| PC-0001 | PURCHASED / CLOSED | Watch deaktiviert; Historie erhalten |
| PC-0002 | WATCHING | Digitus DN-48000/48001/48002 |
| PC-0003 | WATCHING | vier qualifizierte öffentliche Modellquellen; Horizon-1-Budgetstrategie |
| PC-0004 | WATCHING | TL-SG2008P V3 plus drei Alternativen |
| PC-0005 | WATCHING | CyberPower OR1000ERM1U |

Konkrete Quellen stehen in [`config/sources.yaml`](config/sources.yaml),
Portfolio-Budget in [`config/portfolio.yaml`](config/portfolio.yaml) und
Watch-Policy in [`config/watch-policy.yaml`](config/watch-policy.yaml).

## Lokale Daten und Datenschutz

Runtime-Daten werden nicht versioniert. Standardstruktur:

```text
runtime/
├── database.sqlite
├── journals/
├── logs/
├── cache/
└── observations/
```

Produktive Pfade können über `HDC_PROCUREMENT_RUNTIME`,
`HDC_PROCUREMENT_DB`, `HDC_PROCUREMENT_LOGS` und
`HDC_PROCUREMENT_REPORTS` gesetzt werden. Öffentliche Quellen sind login- und
secret-frei; operative Daten bleiben lokal.

## Weitere Befehle

```powershell
python -m procurement_watch db status
python -m procurement_watch migrate
python -m procurement_watch watch runs
python -m procurement_watch doctor
python -m procurement_watch events
python -m procurement_watch backup C:\HDC\Backups\procurement.db
python -m procurement_watch restore C:\HDC\Backups\procurement.db
```

Runbooks:

- [Operations Runbook](operations/Operations-Runbook.md)
- [Task Scheduler](operations/Windows-Task-Scheduler.md)
- [Backup and Restore](operations/Backup-and-Restore.md)

## Tests

```powershell
python -m pytest -q 30-Procurement/tests 20-Operations/tests
```

Tests verwenden isolierte temporäre Datenbanken. Repository- oder produktive
Runtime-Dateien dürfen dabei nicht entstehen.

## Historischer Hinweis

CLI-Beispiele mit aktivem `watch live PC-0001` und Aussagen über fünf aktive
Cases sind seit `knowledge-v1.4.4` superseded. Die Runtime-Funktionalität für
aktive Cases bleibt durch isolierte Regressionstests abgedeckt.
