---
document: PC-0003-Firewall-Appliance-Decision.md
work_order: WO-0033-R2
related_work_order: WO-0033
previous_review: WO-0033-R1
version: 1.2
status: Accepted
owner: Project Owner
reviewed_by: Lead Architect
last_review: "2026-07-31"
classification: Workspace
evaluated_at: "2026-07-31"
---

# PC-0003 – Firewall Appliance

## Entscheidungsvorlage

**Aktuelle Projektphase:** Horizon 1 – Initial Build.

Heute wird ausschließlich die wirtschaftlichste Appliance empfohlen, die im
konkreten Angebot sämtliche Architecture Gates aus WO-0032 erfüllt. Nach der
vorliegenden Kandidaten- und Preisbasis ist dies die HUNSN RJ42 N100 in einer
vollständigen Konfiguration bis 300 EUR. Solange der vollständige Nachweis fehlt,
lautet die Beschaffungsentscheidung `WAIT`.

Eine teurere Appliance ist in Horizon 1 keine alternative Standardempfehlung.
Sie darf erst bewertet werden, wenn die im Kapitel „Empfehlung“ dokumentierten
Trigger einer späteren Projektphase tatsächlich eingetreten und nachgewiesen
sind. Freies Budget bleibt damit für Rack, Managed Switch, USV, Access Point,
Storage und Monitoring verfügbar.

## Bewertungsgrundlage

Jeder Kandidat durchläuft zwei gleichrangige Gates:

1. **Architecture Gate:** Sämtliche Muss-Anforderungen aus WO-0032 müssen
   erfüllt und im konkreten Angebot nachgewiesen sein. Ein günstiger Preis kann
   ein fehlendes Architecture Gate nicht kompensieren.
2. **Project-Strategy Gate:** Unter allen architekturkonformen Kandidaten werden
   Preis, Nutzen im aktuellen Ausbauschritt, Auswirkungen auf das Gesamtbudget
   und späterer Upgradepfad bewertet. Ein höherer Preis ist nur zulässig, wenn
   sein Mehrwert bereits in der aktuellen Phase benötigt wird.

Danach erfolgt die Einordnung in Technical Reference, Best Value Recommendation
und Budget Recommendation. Die Klassen sind Rollen im Entscheidungsmodell und
keine Aussage, dass jeder beobachtete Einzelartikel sofort kaufbar ist.

Preis- und Verfügbarkeitswerte sind Beobachtungen vom 31.07.2026 und keine
Preisgarantie. Herstellerwerte belegen Produktspezifikationen; Händler- oder
Marktseiten belegen nur Preis und Verfügbarkeit.

## Architektur-Compliance gegen WO-0032

| WO-0032 Gate | Nachweis DEC697 | Ergebnis |
|---|---|---|
| OPNsense dauerhaft | OPNsense ist vorinstalliert; Open Source plus ein Jahr Business Edition. Der Open-Source-Betrieb benötigt danach kein Abonnement. | PASS |
| Getrennte WAN-/LAN-Schnittstellen | Vier physisch unabhängige 2,5-GbE-RJ45-Ports; mindestens je ein Port für WAN und LAN. | PASS |
| 802.1Q und mehrere Netze | Hersteller dokumentiert bis zu 4093 virtuelle 802.1Q-Interfaces. | PASS |
| DSL-Leistung mit Reserve | 5 Gbit/s Firewall, 2,3 Gbit/s Port-to-Port und 600 Mbit/s IPsec. Selbst ein 250-Mbit/s-DSL-Anschluss hätte beim IPsec-Wert Faktor 2,4 Reserve; der tatsächliche DSL-Tarif bleibt vor Inbetriebnahme zu bestätigen. | PASS |
| VPN integrierbar | 600 Mbit/s IPsec AES256GCM16 ist dokumentiert. | PASS |
| Vollständig lokal / kein Cloud-Zwang | Lokale OPNsense-Installation und dedizierte Konsole; keine Cloud wird als Betriebsbedingung genannt. | PASS |
| Lokale Konsole und Restore | Console-Port und Konfigurationskabel vorhanden; OPNsense-Konfigurationsbackup ist Teil des WO-0032-Migrationspfads. | PASS |
| Rack-Kompatibilität | 22 × 185 × 134 mm, 0,6 kg, Desktopform. Montage auf belüftetem Rackfachboden; PC-0002 muss diesen Fachboden bereitstellen. | PASS |
| Rack-USV-Kompatibilität | 100–240 V AC, 50–60 Hz, maximal 0,4 A, typisch 13 W. EU-Netzkabel ist Kaufbedingung; 13 W plus Reserve fließen in PC-0005 ein. | PASS |
| Keine Sackgasse | Vier Ports, 802.1Q, VPN, Konsole und Leistungsreserve erlauben Segmentierung und VPN ohne Appliance-Wechsel. | PASS |

## Überarbeitetes Bewertungsmodell

Bewertung: 0 = nicht erfüllt/kein Nachweis, 1 = bedingt, 2 = vollständig.
Architecture Gates sind nicht durch Mehrpunkte kompensierbar. Die gewichtete
Bewertung wird erst nach bestandenem Architecture Gate angewendet.

| Kriterium | Gewicht | DEC697 | DEC740 | Protectli VP3210 | HUNSN RJ42 N100 |
|---|---:|---:|---:|---:|---:|
| OPNsense-Nachweis | 5 | 2 | 2 | 2 | 1 |
| Physische WAN/LAN-Trennung | 5 | 2 | 2 | 2 | 2 |
| 802.1Q/VLAN-Nachweis | 5 | 2 | 2 | 1 | 1 |
| Dokumentierte Firewall-/VPN-Leistung | 5 | 2 | 2 | 1 | 1 |
| Lokaler Betrieb ohne Cloud-Zwang | 5 | 2 | 2 | 2 | 2 |
| Lokale Konsole / Recovery | 4 | 2 | 2 | 1 | 1 |
| Vollständige RAM-/Storage-Konfiguration | 4 | 2 | 2 | 1 | 0 |
| Elektrische Daten / EU-Versorgung | 4 | 2 | 2 | 2 | 2 |
| Maße / Rackfachboden-Kompatibilität | 3 | 2 | 2 | 2 | 2 |
| Hersteller-Support / Garantie | 4 | 2 | 2 | 2 | 1 |
| Energieeffizienz | 2 | 2 | 2 | 1 | 2 |
| Preis-Leistung | 3 | 1 | 0 | 1 | 2 |
| **Gewichtete Punkte (max. 98)** |  | **94** | **91** | **75** | **65** |
| **Architecture Gate – Produktdesign** |  | **PASS** | **PASS** | **bedingt** | **bedingt** |
| **Architecture Gate – konkretes Angebot** |  | **PASS bei EU-Gesamtpreis** | **PASS bei EU-Gesamtpreis** | **offen bis Konfiguration feststeht** | **offen bis Komplettausstattung nachgewiesen ist** |

Die technische Punktzahl erklärt die technische Rangfolge, entscheidet aber
nicht allein über die Beschaffung. Für die aktuelle Phase wird zusätzlich die
folgende Wirtschaftlichkeitsbewertung angewendet.

## Entscheidungsklassen und Wirtschaftlichkeit

| Klasse | Kandidat | Preisbasis | Mehrkosten zur Budgetgrenze | Architektonischer Mehrwert | Operativer Mehrwert | Mehrpreis lohnt sich ab |
|---|---|---:|---:|---|---|---|
| Technical Reference | DEC740 | 878 EUR | 578 EUR | 10-GbE-SFP+, höhere Firewall- und VPN-Reserve | Mehr Reserve für sehr hohe Bandbreiten und anspruchsvolle Security-Dienste | Erst bei bestätigtem 10-GbE-Uplink, mehr als 600 Mbit/s VPN oder messbarer Auslastungsgrenze der kleineren Appliance |
| Best Value Recommendation | DEC697 | 678 EUR | 378 EUR | Vollständig dokumentierte OPNsense-Plattform, vier Ports, VLAN, 8 GB/256 GB | Geringeres Integrations-, Varianten- und Garantierisiko; sofort klarer Supportweg | Wenn die Firewall sofort benötigt wird, kein qualifiziertes Budgetangebot verfügbar ist oder der Project Owner den Supportmehrwert ausdrücklich höher bewertet als 378 EUR Reserve |
| Budget Recommendation | HUNSN RJ42 N100, vollständig | bis 300 EUR | 0 EUR | Vier 2,5-GbE-Ports, OPNsense-/VLAN-/VPN-fähige x86-Plattform und lokaler Betrieb | Erfüllt das erste Product Increment bei geringster Kapitalbindung | Sofort, sobald alle Angebotsbedingungen nachgewiesen sind; späteres Upgrade erst bei gemessenem Bedarf |

Die Protectli VP3210 bleibt eine Zwischenalternative, ist aber weder günstigste
vollständige Lösung noch technischer Referenzpunkt. Sie wird nur betrachtet,
wenn ein vollständiges Angebot unterhalb der DEC697 vorliegt und alle Gates
nachweist.

## Empfehlung

### Horizon 1 – Initial Build

**Status:** Aktuelle Projektphase.

**Empfohlene Beschaffungsstrategie:** Es wird ausschließlich die
wirtschaftlichste Appliance empfohlen, welche sämtliche Architecture Gates aus
WO-0032 vollständig erfüllt.

**Ziel:**

- minimal notwendige Investition,
- vollständige Architekturkonformität,
- keine unnötigen Leistungsreserven,
- später ohne Architekturänderung austauschbar.

**Heute empfohlene Appliance:** HUNSN RJ42 N100, exaktes Modell
`RJ42-N100-00`, als vollständige Konfiguration bis maximal 300 EUR.

Die Kaufempfehlung gilt ausschließlich, wenn der konkrete Artikel ohne weitere
Interpretation alle folgenden Bedingungen erfüllt:

- Neugerät und lieferbar,
- mindestens 8 GB RAM und 128 GB NVMe,
- vier Intel-i226-V-2,5-GbE-Ports,
- OPNsense-/FreeBSD-Kompatibilität und vollständig lokaler Betrieb,
- 12-V-EU-Netzteil sowie dokumentierte Rack-USV-Kompatibilität,
- bekannter Gesamtpreis einschließlich Versand,
- nachvollziehbare Gewährleistung,
- Montage auf einem belüfteten Rackfachboden möglich.

Fehlt eine Bedingung, lautet die Entscheidung `WAIT`. Es wird in Horizon 1
keine teurere Appliance allein wegen Herstellerstatus, theoretischer Leistung
oder möglicher zukünftiger Reserven empfohlen.

> Die für Horizon 1 empfohlene Appliance ist die Standardempfehlung des
> Projekts. Eine höherwertige Appliance darf ausschließlich empfohlen werden,
> wenn dokumentierte technische Anforderungen der aktuellen Projektphase durch
> die Horizon-1-Lösung nicht mehr erfüllt werden.

### Horizon 2 – System Growth

**Empfohlene Beschaffungsstrategie:** Nach steigendem Ressourcenbedarf darf eine
leistungsfähigere Appliance bewertet werden.

Der Übergang zu Horizon 2 erfolgt nicht durch Zeitablauf oder vorsorgliche
Reserveplanung. Mindestens ein Mehrbedarf muss gemessen oder als verbindliche
funktionale Anforderung dokumentiert sein, beispielsweise:

- IDS/IPS ist dauerhaft aktiv und überschreitet nachweislich die verfügbare
  Leistung,
- mehrere gleichzeitig genutzte VPN-Tunnel überschreiten die benötigte
  Durchsatz- oder Latenzgrenze,
- die Internetbandbreite steigt deutlich und kann nicht mehr mit definierter
  Reserve verarbeitet werden,
- mehrere Server erhöhen die Routing- oder Segmentierungslast messbar,
- CPU-, Speicher-, Session- oder Routing-Auslastung erreicht dokumentierte
  Betriebsgrenzen.

Erst nach einem solchen Nachweis werden die bereits dokumentierten Kandidaten
erneut gegen den dann aktuellen Bedarf bewertet. Die bloße Verfügbarkeit höherer
Leistung ist kein Trigger.

### Horizon 3 – Enterprise Expansion

**Empfohlene Beschaffungsstrategie:** Enterprise-Hardware wird ausschließlich
empfohlen, wenn Horizon 2 nachweislich ausgeschöpft wurde oder neue funktionale
Anforderungen entstehen, die mit Horizon-2-Hardware nicht mehr wirtschaftlich
erfüllt werden können.

Zulässige Trigger sind insbesondere verbindliche Anforderungen an hohe
Verfügbarkeit, Hersteller-Support mit definierten Reaktionszeiten, redundante
Hardwarepfade, sehr hohe Port-/VPN-/Security-Leistung oder Betriebsrisiken, deren
Kosten den Mehrpreis nachweislich rechtfertigen. Ein Enterprise-Label oder
ungenutzte Leistungsreserve allein ist kein Beschaffungsgrund.

### Eindeutige Lifecycle-Entscheidung

| Zeitpunkt | Empfehlung | Entscheidungsbedingung |
|---|---|---|
| Heute / Horizon 1 | HUNSN RJ42 N100 vollständig bis 300 EUR | Alle Angebotsbedingungen und sämtliche WO-0032-Gates sind PASS; andernfalls `WAIT`. |
| Später / Horizon 2 | Leistungsfähigere Appliance neu bewerten | Mindestens ein dokumentierter oder gemessener Mehrbedarf aus Horizon 2 liegt vor. |
| Später / Horizon 3 | Enterprise-Appliance neu bewerten | Horizon 2 ist nachweislich ausgeschöpft oder eine neue Enterprise-Anforderung ist wirtschaftlich nicht anders erfüllbar. |

## Kandidatenvergleich

### 1. Deciso DEC697 – Best Value Recommendation

- 4 × 2,5 GbE, 8 GB RAM, 256 GB NVMe, Console-Port
- 5 Gbit/s Firewall, 2,3 Gbit/s Port-to-Port, 600 Mbit/s IPsec
- 4093 virtuelle 802.1Q-Interfaces
- OPNsense vorinstalliert, Open-Source-Regelbetrieb
- 13 W typisch; 22 × 185 × 134 mm; 0,6 kg
- 678 EUR am 31.07.2026, ab Lager; zwei Jahre Carry-in-&-Return-Garantie
- Nachteil: deutlich teurer als OEM-N100-Geräte

### 2. Deciso DEC740 – Technical Reference

- 3 × 2,5 GbE plus 2 × 10 GbE SFP+, 4 GB RAM, 128 GB Storage
- 10 Gbit/s Firewall, 8,5 Gbit/s Port-to-Port, 1,2 Gbit/s IPsec
- 15 W typisch; 28 × 190 × 160 mm; 0,842 kg
- 878 EUR am 31.07.2026
- Für den DSL-Zielpfad überdimensioniert; höhere Leistung rechtfertigt den
  Mehrpreis ohne konkreten 10-GbE-Bedarf nicht.

### 3. Protectli Vault Pro VP3210 – Supportorientierte Barebone-Alternative

- Intel N100, 2 × Intel i226-V 2,5 GbE, DDR5, NVMe, Coreboot-Support
- Hersteller nennt breite Open-Source-Firewall-Kompatibilität und zwei Jahre
  Werksgarantie
- Basispreis 299 EUR; RAM, NVMe, Netzkabel und OS sind optionenabhängig
- Nur zwei integrierte Ports; ausreichend für WO-0032, aber weniger physische
  Reserve. Kauf erst nach vollständigem Konfigurations- und Gesamtpreisnachweis.

### 4. HUNSN RJ42 N100 – Budget Recommendation

- Intel N100, 4 × Intel i226-V 2,5 GbE, AES-NI, lüfterlos
- 145,6 × 126,5 × 53,6 mm; 12 V/5 A Netzteil; 6 W CPU-TDP
- Der beobachtete Barebone-Preis von 240,99 EUR war nicht lieferbar; RAM und
  Storage fehlen
- OPNsense-Kompatibilität ist im Produktangebot genannt, aber Hersteller-,
  Garantie-, Firmware- und Variantenvertrag sind schwächer als bei Deciso
- Ist die Empfehlung für die aktuelle Projektphase; kein `BUY_CANDIDATE` ohne
  exakten Komplettnachweis

## Zielpreis und Kaufregel

| Modell | Bevorzugter Gesamtpreis | Harte Grenze | Kaufstatus |
|---|---:|---:|---|
| DEC697 | 650 EUR | 700 EUR | Kaufen nach Project-Owner-Freigabe, wenn alle Angebotsregeln PASS |
| DEC740 | 750 EUR | 800 EUR | Nur Ausnahmefreigabe bei begründetem 10-GbE-/Performancebedarf |
| VP3210 | 425 EUR | 500 EUR | Nur vollständig mit ≥8 GB RAM, ≥128 GB NVMe und EU-Netzkabel |
| RJ42 N100 | 250 EUR | 300 EUR | Nur vollständig mit ≥8 GB RAM, ≥128 GB NVMe, EU-Netzteil und Gewährleistung |

Der caseweite Zielpreis beträgt 250 EUR, die reguläre harte Grenze 300 EUR. Die
DEC697-Grenze von 700 EUR ist keine Aufhebung des Budgetziels, sondern eine
modellbezogene Ausnahme für den dokumentierten Sofortbedarfsfall. Die DEC740-
Grenze erfordert zusätzlich einen nachgewiesenen Performancebedarf und eine
separate Ausnahmefreigabe.

## Watch-Konfiguration

PC-0003 bleibt bis zur Bestellung `WATCHING`. Der tägliche Watch verarbeitet
vier exakte Produktquellen. Ein Angebot wird nur `BUY_CANDIDATE`, wenn:

1. Modell und Konfiguration eindeutig einem freigegebenen Kandidaten entsprechen.
2. Alle WO-0032-Architecture-Gates `PASS` sind.
3. Zustand neu, Lieferbarkeit und Gewährleistung bestätigt sind.
4. Gesamtpreis einschließlich Versand bekannt und innerhalb der Modellgrenze ist.
5. Ein passendes EU-Netzkabel beziehungsweise EU-Netzteil enthalten ist.
6. Bei Barebones mindestens 8 GB RAM und 128 GB NVMe enthalten sind.
7. Die finale Freigabe durch den Project Owner weiterhin aussteht.

Nicht passende, gemischte oder unvollständige Varianten werden nicht empfohlen.
Es findet keine automatische Bestellung statt.

### End-to-End-Validierung

Der isolierte Live-Lauf `WR-2eb1212c5b71` vom 31.07.2026 war erfolgreich:
vier von vier Quellen wurden ohne Quellenfehler verarbeitet, drei positive
Preisbeobachtungen wurden gespeichert und drei Angebote wurden kanonischen
Modellen zugeordnet. Der Runtime-Status `REVIEW` ist beabsichtigt, weil
Versand-/Gesamtpreis oder vollständige angebotsspezifische Kaufbedingungen noch
nicht bei allen Quellen maschinenlesbar vorliegen. Die Runtime erzeugt daher
korrekt keinen automatischen `BUY_CANDIDATE`. Dies entspricht der R1-Entscheidung
`WAIT`, bis ein Budgetkandidat sämtliche Kaufbedingungen erfüllt.

## Risiken und dokumentierte Alternativen

- **Herstellerbindung:** Deciso ist teurer, reduziert dafür Integrations- und
  Nachweisrisiken. Open-Source-OPNsense verhindert einen Cloud-Lock-in.
- **Desktopgerät im Rack:** DEC697 benötigt einen belüfteten Fachboden. Diese
  Abhängigkeit wird als Gate an PC-0002 weitergegeben.
- **USV-Anschluss:** Das konkrete EU-Netzkabel und die Steckdosenart der
  Rack-USV müssen im Angebot bzw. PC-0005 übereinstimmen.
- **DSL-Tarif unbekannt:** Die dokumentierte Leistung reicht selbst für deutlich
  höhere DSL-Raten; der tatsächliche Tarif wird vor Inbetriebnahme erfasst.
- **DEC677:** Mit 4 GB/32 GB günstiger, aber der Hersteller rät bei schreibintensiven
  Funktionen wie IDS oder Netflow zur DEC697. Deshalb keine Empfehlung.
- **N100-OEM:** Preislich attraktiv, aber erst kaufreif, wenn Modell, Bestückung,
  Netzteil, Gewährleistung und OPNsense-Kompatibilität im konkreten Angebot
  vollständig belegt sind.

## Quellenstand 31.07.2026

- [OPNsense DEC697 Produktseite](https://shop.opnsense.com/product/dec697-opnsense-desktop-security-appliance/)
- [OPNsense DEC740 Produktseite](https://shop.opnsense.com/product/dec740-opnsense-desktop-security-appliance/)
- [OPNsense Hardware Sizing](https://docs.opnsense.org/manual/hardware.html)
- [Protectli VP3210 Produktseite](https://eu.protectli.com/product/vp3210/)
- [HUNSN RJ42 Angebots-/Spezifikationsseite](https://www.handyhuellen.berlin/products/hunsn-micro-firewall-appliance-mini-pc-vpn-router-pc-intel-alder-lake-n-12th-gen-n100-rj42-4-x-2-5gbe-i226-v-2-x-hdmi-dp-tf-type-c-barebone-no-ram-no-storage-no-system)
- [Intel N-Series AES-NI-Dokumentation](https://edc.intel.com/content/www/us/en/design/products/platforms/processor-and-core-i3-n-series-datasheet-volume-1-of-2/001/intel-advanced-encryption-standard-new-instructions/)
- [FreeBSD igc(4) – Intel I225/I226](https://man.freebsd.org/cgi/man.cgi?query=igc)

## Ergebnis

PC-0003 ist entscheidungsreif: Architecture Gates, technische und wirtschaftliche
Matrix, Zielpreise, Alternativen und Watch-Regeln bleiben dokumentiert. Die
finale Empfehlung richtet sich ausschließlich nach dem Projektlebenszyklus.
Horizon 1 ist die aktuelle Phase; empfohlen ist heute ausschließlich die
vollständige HUNSN RJ42 N100 bis 300 EUR, andernfalls `WAIT`. Eine andere
Appliance wird erst nach Eintritt der ausdrücklich dokumentierten Horizon-2-
oder Horizon-3-Trigger bewertet. WO-0033-R2 löst weder Bestellung noch
Inbetriebnahme oder OPNsense-Konfiguration aus.
