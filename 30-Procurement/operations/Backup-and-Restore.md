---
document: Backup-and-Restore.md
version: 1.0
status: Draft
owner: Project Owner
reviewed_by: Lead Architect
last_review: ""
classification: Workspace
---

# Backup und Restore

## Grundsätze

- Die operative SQLite-Datenbank bleibt außerhalb des Git-Repositories.
- Backups werden aus einer konsistenten SQLite-Sicherung erzeugt.
- Konfigurationstemplates sind reproduzierbar im Repository; lokale Konfigurationen werden separat geschützt gesichert.
- Reports sind aus Datenbank und Code reproduzierbar und müssen nicht in Git gespeichert werden.
- Logs sind optionale Betriebsdaten und werden nach lokalem Aufbewahrungsbedarf gesichert.

## Backup

```powershell
.\30-Procurement\scripts\backup.ps1 C:\HDC\Backups\procurement-$(Get-Date -Format yyyyMMdd-HHmmss).db
```

Die Runtime verwendet die SQLite-Backup-API. Dadurch wird auch bei WAL-Betrieb eine konsistente Sicherung erzeugt.

## Restore

Ein Restore überschreibt keine bestehende Datenbank ohne ausdrückliche Bestätigung:

```powershell
.\30-Procurement\scripts\restore.ps1 C:\HDC\Backups\procurement-20260721-090000.db
.\30-Procurement\scripts\restore.ps1 C:\HDC\Backups\procurement-20260721-090000.db -Overwrite
```

Nach Restore:

```powershell
python -m procurement_watch db status
python -m procurement_watch doctor
python -m procurement_watch status
```

`runtime_metadata` zeigt, zu welchem Repository-Commit und welcher Schema-Version die Datenbank ursprünglich erzeugt wurde. Vor einem Update Backup erstellen, danach Migrationen ausführen und die DB erneut prüfen.
