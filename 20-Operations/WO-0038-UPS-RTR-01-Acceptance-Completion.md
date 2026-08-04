---
document: WO-0038-UPS-RTR-01-Acceptance-Completion.md
version: 1.0
status: Accepted
owner: Project Owner
reviewed_by: Lead Architect
last_review: "2026-08-04"
last_updated: "2026-08-04"
work_order: WO-0038
classification: Workspace
---

# UPS-RTR-01 Acceptance Completion

## Scope und Ergebnis

WO-0038 schließt ausschließlich die Acceptance von `UPS-RTR-01` ab. Der
Infrastructure Core, Procurement und andere Assets bleiben unverändert. Alle
definierten Prüfungen wurden erfolgreich durchgeführt; das Asset wechselt am
2026-08-04 von `ACCEPTANCE` nach `PRODUCTION`.

## Verbindliche Assetdaten

| Feld | Wert |
|---|---|
| Asset-ID | `UPS-RTR-01` |
| Hersteller | Eaton |
| Produktserie | Eaton 3S |
| Modell / Catalog No. | 3S850D |
| MFG ID | 9400-A303 Rev. 00 |
| Seriennummer | GE67V13292 |
| Kaufdatum | 29.07.2026 |
| Kaufpreis | 127,12 EUR |
| Standort | Internet-Gateway / Speedport-Standort |
| Infrastruktur | `gateway` |
| mounted_in_rack | `false` |

## Garantie

| Feld | Wert |
|---|---|
| Status | Manufacturer Warranty |
| Umfang | Herstellergarantie |
| Enddatum | `PENDING_CONFIRMATION` |

Das Garantieende wird nicht geschätzt. Es wird erst nach einem belastbaren
Nachweis aus Rechnung oder Herstellerangabe ergänzt.

## Externe Verbraucher

Speedport Smart 4, Telefon und Elspet Automatic Litter Box bleiben als
`External Loads` dokumentiert. Sie sind keine HDC-OS-Assets.

## Acceptance-Protokoll

| Test | Durchführung und Ergebnis | Status |
|---|---|---|
| Netzbetrieb | USV arbeitet fehlerfrei im Normalbetrieb. | PASS |
| Netzausfall | Netzversorgung getrennt; Batteriebetrieb startete automatisch. Router und Internet blieben aktiv, LED blinkte und der akustische Alarm war aktiv. | PASS |
| Wiederkehr Netzspannung | Netzversorgung wiederhergestellt; automatische Rückkehr ohne Unterbrechung von Router oder Internet. Alarm endete und LED wechselte in Dauerbetrieb. | PASS |
| Sichtprüfung | Typenschild geprüft; Hersteller, Modell, Seriennummer und MFG ID bestätigt. | PASS |

## Lifecycle-Entscheidung

Alle definierten Acceptance-Kriterien sind erfüllt.

```yaml
status: PRODUCTION
acceptance:
  completed: true
acceptance_date: 2026-08-04
production_date: 2026-08-04
```

PC-0001 bleibt ohne Rückwirkung `PURCHASED` und `CLOSED`. Seine historischen
Daten und das deaktivierte Watch-Verhalten bleiben unverändert.
