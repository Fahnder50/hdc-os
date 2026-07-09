---
document: Bausteine.md
version: 0.2
status: Draft
owner: Project Owner
reviewed_by: Lead Architect
last_review: -
classification: Workspace
---

# Bausteine

HDC-OS besteht aus mehreren Bausteinen.

Ein Baustein ist ein logisch abgegrenzter Teil des Systems. Jeder Baustein erfüllt eine bestimmte Aufgabe und arbeitet mit anderen Bausteinen zusammen.

Dieses Dokument beschreibt die zentralen Bausteine von HDC-OS. Die Beziehungen zwischen den Bausteinen werden im Dokument `Systemmodell.md` beschrieben.

---

## Operations Platform

Die Operations Platform ist der betriebliche Kern von HDC-OS.

Sie verbindet Infrastruktur, Services, Automatisierung, Wissen und Benutzerinteraktion zu einem gemeinsamen System.

---

## Services

Services sind fachliche Funktionsbereiche innerhalb von HDC-OS.

Ein Service beschreibt einen klar abgegrenzten Teil dessen, was HDC-OS leistet.

Beispiele:

- Network Security
- Monitoring
- Procurement
- Documentation
- Knowledge
- Backup
- Device Management

---

## Assets

Assets sind konkrete Objekte, die von HDC-OS verwaltet, überwacht oder dokumentiert werden.

Beispiele:

- Firewall
- Switch
- Router
- Laptop
- NAS
- Access Point
- Kamera
- Temperatursensor

---

## Knowledge Base

Die Knowledge Base ist das Wissensfundament von HDC-OS.

Sie enthält bestätigtes Wissen über Infrastruktur, Entscheidungen, Zusammenhänge, Betriebszustände und Erfahrungen.

---

## AI Services

AI Services erweitern HDC-OS um Analyse, Empfehlungen und Wissensaufbereitung.

HDC-OS muss auch ohne AI Services funktionsfähig bleiben. Die KI verbessert das System, ist aber keine Voraussetzung für den Grundbetrieb.

---

## Automation

Automation führt definierte Abläufe kontrolliert aus.

Automatisierung basiert auf Regeln, Services, Wissen und Freigaben. Kritische Aktionen benötigen menschliche Kontrolle.

---

## Benutzer

Benutzer sind Menschen, die HDC-OS verwenden, Entscheidungen treffen oder Freigaben erteilen.

In Horizon 1 ist der primäre Benutzer Daniel. Später können weitere Benutzer oder Administratoren hinzukommen.