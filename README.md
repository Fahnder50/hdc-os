---
document: README.md
version: 1.4.4-baseline
status: Accepted
owner: Project Owner
reviewed_by: Lead Architect
last_review: "2026-08-03"
release_reference: knowledge-v1.4.4
last_updated: "2026-08-03"
classification: Public
---

# HDC-OS

HDC-OS ist eine vollständig lokal betreibbare, KI-gestützte Operations-Plattform
für den sicheren, nachvollziehbaren und nachhaltigen Betrieb eines Home
Datacenters. Das Projekt beginnt bewusst klein und verbindet Architektur,
Procurement, physische Assets, Wissen und später Automation sowie Monitoring in
einem kontrollierten Lebenszyklus.

## Aktueller Stand

| Feld | Stand |
|---|---|
| Aktuelles Release | `knowledge-v1.4.4` |
| Sprint | Sprint 4 – First Deployment |
| Projektphase | Horizon 1 – Initial Build |
| Status | Foundation und Operations-Grundlage abgeschlossen; physischer Aufbau begonnen |
| Aktueller Fokus | Router-USV-Acceptance und Vorbereitung der ersten Netzwerkinbetriebnahme |
| Nächstes Zwischenziel | Ein Laptop erreicht per LAN oder WLAN hinter OPNsense sicher das Internet |
| Langfristige Vision | Vollständig lokales Home Datacenter mit KI-gestütztem Infrastrukturbetrieb |

## Projektfortschritt

Die Balken zeigen abgeschlossene Grundlagen beziehungsweise real umgesetzte
Deployment-Schritte, keine Marketingbewertung.

```text
Vision                 ████████████░░░░░░░░░░░░
Foundation             ████████████████████████
Procurement Foundation ████████████████████████
Operations Foundation  ████████████████████████
Physical Deployment    ██░░░░░░░░░░░░░░░░░░░░░░
Automation             ░░░░░░░░░░░░░░░░░░░░░░░░
```

„Procurement Foundation“ bedeutet, dass Entscheidungsmodell, Watch, Historie
und Übergabeprozess existieren – nicht, dass alle Hardware gekauft wurde.

## Was bereits existiert

- verbindliches Network Design v0.1,
- lokaler Procurement Watch mit fünf Cases und historienfähiger Runtime,
- generischer Infrastructure Core,
- generischer Asset Lifecycle und zentrale Asset Registry,
- abgeschlossener Procurement-to-Operations-Übergang für PC-0001,
- physisch vorhandene Eaton 3S850D Router-USV als `UPS-RTR-01` in `ACCEPTANCE`.

Noch nicht beschafft oder produktiv aufgebaut sind Rack, OPNsense-Firewall,
Managed Switch, Rack-USV und Access Point. `UPS-RTR-01` wird erst nach
dokumentierter Acceptance nach `PRODUCTION` überführt.

## Einstieg und Dokumenthierarchie

1. [Project Status](Project-Status.md) – schneller, operativer Gesamtüberblick.
2. [Project](Project.md) – Ziele, Reifegrad, Arbeitsweise und Meilensteine.
3. [Network Design v0.1](20-Operations/Network-Design-v0.1.md) – verbindliche Infrastrukturarchitektur.
4. [Procurement](30-Procurement/Procurement.md) – Cases, Empfehlungen und Watch-Status.
5. [Operations](20-Operations/Infrastructure.md) – physischer Zustand, Asset Lifecycle und Acceptance.
6. [Engineering](10-Engineering/DEVELOPMENT.md) – Entwicklungs- und Reviewprozess.
7. [Roadmap](40-Backlog/Roadmap.md) – abgeschlossene Bereiche und nächste Ziele.

Ergänzend:

- [Constitution](00-Foundation/Constitution.md)
- [Systemmodell](00-Foundation/Systemmodell.md)
- [Procurement Runtime](30-Procurement/README.md)
- [Asset Lifecycle & Registry](20-Operations/Asset-Lifecycle-and-Registry.md)
- [WO-0036 Handover](20-Operations/WO-0036-Procurement-to-Asset-Handover.md)
- [Dokumentations-Konsistenzbericht](Documentation-Consistency-Report.md)

## Repositorystruktur

```text
00-Foundation/    Visionstragende Prinzipien und Systemmodell
10-Engineering/   Governance, Entwicklung, ADRs und historische Sprintabschlüsse
20-Operations/    Netzwerkdesign, Infrastrukturzustand, Assets und Acceptance
30-Procurement/   Cases, Entscheidungen, Watch-Runtime und historische Daten
40-Backlog/       Roadmap, Vision, Ideen und Archiv
shared/           neutraler Infrastructure Core
```

## Verbindlicher Workflow

```text
Work Order → Umsetzung als Draft → Review → Accepted → Commit → Knowledge Release
Procurement PURCHASED → Asset ACCEPTANCE → bestandene Prüfung → PRODUCTION
```

Kritische Änderungen und Käufe bleiben unter menschlicher Kontrolle. Weder der
Procurement Watch noch der Asset Lifecycle bestellen oder aktivieren Hardware
automatisch.

## Historischer Hinweis

Frühere Einstiegsstände beschrieben Sprint 1/2, M2.1/M2.2 und SG2218 als
vorgesehenen Horizon-1-Switch. Diese Aussagen sind seit `knowledge-v1.4.4`
superseded. Die historischen Abschlüsse bleiben unter
[`10-Engineering/Sprints`](10-Engineering/Sprints/) und im Git-Verlauf erhalten.
