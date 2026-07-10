---
document: Milestone-M2.1-Closure.md
version: 1.0
status: Accepted
owner: Project Owner
reviewed_by: Lead Architect
last_review: "2026-07-10"
classification: Internal
sprint: "Sprint 2"
milestone: "M2.1 – Knowledge Consolidation"
---

# Meilenstein M2.1 Abschluss

## Ziel des Meilensteins

Bevor die Infrastruktur geplant wird, werden die letzten Wissenslücken aus Sprint 1 geschlossen und der Workspace wieder als alleinige Source of Truth hergestellt.

---

## Ausgangslage

Sprint 1 war fachlich abgeschlossen.

Relevantes Wissen war teilweise nur im Chat vorhanden.

Besonders betroffen waren Procurement, Infrastruktur und ergänzende Governance-Regeln.

Der Procurement Watch war nicht vollständig aus dem Repository rekonstruierbar.

Die fehlende Preiszeitreihe konnte nicht nachträglich rekonstruiert werden.

---

## Durchgeführte Work Orders

### WO-0012 – Sprint 1 Knowledge Recovery & Repository Consolidation

Ziel war die Überführung dauerhaft relevanter Sprint-1-Erkenntnisse in den Workspace.

Die erste Umsetzung erhielt im Review den Status Changes Requested.

Die Korrektur erfolgte mit RWO-0006.

Der korrigierte Stand wurde Accepted.

### RWO-0006 – Korrektur der Knowledge Recovery aus WO-0012

Ziel war die sachlich korrekte Trennung von festgelegten Entscheidungen, provisorischen Arbeitswerten, diskutierten Inhalten, offenen Punkten und historischen Datenlücken.

Ergebnis ist die konsolidierte Dokumentation von Procurement-, Infrastruktur- und Governance-Wissen.

Reviewstatus: Accepted.

### WO-0013 – Abschluss und Zwischenrelease von Sprint-2-Meilenstein M2.1

Ziel ist der formale Abschluss von M2.1 und die Vorbereitung des Zwischenrelease.

Ergebnis ist dieses Closure-Dokument mit aktualisiertem Projektstatus und vorbereitetem Release.

Reviewstatus: In Review.

---

## Erstellte Dokumente

- `10-Engineering/Governance.md`
- `10-Engineering/Knowledge-Recovery-Sprint1.md`
- `20-Operations/Infrastructure.md`
- `30-Procurement/Procurement.md`
- `10-Engineering/Sprints/Milestone-M2.1-Closure.md`

---

## Aktualisierte Dokumente

- `README.md`
- `Project.md`

`README.md` wurde hinsichtlich Metadaten und bestehender Verweise geprüft.

`Project.md` wurde auf den aktuellen Stand von Sprint 2 und M2.1 gebracht.

---

## Erreichte Ergebnisse

- Procurement-Produktgruppen sind dokumentiert.
- Technische Mindestanforderungen sind dokumentiert.
- Provisorische Preiswerte sind von verbindlichen Entscheidungen getrennt.
- Das maximale Horizon-1-Gesamtbudget von 2.000 € ist dokumentiert.
- Händlerregeln und Ausschlusskriterien sind dokumentiert.
- Kaufregeln und Drei-Ampel-Logik sind dokumentiert.
- Watch-Intervall und letzter bekannter Watch-Status sind dokumentiert.
- Die fehlende historische Preiszeitreihe ist transparent als Datenlücke erfasst.
- Die Infrastruktur-Grundtopologie ist dokumentiert.
- OPNsense, Speedport Smart 4 und SG2218 sind korrekt eingeordnet.
- VLAN-, Firewall-, Backup- und Monitoring-Grundsätze sind dokumentiert.
- Festgelegte, provisorische, diskutierte und offene Inhalte werden klar unterschieden.
- Governance-Regeln für Scope, Review, Commit und Release sind dokumentiert.
- Der Workspace bildet die bekannten Sprint-1-Erkenntnisse wieder als Source of Truth ab.

---

## Bewusst offene Punkte

### Procurement

- konkretes Fabrikat der N100-Firewall
- konkretes Rack-USV-Modell
- konkretes Router-USV-Modell
- Omada-Access-Point und Anzahl
- Compute- und NAS-Hardware
- verbindliche Teilbudgets
- belastbare Preiszeitreihe

### Infrastruktur

- VLAN-IDs
- finale Zonennamen
- Gerätezuordnung
- Inter-VLAN-Regeln
- IP- und Subnetzkonzept
- DHCP- und DNS-Konzept
- konkrete Firewall-Regeln
- NordVPN-Routing
- IDS/IPS
- Notfallzugang
- Backupsoftware und Backupziele
- RPO und RTO
- Monitoring-Tooling und Alarmgrenzen

Diese Punkte sind keine verbliebenen Wissensverluste aus Sprint 1, sondern bewusst offene Entscheidungen für spätere Meilensteine.

---

## Historische Datenlücke

Es konnte keine belastbare Preiszeitreihe des bisherigen Procurement Watch rekonstruiert werden.

Frühere Händlerpreise, Zeitstempel und historische Tiefstpreise wurden nicht strukturiert gespeichert.

Diese Lücke bleibt dauerhaft nachvollziehbar dokumentiert.

Ab M2.2 muss der Procurement Watch eine strukturierte Historie erzeugen.

---

## Lessons Learned

- Chat ist kein dauerhafter Wissensspeicher.
- Relevantes Wissen muss zeitnah in den Workspace übernommen werden.
- Eine Sprint- oder Meilenstein-Closure benötigt eine Wissensvollständigkeitsprüfung.
- „Offen“ darf nicht mit „nicht im Repository dokumentiert“ verwechselt werden.
- Provisorische Arbeitswerte müssen erhalten und klar klassifiziert werden.
- Ein Review muss Inhalte gegen ihre Quellen prüfen, nicht nur Struktur und Format.
- Procurement benötigt eine eigenständige, repositorygestützte Struktur.
- Preisbeobachtungen benötigen eine persistente Historie.

---

## Abschlussbewertung

Meilenstein M2.1 – Knowledge Consolidation ist fachlich abgeschlossen.

Der Workspace bildet die bekannten dauerhaft relevanten Sprint-1-Erkenntnisse wieder als maßgebliche Source of Truth ab.

Die verbleibenden offenen Punkte sind dokumentierte Folgeentscheidungen und keine unkontrollierten Wissenslücken.

---

## Nächster Meilenstein

M2.2 – Procurement Foundation

Vorgesehenes Ziel:

Der Procurement Watch wird von einer chatabhängigen Übergangslösung in einen strukturierten, repositorygestützten und historienfähigen Prozess überführt.
