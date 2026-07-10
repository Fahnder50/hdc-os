---
document: Governance.md
version: 1.0
status: Accepted
owner: Project Owner
reviewed_by: Lead Architect
last_review: "2026-07-10"
classification: Workspace
---

# Governance

## Zweck

Dieses Dokument ergänzt die in Sprint 1 entstandenen Arbeitsregeln.

Es wiederholt nicht den Entwicklungsprozess, sondern dokumentiert ergänzende Regeln für saubere Repository-Arbeit.

---

## Freigabe und Commit

Der Repository Engineer führt keinen Commit ohne ausdrückliche Freigabe des Project Owners aus.

`Accepted` ist die fachliche Freigabe eines Artefakts.

Ein Commit, Push, Tag oder Release erfolgt nur, wenn dies ausdrücklich beauftragt oder freigegeben wurde.

Kritische Architektur-, Sicherheits- oder Governance-Änderungen benötigen eine bewusste und dokumentierte Freigabe des Project Owners.

---

## Nachweis nach Umsetzung

Nach jeder Work Order müssen mindestens gezeigt beziehungsweise protokolliert werden:

```text
git status
git diff
```

Bei bereits gestagten Änderungen ist zusätzlich ein geeigneter Diff des Staging-Bereichs bereitzustellen.

---

## Repository Health Check

Vor einem Abschluss oder Release wird der Repository-Zustand geprüft.

Der Health Check umfasst mindestens:

- `git status`
- relevante Diffs
- gültiges YAML-Front-Matter
- Markdown-Rendering
- interne relative Links
- Dateipfade und Dateinamen
- ungewollte Dateien
- bestehende Tags und Releases
- Konsistenz zwischen Dokumentstatus, Commit und Releasezustand
- README-Rendering auf GitHub, sofern GitHub-Zugriff verfügbar ist

---

## Scope-Regeln für Work Orders

Der Scope einer Work Order ist verbindlich.

Nur der ausdrücklich erlaubte Dateiscope darf verändert werden.

Der Scope darf nicht eigenmächtig erweitert werden.

Nicht angeforderte „Verbesserungen“ sind ausgeschlossen.

Bei Widersprüchen oder fehlenden Informationen darf keine neue fachliche Entscheidung erfunden werden.

Die Unklarheit ist als Review Finding zu dokumentieren.

---

## Git-Arbeitsweise

Änderungen werden erst nach Review und Freigabe committed.

Commits erhalten eine nachvollziehbare Commit Message.

Tags markieren definierte Projektstände.

Der Remote-Stand auf GitHub wird nach Pushes geprüft.

---

## Release-Vorbereitung

Vor einem Release müssen die betroffenen Dokumente fachlich freigegeben sein.

Der Release-Zustand wird im Repository dokumentiert.

Ein Release-Tag wird nur erstellt, wenn der Auftrag dies ausdrücklich vorsieht.

---

## Review-Erkenntnisse

Reviews dienen dazu, Dokumente zu schärfen, Scope-Fehler zu erkennen und den Workspace konsistent zu halten.

Review-Ergebnisse werden über Review Work Orders nachvollziehbar umgesetzt.

Accepted bedeutet fachliche Freigabe, Released bedeutet veröffentlichter Projektstand.

---

## Chat und Workspace

Der Chat bleibt Denk- und Arbeitsraum.

Dauerhaft relevantes Wissen muss in den Workspace überführt werden.

Der Workspace ist die verbindliche Source of Truth.
