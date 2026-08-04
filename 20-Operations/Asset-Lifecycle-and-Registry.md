---
document: Asset-Lifecycle-and-Registry.md
version: 1.0
status: Accepted
owner: Project Owner
reviewed_by: Lead Architect
last_review: "2026-08-03"
release_reference: knowledge-v1.4.4
last_updated: "2026-08-03"
work_order: WO-0035
classification: Workspace
---

# Infrastructure Asset Lifecycle & Registry

## Zweck und Systemgrenze

Die Asset Registry ist die verbindliche Operations-Schnittstelle für physische
Infrastruktur. Procurement endet mit `Purchased`; Operations beginnt mit
`Asset Acceptance`. Das Asset-Modell importiert keinen Procurement-Code und
kennt weder Preise noch Bestelllogik. `procurement_case` ist ausschließlich eine
optionale Herkunftsreferenz.

Die Implementierung liegt im neutralen Infrastructure Core unter
`shared/assets.py`. Registry-Daten liegen unter `20-Operations/assets/`. Es gibt
keine Datenbank und keine beim Betrieb erzeugten Runtime-Dateien.

## Generisches Asset-Modell

Jedes Asset besitzt:

- Identität: Asset-ID, Hersteller, Modell, Seriennummer, Kaufdatum, Garantieende,
- Ort: Standort, Raum, Infrastrukturbereich, Rack-Zuordnung,
- Lifecycle: Status sowie Acceptance-, Produktions- und Außerbetriebnahmedatum,
- Beziehungen: `powers`, `powered_by`, `depends_on`,
- optionale Herkunft: `procurement_case`.

Assetklassen sind Daten in `asset-classes.yaml`. Der Core enthält keine Liste
zulässiger Gerätetypen. Eine neue Klasse wird durch einen Katalogeintrag ergänzt,
ohne Python-Code zu ändern.

## Verbindlicher Lifecycle

```text
PLANNED → ORDERED → DELIVERED → ACCEPTANCE → PRODUCTION
                                              ↓
                                         MAINTENANCE → RETIRED
```

Es sind ausschließlich diese sieben Zustände und der jeweils nächste Übergang
zulässig. Insbesondere ist `DELIVERED` nicht produktiv. `ACCEPTANCE → PRODUCTION`
ist nur möglich, wenn Identität und Garantiedaten vollständig erfasst sowie alle
Acceptance-Phasen erfolgreich und personengebunden bestätigt wurden.

## Acceptance Workflow

1. **Sichtprüfung:** korrektes Modell, unbeschädigte Verpackung, vorhandene
   Seriennummer.
2. **Lieferumfang:** Zubehör vollständig, Dokumentation vorhanden.
3. **Funktionsprüfung:** gerätespezifische Testnamen im Asset-Datensatz, alle
   erfolgreich.
4. **Asset Acceptance:** Prüfer und Datum dokumentiert; erst danach ist der
   Übergang nach `PRODUCTION` zulässig.

Ein fehlender Wert oder fehlgeschlagener Test blockiert die Produktionsfreigabe.

## Beziehungen und Graphen

`depends_on` bildet funktionale Abhängigkeiten ab und darf innerhalb der Registry
keine Zyklen enthalten. `powers` und `powered_by` bilden die Stromversorgung ab.
Beziehungen dürfen auf registrierte Assets oder explizit benannte bestehende
externe Komponenten zeigen. Unbekannte Ziele werden abgelehnt.

Der Core stellt Lookup, Relationship-Abfrage, Dependency Graph und Power Graph
als reine In-Memory-Operationen bereit.

## Gateway- und Rack-Trennung

Gateway-Infrastruktur darf nicht als rackmontiert markiert werden;
Rack-Infrastruktur muss rackmontiert sein. Damit gilt verbindlich:

| Asset | infrastructure | mounted_in_rack |
|---|---|---:|
| Router-USV | `gateway` | `false` |
| Rack-USV | `rack` | `true` |

Die Router-USV bleibt am Speedport-Standort außerhalb des Arbeitszimmers und
gehört weder logisch noch elektrisch zur Rack-Infrastruktur.

## Erstes Asset: UPS-RTR-01

`UPS-RTR-01` ist als `gateway_power` im Zustand `PRODUCTION` registriert.
Hersteller Eaton, Modell 3S850D, Produktbezeichnung Eaton 3S 850 DIN,
Seriennummer und Kaufdaten sind bestätigt. Das Garantieende bleibt bis zu einem
belastbaren Nachweis `PENDING_CONFIRMATION`. Das Asset versorgt als externe
Lasten Speedport Smart 4, Telefon und Elspet Automatic Litter Box; diese
Verbraucher sind keine Assets.

Vor `PRODUCTION` müssen folgende Router-USV-Tests bestanden werden:

- automatischer Batteriebetrieb,
- Rückkehr auf Netzbetrieb,
- fehlerfreier Betrieb.

Diese Prüfungen wurden mit WO-0038 am 04.08.2026 erfolgreich dokumentiert; das
Asset wurde anschließend nach `PRODUCTION` überführt.
