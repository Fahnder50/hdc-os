---
document: DEVELOPMENT.md
version: 1.0
status: Draft
owner: Project Owner
reviewed_by: Lead Architect
last_review: ""
classification: Workspace
---

# Entwicklung

## Zweck

Dieses Dokument beschreibt den offiziellen Entwicklungsprozess von HDC-OS.

Ziel ist es, dass HDC-OS jederzeit anhand des Repositories weiterentwickelt werden kann, ohne auf Wissen aus einzelnen Chats angewiesen zu sein.

---

## Entwicklungsprinzipien

### Architektur vor Implementierung

Arbeit beginnt mit einem fachlich nachvollziehbaren Ziel und einer passenden Einordnung in die bestehende Architektur.

### Kleine nachvollziehbare Schritte

Änderungen werden in kleinen, prüfbaren Einheiten umgesetzt.

### Sprintziel vor neuen Ideen

Neue Ideen werden erst eingeordnet, wenn das aktuelle Sprintziel nicht gefährdet wird.

### Review vor Commit

Änderungen werden vor einem Commit geprüft und erst nach Freigabe übernommen.

### Wissen wird unmittelbar dokumentiert

Dauerhaft relevantes Wissen wird zeitnah in geeigneten Repository-Dokumenten festgehalten.

### Dauerhaft relevantes Wissen gehört in das Repository

Der Workspace bleibt die verbindliche Wissensbasis für HDC-OS.

---

## Rollen

### Project Owner

Der Project Owner verantwortet Vision, Prioritäten und Freigaben.

### Lead Architect

Der Lead Architect verantwortet Architektur, Konsistenz und Reviews.

### Repository Engineer

Der Repository Engineer setzt Änderungen im Repository um, dokumentiert Ergebnisse und hält die Struktur nachvollziehbar.

### Benutzer

Benutzer nutzen HDC-OS, geben Feedback und treffen Entscheidungen im vorgesehenen Rahmen.

---

## Arbeitsartefakte

### Work Order (WO)

Eine Work Order beschreibt neue Arbeit.

### Review Work Order (RWO)

Eine Review Work Order beschreibt die Überarbeitung bestehender Arbeit.

### Workspace Audit (WA)

Ein Workspace Audit prüft, ob dauerhaft relevantes Wissen vollständig im Repository dokumentiert ist.

### Review

Ein Review ist die fachliche Prüfung eines Artefakts.

### Accepted

Accepted ist die fachliche Freigabe eines Artefakts vor dem Commit.

### Commit

Ein Commit übernimmt akzeptierte Änderungen in die Versionshistorie.

### Release

Ein Release veröffentlicht einen definierten Projektstand.

---

## Lebenszyklus eines Artefakts

### Draft

Ein Artefakt befindet sich in Bearbeitung. Es ist noch nicht freigegeben.

### Review

Das Artefakt wird geprüft. Änderungsbedarf wird als Review Work Order dokumentiert.

### Accepted

Das Artefakt ist fachlich freigegeben. Es kann in die Versionshistorie übernommen werden.

Accepted bedeutet nicht automatisch Released.

### Committed

Die akzeptierte Änderung ist im Git Repository versioniert.

### Released

Ein definierter Projektstand wurde veröffentlicht und kann als Referenz genutzt werden.

---

## Sprintmodell

### Sprint Planning

Das Sprintziel wird festgelegt und die nächsten Arbeiten werden eingeordnet.

### Umsetzung

Die geplanten Arbeiten werden über Work Orders im Repository umgesetzt.

### Review

Ergebnisse werden geprüft und bei Bedarf über Review Work Orders überarbeitet.

### Workspace Audit

Der Workspace wird auf Vollständigkeit, Nachvollziehbarkeit und dauerhaft relevantes Wissen geprüft.

### Sprint Retrospektive

Der Ablauf wird kurz ausgewertet, damit der Entwicklungsprozess verbessert werden kann.

### Sprint Closed

Der Sprint wird geschlossen, wenn die akzeptierten Ergebnisse committed und bei Bedarf released wurden.

---

## Source of Truth

Der Workspace ist die verbindliche Wissensbasis von HDC-OS.

Der Chat dient ausschließlich der Diskussion, Ideenfindung und gemeinsamen Ausarbeitung.

Dauerhaft relevantes Wissen darf nicht ausschließlich in Chats verbleiben.

Eine Entscheidung gilt erst dann als Bestandteil von HDC-OS, wenn sie im Repository dokumentiert und versioniert wurde.

---

## Schlussregel

Ein neuer Chat muss HDC-OS allein anhand des Repositories vollständig weiterentwickeln können.
