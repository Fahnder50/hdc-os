---
document: Systemmodell.md
version: 1.0
status: Released
owner: Project Owner
reviewed_by: Lead Architect
last_review: ""
classification: Workspace
---

# Systemmodell

Dieses Dokument beschreibt den Informationsfluss und die Zusammenarbeit der Bausteine von HDC-OS.

Es dient als Referenzmodell für Horizon 1 und wird gemeinsam mit HDC-OS kontinuierlich weiterentwickelt.

Die einzelnen Bausteine werden hier nicht erneut erklärt. Der Text erläutert ausschließlich das folgende Diagramm.

```text
                        Benutzer
                            │
                            ▼
                 Operations Platform
                            │
        ┌───────────┬───────────┐
        ▼           ▼           ▼
    Services      Assets   Knowledge Base
        │            │           │
        └──────┬─────┘           │
               ▼                 │
             Events              │
               │                 │
               └────────► AI Services
                              │
                              ▼
                       Empfehlungen
                              │
                              ▼
                         Automation
                              │
                              ▼
                           Benutzer
```

---

## Grundprinzip

Das Systemmodell zeigt, wie Benutzer über die Operations Platform mit HDC-OS arbeiten.

Die Operations Platform verbindet die weiteren Bausteine zu einem gemeinsamen System und koordiniert deren Zusammenarbeit.

Das Diagramm beschreibt keine technische Implementierung. Es zeigt die fachliche Richtung des Informationsflusses.

---

## Informationsfluss

Der Informationsfluss beginnt beim Benutzer und läuft über die Operations Platform.

Von dort werden Services, Assets und Knowledge Base eingebunden.

Services und Assets können relevante Events erzeugen. Diese Events fließen weiter zu den AI Services.

Die daraus entstehenden Empfehlungen können durch den Benutzer bewertet oder – sofern zulässig – durch Automatisierungen umgesetzt werden.

---

## Rolle der Knowledge Base

Die Knowledge Base steht im Diagramm neben Services und Assets, weil sie den gemeinsamen Wissensstand bereitstellt.

Sie liefert Kontext für die Bewertung von Informationen und für die weitere Verarbeitung durch AI Services.

Im Diagramm fließt ihr Wissen direkt in Richtung AI Services.

---

## Rolle der AI Services

AI Services erhalten Informationen aus Events und aus der Knowledge Base.

Sie bereiten daraus Empfehlungen vor.

Die Empfehlungen sind Zwischenergebnisse. Sie ersetzen keine Entscheidung des Benutzers.

---

## Rolle der Automation

Automation folgt im Diagramm auf Empfehlungen.

Sie führt nur definierte Abläufe aus, wenn Regeln, Wissen und Freigaben dies zulassen.

Nach der Ausführung führt der Informationsfluss zurück zum Benutzer.

---

## Weiterentwicklung

Das Systemmodell beschreibt den Ausgangspunkt für Horizon 1.

Es kann erweitert werden, wenn HDC-OS zusätzliche Bausteine, Rollen oder Abläufe erhält.

Änderungen am Systemmodell müssen nachvollziehbar bleiben und dürfen keine neue Architektur ohne Review einführen.
