---
document: Procurement.md
version: 1.0
status: Accepted
owner: Project Owner
reviewed_by: Lead Architect
last_review: "2026-07-10"
classification: Workspace
---

# Procurement

## Zweck

Dieses Dokument sammelt die in Sprint 1 bekannten Procurement-Erkenntnisse für HDC-OS.

Es dokumentiert festgelegte Entscheidungen, provisorische Arbeitswerte, diskutierte Inhalte und offene Punkte getrennt voneinander. Es trifft keine neuen Beschaffungsentscheidungen.

---

## Überwachte Produktgruppen

| Produktgruppe | Status | Favorit oder bekannter Stand | Offene Modellwahl |
|---------------|--------|------------------------------|-------------------|
| Rack | Festgelegte Produktgruppe | Extralink 12U Rack als Favorit | konkretes Angebot bleibt zu prüfen |
| Firewall-Appliance | Festgelegte Produktgruppe | Intel-N100-Appliance mit vier Intel-i226-Ports | konkretes Fabrikat offen |
| Switch | Festgelegte Produktgruppe | TP-Link Omada SG2218 | für Horizon 1 als ausreichend bewertet |
| Rack-USV | Festgelegte Produktgruppe | Versorgung der Kernkomponenten im Rack | konkretes Modell offen |
| Router-USV | Festgelegte Produktgruppe | separate USV für Speedport Smart 4 | konkretes Modell offen |

Diese Produktgruppen bilden die bekannte Hardware-Vorauswahl aus Sprint 1.

---

## Provisorische Preisgrenzen

Die folgenden Werte sind provisorische, noch nicht formal freigegebene Watch-Arbeitswerte.

Sie sind keine verbindlichen Kaufpreise und keine automatische Kaufentscheidung.

| Komponente | Zielpreis | Maximalpreis |
|------------|----------:|-------------:|
| Extralink Rack | 120 € | 150 € |
| N100-Firewall | 220 € | 260 € |
| TP-Link Omada SG2218 | 150 € | 180 € |
| Rack-USV | 170 € | 220 € |
| Router-USV | noch nicht festgelegt | noch nicht festgelegt |

Zielpreis bedeutet: Kauf prüfen.

---

## Gesamtbudget

Das bekannte Horizon-1-Gesamtbudget beträgt maximal 2.000 €.

Dieses Gesamtbudget wurde in Sprint 1 festgelegt.

Teilbudgets sind nicht abschließend freigegeben.

Die Firewall befindet sich voraussichtlich am oberen Rand ihres vorgesehenen Teilbudgets.

---

## Technische Mindestanforderungen

### Rack

Status: festgelegte Mindestanforderungen aus Sprint 1.

- ungefähr 12 HE
- kompakt und wohnraumtauglich
- keine zwingende Wandmontage
- transportabel, idealerweise rollbar
- Platz für Firewall, Switch, Kabelmanagement, USV und spätere Kernkomponenten
- leise beziehungsweise ohne störende aktive Komponenten

### Firewall

Status: festgelegte Mindestanforderungen aus Sprint 1.

- dedizierte Appliance
- Intel N100 als Zielplattform
- vier Intel-i226-Ethernetports
- OPNsense-kompatibel
- energieeffizient und leise
- ausreichend für 200-Mbit/s-DSL einschließlich Sicherheitsdiensten und Reserven
- VLAN- und VPN-fähig
- NordVPN optional als VPN-Gateway nutzbar
- kein dauerhaftes Firewall-Hosting auf einem täglich genutzten Laptop

### Switch

Status: festgelegte Mindestanforderungen aus Sprint 1.

- managed
- VLAN-fähig
- Omada-Integration
- ausreichende Portzahl für Firewall, PS5, Arbeitsgeräte, Access Points und Wachstum
- SG2218 wurde für Horizon 1 als ausreichend bewertet

### Rack-USV

Status: festgelegte Mindestanforderungen aus Sprint 1.

- Versorgung der Kernkomponenten im Rack
- Überbrückung kurzer Stromausfälle
- Unterstützung eines kontrollierten Herunterfahrens
- wohnraumgeeignet
- Monitoring beziehungsweise automatisierte Shutdown-Unterstützung erwünscht

### Router-USV

Status: festgelegte Mindestanforderungen aus Sprint 1.

- separate kompakte USV am Routerstandort
- möglichst unauffällige Installation
- kompatibel mit Speedport Smart 4
- Erhalt des Router- und Internetbetriebs bei kurzen Stromausfällen

---

## Händlerregeln

Status: in Sprint 1 verwendet, aber noch nicht als formale Procurement Policy freigegeben.

Festgehalten:

- Es gibt keine namentlich bevorzugten Händler.
- Es gibt keine namentlich ausgeschlossenen Händler.
- Seriöse Händler sind zu bevorzugen.
- Gesamtangebote, Mengenrabatte, Gutscheine, Cashback und Versandkosten sind einzubeziehen.
- Der niedrigste Einzelpreis ist nicht allein entscheidend.

Ausschlusskriterien:

- zweifelhafte Marktplatzanbieter
- unklare Gewährleistung
- nicht nachvollziehbare Importware
- schlechte Rückgabe- oder Supportbedingungen
- unklare Netzwerkkartenbestückung
- unkalkulierbare Zoll- oder Versandkosten

---

## Verworfene oder zurückgestellte Alternativen

### Verworfen beziehungsweise nicht weiterverfolgt

- wandmontiertes Rack
- großes Rack als Horizon-1-Standard
- Austausch des Speedport Smart 4
- Solar beziehungsweise Balkonkraftwerk als früher Bestandteil
- sofortiger Server- oder NAS-Kauf
- Laptop als dauerhafte produktive Firewall

### Noch offen

- konkretes Fabrikat der N100-Firewall
- konkretes Rack-USV-Modell
- konkretes Router-USV-Modell
- Omada-Access-Point und Anzahl der Access Points
- Compute- und NAS-Hardware

---

## Prüfintervall und Watch-Status

Status: in Sprint 1 eingerichtet und verwendet.

- Prüfung einmal täglich
- bisheriger Lauf ungefähr 09:00 Uhr Europe/Berlin
- Watch aktiviert
- Benachrichtigungen und E-Mail-Ausgabe derzeit deaktiviert
- letzter bekannter protokollierter Lauf: 9. Juli 2026

Der Watch soll beobachten:

- Preisrückgänge
- Gutscheine
- Cashback
- Lieferbarkeit
- seriöse Alternativangebote
- gute Kaufzeitpunkte

---

## Kaufregeln

Die Drei-Ampel-Regel aus Sprint 1 lautet:

1. Architektur passt.
2. Technik erfüllt die Anforderungen.
3. Wirtschaftlichkeit und Zeitpunkt sind sinnvoll.

Zusätzlich gilt:

- kein Impulskauf
- kurzfristiger Bedarf muss bestehen
- 2.000-€-Gesamtbudget muss eingehalten werden
- niedriger Preis allein reicht nicht
- Zielpreis bedeutet „Kauf prüfen“, nicht automatischer Kauf
- finale Freigabe erfolgt durch den Project Owner
- Gesamtbetriebskosten, Garantie, Händlerqualität und Zukunftsfähigkeit zählen mit
- keine Beschaffung, die wichtigere Komponenten finanziell gefährdet

---

## Reaktion auf Preisänderungen

### Kleine Preisänderung

Kleine Preisänderungen werden beobachtet und dokumentiert.

Sie lösen keine Kaufempfehlung aus.

### Deutliche Preissenkung

Deutliche Preissenkungen werden als relevanter Watch-Hinweis behandelt.

Sie können eine erneute Bewertung auslösen.

### Zielpreis erreicht oder unterschritten

Wenn ein Zielpreis erreicht oder unterschritten wird, darf ausschließlich der Status Buy Candidate beziehungsweise „Kauf prüfen“ vergeben werden.

Ein automatischer Kauf ist ausgeschlossen.

### Preisanstieg

Preisanstiege werden beobachtet.

Sie können die Bewertung des Kaufzeitpunkts verschlechtern.

### Gutschein oder Cashback

Gutscheine und Cashback werden in die Gesamtbewertung einbezogen.

Entscheidend ist der nachvollziehbare Gesamtpreis einschließlich Versand und Bedingungen.

---

## Fehlende Historie

Die Watch wurde eingerichtet und ausgeführt.

Mehrfach wurden keine außergewöhnlichen Preisbewegungen festgestellt.

Es existiert keine belastbare Preiszeitreihe.

Händlerpreise, Zeitstempel und historische Bestpreise wurden nicht strukturiert gespeichert.

Die bisherige Historie ist deshalb nicht rekonstruierbar.

### Zukünftige Mindestfelder einer Beobachtung

Status: erkannte Anforderung für eine nachfolgende Procurement-Watch-Work-Order, nicht implementierte Funktion.

- Datum
- Komponente
- genaues Produkt
- Händler
- Preis einschließlich Versand
- Gutschein oder Cashback
- Verfügbarkeit
- bisheriger Tiefstpreis
- Zielpreis
- Empfehlung
- Quelle
