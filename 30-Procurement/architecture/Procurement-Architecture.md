---
document: Procurement-Architecture.md
version: 1.0
status: Accepted
owner: Project Owner
reviewed_by: Lead Architect
last_review: "2026-07-20"
classification: Workspace
---

# Procurement-Architektur

## Zweck

Der Procurement Watch ist ein eigenständig ausführbares, lokal betriebenes HDC-OS-Subsystem. Er verwaltet Beschaffungsfälle, Anforderungen, Produktkandidaten, Händlerangebote und lokale Beobachtungshistorien. CLI und lokaler HTML-Report sind die ersten Benutzeroberflächen; Chats und KI-Systeme sind weder erforderlich noch operative Datenhaltung.

PC-0001 – Router-USV für einen geplanten Stromausfall – ist der vertikale Referenzfall. Der Fall dient zur Validierung der Architektur, ohne die Architektur auf eine einzelne USV oder einen einzelnen Händler zu begrenzen.

## Systemgrenzen

### Im Subsystem enthalten

- versionierte Procurement Cases, Anforderungen, Regeln und Konfigurationstemplates
- lokale Erfassung und Speicherung von Produkten, Angeboten und Preisbeobachtungen
- Quellenadapter, Normalisierung und Validierung
- Watch-Läufe, Regelbewertungen und nachvollziehbare Events
- lokale SQLite-Datenbank, CLI und HTML-Report
- vorbereitete Integration in einen späteren HDC-OS-Scheduler

### Ausdrücklich nicht enthalten

- automatische Bestellung, Zahlungsabwicklung oder Händlerkonten
- universelle Produktsuche, Browserautomatisierung oder Schutzmaßnahmen-Umgehung
- Cloud- oder KI-Abhängigkeit
- vollständiges Asset Management oder Monitoring gekaufter Geräte
- zentrales Dashboard, REST-API, Benutzerverwaltung und Remotezugriff

## Verantwortlichkeiten und Komponenten

| Komponente | Verantwortung | Darf nicht enthalten |
|---|---|---|
| Case Loader | Versionierte Cases und Anforderungen laden und validieren | operative Laufzeitdaten persistieren |
| Source Adapter | Angebote aus einer definierten Quelle lesen | fachliche Kaufentscheidung treffen |
| Collector | Quellen in einem Watch-Lauf anstoßen und Fehler isolieren | Normalisierungslogik duplizieren |
| Normalizer | Quellenformate in ein kanonisches Angebotsmodell überführen | unbekannte Werte als Fakten ergänzen |
| Validator | Pflichtfelder, Wertebereiche und Nachvollziehbarkeit prüfen | fehlende Nachweise als PASS werten |
| Procurement Service | Anwendungsfälle orchestrieren und Transaktionen steuern | Scheduler- oder UI-spezifische Logik enthalten |
| Rule Evaluator | Anforderungen und Kaufregeln auswerten | automatisch bestellen |
| Repository Layer | Domänenobjekte lesen und schreiben | Speicherabhängigkeiten in CLI oder Adapter tragen |
| SQLite Storage | lokale operative Daten persistent speichern | produktive DB im Repository ablegen |
| Event Generator | relevante Zustandsänderungen als Events erzeugen und deduplizieren | Benachrichtigungen versenden |
| CLI | Diagnose, Import, Watch und Auswertung auslösen | eigene Fachlogik implementieren |
| HTML Report Generator | lokale Darstellung aus der Service-Schicht erzeugen | abweichende Bewertungslogik enthalten |
| Scheduler Integration | externe Zeitplanung ansprechen bzw. dokumentieren | fachliche Abläufe in PowerShell verstecken |

## Write Path

Der Write Path ist der einzige Pfad für operative Änderungen:

```text
Source Adapter / manuelle Eingabe
  → Collector
  → Normalizer
  → Validator
  → Procurement Service
       ├── Repository Layer → SQLite Storage
       ├── Rule Evaluator
       └── Event Generator → Repository Layer → SQLite Storage
```

Konfiguration und Case werden vom Procurement Service als Ausführungskontext geladen. Der Service orchestriert die Verarbeitung, veranlasst nach erfolgreicher Validierung die Speicherung über den Repository Layer, übergibt den gespeicherten Zustand an den Rule Evaluator und persistiert daraus abgeleitete Events wieder über dieselbe Schicht. Events entstehen damit erst nach der Regelbewertung.

Jeder Watch-Lauf erhält eine Identität und einen Status. Angebote werden von Preisbeobachtungen getrennt gespeichert. Fehler einzelner Quellen werden am Lauf protokolliert und dürfen andere Quellen nicht unkontrolliert abbrechen; kritische Infrastruktur- oder Konfigurationsfehler beenden den Lauf mit Fehlerstatus.

## Read Path

CLI und HTML-Report lesen ausschließlich über dieselbe Service- und Repository-Schicht:

```text
SQLite Storage
  → Repository Layer
  → Procurement Service / Auswertung
  → CLI oder HTML Report Generator
```

Damit bleiben Statusermittlung, Regelbewertung und Empfehlungen zwischen CLI und Report identisch. `BUY_CANDIDATE` bedeutet ausschließlich „Kauf prüfen“ und löst keine Bestellung aus.

## Datenfluss und Laufzeitdaten

Versioniert werden Quellcode, Schema und Migrationen, Case-Definitionen, Regeldefinitionen, Konfigurationstemplates, Adapter, Tests, Skripte, Report-Templates und Dokumentation.

Lokal und außerhalb von Git bleiben die produktive SQLite-Datei, Preisbeobachtungen, Watch-Läufe, Logs, generierte Reports, lokale Konfigurationen und eventuelle Secrets. Pfade werden konfigurierbar gehalten; eine feste Abhängigkeit von `C:\HDC\Data` ist nicht Bestandteil der Architektur.

Zeitstempel werden einheitlich in UTC gespeichert. Eine lokale Darstellung darf die konfigurierte Zeitzone verwenden.

## Schnittstellen zu späteren HDC-OS-Modulen

Das Subsystem wird über stabile fachliche Services und IDs integriert, nicht über Chatverläufe oder direkte Datenbankzugriffe. Vorgesehene spätere Schnittstellen sind:

- Übergabe von Cases, Anforderungen und Freigabekontexten
- Abfrage von Status, Bewertungen, Angeboten und Events
- Übergabe eines bestätigten `AssetHandover` an ein späteres Asset-Modul
- Ausführung über einen späteren HDC-OS-Scheduler

Die lokale CLI und der HTML-Report bleiben als Diagnose- und Notfallwerkzeuge erhalten.

## Fehlerbehandlung

Validierungsfehler nennen Quelle, Case und Feld. Adapterfehler werden klassifiziert, lokal protokolliert und dem Watch-Lauf zugeordnet. Transaktionale Datenbankfehler führen zu Rollback und einem fehlgeschlagenen Lauf. Es werden keine Secrets oder vollständigen Zugangsdaten in Logs, Events oder Reports geschrieben.

## Erweiterbarkeit

Neue Quellen werden als Adapter ergänzt und liefern dasselbe kanonische Angebotsmodell. Weitere Regeltypen werden im Evaluator registriert. Repository Layer und SQLite Storage bleiben austauschbar, ohne Case-, Service- oder UI-Verträge zu verändern. Ein späterer Scheduler oder ein Dashboard ruft dieselben Services auf.

## Zielstruktur

```text
30-Procurement/
├── README.md
├── Procurement.md
├── architecture/
│   ├── Procurement-Architecture.md
│   ├── Data-Model.md
│   └── Execution-Model.md
├── cases/
├── config/
├── schema/migrations/
├── src/procurement_watch/
├── templates/
├── tests/
├── scripts/
└── examples/
```

Die Verzeichnisse für Runtime-Code und Laufzeitdaten werden in WO-0015 nur als Zielstruktur beschrieben. Ihre Implementierung folgt erst nach Review und Freigabe dieser Work Order.
