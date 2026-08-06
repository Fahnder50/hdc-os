---
document: Project-Status.md
version: 1.0
status: Accepted
owner: Project Owner
reviewed_by: Lead Architect
last_review: "2026-08-06"
release_reference: knowledge-v1.5.8
last_updated: "2026-08-06"
classification: Living
---

# Project Status – knowledge-v1.5.8

## Zehn-Minuten-Überblick

HDC-OS ist eine lokale, KI-gestützte Operations-Plattform für ein schrittweise
aufgebautes Home Datacenter. Foundation, Knowledge, Procurement-System,
Netzwerkarchitektur, Infrastructure Core, Asset Lifecycle, Agent Runtime,
Scheduler Lifecycle und automatischer Cockpit-Refresh sind abgeschlossen.
Das Projekt befindet sich in Sprint 4 – First Deployment.

| Frage | Antwort |
|---|---|
| Was ist das Ziel? | Sicherer, lokaler und nachvollziehbarer Betrieb physischer und später virtueller Infrastruktur mit KI-Unterstützung. |
| Was existiert technisch? | Repository, Procurement Watch, Network Design, Infrastructure Core, Asset Registry, Acceptance Workflow, Agent Runtime, Scheduler Lifecycle und automatischer Cockpit-Refresh. |
| Was existiert physisch neu? | Eaton 3S850D Router-USV, Asset `UPS-RTR-01`, Status `PRODUCTION`. |
| Was wurde gekauft? | PC-0001 Router-USV; Procurement ist abgeschlossen. |
| Was fehlt? | Rack, Firewall, Managed Switch, Rack-USV, Access Point und deren Deployment. |
| Aktueller Sprint? | Sprint 4 – First Deployment. |
| Nächstes Zwischenziel? | Laptop hinter OPNsense per LAN oder WLAN sicher im Internet. |
| Große Vision? | Vollständig lokales Home Datacenter mit KI-gestütztem Infrastrukturbetrieb. |

## Procurement- und Assetstatus

| Case/Asset | Status | Aktueller Stand |
|---|---|---|
| PC-0001 Router-USV | **PROCUREMENT COMPLETED / PURCHASED** | an Operations übergeben |
| UPS-RTR-01 | **PRODUCTION** | Acceptance am 04.08.2026 erfolgreich abgeschlossen |
| PC-0002 Rack | WATCHING | drei Digitus-Kandidaten; Entscheidung offen |
| PC-0003 Firewall | WATCHING | Horizon-1-Standard: qualifizierte HUNSN RJ42 N100 bis 300 EUR; sonst WAIT |
| PC-0004 Switch | WATCHING | TL-SG2008P V3; Ziel 100 EUR, harte Gesamtgrenze 130 EUR |
| PC-0005 Rack-USV | WATCHING | OR1000ERM1U beobachtet; Requirements noch offen |
| Access Point | kein Case | vor Beschaffung anzulegen; muss PC-0004-PoE-Gate erfüllen |

## Verbindlicher Governance-Snapshot

| Dimension | Aktueller Stand |
|---|---|
| Release / Sprint | `knowledge-v1.5.8` / Sprint 4 – First Deployment |
| Projektstatus | Foundations abgeschlossen; First Deployment vorbereitet, noch nicht startbereit |
| Current Bottleneck | Firewall und Managed Switch fehlen; weitere WO-0041-Nachweise sind offen |
| Current Physical State | Speedport, Telefon, Netgear Switch, PS5 und Sky Box in Production/Legacy-Betrieb; Router-USV in `PRODUCTION` |
| Deployment-Status | `NOT_READY` gemäß WO-0041 |
| PC-0001 | `PURCHASED` / Completed Procurement |
| PC-0002 | `WATCHING` |
| PC-0003 | `WATCHING` |
| PC-0004 | `WATCHING` |
| PC-0005 | `WATCHING` |
| Produktive Assets | `UPS-RTR-01` – `PRODUCTION` |

## Current Bottleneck

Der aktuelle Engpass ist der noch fehlende physische Horizon-1-Netzwerkpfad,
nicht fehlende Architektur- oder Prozessinformation.

**Hardware currently missing**

- [ ] Rack
- [ ] Firewall
- [ ] Managed Switch
- [ ] Rack-USV
- [ ] Access Point

## Current Physical State

Diese Tabelle ist eine operative Momentaufnahme und ausdrücklich keine Asset
Registry. Der Status beschreibt die reale Nutzung, nicht die formale Aufnahme
jedes Geräts als HDC-OS-Asset.

| Physisch vorhanden | Status |
|---|---|
| Speedport Smart 4 | Production |
| Router-USV | Production |
| Telefon | Production |
| Netgear Switch | Production (Legacy) |
| PS5 | Production |
| Sky Box | Production |

## Entfernung zum Zwischenziel

Architektur und Beschaffungsregeln stehen. Der reale Zielpfad ist noch nicht
aufgebaut. Für das in WO-0041 definierte LAN-First-Deployment sind insbesondere
Firewall, Managed Switch, geschlossene Readiness-Gates, physische Installation,
OPNsense-Basiskonfiguration und Validierung erforderlich. Rack, Rack-USV und
Access Point bleiben spätere Integrationsziele und blockieren diesen Erstaufbau
nicht.

## Verbindliche nächste Leserouten

- Architektur: [Network Design v0.1](20-Operations/Network-Design-v0.1.md)
- Procurement: [Procurement](30-Procurement/Procurement.md)
- Operations: [Infrastructure](20-Operations/Infrastructure.md)
- Roadmap: [Roadmap](40-Backlog/Roadmap.md)
- Cockpit: [Operations Cockpit](Dashboard/Latest.md)
