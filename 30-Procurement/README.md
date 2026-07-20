---
document: README.md
version: 1.0
status: Draft
owner: Project Owner
reviewed_by: Lead Architect
last_review: ""
classification: Workspace
---

# Procurement Watch

## Voraussetzungen

- Windows 11 und Python 3.12
- PowerShell
- lokale Schreibrechte für den konfigurierten Daten-, Log- und Reportpfad

## Installation und Initialisierung

```powershell
.\30-Procurement\scripts\install.ps1
.\30-Procurement\scripts\initialize.ps1
```

Die produktive SQLite-Datenbank liegt standardmäßig unter `C:\HDC\Data\procurement\procurement.db` und wird nicht im Repository erzeugt. Bei der Initialisierung werden Repository-Commit, Repository-Version, Schema-Version und Erstellungszeitpunkt in `runtime_metadata` gespeichert.

## CLI

```powershell
python -m procurement_watch db init
python -m procurement_watch db status
python -m procurement_watch migrate
python -m procurement_watch watch run
python -m procurement_watch status
```

Ohne konfigurierte Händlerquellen führt `watch run` einen kontrollierten Foundation-Lauf aus. Echte Quellen sind Bestandteil späterer Work Orders.

## Lokale Pfade

Die Pfade können über `HDC_PROCUREMENT_DB`, `HDC_PROCUREMENT_LOGS` und `HDC_PROCUREMENT_REPORTS` überschrieben werden. Ein Repository-Versionslabel kann über `HDC_REPOSITORY_VERSION` gesetzt werden; ansonsten wird der letzte Git-Tag oder `unreleased` verwendet.

## Tests

```powershell
python -m pytest
```

Tests verwenden ausschließlich temporäre Datenbanken.

Konfigurationstemplates werden mit `load_yaml_config` geladen und validieren eine Mapping-Struktur. Die Foundation führt noch keine Quellen aus.

## Datenschutz und Einschränkungen

Operative Daten, Logs und Reports bleiben lokal. Keine Secrets werden versioniert. Die Runtime enthält noch keine Live-Händlerabrufe, automatische Kaufentscheidung, Bestellung, Benachrichtigung oder KI-Integration.

## Troubleshooting

- Fehlt Python, zuerst Python 3.12 installieren und erneut `install.ps1` ausführen.
- Fehlt die virtuelle Umgebung, `install.ps1` erneut ausführen.
- Prüfe bei Datenbankproblemen den Pfad mit `db status` und die Schreibrechte des Zielordners.
- Prüfe die gespeicherte Herkunft einer Datenbank über die Tabelle `runtime_metadata`.
