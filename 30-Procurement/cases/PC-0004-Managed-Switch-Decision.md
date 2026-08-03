---
document: PC-0004-Managed-Switch-Decision.md
work_order: WO-0034-R1
version: 1.1
status: Accepted
owner: Project Owner
reviewed_by: Lead Architect
last_review: "2026-07-31"
release_reference: knowledge-v1.4.4
last_updated: "2026-08-03"
classification: Workspace
---

# PC-0004 – Managed Switch Decision

| Feld | Wert |
|---|---|
| Status | **Accepted** |
| Work Order | WO-0034 |
| Architektur | WO-0032 |
| Governance | WO-0033-R2 |
| Projektphase | **Horizon 1 – Initial Build** |
| Stand | 2026-07-31 |
| Reviewed by | Lead Architect |
| Last review | 2026-07-31 |
| Bestellung | Nicht Bestandteil; keine automatische Bestellung |

## 1. Executive Decision

**Horizon-1-Standardempfehlung: TP-Link TL-SG2008P V3**, sofern ein konkretes
Neugerät-Angebot einschließlich Versand und erforderlicher Rackablage höchstens
130 EUR kostet und die Hardwareversion V3, das Netzteil, Verfügbarkeit sowie
Garantie/Gewährleistung eindeutig bestätigt sind.

Das Modell erfüllt die Architecture Gates mit acht Gigabit-Ports, lokaler
Standalone-Verwaltung, IEEE 802.1Q, Konfigurationssicherung und lüfterlosem
Betrieb. Vier Ports liefern IEEE 802.3af/at PoE+ mit 30 W je Port und 62 W
Gesamtbudget. Der geplante Access Point kann dadurch ohne separaten Injector
zentral über die Rack-USV versorgt werden. Das ist für den aktuellen Ausbau die
wirtschaftlichste vollständige Systemlösung, nicht die leistungsstärkste
Hardware.

**Warum Omada?** Omada ist kein Architecture Gate und kein Grund für einen
Enterprise-Aufpreis. Bei vergleichbaren Gesamtkosten bietet es jedoch einen
konkreten Integrationsvorteil: Switch und ein später kompatibel ausgewählter
Access Point können optional gemeinsam verwaltet werden. Die Empfehlung bleibt
auch ohne Omada-Controller vollständig funktionsfähig.

**Warum lokales Management?** HDC-OS muss vollständig lokal betreibbar bleiben.
Lokales Management erhält Konfigurations-, Backup- und Wiederherstellungszugriff
auch bei Internetausfall, Herstellerstörung oder abgeschaltetem externem Dienst.
Es macht den Switch außerdem unabhängig von einer separaten Managementplattform
während Aufbau und Fehlerbehebung.

**Warum kein Cloud-Zwang?** Die Firewall-nahe Kerninfrastruktur darf weder für
den Betrieb noch für Änderungen von einem Herstellerkonto oder externen Dienst
abhängen. Cloud-Ausfall, Produktabkündigung oder geänderte Lizenzbedingungen
dürfen die lokale Netzfunktion nicht beeinträchtigen. Cloud- und
Controllerfunktionen sind daher ausschließlich optionale Ergänzungen.

**Entscheidungszielpreis:** 100 EUR Gesamtpreis.

**Harte Entscheidungsgrenze:** 130 EUR Gesamtpreis.
Der Gesamtpreis umfasst Switch, Versand, notwendiges Netzteil und erforderliche
Rackablage. Bei Nicht-PoE-Kandidaten zählt zusätzlich ein passender
802.3af/at-PoE+-Injector. Die bestehende Case-Hülle von 150/220 EUR bleibt als
Portfolio-Budget erhalten, ist aber keine Kaufvollmacht und hebt die strengere
Horizon-1-Grenze nicht auf.

Der beobachtete Gerätepreis der Empfehlung lag am 31.07.2026 ab etwa 86 EUR.
Gegenüber dem günstigsten beobachteten Nicht-PoE-Gerät (Zyxel GS1900-8, etwa
67,15 EUR) beträgt der reine Geräte-Mehrpreis rund 18,85 EUR. Nach Hinzurechnung
eines geeigneten PoE+-Injectors zur Nicht-PoE-Lösung ist der wirtschaftliche
Abstand voraussichtlich null oder gering; der exakte Abstand wird erst mit
vollständigen Angeboten festgestellt.

## 2. Abgeleiteter Bedarf

Der Switch sitzt ausschließlich hinter der OPNsense-Firewall:

`Speedport Smart 4 → OPNsense → Managed Switch → Clients / Access Point`

| Verwendung | Ports |
|---|---:|
| Firewall-Uplink | 1 |
| PS5 | 1 |
| Sky Box | 1 |
| Access Point | 1 |
| HDC-OS-Host | 1 |
| Wartungsport | 1 |
| Reserve | 2 |
| **Minimum** | **8** |

Acht Ports sind damit kein Schätzwert, sondern die kleinste vollständige
Belegung. Der Wartungsport darf temporär als Reserve dienen, wird aber nicht aus
der Kapazitätsrechnung entfernt. 2,5-Gbit/s-Ports oder SFP-Uplinks sind für den
aktuellen DSL-Ausbau nicht erforderlich.

## 3. Architecture Compliance

| Gate | Nachweis / Beschaffungsregel | Ergebnis |
|---|---|---|
| AG01 Managed | Web-/CLI-verwaltete Kandidaten; unmanaged und cloud-only ausgeschlossen | PASS |
| AG02 VLAN | IEEE 802.1Q, tagged/untagged, Trunk, Port-VLAN und Management-VLAN erforderlich | PASS |
| AG03 Lokal | Betrieb und Konfiguration ohne Cloudkonto; Omada/Cloud nur optional | PASS |
| AG04 Ports | Herleitung oben ergibt mindestens 8 physische Ethernet-Ports | PASS |
| AG05 Geschwindigkeit | Alle betrachteten RJ45-Ports sind mindestens 1 Gbit/s | PASS |
| AG06 PoE | Entscheidung geschlossen: PoE+ wirtschaftlich sinnvoll; Nicht-PoE nur mit eingepreistem Injector | PASS |
| AG07 Rack | 19-Zoll-Gerät oder sichere belüftete Rackablage; Zubehör ist Teil des Gesamtpreises | PASS |
| AG08 Strom/Lärm | Nur lüfterlose Kandidaten; Verbrauch und PoE-Last werden in Abschnitt 5 betrachtet | PASS |
| AG09 Backup | Lokaler Konfigurationsexport und Restore beziehungsweise reproduzierbare Konfiguration erforderlich | PASS |
| AG10 Segmentierung | VLANs für Client, Server, Management, IoT und Guest vorbereitbar; Aktivierung erst später | PASS |

Ein fehlender Nachweis in einem konkreten Angebot ist kein stillschweigender
PASS: fehlendes Architecture Gate führt zu **REJECT**, fehlende Angebotsdaten zu
**WAIT**.

## 4. PoE-Entscheidung

**Gewählt ist Option A: PoE ist in Horizon 1 wirtschaftlich sinnvoll.**

Der eine geplante Access Point benötigt dann weder einen separaten Injector noch
eine zusätzliche Steckdose. Strom und Daten werden gemeinsam über die
Rack-USV-geschützte Switch-Verbindung geführt. Die Empfehlung bietet vier
802.3af/at-Ports, maximal 30 W pro Port und 62 W Gesamtbudget. Für PC-0005 sind
nicht pauschal 62 W Dauerlast anzusetzen, sondern 7,9 W Switch-Grundlast plus die
Maximalaufnahme des später ausgewählten Access Points; für den Worst Case der
Switch-Auslegung sind bis zu 77,3 W dokumentiert.

PoE bleibt bewusst kein Architekturzwang. Ein Nicht-PoE-Switch ist zulässig,
wenn ein normgerechter 802.3af/at-Injector einschließlich Netzteil, Platz,
Verkabelung und USV-Last im Gesamtpreis enthalten ist und die Gesamtlösung
günstiger bleibt. Benötigt der spätere Access Point mehr als 30 W oder IEEE
802.3bt, ist die Empfehlung vor Kauf des AP neu zu bewerten.

**Verbindliches Cross-Case-Gate PC-0004 ↔ Access-Point-Case:** Der ausgewählte
Access Point muss IEEE 802.3af oder IEEE 802.3at unterstützen und innerhalb von
30 W je Port sowie des verfügbaren 62-W-Gesamtbudgets liegen. Fehlt dieser
Nachweis vor dem AP-Kauf oder benötigt der AP einen anderen PoE-Standard, wird
PC-0004 vor dem Kauf neu bewertet. Der AP darf dann nicht stillschweigend gegen
den bestehenden Switch freigegeben werden.

## 5. Technischer Kandidatenvergleich

| Kriterium | TL-SG2008 V4 | **TL-SG2008P V3** | Zyxel GS1900-8 | SG2218 V1.30 |
|---|---|---|---|---|
| Rolle | Economic Omada | **Omada PoE** | Economic other vendor | Stronger reference |
| RJ45 | 8 × 1 GbE | 8 × 1 GbE | 8 × 1 GbE | 16 × 1 GbE |
| Zusätzliche Ports | – | – | – | 2 × 1G SFP |
| PoE | Nein | **4 × 802.3af/at, 30 W/Port, 62 W** | Nein | Nein |
| Management | lokal Standalone; Omada optional | lokal Standalone; Omada optional | lokale Weboberfläche | lokal Web/CLI; Omada optional |
| VLAN/Trunk | 802.1Q | 802.1Q | 802.1Q | 802.1Q |
| Backup/Restore | lokaler Export/Import | lokaler Export/Import, Dual Configuration | lokales Backup/Restore | lokaler Export/Import, Dual Configuration |
| Lüfter | fanless | **fanless** | fanless / 0 dBA | fanless |
| Verbrauch | max. 6,4 W | 7,9 W ohne PD; bis 77,3 W mit 62-W-PD-Last | max. 5,0 W | standby 3,8 W; max. 12,3 W |
| Maße B×T×H | 209×126×26 mm | 209×126×26 mm | 250×104×27 mm | 440×180×44 mm |
| Nettogewicht | Herstellerangabe nicht gefunden | Herstellerangabe nicht gefunden | 0,65 kg | 1,8 kg |
| Montage | Desktop/Wand; Rackablage | Desktop/Wand; **Rackablage** | Desktop/Wand; Rackablage | 19 Zoll, 1 HE |
| Netzteil | extern; exakte V4-Ausführung prüfen | extern 53,5 V/1,31 A; muss enthalten sein | extern | intern 100–240 V AC |
| Beobachteter Preis | ab ca. 71,79 EUR | **ab ca. 86,00 EUR** | ca. 67,15 EUR; Verfügbarkeit unklar | ab ca. 114,90 EUR |
| Horizon-1-Ergebnis | Alternative mit Injector | **Empfehlung** | Budgetalternative mit Injector | Nicht empfohlen |

Alle Preise sind Marktbeobachtungen vom 31.07.2026, keine garantierten
Kaufpreise. Bei TP-Link-Desktopgeräten war in den herangezogenen
Herstellerunterlagen kein Nettogewicht ausgewiesen. Das ist transparent als
fehlende Produktangabe dokumentiert; für die geringe statische Ablagelast ist es
kein Architekturhindernis. Das konkrete Angebot muss jedoch Versandgewicht und
geeignete Ablage nicht verwechseln. Unklarheit über Modell, Hardwareversion oder
Zubehör führt zu WAIT.

## 6. Bewertungsmodell

Architecture Gates sind Ausschlusskriterien und werden nicht durch Punkte
kompensiert. Nur vollständig konforme Kandidaten werden gewichtet. Skala 0–5;
gewichtetes Maximum 235.

| Kriterium | Gewicht | TL-SG2008 | TL-SG2008P | GS1900-8 | SG2218 |
|---|---:|---:|---:|---:|---:|
| Lokale Verwaltung | 5 | 5 | 5 | 5 | 5 |
| VLAN | 5 | 5 | 5 | 5 | 5 |
| Portanzahl | 5 | 5 | 5 | 5 | 5 |
| PoE-Eignung | 4 | 1 | 5 | 1 | 1 |
| Rack-Kompatibilität | 4 | 3 | 3 | 3 | 5 |
| Lautstärke | 4 | 5 | 5 | 5 | 5 |
| Energieverbrauch | 3 | 5 | 4 | 5 | 3 |
| Backup/Restore | 4 | 5 | 5 | 4 | 5 |
| Hersteller/Warranty | 2 | 4 | 4 | 4 | 4 |
| Integration | 3 | 5 | 5 | 3 | 5 |
| Preis/Wert | 5 | 4 | 5 | 4 | 2 |
| USV-Auswirkung | 3 | 3 | 5 | 3 | 2 |
| **Gewichtete Punkte** |  | **193** | **221** | **184** | **184** |

Die Punkte dienen nur der nachvollziehbaren Rangfolge. Sie machen eine teurere
Lösung nicht automatisch besser und dürfen kein Gate oder die harte Preisgrenze
überstimmen.

## 7. Wirtschaftlichkeit und Projektlebenszyklus

### Horizon 1 – Initial Build (aktuell)

Empfohlen wird TL-SG2008P V3, weil es den Bedarf ohne ungenutzte Port- oder
Uplink-Überdimensionierung deckt und den AP-Injector ersetzt. Gegenüber der
reinen Budget-Hardware GS1900-8 beträgt der beobachtete Geräte-Mehrpreis rund
18,85 EUR; der operative Mehrwert ist zentrale USV-geschützte AP-Versorgung,
weniger Netzteile und weniger Verkabelung. Der Mehrpreis lohnt sich sofort,
sobald der AP per PoE betrieben wird und der ansonsten erforderliche Injector
den Preisabstand nicht unterschreitet.

Kann ein vollständiges GS1900-8-plus-Injector-Angebot mindestens 15 EUR günstiger
als ein vollständiges TL-SG2008P-V3-Angebot beschafft werden, wird die
Budgetalternative vorgelegt. Liegt die Empfehlung über 130 EUR Gesamtpreis,
lautet der Status WAIT; es wird nicht auf die stärkere Referenz ausgewichen.

### Horizon 2 – System Growth

Ein stärkerer Switch darf neu bewertet werden, wenn der dokumentierte Bedarf
acht Ports überschreitet, mehrere PoE-Geräte das 62-W-Budget auslasten,
2,5-Gbit/s-Links tatsächlich benötigt werden oder messbare Switching-/Uplink-
Engpässe entstehen. Die heutige Reserve allein ist kein Beschaffungsgrund.

### Horizon 3 – Enterprise Expansion

Enterprise-Hardware ist erst zulässig, wenn Horizon 2 nachweislich ausgeschöpft
ist oder neue Funktionen mit Horizon-2-Hardware nicht wirtschaftlich erfüllt
werden können. SG2218 ist heute lediglich eine stärkere Referenz: mehr Ports,
SFP und native Rackmontage rechtfertigen den Mehrpreis und den weiterhin nötigen
PoE-Injector im aktuellen Ausbau nicht.

## 8. Rack-, Kühlungs- und USV-Bewertung

Die Empfehlung benötigt eine belüftete 19-Zoll-Rackablage; sie belegt keine
eigene 19-Zoll-Befestigung. Das externe Netzteil muss zugentlastet im Rack
platziert werden. Oberhalb des lüfterlosen Gehäuses bleibt Luftzirkulation frei.
Eine Ablage darf mit Firewall-Komponenten geteilt werden, sofern Maße,
Tragfähigkeit, Wärmeabfuhr und Kabelradien dies zulassen; ihr anteiliger oder
voller Preis wird trotzdem im Gesamtangebot ausgewiesen. Die Rackablage ist
damit kein stillschweigend vorhandenes Zubehör, sondern verpflichtender
Bestandteil der vollständigen Beschaffungslösung. Nach der Beschaffung wird sie
als eigenes Asset beziehungsweise als eindeutig zugeordnetes Rackzubehör in die
HDC-OS-Asset-Liste aufgenommen.

Die Rack-USV versorgt Switch und AP. Für die Laufzeitrechnung gilt:

`Switch 7,9 W + tatsächliche AP-Maximalaufnahme + Netzteilverluste`

Für thermische und elektrische Absicherung ist zusätzlich der dokumentierte
Worst Case von bis zu 77,3 W für TL-SG2008P V3 zu berücksichtigen. Die
Router-USV außerhalb des Arbeitszimmers bleibt unverändert ausschließlich dem
Speedport-Standort zugeordnet.

## 9. Procurement Watch

Aktive öffentliche Preisquellen sind für alle vier Kandidaten in
`config/sources.yaml` eingerichtet. Die Empfehlung und mindestens eine
wirtschaftliche Alternative werden damit beobachtet.

Ein Angebot ist nur vollständig, wenn folgende Felder bekannt sind:

- exaktes Modell und Hardwareversion,
- Neuwarezustand und Verfügbarkeit,
- Produktpreis, Versand und Gesamtpreis,
- Anbieter sowie Garantie/Gewährleistung,
- enthaltenes und passendes Netzteil,
- PoE-Standard, -Budget und nutzbare Ports beziehungsweise der konkrete Injector,
- erforderliche Rackablage oder Montagekomponenten.

Statuslogik:

| Bedingung | Status |
|---|---|
| Mindestens ein Architecture Gate fehlt | REJECT |
| Pflichtangabe oder belastbarer Gesamtpreis fehlt | WAIT |
| Alle Gates erfüllt, Angaben vollständig, Gesamtpreis ≤ 130 EUR | REVIEW |
| Project Owner gibt genau dieses Angebot frei | BUY_CANDIDATE |

BUY_CANDIDATE löst keine Bestellung aus. Bestellung, Inbetriebnahme,
VLAN-Aktivierung und Netzwerkumbau liegen ausdrücklich außerhalb dieses Cases.

## 10. Alternativen und Ausschlussgründe

- **TL-SG2008 V4:** technisch konform und Omada-kompatibel. Ohne Injector ist
  die AP-Stromversorgung unvollständig; all-in nur wählen, wenn nachweislich
  günstiger.
- **Zyxel GS1900-8:** günstigste Geräteklasse und lokal/fanless. Fehlendes PoE
  und keine Omada-Integration; mit qualifiziertem Injector valide
  Budgetalternative.
- **SG2218 V1.30:** technisch stärker und direkt rackfähig, aber 16 RJ45-Ports
  und SFP sind in Horizon 1 ungenutzt; kein PoE. Mehrpreis und USV-Last sind
  aktuell nicht gerechtfertigt.
- Cloud-only-, unmanaged- und aktive laute Switches sind ausgeschlossen.

## 11. Annahmen und offene Punkte

Es gibt keine impliziten Annahmen. Folgende Punkte bleiben explizit offen und
werden als Angebots- beziehungsweise Cross-Case-Gates behandelt:

1. Das konkrete Access-Point-Modell und der zugehörige Procurement Case sind
   noch nicht festgelegt. Vor dessen Kauf sind IEEE-Standard und
   Maximalleistung gegen 802.3af/at, 30 W je Port und 62 W Gesamtbudget zu
   prüfen. PC-0005 bleibt ausschließlich der Rack-USV zugeordnet.
2. Rackmodell und verfügbare Ablagefläche stammen aus PC-0002. Vor Freigabe muss
   eine Ablage mit mindestens 209×126 mm Stellfläche, ausreichender Traglast und
   Luftzirkulation bestätigt, im Gesamtangebot eingepreist und für die spätere
   Aufnahme in die Asset-Liste eindeutig bezeichnet sein.
3. Die Nettogewichte von TL-SG2008 V4 und TL-SG2008P V3 wurden in den
   herangezogenen Herstellerunterlagen nicht veröffentlicht. Für die
   Rackplanung wird kein Wert erfunden; der Anbieter oder eine belastbare
   Produktunterlage muss ihn vor finaler mechanischer Freigabe bestätigen.
4. Garantie-/Gewährleistungsumfang ist anbieter- und landesspezifisch und wird
   am konkreten Angebot geprüft.
5. Marktpreise und Lieferbarkeit ändern sich. Der Watch ersetzt deshalb die
   Beobachtungswerte durch einen vollständigen Angebotssnapshot.

Keiner dieser Punkte erlaubt eine automatische Hochstufung auf stärkere oder
teurere Hardware.

## 12. Quellenstand

- TP-Link, TL-SG2008 V4 Produktseite und Datenblatt.
- TP-Link, TL-SG2008P V3 Produktseite, Datenblatt und Configuration Guide.
- Zyxel, GS1900 Series Specification und GS1900 User Guide.
- TP-Link, SG2218 V1.30 Datenblatt.
- Geizhals-Produktseiten der vier Kandidaten, beobachtet am 31.07.2026.

Die konkreten URLs sind zugleich in `30-Procurement/config/sources.yaml`
beziehungsweise in den Watch-Evidenzen hinterlegt. Herstellerdaten haben bei
technischen Merkmalen Vorrang; Preisportale dienen nur der Marktbeobachtung.
