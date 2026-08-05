---
document: Roadmap.md
version: 1.0
status: Accepted
owner: Project Owner
reviewed_by: Lead Architect
last_review: "2026-08-03"
release_reference: knowledge-v1.5.5
last_updated: "2026-08-05"
classification: Living
---

# HDC-OS Roadmap

## Abgeschlossen

### Foundation und Knowledge

- Constitution, Bausteine und Systemmodell,
- Repository als Source of Truth,
- Work-Order-, Review-, Commit- und Knowledge-Release-Prozess,
- Knowledge Consolidation und Recovery.

### Procurement Foundation

- lokale historienfähige Procurement Runtime,
- Architecture Gates und objektive Entscheidungsmodelle,
- Horizon-basierte Wirtschaftlichkeitsstrategie,
- PC-0001 bis PC-0005 als strukturierte Cases,
- PC-0001 abgeschlossen und an Operations übergeben.

### Operations Foundation

- Network Design v0.1,
- generischer Infrastructure Core,
- generischer Asset Lifecycle und Registry,
- Acceptance Workflow, Relationships, Dependency und Power Graph,
- erstes Asset `UPS-RTR-01` registriert.
- Acceptance von `UPS-RTR-01` abgeschlossen; Asset in `PRODUCTION`.
- First Deployment Readiness mit WO-0041 verbindlich definiert.

## Verbindlicher Governance-Snapshot

| Dimension | Aktueller Stand |
|---|---|
| Release / Sprint | `knowledge-v1.5.5` / Sprint 4 – First Deployment |
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

## Aktuell: Sprint 4 – First Deployment

Ziel ist der erste vollständige reale Netzwerkpfad:

> Laptop → Managed Switch → OPNsense → Speedport → Internet

Telefonie bleibt unverändert. VLANs werden vorbereitet, aber erst nach stabilem
Basisbetrieb aktiviert.

Aktuelle Arbeiten:

- Acceptance von `UPS-RTR-01` abgeschlossen; erstes Asset in `PRODUCTION`,
- PC-0002 bis PC-0005 in konkrete Kaufentscheidungen überführen,
- Access-Point-Anforderungen und Case festlegen,
- Deployment Work Orders für Rack, Firewall, Switch, USV und AP vorbereiten.

## Nächste Ziele

1. Horizon-1-Firewallangebot qualifizieren und freigeben.
2. TL-SG2008P-V3-Gesamtangebot inklusive Rackablage qualifizieren.
3. Offene Hardware-, Konfigurations-, Test- und Rollback-Gates aus WO-0041 schließen.
4. LAN-Grundtopologie installieren und das Laptop-Zwischenziel validieren.
5. Rack beschaffen, registrieren und akzeptieren.
6. Rack-USV-Case vervollständigen und entscheiden.
7. IEEE-802.3af/at-kompatiblen Access Point auswählen und WLAN später integrieren.

Automation, Monitoring, Storage, Compute, lokale KI und weitergehende
Segmentierung folgen erst nach dem stabilen First Deployment. Es gibt hierfür in
dieser Roadmap keine vorgezogene Fertigstellungsaussage.

## Historische Roadmapstände

Sprint 1, M2.1 und M2.2 sind abgeschlossen. Ihre Detailpläne bleiben in
[`10-Engineering/Sprints`](../10-Engineering/Sprints/) und Git erhalten; sie
sind keine aktuelle Roadmap.
