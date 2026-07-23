---
document: Data-Model.md
version: 1.0
status: Accepted
owner: Project Owner
reviewed_by: Lead Architect
last_review: "2026-07-20"
classification: Workspace
---

# Procurement-Datenmodell

## Speicher- und Identitätsregeln

Repository-Dateien definieren Cases, Anforderungen, Regeln und Templates. Operative Entitäten und ihre Historien werden lokal in SQLite gespeichert. Fachliche IDs sind stabil, menschenlesbar und von technischen Primärschlüsseln unabhängig. Zeitstempel werden in UTC geführt.

Ein `Product` beschreibt einen Produktkandidaten. Ein `Offer` beschreibt das Angebot eines Händlers für dieses Produkt zu einem bestimmten Abrufkontext. Eine `PriceObservation` beschreibt einen beobachteten Zustand eines Angebots zu einem Zeitpunkt. Diese drei Ebenen werden nicht zusammengelegt.

## Entitäten

| Entität | Zweck und wichtigste Felder | Identität und Beziehungen | Lebenszyklus / Zuständigkeit / Speicher |
|---|---|---|---|
| `ProcurementCase` | Beschaffungsbedarf mit Titel, Status, Priorität, Budget und Need | `case_id`; hat Requirements und CaseProducts | Need → Evaluation → Decision → Ordered → Received → Handover; Case Loader / Repository-Datei plus SQLite-Projektion |
| `Requirement` | Prüfkriterium eines Cases, inklusive Sollwert, Pflichtgrad und Nachweisstatus | `requirement_id` innerhalb des Cases; gehört zu ProcurementCase | offen → bewertet; Rule Evaluator / Case-Datei, Ergebnis in SQLite |
| `Product` | Technischer Produktkandidat mit Hersteller, Modell, Referenz und bekannten Eigenschaften | `product_id`; wird über CaseProduct Cases zugeordnet und von Offers referenziert | Kandidat → bewertet → ausgewählt oder verworfen; Procurement Service / SQLite |
| `CaseProduct` | Zuordnung eines Produkts zu einem Case, einschließlich Kandidatenstatus | Kombination aus `case_id` und `product_id` | vorgeschlagen → geprüft → aktiv/inaktiv; Procurement Service / SQLite |
| `Vendor` | Händler- oder Anbieteridentität mit Qualitäts- und Quellenmerkmalen | `vendor_id`; referenziert von Offers | bekannt → geprüft → gesperrt/aktiv; Procurement Service / SQLite |
| `Offer` | Konkretes Händlerangebot mit URL/Quelle, Preis, Versand und Verfügbarkeit | `offer_id`; gehört zu Product und Vendor | entdeckt → beobachtet → abgelaufen/ungültig; Collector / SQLite |
| `PriceObservation` | Unveränderliche Momentaufnahme von Preis, Versand, Gesamtpreis, Währung, Verfügbarkeit und Quelle | `observation_id`; gehört zu Offer und WatchRun | erzeugt und unverändert archiviert; Collector/Normalizer / SQLite |
| `Evaluation` | Ergebnis einer Regelprüfung mit PASS, FAIL, UNKNOWN oder NOT_APPLICABLE und Begründung | `evaluation_id`; referenziert Case, Requirement und optional Offer/Run | je Lauf neu nachvollziehbar; Rule Evaluator / SQLite |
| `WatchRun` | Ausführungskontext mit Start, Ende, Status und Fehlerzähler | `watch_run_id`; enthält Results und Observations | started → succeeded/failed/partial; Procurement Service / SQLite |
| `WatchRunResult` | Ergebnis einer Quelle oder Case-Verarbeitung innerhalb eines WatchRuns | `result_id`; gehört zu WatchRun, optional Case und Source | pending → succeeded/failed/skipped; Collector / SQLite |
| `Event` | Nachvollziehbarer relevanter Zustand oder Zustandswechsel, z. B. BudgetExceeded | `event_id`, `event_type`, `severity`; deduplizierbarer Schlüssel aus Typ und fachlichem Kontext | open → acknowledged/resolved/superseded; Event Generator / SQLite |
| `PurchaseDecision` | Menschlich verantwortete Entscheidung oder Freigabe mit Begründung | `decision_id`; gehört zu ProcurementCase und referenziert Evaluationsstand | proposed → approved/rejected/withdrawn; Project Owner / SQLite |
| `AssetHandover` | Übergabe eines erhaltenen Beschaffungsgegenstands an ein späteres Asset-Modul | `handover_id`; gehört zu Case/Product und referenziert PurchaseDecision | planned → handed_over/cancelled; Procurement Service / SQLite |

## Event-Vertrag

Jedes Event besitzt neben seinem fachlichen `event_type` eine feste Schweregrad-Klassifizierung. Verbraucher wie HTML-Report, Scheduler und spätere Benachrichtigungen verwenden diese Klassifizierung und leiten die Dringlichkeit nicht aus dem Text ab.

Erlaubte Schweregrade:

```text
INFO
NOTICE
WARNING
ACTION_REQUIRED
ERROR
```

Erlaubte fachliche Typen und ihre Standardklassifizierung:

| Event-Typ | Standardklassifizierung |
|---|---|
| `BUY_CANDIDATE` | `ACTION_REQUIRED` |
| `PRICE_DROP` | `NOTICE` |
| `PRICE_INCREASE` | `NOTICE` |
| `RULE_FAILED` | `WARNING` |
| `CASE_COMPLETED` | `INFO` |
| `CASE_CHANGED` | `INFO` |
| `BUDGET_EXCEEDED` | `WARNING` |
| `PRODUCT_UNAVAILABLE` | `WARNING` |
| `PRODUCT_AVAILABLE` | `INFO` |
| `PRODUCT_AVAILABLE_AGAIN` | `INFO` |
| `REQUIREMENT_UNKNOWN` | `NOTICE` |
| `OFFER_CHANGED` | `NOTICE` |
| `PRICE_TARGET_REACHED` | `ACTION_REQUIRED` |
| `SOURCE_FAILED` | `ERROR` |

Unbekannte Event-Typen oder Schweregrade sind ungültig. Die Klassifizierung wird beim Erzeugen validiert und zusammen mit dem Event gespeichert.

## Fachliche Abgrenzungen

- Ein Produkt ist nicht gleich ein Angebot: ein Produkt kann mehrere Händlerangebote haben.
- Ein Angebot ist nicht gleich eine Preisbeobachtung: ein Angebot besitzt eine zeitliche Historie von Beobachtungen.
- Ein Procurement Case ist nicht gleich ein Produkt: ein Case beschreibt einen Bedarf und kann mehrere Kandidaten enthalten.
- Eine Kaufentscheidung ist nicht gleich eine automatische Bestellung: jede Entscheidung bleibt menschlich freigegeben; Bestellung ist außerhalb dieses Meilensteins.
- Ein Asset-Handover ist nicht gleich vollständiges Asset Management: die Übergabe bildet nur die Integrationsgrenze für ein späteres Modul.

## Zuständigkeiten

## WO-0019 Live-Angebotsdaten

Live-Angebote speichern neben Preis und Verfügbarkeit die ursprüngliche Lieferangabe, frühestes und spätestes normalisiertes Lieferdatum, Lieferkonfidenz, Fristberechtigung, Fulfillment-Typ, Abholort und Quellen-URL. Diese Felder werden sowohl am aktuellen Angebot als auch an der unveränderlichen `PriceObservation` gespeichert. Unbekannte Versandkosten oder Lieferangaben bleiben unbekannt und werden nicht optimistisch ergänzt.

Die Lieferbewertung unterscheidet `true`, `false` und `unknown`. Eine Abholung kann nach dem Versandstichtag fristgerecht bleiben, wenn lokale Verfügbarkeit und Standort dokumentiert sind. `BUY_CANDIDATE` entsteht nur bei erfüllten Pflichtanforderungen, verfügbarer fristgerechter Beschaffung und zulässigem Gesamtpreis; die endgültige Kaufentscheidung bleibt beim Project Owner.

Der Case Loader verantwortet versionierte fachliche Ausgangsdaten. Der Collector erfasst Quelldaten und der Normalizer überführt sie in das kanonische Modell. Nach erfolgreicher Validierung veranlasst der Procurement Service die Speicherung der Beobachtungen über den Repository Layer. Der Rule Evaluator verantwortet Bewertungen, der Event Generator deren Ableitung und Klassifizierung. Der Project Owner verantwortet Kaufentscheidungen.
## Product Evidence

Technische Modelldaten werden in einem versionierten lokalen Produktkatalog
geführt und beim Speichern einer Live-Beobachtung als Evidenz-Snapshot
übernommen. Modellnummer und Region-Variante bilden eine strikte Identität;
`unknown` bleibt unbekannt und wird nicht als positive Eigenschaft bewertet.
