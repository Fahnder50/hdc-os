---
document: Procurement.md
version: 1.4.4-baseline
status: Accepted
owner: Project Owner
reviewed_by: Lead Architect
last_review: "2026-08-03"
release_reference: knowledge-v1.4.4
last_updated: "2026-08-03"
classification: Workspace
---

# Procurement

## Repository Baseline

| Feld | Stand |
|---|---|
| Release | `knowledge-v1.4.4` |
| Sprint | Sprint 4 – First Deployment |
| Abgeschlossene Grundlage | Procurement Foundation und Operations Transition für PC-0001 |
| Aktueller Fokus | PC-0002 bis PC-0005 zur konkreten Horizon-1-Kaufentscheidung führen |

## Zweck und Governance

Procurement übersetzt die Accepted-Architektur in nachvollziehbare,
wirtschaftliche Kaufentscheidungen. In Horizon 1 gilt die günstigste vollständig
architekturkonforme Lösung als Standard. Ungenutzte Leistungsreserven,
Enterprise-Klasse oder Herstellerstatus rechtfertigen keinen Mehrpreis.

Der Watch beobachtet und bewertet; er bestellt nicht. Der Project Owner gibt ein
konkretes Angebot frei. Mit `PURCHASED` endet Procurement. Danach ist
ausschließlich die Asset Registry für Acceptance und Betriebsstatus maßgeblich.

Procurement setzt ausdrücklich keine Asset-Erstellung voraus. Nach einem Kauf
wird außerhalb dieses Systems entschieden, ob überhaupt ein Asset oder eine
andere nachgelagerte Behandlung entsteht. Ohne externe Asset-Entscheidung endet
der Ablauf vollständig bei Procurement.

## Aktuelles Portfolio

| Case | Status | Entscheidung / nächster Schritt |
|---|---|---|
| PC-0001 Router-USV | **PROCUREMENT COMPLETED (`PURCHASED`)** | Eaton 3S850D an `UPS-RTR-01` übergeben; kein Watch und keine neue Kaufempfehlung |
| PC-0002 Rack | WATCHING | Digitus DN-48000/48001/48002; Requirements und Gesamtentscheidung noch offen |
| PC-0003 Firewall | WATCHING | Horizon-1-Standard ist ein vollständig qualifiziertes HUNSN RJ42 N100-Angebot; andernfalls `WAIT` |
| PC-0004 Managed Switch | WATCHING | TL-SG2008P V3 als Horizon-1-Standard; vollständiges Angebot abwarten |
| PC-0005 Rack-USV | WATCHING | CyberPower OR1000ERM1U beobachtet; Requirements noch offen |

PC-0001 bleibt mit Preis-, Händler-, Entscheidungs-, Report- und
Beschaffungshistorie erhalten. Es wird nicht mehr ausgewertet. PC-0002 bis
PC-0005 bilden das aktive Watch-Portfolio.

## PC-0003 – Firewallstrategie

Aktuelle Projektphase ist Horizon 1 – Initial Build. Standardempfehlung ist
HUNSN RJ42 N100 als vollständiges Neugerät mit mindestens 8 GB RAM, 128 GB NVMe,
vier Intel-i226-V-2.5GbE-Ports, EU-Netzteil, Gewährleistung, Lieferbarkeit und
bekanntem Gesamtpreis.

| Grenze | Wert |
|---|---:|
| Zielpreis | 250 EUR |
| Reguläre harte Gesamtgrenze | 300 EUR |

DEC697 ist nur ein dokumentierter Fallback bei bestätigtem Sofortbedarf und
fehlendem qualifiziertem Budgetangebot. DEC740 ist Technical Reference. Höhere
Leistung oder theoretische Reserven lösen in Horizon 1 keine Hochstufung aus.
Verbindliche Details stehen in der
[Firewall-Entscheidung](cases/PC-0003-Firewall-Appliance-Decision.md).

## PC-0004 – Switchstrategie

Horizon-1-Standard ist der lüfterlose TP-Link TL-SG2008P V3 mit acht
Gigabit-Ports, lokaler Verwaltung und vier IEEE-802.3af/at-PoE+-Ports.

| Grenze | Wert |
|---|---:|
| Entscheidungszielpreis einschließlich Pflichtzubehör | 100 EUR |
| Harte Gesamtgrenze | 130 EUR |

Rackablage, Versand und notwendiges Netzteil gehören zum Gesamtangebot und die
Rackablage später in die Asset-Liste. Verbindliches Cross-Case-Gate: Der Access
Point muss IEEE 802.3af/at unterstützen und innerhalb von 30 W je Port sowie
62 W Gesamtbudget bleiben; andernfalls ist PC-0004 vor AP-Kauf neu zu bewerten.
Details: [Managed-Switch-Entscheidung](cases/PC-0004-Managed-Switch-Decision.md).

## PC-0005 – Rack-USV

PC-0005 bleibt `WATCHING`. CyberPower OR1000ERM1U ist der aktuelle Kandidat;
Zielpreis 170 EUR, maximale Gesamtgrenze 350 EUR. Rackmontage, Laufzeit,
Monitoring, Linux-Kompatibilität, Erweiterbarkeit und reale Racklasten sind noch
offene Requirements. Es gibt noch keine Kaufentscheidung.

## Preis- und Entscheidungslogik

1. Architecture Gates müssen vollständig PASS sein.
2. Exaktes Modell, Neuware, Verfügbarkeit, Händler, Garantie, Versand,
   Stromversorgung und Gesamtpreis müssen bekannt sein.
3. Fehlendes Gate führt zu Ablehnung; fehlende Angebotsdaten zu `WAIT`.
4. Ein vollständiges Angebot innerhalb der Grenze wird zur Review vorgelegt.
5. Erst die Freigabe des konkreten Angebots durch den Project Owner macht es zum
   Kaufkandidaten.
6. Es gibt keine automatische Bestellung.

Das Portfolio-Gesamtbudget beträgt 2.000 EUR. Freies Budget soll den
Gesamtfortschritt – Rack, Switch, USV, AP, Storage und Monitoring – fördern,
nicht einzelne Komponenten früh überdimensionieren.

## Übergang zu Operations

```text
WATCHING → QUALIFYING → READY_FOR_REVIEW → BUY_CANDIDATE
                                             └─ PURCHASED

Jeder aktive Zustand → CANCELLED
```

Nur aktive Zustände werden beobachtet oder bewertet. Asset-Handover ist ein
optionaler, externer Folgeprozess und kein Bestandteil dieses Lifecycles.
`CLOSED` ist kein persistenter Status, sondern nur die automatisch erzeugte
Archivansicht von `PURCHASED` und `CANCELLED`.

Der Übergang von PC-0001 ist in
[WO-0036](../20-Operations/WO-0036-Procurement-to-Asset-Handover.md)
dokumentiert. Assetzustände werden niemals aus Procurement abgeleitet.

## Architektur und Runtime

- [Procurement-Architektur](architecture/Procurement-Architecture.md)
- [Datenmodell](architecture/Data-Model.md)
- [Generic Procurement Lifecycle](architecture/Generic-Procurement-Lifecycle.md)
- [Ausführungsmodell](architecture/Execution-Model.md)
- [Runtime-Betrieb](README.md)

## Historischer Hinweis

Die frühere Sprint-1-Vorauswahl – insbesondere Extralink Rack, pauschaler
Intel-N100-Favorit, SG2218 als Horizon-1-Switch und eine offene Router-USV – ist
superseded. Historische Entscheidungsgrundlagen bleiben in Git, den Case-Dateien
und den Sprint-/Knowledge-Dokumenten erhalten.
