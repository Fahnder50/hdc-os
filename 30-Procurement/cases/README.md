---
document: README.md
version: 1.0
status: Draft
owner: Project Owner
reviewed_by: Lead Architect
last_review: ""
classification: Workspace
---

# Procurement Cases

## PC-0001

`PC-0001-Router-USV.yaml` ist der erste ausführbare Referenzfall des Procurement Watch. Die Datei enthält den Bedarf, das Zielgerät, das Budget und die zu prüfenden Anforderungen.

Technische Werte von Produkten werden nicht als bestätigte Tatsachen in den Case geschrieben. Fehlende Nachweise bleiben im Bewertungsstatus `UNKNOWN`.

Import:

```powershell
python -m procurement_watch case import 30-Procurement/cases/PC-0001-Router-USV.yaml
```
