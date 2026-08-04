---
document: Infrastructure.md
version: 1.4.4-baseline
status: Accepted
owner: Project Owner
reviewed_by: Lead Architect
last_review: "2026-08-03"
release_reference: knowledge-v1.4.4
last_updated: "2026-08-03"
classification: Workspace
---

# Operations und Infrastruktur

## Repository Baseline

| Feld | Stand |
|---|---|
| Release | `knowledge-v1.4.4` |
| Sprint | Sprint 4 – First Deployment |
| Abgeschlossene Grundlage | Network Design, Infrastructure Core, Asset Lifecycle und erster Handover |
| Aktueller Fokus | Router-USV-Acceptance und Vorbereitung des ersten realen Netzwerkpfads |

## Betriebsziel

HDC-OS baut in Horizon 1 einen kleinen, vollständig lokalen und sicher
betreibbaren Infrastrukturpfad auf. Aktuelles Zwischenziel:

> Ein Laptop nutzt per LAN oder WLAN hinter der OPNsense-Firewall sicher das
> Internet; Speedport Smart 4 bleibt DSL-Gateway und Telefonie funktioniert
> unverändert.

Die verbindliche Architektur steht im
[Network Design v0.1](Network-Design-v0.1.md).

## Aktueller physischer Zustand

| Standort | Komponente | Status |
|---|---|---|
| Routerstandort außerhalb des Arbeitszimmers | Speedport Smart 4 und Telefonie | vorhanden und in Betrieb |
| Routerstandort | Eaton 3S850D / `UPS-RTR-01` | Acceptance abgeschlossen, `PRODUCTION` |
| Verbindung zum Arbeitszimmer | ein Ethernet-Kabel | vorhanden; später OPNsense-WAN-Uplink |
| Arbeitszimmer | unmanaged Netgear Switch | bestehender Ist-Zustand |
| Arbeitszimmer | PS5, Sky Box, Laptop | vorhandene Clients |
| Arbeitszimmer | Rack, OPNsense, Managed Switch, Rack-USV, AP | noch nicht beschafft beziehungsweise aufgebaut |

Die Router-USV versorgt Speedport, Telefon und Elspet Automatic Litter Box. Die
drei Verbraucher sind externe Lasten; nur die USV ist ein HDC-OS-Asset.

## Zielarchitektur

```text
Telekom DSL
  → Speedport Smart 4 (Telefonie bleibt hier)
  → OPNsense WAN
  → OPNsense LAN
  → Managed Switch
      → Laptop per LAN
      → Access Point → Laptop per WLAN
      → PS5 / Sky Box / HDC-OS Host
```

Router-USV und Rack-USV bleiben getrennte Stromdomänen. Die Router-USV ist
`infrastructure: gateway`, `mounted_in_rack: false`; Rackkomponenten werden
durch die spätere Rack-USV versorgt.

## Infrastructure Core

Der neutrale Shared Core modelliert Komponenten, Rollen, Capabilities,
Abhängigkeiten sowie den generischen Asset Lifecycle. Er besitzt keine
Procurement-, Hersteller- oder Geräteabhängigkeit. Neue Assetklassen werden über
Daten ergänzt, nicht über Core-Code.

## Asset Lifecycle und Registry

```text
PLANNED → ORDERED → DELIVERED → ACCEPTANCE → PRODUCTION
                                              ↓
                                         MAINTENANCE → RETIRED
```

Die zentrale Registry liegt unter [`assets/registry.yaml`](assets/registry.yaml).
Sie unterstützt Asset Lookup, Relationships, Dependency Graph und Power Graph.
Details: [Asset Lifecycle & Registry](Asset-Lifecycle-and-Registry.md).

## Acceptance

Jedes Asset durchläuft:

1. Sichtprüfung,
2. Prüfung des Lieferumfangs,
3. gerätespezifische Funktionsprüfung,
4. dokumentierte Asset Acceptance.

`PRODUCTION` ist erst nach vollständiger Acceptance zulässig. Für
`UPS-RTR-01` wurden Seriennummer, Kaufdaten, Sichtprüfung, automatischer
Batteriebetrieb, Netzrückkehr und Abschlussdokumentation am 04.08.2026
bestätigt. Das Garantieende bleibt bewusst `PENDING_CONFIRMATION`. Maßgeblich
ist die [Acceptance-Datei](assets/acceptance/UPS-RTR-01.yaml).

## Procurement-Übergang

PC-0001 ist `PURCHASED` und wird nicht mehr überwacht. Historische
Procurement-Daten bleiben erhalten; der Betriebszustand wird ausschließlich aus
der Asset Registry gelesen. Der vollständige Handover steht in
[WO-0036](WO-0036-Procurement-to-Asset-Handover.md).

## Aktueller Deploymentpfad

1. PC-0002 bis PC-0005 zur konkreten Kaufentscheidung führen.
2. Access Point gegen das IEEE-802.3af/at-Cross-Case-Gate auswählen.
3. Jedes neue Gerät registrieren und akzeptieren.
4. OPNsense, Switch und AP zunächst unsegmentiert aufbauen.
5. Laptop-LAN, Laptop-WLAN, Internet und Telefonie validieren.
6. VLANs erst nach stabilem Basisbetrieb aktivieren.

## Historischer Hinweis

Die frühere Sprint-1-Grundtopologie mit SG2218 als vorgesehenem Switch und
„technischem Detaildesign offen“ ist superseded. Heute gelten Network Design
v0.1 und die Accepted PC-0003-/PC-0004-Entscheidungen. Historische Anforderungen
bleiben in [Infrastructure Requirements](Infrastructure-Requirements.md), den
Sprintabschlüssen und Git erhalten.
