---
document: Windows-Task-Scheduler.md
version: 1.0
status: Draft
owner: Project Owner
reviewed_by: Lead Architect
last_review: ""
classification: Workspace
---

# Windows Task Scheduler

Die Aufgabe wird nicht automatisch angelegt. Die Einrichtung erfolgt kontrolliert durch den Project Owner.

## Empfohlene Konfiguration

- Aufgabenname: `HDC-OS Procurement Watch`
- Programm: `C:\HDC\Workspace\30-Procurement\.venv\Scripts\python.exe`
- Argumente: `-m procurement_watch watch run`
- Arbeitsverzeichnis: `C:\HDC\Workspace\30-Procurement`
- Benutzerkontext: Benutzerkonto mit Schreibrechten auf Daten-, Log- und Reportpfad
- Intervall: einmal täglich, passend zum bestehenden Watch-Fenster
- Bei verpasstem Start: nächsten möglichen Start nachholen
- Bei Fehler: Task Scheduler protokolliert den Exit-Code; Diagnose über `doctor`, `events` und `watch runs`

## Manuelle Prüfung

```powershell
Set-Location C:\HDC\Workspace\30-Procurement
.\scripts\run-watch.ps1
python -m procurement_watch doctor
python -m procurement_watch watch runs
```

Die Aufgabe darf nur gestartet werden, wenn Pfade, Benutzerkontext und Umgebung geprüft wurden. Keine Secrets in Task-Argumenten hinterlegen.

## Deaktivierung und Entfernung

```powershell
Disable-ScheduledTask -TaskName "HDC-OS Procurement Watch"
Unregister-ScheduledTask -TaskName "HDC-OS Procurement Watch" -Confirm:$true
```

Vor der Entfernung einen letzten Status- und Backup-Check durchführen.
