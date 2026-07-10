---
document: Bausteine.md
version: 1.0
status: Accepted
owner: Project Owner
reviewed_by: Lead Architect
last_review: -
classification: Workspace
---

# Bausteine

Dieses Dokument beschreibt die grundlegenden Bausteine von HDC-OS.

Ein Baustein ist ein logisch abgegrenzter Teil des Systems. Er hat eine klare Aufgabe und kann später erweitert werden.

Die Beziehungen zwischen den Bausteinen werden nicht in diesem Dokument beschrieben. Sie gehören in das spätere Dokument `Systemmodell.md`.

---

## Operations Platform

Die Operations Platform bildet den zentralen Betriebsbaustein von HDC-OS.

Sie verbindet alle weiteren Bausteine zu einem gemeinsamen System und koordiniert deren Zusammenarbeit.

---

## Services

Services sind fachliche Funktionsbereiche innerhalb von HDC-OS.

Ein Service übernimmt einen klar abgegrenzten fachlichen Aufgabenbereich innerhalb von HDC-OS.

Services können später verfeinert oder durch weitere Services ergänzt werden.

---

## Assets

Assets sind konkrete Objekte, die in HDC-OS verwaltet, überwacht oder dokumentiert werden.

Assets können physisch, virtuell oder logisch sein.

Der Fokus liegt auf der Infrastruktur, die für den Aufbau und Betrieb von HDC-OS relevant ist.

---

## Knowledge Base

Die Knowledge Base ist die Wissensbasis von HDC-OS.

Sie enthält bestätigtes Wissen über Infrastruktur, Entscheidungen, Betriebsinformationen und Erfahrungen.

Sie bildet die gemeinsame Wissensgrundlage für Services, AI Services und Automatisierungen.

Wissen wird bewusst einfach, nachvollziehbar und prüfbar gehalten.

---

## AI Services

AI Services erweitern HDC-OS um Analyse, Empfehlungen und Entscheidungsunterstützung.

AI Services analysieren Informationen, bereiten Empfehlungen vor und unterstützen Benutzer bei Entscheidungen.

HDC-OS bleibt ohne AI Services vollständig funktionsfähig.

AI Services unterstützen den Menschen, ersetzen ihn aber nicht.

---

## Automation

Automation führt definierte Prozesse kontrolliert auf Basis von Regeln, Wissen und Freigaben aus.

Kritische Änderungen bleiben an menschliche Kontrolle gebunden.

---

## Benutzer

Benutzer sind Menschen, die HDC-OS verwenden, Entscheidungen treffen oder Freigaben erteilen.

In der ersten Ausbaustufe ist der primäre Benutzer der Project Owner.

Das Modell bleibt offen für weitere Benutzer, Rollen oder Verantwortlichkeiten in späteren Ausbaustufen.
