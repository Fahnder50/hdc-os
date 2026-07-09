---
document: Begriffe.md
version: 0.1
status: Draft
owner: Project Owner
reviewed_by: Lead Architect
last_review: -
classification: Workspace
---

# Begriffe

Dieses Dokument erklärt zentrale Begriffe von HDC-OS.

Es ist kein Architekturmodell und keine Betriebsdokumentation. Es dient dazu, Begriffe einheitlich zu verwenden, damit Menschen und spätere KI-Komponenten dieselbe Sprache sprechen.

---

## HDC-OS

HDC-OS ist eine KI-gestützte Operations-Plattform für den sicheren, automatisierten und nachhaltigen Betrieb einer IT-Infrastruktur.

HDC-OS besteht aus mehreren Services, Dokumentationsbestandteilen, Automatisierungen, Betriebsprozessen und später KI-gestützten Agenten.

---

## Service

Ein Service ist ein klar abgegrenzter Funktionsbereich innerhalb von HDC-OS.

Ein Service beschreibt nicht das gesamte HDC-OS, sondern einen Teil dessen, was HDC-OS leistet.

Beispiele:

- Network Security Service
- Knowledge Service
- Procurement Service
- Documentation Service
- Project Governance Service

---

## Agent

Ein Agent ist eine spezialisierte unterstützende Rolle innerhalb von HDC-OS.

Ein Agent kann Informationen analysieren, Empfehlungen geben, Aufgaben vorbereiten oder später definierte Automatisierungen auslösen.

Ein Agent handelt nicht unkontrolliert. Kritische Entscheidungen benötigen menschliche Freigabe.

Beispiele:

- Documentation Agent
- Procurement Agent
- Operations Agent
- Architecture Review Agent

---

## Asset

Ein Asset ist ein konkretes Objekt innerhalb der Infrastruktur oder des Projekts.

Assets können physisch, virtuell oder logisch sein.

Beispiele:

- Firewall
- Switch
- Laptop
- Rack
- USV
- Dokument
- Repository

---

## Workspace

Der Workspace ist der zentrale Arbeitsbereich für die Entwicklung und Dokumentation von HDC-OS.

Er enthält Projektdokumente, Architekturentscheidungen, Betriebsinformationen und später weitere Wissensartefakte.

---

## Knowledge Base

Die Knowledge Base ist die wachsende Wissensbasis von HDC-OS.

Sie enthält bestätigtes Wissen über Infrastruktur, Entscheidungen, Services, Assets, Betriebsprozesse und Zusammenhänge.

---

## Systemmodell

Das Systemmodell beschreibt die Beziehungen zwischen Begriffen, Services, Assets, Agenten, Events, Tickets und Automatisierungen.

Es erklärt nicht nur, was einzelne Begriffe bedeuten, sondern wie sie zusammenwirken.

---

## Event

Ein Event ist ein relevantes Ereignis innerhalb von HDC-OS.

Ein Event kann durch Monitoring, Benutzerinteraktion, Automatisierung oder externe Informationen entstehen.

Beispiele:

- Update verfügbar
- Gerät offline
- Preisziel erreicht
- Sicherheitswarnung erkannt
- Backup fehlgeschlagen

---

## Ticket

Ein Ticket dokumentiert eine Aufgabe, Entscheidung, Störung, Änderung oder Empfehlung.

Tickets dienen der Nachvollziehbarkeit und können später durch Agents vorbereitet oder erzeugt werden.

---

## Review

Ein Review ist die Prüfung eines Dokuments, einer Entscheidung oder eines Änderungsvorschlags.

Ein Review kann zu Freigabe, Änderungswunsch oder Ablehnung führen.

---

## Release

Ein Release ist eine freigegebene Version eines Dokuments oder Artefakts, die offiziell in den Workspace übernommen wird.

---

## Automation

Automation bezeichnet eine definierte, wiederholbare Ausführung von Aufgaben.

Automatisierung erfolgt in HDC-OS kontrolliert, dokumentiert und mit klarer Freigabelogik.

---

## Policy

Eine Policy ist eine verbindliche Regel, nach der HDC-OS Entscheidungen vorbereitet oder bewertet.

Beispiele:

- Kritische Änderungen benötigen Freigabe.
- Produktive Geräte dürfen nicht dauerhaft außerhalb der Firewall betrieben werden.
- Hardware wird erst gekauft, wenn Architektur, Technik und Wirtschaftlichkeit erfüllt sind.
