---
document: Operations-Runbook.md
version: 1.0
status: Draft
owner: Project Owner
reviewed_by: Lead Architect
last_review: ""
classification: Workspace
---

# Procurement Watch Operations Runbook

## Installation

```powershell
Set-Location C:\HDC\Workspace
.\30-Procurement\scripts\install.ps1
.\30-Procurement\scripts\initialize.ps1
```

## Manueller Lauf

```powershell
python -m procurement_watch watch live PC-0001
```

Der Live-Lauf verwendet Timeout und begrenzte Wiederholungen. Teilfehler werden als `SOURCE_FAILED` gespeichert; mindestens eine erfolgreiche Quelle lässt den Lauf technisch erfolgreich bleiben. Lieferdaten werden gegen den 03.08.2026 bewertet. Der Befehl bestellt niemals automatisch.

```powershell
.\30-Procurement\scripts\run-watch.ps1
python -m procurement_watch status
python -m procurement_watch report PC-0001
```

Der Report liegt im konfigurierten lokalen Reportpfad. Er enthält keinen externen CDN- oder Cloud-Inhalt.

## Diagnose

```powershell
python -m procurement_watch doctor
python -m procurement_watch events
python -m procurement_watch watch runs
python -m procurement_watch db status
```

## Typische Fehler

- **Datenbank nicht erreichbar:** Pfad und Schreibrechte prüfen; keine DB im Repository anlegen.
- **Migration fehlt:** `python -m procurement_watch migrate` ausführen und danach `db status` prüfen.
- **Quelle fehlerhaft:** Source-ID und Fehlerklasse im JSONL-Log prüfen; einzelne Quellen dürfen den Gesamtlauf nicht unkontrolliert beenden.
- **Report fehlt:** Reportpfad prüfen, `report PC-0001` manuell ausführen und Logdatei kontrollieren.
- **Watch-Lauf fehlgeschlagen:** Exit-Code, `watch runs`, `events` und JSONL-Log korrelieren.

## Update

1. Watcher deaktivieren.
2. Datenbank und lokale Konfiguration sichern.
3. Repository aktualisieren.
4. Umgebung prüfen und `pip install -e .` ausführen.
5. `python -m procurement_watch migrate` ausführen.
6. `doctor`, Status und Report prüfen.
7. Watcher wieder aktivieren.

## Sicherheit und Datenschutz

Alle operativen Daten bleiben lokal. Keine Secrets in Repository, CLI-Argumente, Reports oder Logs speichern. Keine Zahlungsdaten, Händlerkonten oder automatische Bestellung verwenden. Öffentliche Quellen nur im erforderlichen Umfang und mit begrenzten Abrufintervallen nutzen.

## Deaktivierung

Task Scheduler deaktivieren, letzten Status erfassen, optional Backup erstellen und lokale Reports/Logs nach Aufbewahrungsregeln behandeln. Die SQLite-Datenbank nicht unkontrolliert löschen.
