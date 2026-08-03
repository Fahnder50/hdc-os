---
document: Project.md
version: 1.4.4-baseline
status: Accepted
owner: Project Owner
reviewed_by: Lead Architect
last_review: "2026-08-03"
release_reference: knowledge-v1.4.4
last_updated: "2026-08-03"
classification: Workspace
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
| Release | `knowledge-v1.4.4` |
| Sprint | Sprint 4 – First Deployment |
| Horizon | Horizon 1 – Initial Build |
| Reifegrad | Architektur-, Procurement- und Operations-Foundation abgeschlossen |
| Physischer Stand | Router-USV geliefert und als Asset in `ACCEPTANCE` |
| Deploymentfokus | Acceptance abschließen; Rack-, Firewall-, Switch-, USV- und AP-Aufbau vorbereiten |
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

## Existierende Systeme

| System | Status |
|---|---|
| Knowledge Repository | produktive Source of Truth |
| Procurement Watch | lokal betreibbar; PC-0002 bis PC-0005 aktiv |
| Infrastructure Core | generisch implementiert |
| Asset Registry | implementiert; `UPS-RTR-01` registriert |
| Network Design | Accepted, noch nicht physisch umgesetzt |
| Monitoring/Automation | noch nicht implementiert |

## Physische Infrastruktur

Bereits vorhanden sind der Telekom-Anschluss, Speedport Smart 4, Telefonie,
vorhandenes Kabel ins Arbeitszimmer, unmanaged Netgear Switch, PS5, Sky Box und
der Laptop. Neu beschafft wurde die Eaton 3S850D Router-USV. Sie versorgt real
Speedport, Telefon und Elspet Automatic Litter Box; diese Verbraucher sind
externe Lasten, keine neuen HDC-OS-Assets.

`UPS-RTR-01` bleibt in `ACCEPTANCE`, bis Seriennummer, Kaufdatum, Garantie,
automatischer Batteriebetrieb, Netzrückkehr und Abschlussdokumentation bestätigt
sind.

## Aktueller Sprint: First Deployment

Sprint 4 überführt die abgeschlossenen Grundlagen in einen ersten realen,
prüfbaren Infrastrukturpfad. Definition des Zwischenziels:

> Ein Laptop erhält hinter OPNsense per LAN oder WLAN eine gültige lokale
> Netzkonfiguration und erreicht über Managed Switch, Firewall, Speedport und
> Telekom DSL sicher das Internet; Telefonie bleibt funktionsfähig.

Noch fehlen dafür mindestens Rackentscheidung, qualifiziertes Firewall-Angebot,
Managed Switch, Rack-USV, Access Point, physischer Aufbau, Basiskonfiguration und
Migrationstest.

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

1. Acceptance von `UPS-RTR-01` vollständig dokumentieren.
2. PC-0002 Rack zur Kaufreife und Entscheidung führen.
3. Qualifiziertes Horizon-1-Angebot für PC-0003 bewerten.
4. PC-0004 Switch-Angebot inklusive Rackablage und AP-Cross-Case-Gate bewerten.
5. PC-0005 Rack-USV vervollständigen.
6. Access-Point-Case und Deployment Work Orders erstellen.
7. Netzwerkpfad schrittweise mit dokumentiertem Rollback aufbauen und validieren.

## Historische Baseline

Sprint 1, M2.1 Knowledge Consolidation und Sprint 2/M2.2 Procurement Foundation
sind abgeschlossen und nicht mehr der aktuelle Projektstatus. Die damaligen
Details bleiben in den Sprint-Closure-, Knowledge-Recovery- und Git-Historien
archiviert; frühere Hardwarefavoriten sind keine heutigen Kaufentscheidungen.
