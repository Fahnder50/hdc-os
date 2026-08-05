---
document: Project.md
version: 1.5.7-baseline
status: Accepted
owner: Project Owner
reviewed_by: Lead Architect
last_review: "2026-08-03"
release_reference: knowledge-v1.5.7
last_updated: "2026-08-05"
classification: Living
---

# HDC-OS Project

## Auftrag und Vision

HDC-OS entwickelt ein vollständig lokales Home Datacenter mit KI-gestütztem,
sicherem und nachvollziehbarem Infrastrukturbetrieb. Die KI bereitet Wissen,
Analysen und Empfehlungen auf; Freigaben für kritische Änderungen bleiben beim
Menschen. Das System wächst über mehrere Jahre in kleinen, austauschbaren
Horizon-Schritten.

## Projektstatus

| Feld | Stand |
|---|---|
| Release | `knowledge-v1.5.7` |
| Sprint | Sprint 4 – First Deployment |
| Horizon | Horizon 1 – Initial Build |
| Reifegrad | Architektur-, Procurement- und Operations-Foundation abgeschlossen |
| Physischer Stand | Router-USV akzeptiert und als erstes Infrastruktur-Asset in `PRODUCTION` |
| Deploymentfokus | Firewall und Managed Switch beschaffen; WO-0041-Gates für den LAN-Erstaufbau schließen |
| Zwischenziel | Laptop hinter OPNsense per LAN oder WLAN sicher im Internet |

## Abgeschlossene Foundation

- Foundation, Constitution und Systemmodell,
- Repository-gestützter Work-Order-, Review-, Commit- und Releaseprozess,
- konsolidierte Knowledge Base und nachvollziehbare Knowledge Releases,
- Procurement Domain, Runtime, Watch, Evidenz- und Entscheidungsmodell,
- Network Design v0.1 als Architekturreferenz,
- Horizon-basierte Firewall- und Switchentscheidungen,
- generischer Infrastructure Core,
- generischer Asset Lifecycle, Registry, Relationships und Graphen,
- generische Agent Runtime und Procurement Agent v1 mit lokaler KI-Analyse,
- zentrales Operations Cockpit und Daily Briefing als menschenorientierte Gesamtsicht,
- erster Procurement-to-Operations-Handover für PC-0001.

Relevante aktuelle Work Orders:

| Work Order | Ergebnis |
|---|---|
| WO-0026 | Shared Infrastructure Core |
| WO-0032 | Network Design v0.1 Accepted |
| WO-0033 / R1 / R2 | Firewallentscheidung auf Horizon 1 ausgerichtet |
| WO-0034 / R1 | Managed-Switch-Entscheidung und Cross-Case-Gate |
| WO-0035 | Asset Lifecycle & Registry |
| WO-0036 | PC-0001 geschlossen und an Asset Lifecycle übergeben |
| WO-0038 | UPS-RTR-01-Acceptance abgeschlossen; Status `PRODUCTION` |
| WO-0041 | First Deployment Readiness definiert; operativer Status `NOT_READY` |
| WO-0043 / R1 | Generische Agent Runtime, Procurement Agent v1 und realer Scheduled-Betrieb |
| WO-0044 | Contract-basiertes Operations Cockpit und Daily Briefing |

## Verbindlicher Governance-Snapshot

| Dimension | Aktueller Stand |
|---|---|
| Release / Sprint | `knowledge-v1.5.7` / Sprint 4 – First Deployment |
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

## Existierende Systeme

| System | Status |
|---|---|
| Knowledge Repository | produktive Source of Truth |
| Procurement Watch | lokal betreibbar; PC-0002 bis PC-0005 aktiv |
| Infrastructure Core | generisch implementiert |
| Asset Registry | implementiert; `UPS-RTR-01` registriert |
| Agent Runtime | generisch implementiert; Procurement Agent v1 lokal und geplant betreibbar |
| Operations Cockpit | implementiert; fester Einstieg über `Dashboard/Latest.md` und `Latest.html` |
| Network Design | Accepted, noch nicht physisch umgesetzt |
| Monitoring/Automation | noch nicht implementiert |

## Physische Infrastruktur

Bereits vorhanden sind der Telekom-Anschluss, Speedport Smart 4, Telefonie,
vorhandenes Kabel ins Arbeitszimmer, unmanaged Netgear Switch, PS5, Sky Box und
der Laptop. Neu beschafft wurde die Eaton 3S850D Router-USV. Sie versorgt real
Speedport, Telefon und Elspet Automatic Litter Box; diese Verbraucher sind
externe Lasten, keine neuen HDC-OS-Assets.

`UPS-RTR-01` ist seit dem 04.08.2026 in `PRODUCTION`. Seriennummer, Kaufdaten,
Sichtprüfung, automatischer Batteriebetrieb und Netzrückkehr sind dokumentiert.
Nur das Garantieende bleibt bis zum belastbaren Nachweis `PENDING_CONFIRMATION`.

## Aktueller Sprint: First Deployment

Sprint 4 überführt die abgeschlossenen Grundlagen in einen ersten realen,
prüfbaren Infrastrukturpfad. Definition des Zwischenziels:

> Ein Laptop erhält hinter OPNsense per LAN oder WLAN eine gültige lokale
> Netzkonfiguration und erreicht über Managed Switch, Firewall, Speedport und
> Telekom DSL sicher das Internet; Telefonie bleibt funktionsfähig.

Für das LAN-First-Deployment fehlen mindestens ein qualifiziertes
Firewall-Angebot, der Managed Switch, die offenen WO-0041-Gate-Nachweise,
physischer Aufbau, Basiskonfiguration und Migrationstest. Rack, Rack-USV und
Access Point sind spätere Integrationsschritte und blockieren diesen Erstaufbau
nicht.

## Arbeits- und Governance-Modell

- Repository und Accepted-Dokumente sind Source of Truth.
- Architekturänderungen erfolgen über Work Orders oder ADRs.
- Procurement bewertet gegen Architektur und aktuelle Projektphase.
- Kein automatischer Kauf; Freigabe durch den Project Owner.
- `PURCHASED` beendet Procurement; Operations beginnt mit `ACCEPTANCE`.
- Assets werden erst nach vollständiger Acceptance `PRODUCTION`.
- Änderungen werden getestet, reviewed, committed und als Knowledge Release
  veröffentlicht.

## Nächste Schritte

1. PC-0002 Rack zur Kaufreife und Entscheidung führen.
2. Qualifiziertes Horizon-1-Angebot für PC-0003 bewerten.
3. PC-0004 Switch-Angebot inklusive Rackablage und AP-Cross-Case-Gate bewerten.
4. PC-0005 Rack-USV vervollständigen.
5. Access-Point-Case und Deployment Work Orders erstellen.
6. Netzwerkpfad schrittweise mit dokumentiertem Rollback aufbauen und validieren.

## Historische Baseline

Sprint 1, M2.1 Knowledge Consolidation und Sprint 2/M2.2 Procurement Foundation
sind abgeschlossen und nicht mehr der aktuelle Projektstatus. Die damaligen
Details bleiben in den Sprint-Closure-, Knowledge-Recovery- und Git-Historien
archiviert; frühere Hardwarefavoriten sind keine heutigen Kaufentscheidungen.
