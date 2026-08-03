---
document: Roadmap.md
version: 1.0
status: Accepted
owner: Project Owner
reviewed_by: Lead Architect
last_review: "2026-08-03"
release_reference: knowledge-v1.4.4
last_updated: "2026-08-03"
classification: Workspace
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

## Aktuell: Sprint 4 – First Deployment

Ziel ist der erste vollständige reale Netzwerkpfad:

> Laptop → LAN oder WLAN → Managed Switch/AP → OPNsense → Speedport → Internet

Telefonie bleibt unverändert. VLANs werden vorbereitet, aber erst nach stabilem
Basisbetrieb aktiviert.

Aktuelle Arbeiten:

- Acceptance von `UPS-RTR-01` abschließen,
- PC-0002 bis PC-0005 in konkrete Kaufentscheidungen überführen,
- Access-Point-Anforderungen und Case festlegen,
- Deployment Work Orders für Rack, Firewall, Switch, USV und AP vorbereiten.

## Nächste Ziele

1. Seriennummer, Kaufdatum, Garantie und Funktionstest der Router-USV erfassen.
2. Rack beschaffen, registrieren und akzeptieren.
3. Horizon-1-Firewallangebot qualifizieren und freigeben.
4. TL-SG2008P-V3-Gesamtangebot inklusive Rackablage qualifizieren.
5. Rack-USV-Case vervollständigen und entscheiden.
6. IEEE-802.3af/at-kompatiblen Access Point auswählen.
7. Grundtopologie installieren und das Laptop-Zwischenziel validieren.

Automation, Monitoring, Storage, Compute, lokale KI und weitergehende
Segmentierung folgen erst nach dem stabilen First Deployment. Es gibt hierfür in
dieser Roadmap keine vorgezogene Fertigstellungsaussage.

## Historische Roadmapstände

Sprint 1, M2.1 und M2.2 sind abgeschlossen. Ihre Detailpläne bleiben in
[`10-Engineering/Sprints`](../10-Engineering/Sprints/) und Git erhalten; sie
sind keine aktuelle Roadmap.
