---
document: Generic-Procurement-Lifecycle.md
version: 1.0
status: Accepted
owner: Project Owner
reviewed_by: Lead Architect
last_review: "2026-08-04"
last_updated: "2026-08-04"
work_order: WO-0039
classification: Workspace
---

# Generic Procurement Lifecycle

## Systemgrenze

Procurement beantwortet ausschließlich, ob ein beobachtetes Objekt heute
gekauft werden soll. Der Core bewertet Markt, Preis, Lieferbarkeit, technische
Qualifikation und Kaufempfehlung. Er kennt keine spätere Verwendung und setzt
weder Asset-Erstellung noch Inventarisierung oder Operations-Handover voraus.

Ein Case kann Hardware, Möbel, Haushaltsgerät, Elektronik, Werkzeug,
Verbrauchsmaterial, Geschenk, Hobbyartikel oder eine reine Preisbeobachtung
betreffen. Diese Kategorien erfordern keine Architekturänderung.

## Statusmodell

```text
WATCHING → QUALIFYING → READY_FOR_REVIEW → BUY_CANDIDATE
                                             │
                                             └─ PURCHASED

WATCHING / QUALIFYING / READY_FOR_REVIEW / BUY_CANDIDATE → CANCELLED
```

Diese sechs Werte sind die vollständige und einzige Liste persistenter Status.
`CLOSED` gehört ausdrücklich nicht zu dieser Liste. Die Runtime erzeugt
`CLOSED` ausschließlich als nicht persistierte Archivansicht für `PURCHASED`
oder `CANCELLED`. YAML, Datenbank, Import, Migration und manuelle Statussetzung
dürfen `CLOSED` niemals akzeptieren.

| Status | Eindeutige Bedeutung |
|---|---|
| `WATCHING` | Marktbeobachtung aktiv; noch keine qualifizierte Entscheidungsbasis. |
| `QUALIFYING` | Angebote oder Nachweise werden fachlich qualifiziert. |
| `READY_FOR_REVIEW` | Entscheidungsbasis ist zur menschlichen Prüfung vorbereitet. |
| `BUY_CANDIDATE` | Die objektiven Kaufbedingungen sind erfüllt; keine automatische Bestellung. |
| `PURCHASED` | Der Case endete mit Kauf. Einziger positiver Abschlussstatus. |
| `CANCELLED` | Der Case endete ohne Kauf. Einziger negativer Abschlussstatus. |

## Transition Contract

Die einzige technische Prüffunktion für Statuswechsel ist
`transition_case_status`. Zulässig sind ausschließlich:

| Ausgang | Zulässiges Ziel |
|---|---|
| `WATCHING` | `QUALIFYING`, `CANCELLED` |
| `QUALIFYING` | `READY_FOR_REVIEW`, `CANCELLED` |
| `READY_FOR_REVIEW` | `BUY_CANDIDATE`, `CANCELLED` |
| `BUY_CANDIDATE` | `PURCHASED`, `CANCELLED` |
| `PURCHASED` | kein Ziel |
| `CANCELLED` | kein Ziel |

Identische Statuswerte sind idempotent. Jeder andere Wechsel wird abgelehnt.
Persistente Änderungen aus Import und Runtime müssen denselben zentralen
Transition Contract verwenden.

`REVIEW`, `UNKNOWN`, `FAIL`, `PASS` und `NOT_VERIFIED` bleiben ausschließlich
Ergebnisse einzelner technischer Regeln. `EVALUATING`, `WAIT`, `NO_CANDIDATE`
und `CONDITIONAL_BUY` sind keine Lifecycle- oder Empfehlungszustände mehr.

## Aktiver Runtime-Vertrag

Nur die vier aktiven Zustände dürfen Watch, Web Requests, Preisabfragen,
Händlerprüfung, technische Bewertung, Kaufempfehlung, operative Reports oder
neue Journal-Einträge auslösen. Portfolio Watch und Statusübersicht filtern
zentral über denselben Statuskatalog.

`PURCHASED` und `CANCELLED` werden vollständig übersprungen. Eine
direkte manuelle Abfrage bleibt möglich, liefert aber nur Abschlussstatus,
Abschlussdatum, historische Metadaten und eine optionale externe Übergabereferenz.
Sie startet keine neue Bewertung. Ein manueller historischer Report kennzeichnet
den Case durch die abgeleitete Ansicht `CLOSED` eindeutig als abgeschlossen.

## Nachgelagerte Verwendung

Nach `PURCHASED` wird außerhalb von Procurement genau eine fachliche Frage
beantwortet: Soll der Kauf ein Asset werden? Bei `NO` endet der Ablauf ohne
Operations-Komponenten. Nur bei `YES` kann ein externer Prozess Handover,
Acceptance und Production ausführen. Procurement erzeugt diese Objekte nicht.

Der Core akzeptiert ausschließlich das domänenneutrale optionale Feld
`external_reference`. Er interpretiert weder Typ noch Ziel dieser Referenz. Die
seit der initialen Foundation vorhandene Datenbanktabelle `asset_handovers` ist
Legacy-Schema, wird vom Procurement Core nicht gelesen oder beschrieben und
begründet keine Asset-Abhängigkeit. Ebenso wird das historische Case-Feld
`operations_handover` vom Core nicht gelesen oder importiert.

## KI-Agenten-Kompatibilität

Ein zukünftiger Agent kann einen normalen Case aus Produkt, Zeitraum, Budget,
Anforderungen und Quellen erzeugen, beispielsweise „Beobachte Produkt X für
zwei Wochen“. Der Case beginnt in `WATCHING` und durchläuft exakt denselben
Lifecycle wie jeder manuell erzeugte Case. Es existiert weder ein KI-Status noch
eine produkt- oder domänenspezifische Sonderlogik.

## Historie und Migration

Alle fünf bestehenden Cases sind mit `lifecycle_version: 2` gekennzeichnet.
PC-0001 bleibt `PURCHASED`; PC-0002 bis PC-0005 bleiben aktiv in `WATCHING`.
Beim erneuten Import eines abgeschlossenen Cases werden Anforderungen,
Bewertungen, Preisbeobachtungen, Händlerdaten, Reports und Journalhistorie nicht
gelöscht. Abschlussdatum und optionale externe Übergabereferenz werden als
Metadaten ergänzt.

## Reportkonsistenz

Aktive Reports verwenden für Top-Angebote, Preishistorie, Budget und Empfehlung
denselben Case- und Angebotszustand. Ein abgeschlossener Report enthält keine
aktive Kaufempfehlung. Historische Angebote und Preisverläufe dürfen weiterhin
sichtbar sein, werden aber ausdrücklich als Historie dargestellt.
