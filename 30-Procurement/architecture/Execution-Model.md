---
document: Execution-Model.md
version: 1.0
status: Accepted
owner: Project Owner
reviewed_by: Lead Architect
last_review: "2026-07-20"
classification: Workspace
---

# Procurement-Ausführungsmodell

## Standardablauf

```text
Konfiguration laden
  → Case laden
  → aktive Quellen bestimmen
  → Angebote abrufen
  → Daten normalisieren
  → Daten validieren
  → Beobachtungen speichern
  → Regeln auswerten
  → Events erzeugen
  → Lauf protokollieren
  → CLI- und Report-Daten bereitstellen
```

Die Schritte werden durch den Procurement Service orchestriert. Fachlogik liegt weder im Scheduler noch in PowerShell-Wrappern. Jede Ausführung erhält eine `WatchRun`-ID; Start, Ende, Status und Teilergebnisse werden lokal gespeichert.

## Schrittverträge

1. **Konfiguration laden:** Pfade, Quellen und Regeln laden; fehlende oder ungültige Pflichtwerte führen zu einem verständlichen Konfigurationsfehler.
2. **Case laden:** aktive, versionierte Cases laden und fachliche IDs prüfen.
3. **Aktive Quellen bestimmen:** nur konfigurierte und für den Case zugelassene Adapter verwenden.
4. **Angebote abrufen:** jede Quelle isoliert ausführen; ein Quellenfehler wird als Ergebnis protokolliert.
5. **Normalisieren:** Quellenformate in Product-, Vendor- und Offer-Werte überführen; unbekannte Werte bleiben unbekannt.
6. **Validieren:** Wertebereiche, Pflichtfelder und Quellenbezug prüfen. Ungültige Daten werden nicht als gültige Beobachtung weitergereicht.
7. **Beobachtungen speichern:** Offer und PriceObservation getrennt speichern; Historie bleibt nachvollziehbar.
8. **Regeln auswerten:** Anforderungen und Kaufregeln mit PASS, FAIL, UNKNOWN oder NOT_APPLICABLE bewerten.
9. **Events erzeugen:** relevante neue Zustände oder Zustandswechsel dedupliziert erzeugen.
10. **Lauf protokollieren:** erfolgreich, teilweise erfolgreich oder fehlgeschlagen abschließen; kritische Fehler erhalten einen Fehler-Exit-Code.
11. **Daten bereitstellen:** CLI und Report lesen denselben aufbereiteten Service-Zustand.

## Ausführungsarten

### Manueller CLI-Aufruf

Die CLI ist der primäre Diagnose- und Startpunkt. Sie ruft ausschließlich den Procurement Service auf und kann einzelne Status-, Import- oder Watch-Operationen auslösen.

### PowerShell-Wrapper

PowerShell-Skripte prüfen Umgebung und Exit-Code, rufen das Python-Paket auf und zeigen Fehler verständlich an. Sie enthalten keine Case-, Regel- oder Quellenlogik.

### Windows Task Scheduler

Der Scheduler startet den dokumentierten Wrapper unter einem festgelegten Arbeitsverzeichnis und Benutzerkontext. Die Aufgabe wird nicht automatisch angelegt. Einrichtung und Deaktivierung werden als Betriebsdokumentation bereitgestellt.

### Später Linux/systemd

Ein späterer systemd-Timer kann denselben CLI-Einstiegspunkt verwenden. Plattformabhängige Pfade, Benutzerrechte und Logging werden außerhalb der Fachlogik konfiguriert.

### Späterer HDC-OS Scheduler

Eine Integration in HDC-OS verwendet den gleichen Service-Aufruf und die gleichen Run- und Event-Verträge. Der Procurement Watch bleibt lokal lauffähig, falls HDC-OS oder ein Chat nicht verfügbar ist.

## Fehler- und Wiederholungsstrategie

Quellenfehler werden pro Source und Case isoliert. Ein Lauf kann dadurch teilweise erfolgreich sein. Datenbank-, Migrations- und Konfigurationsfehler sind kritisch: Transaktionen werden zurückgerollt, der Lauf wird als fehlgeschlagen markiert und der Prozess beendet sich mit Fehlerstatus. Wiederholungen müssen idempotent sein; bereits angewandte Migrationen und identische fachliche Zustände dürfen keine unkontrollierten Duplikate erzeugen.

## Write Path und Read Path

Der Write Path endet nach Validierung in SQLite und erzeugt daraus Bewertungen und Events. Der Read Path beginnt bei SQLite und führt über Repository und Procurement Service zu CLI oder Report. Kein Ausführungstyp darf einen zweiten Bewertungsweg einführen.

## Scope von WO-0015

Dieses Dokument definiert Verträge und Ablauf, implementiert aber noch keine Python-Komponenten, SQLite-Migrationen, Händleradapter, CLI, Reports oder Scheduler-Aufgaben. PC-0001 bleibt ein vorgesehener Referenzfall und wird erst in einer freigegebenen Folge-Work-Order ausführbar.
