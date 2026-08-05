---
work_order: WO-0041
title: First Deployment Readiness
type: Operations / Deployment
status: Accepted
priority: High
sprint: Sprint 4 – First Deployment
date: 2026-08-04
reviewed_by: Lead Architect
last_review: 2026-08-05
---

# WO-0041 – First Deployment Readiness

## 1. Zweck und verbindlicher Status

Dieses Dokument definiert ausschließlich das Gate, ab dem das erste physische
HDC-OS-Deployment beginnen darf. Es beschafft, installiert und konfiguriert
nichts.

**Aktueller Gate-Status: `NOT_READY`**

Begründung: Firewall und Managed Switch sind noch nicht vorhanden. Der Zustand
`READY_FOR_FIRST_DEPLOYMENT` darf erst gesetzt werden, wenn alle Gates in
Abschnitt 9 nachweislich `PASS` sind. Teilfreigaben sind unzulässig.

## 2. Deployment-Ziel und Abgrenzung

Das First Deployment weist genau diesen architekturkonformen Erfolgspfad nach:

```text
Laptop
  │ LAN
  ▼
Managed Switch
  │ LAN-Uplink
  ▼
OPNsense Firewall
  │ WAN über vorhandenes Wohnungskabel
  ▼
Speedport Smart 4
  │ Telekom DSL
  ▼
Internet
```

Die Komponentenfolge aus RD-01 wird als Sicherheits- und Funktionspfad
verstanden. Die verbindliche physische Portreihenfolge folgt WO-0032: Der
Laptop ist LAN-seitig am Managed Switch angeschlossen; der Switch liegt hinter
der Firewall und niemals zwischen Firewall-WAN und Speedport. Damit entsteht
keine neue Architekturentscheidung.

Erfolg bedeutet: Der Laptop erhält seine Netzkonfiguration ausschließlich von
OPNsense und erreicht das Internet über OPNsense-NAT und Speedport-NAT. Der
Speedport bleibt DSL-Gateway und Telefonie-Plattform.

Nicht Teil dieses Deployments und keine Startblocker sind:

- Rack und Rack-USV,
- Access Point und WLAN,
- NAS und HDC-OS-Server,
- Monitoring und Automationen,
- VPN, VLAN-Aktivierung und KI-Komponenten,
- PS5, Sky Box und weitere produktive Clients.

Die Geräte werden für das First Deployment frei auf einer geeigneten, stabilen
Arbeitsfläche betrieben. Das ist ein temporärer Aufbau, keine Änderung des
Rack-Zieldesigns.

## 3. Hardware Checklist

### 3.1 Pflicht-Hardware

| ID | Komponente | Zweck | Nachweis vor Start | Aktueller Stand |
|---|---|---|---|---|
| HW-01 | OPNsense-fähige Firewall mit getrenntem WAN und LAN | Sicherheitsgrenze, Routing, NAT, DHCP und DNS | Gerät vorhanden; Netzteil und WAN-/LAN-Ports geprüft | **FEHLT / BLOCKER** |
| HW-02 | Managed Switch | LAN-Verteilung zwischen Firewall und Laptop | Gerät vorhanden; Netzteil und Managementzugang geprüft | **FEHLT / BLOCKER** |
| HW-03 | Speedport Smart 4 | Bestehendes DSL-Gateway und Telefonie | Internet und Telefonie vor Umbau funktionsfähig | Vorhanden; Baseline am Deployment-Tag erneut prüfen |
| HW-04 | Laptop | Installations- und Abnahmeclient | LAN-Schnittstelle oder funktionsfähiger Adapter; Netzteil vorhanden | Vorhanden; Schnittstelle noch zu bestätigen |
| HW-05 | Patchkabel 1: RJ45, mindestens Cat6, mindestens 1 Gbit/s | Firewall-LAN zu Managed Switch | Linktest mit mindestens 1 Gbit/s bestanden; beschriftet | Bestand/Funktion offen |
| HW-06 | Patchkabel 2: RJ45, mindestens Cat6, mindestens 1 Gbit/s | Managed Switch zu Laptop | Linktest mit mindestens 1 Gbit/s bestanden; beschriftet | Bestand/Funktion offen |
| HW-07 | Vorhandenes Wohnungskabel | Speedport-LAN zu Firewall-WAN | Linktest bestanden; Arbeitszimmer-Ende identifiziert | Vorhanden; Funktion erneut prüfen |
| HW-08 | Stromversorgung | Firewall, Switch und Laptop versorgen | Netzteile, Steckdosen und sichere Kabelführung geprüft | Offen |

Fehlt ein Gegenstand oder sein Funktionsnachweis, bleibt `Hardware Ready = FAIL`.
Die Router-USV bleibt unverändert am Speedport-Standort. Eine USV-Versorgung von
Firewall und Switch ist für dieses Deployment ausdrücklich keine Voraussetzung.

### 3.2 Hilfsmittelklassifikation

| Hilfsmittel | Klassifikation | Verbindliche Festlegung |
|---|---|---|
| USB-Ethernet-Adapter | Optional | Vor Start erforderlich machen, falls der Laptop keinen funktionsfähigen RJ45-Port besitzt. |
| HDMI-Monitor | Optional | Vor Start erforderlich machen, falls die ausgewählte Firewall für Installation oder Recovery eine lokale Bildausgabe benötigt. |
| Tastatur | Optional | Gemeinsam mit lokalem Monitor erforderlich machen, falls die Appliance keine andere bedienbare Installationskonsole bietet. |
| Maus | Nicht benötigt | OPNsense-Installation und WebGUI benötigen keine Maus. |
| USB-Stick | Erforderlich | Bootfähiges, verifiziertes OPNsense-Installationsmedium; ein zweiter Stick ist optional. |
| Serieller Konsolenadapter | Optional | Vor Start erforderlich machen, wenn die ausgewählte Appliance seriell installiert oder wiederhergestellt werden muss; Kabeltyp muss zum Konsolenport passen. |

`Optional` bedeutet nicht, dass die Entscheidung während des Deployments fallen
darf. Nach Feststehen der konkreten Firewall wird die Konsolenmethode vor dem
Gate dokumentiert; alle dafür nötigen Hilfsmittel müssen dann vorhanden sein.

### 3.3 Existing Network Baseline

Unmittelbar vor Beginn des Deployments ist der funktionierende Ausgangszustand
zu protokollieren. Die Baseline ist nur vollständig, wenn alle folgenden Punkte
mit Zeitstempel und verantwortlicher Person als `PASS` bestätigt sind:

| ID | Baseline-Prüfung | PASS-Kriterium | Aktueller Nachweis |
|---|---|---|---|
| BL-01 | DSL synchron | Speedport zeigt eine stabile DSL-Synchronisation. | Am Deployment-Tag zu bestätigen |
| BL-02 | Internet erreichbar | Ein bestehender Client erreicht einen externen IP-Endpunkt und ein HTTPS-Ziel. | Am Deployment-Tag zu bestätigen |
| BL-03 | Telefonie funktionsfähig | Ein ausgehender und ein eingehender Testanruf sind erfolgreich. | Am Deployment-Tag zu bestätigen |
| BL-04 | Speedport erreichbar | Die lokale Speedport-Verwaltungsoberfläche ist über den bestehenden Netzwerkpfad erreichbar. | Am Deployment-Tag zu bestätigen |
| BL-05 | Netgear Switch funktionsfähig | Bestehende Linkverbindungen sind aktiv und ein angeschlossener Client besitzt Konnektivität. | Am Deployment-Tag zu bestätigen |
| BL-06 | Laptop besitzt Internet | Der Deployment-Laptop erreicht vor dem Umbau DNS und Internet über das bestehende Netz. | Am Deployment-Tag zu bestätigen |
| BL-07 | Router-USV im Normalbetrieb | `UPS-RTR-01` zeigt Netzbetrieb ohne aktiven Alarm oder bekannte Störung. | Am Deployment-Tag zu bestätigen |

Ein `FAIL`, `UNKNOWN` oder nicht ausgeführter Baseline-Punkt sperrt den Beginn.
Die dokumentierten Istwerte dienen nach Deployment oder Rollback als
Vergleichsgrundlage. Die Baseline führt keine Konfigurationsänderung durch.

## 4. Configuration Checklist

Die folgenden Sollwerte sind die verbindliche Horizon-1-Baseline. Sie aktivieren
keine VLANs und setzen keine späteren Detaildesigns voraus.

| ID | Parameter | Sollwert | Begründung / Gate-Nachweis |
|---|---|---|---|
| CFG-01 | Firewall-Hostname | `fw-hdc-01` | Eindeutiger lokaler Infrastruktur-Hostname. |
| CFG-02 | Firewall-LAN / Management-IP | `10.41.0.1/24` | OPNsense ist Gateway, DHCP- und DNS-Endpunkt des Basis-LAN. Vor Start ist Nichtüberlappung mit dem Speedport-Netz nachzuweisen. |
| CFG-03 | LAN-Netz | `10.41.0.0/24` | Separates RFC1918-Netz hinter OPNsense; VLAN-freie First-Deployment-Baseline. |
| CFG-04 | DHCP-Bereich | `10.41.0.100–10.41.0.199` | Genügend dynamische Adressen; unterer Bereich bleibt für Infrastruktur reserviert. |
| CFG-05 | Switch-Management-IP | `10.41.0.2/24`, Gateway/DNS `10.41.0.1` | Lokales Management hinter OPNsense; kein Cloud-Zwang. |
| CFG-06 | DNS-Strategie | Laptop nutzt ausschließlich `10.41.0.1`; OPNsense stellt lokalen Resolver/Forwarder bereit und verwendet definierte WAN-Upstreams. | Trennt Client-DNS vom Speedport; konkrete Upstream-Resolver werden vor Start dokumentiert. |
| CFG-07 | Administratorzugang | Individuelles lokales Administratorkonto; starkes einmaliges Initialpasswort; kein Cloudkonto; Geheimnis nicht im Repository. | Zugangsdaten werden vor Start in der freigegebenen lokalen Geheimnisablage hinterlegt. Standardpasswort muss beim Erstzugang geändert werden. |
| CFG-08 | Backup-Strategie | Vor WAN-Umschaltung Export der OPNsense-Grundkonfiguration und des Switch-Setups auf den Laptop; zweite Offline-Kopie; Dateihash und Restore-Schritte dokumentieren. | Rollback darf nicht von Cloud oder laufender Firewall abhängen. |
| CFG-09 | WAN-Strategie | OPNsense-WAN bezieht eine Adresse aus dem Speedport-LAN; bevorzugt DHCP-Reservierung. | Speedport bleibt Default Gateway; Speedport- und LAN-Netz dürfen nicht überlappen. |
| CFG-10 | VLAN-Zustand | Nicht aktiviert | VLANs sind vorbereitet, aber ausdrücklich nicht Bestandteil des First Deployments. |

Noch vor dem Deployment zwingend zu bestätigen:

- tatsächliches Speedport-Subnetz und dessen Nichtüberlappung mit
  `10.41.0.0/24`,
- freie und konfliktfreie Adressen `10.41.0.1` und `10.41.0.2`,
- OPNsense-WAN-Reservierung oder dokumentierte DHCP-Zuweisung,
- konkrete DNS-Upstream-Resolver,
- konkrete lokale Geheimnisablage und Recovery-Zugriff,
- Installations-/Konsolenmethode der beschafften Firewall.

Bis diese Bestätigungen vorliegen, ist `Configuration Ready = FAIL`.

## 5. Physical Topology und Portplan

| Verbindung | Seite A | Seite B | Kabel / Zweck |
|---|---|---|---|
| WAN-01 | Speedport freier LAN-Port | OPNsense-Port `WAN` | Vorhandenes Speedport–Arbeitszimmer-Kabel; ausschließlich WAN-Transit |
| LAN-01 | OPNsense-Port `LAN` | Managed-Switch-Port 1 | Geprüftes Patchkabel 1; ungetaggtes Basis-LAN |
| CLIENT-01 | Managed-Switch-Port 2 | Laptop-LAN | Geprüftes Patchkabel 2; ungetaggter Client-Port |

Verbindliche Regeln:

- WAN- und LAN-Port der Firewall werden vor dem Einschalten sichtbar
  beschriftet.
- Das vorhandene Wohnungskabel wird vom Netgear Switch gelöst und ausschließlich
  mit OPNsense-WAN verbunden.
- Der Managed Switch besitzt im First Deployment keinen Uplink zum Speedport.
- Weitere Switch-Ports bleiben unbenutzt und administrativ im sicheren
  Standardzustand.
- Der Netgear Switch und Bestandsclients bleiben außerhalb des Testpfads und
  bilden den dokumentierten Rollback-Pfad.
- Telefonieanschlüsse und Router-USV am Speedport werden nicht verändert.

## 6. Installation Checklist und verbindliche Reihenfolge

Die Reihenfolge darf während des Deployments nicht umgestellt werden.

1. **Baseline festhalten:** Internet, DNS, Speedport-Zugang und Telefonie im
   Ursprungsnetz prüfen; aktuelle Kabel- und Portbelegung fotografieren oder
   protokollieren.
2. **Rollback bereitlegen:** Netgear-Ursprungsport markieren, zwei Patchkabel
   prüfen, Speedport-Zugangsdaten und Rückbauplan lokal verfügbar halten.
3. **Hardware offline aufbauen:** Firewall, Switch und Laptop standsicher
   platzieren; Netzteile zuordnen; WAN/LAN und Switch-Ports beschriften.
4. **OPNsense installieren:** Verifiziertes Installationsmedium und vorab
   festgelegte Konsolenmethode verwenden; WAN und LAN eindeutig zuweisen.
5. **Firewall offline grundkonfigurieren:** Hostname, LAN-IP, DHCP, DNS,
   Administratorzugang und Baseline-Regeln gemäß Abschnitt 4 setzen.
6. **Switch lokal vorbereiten:** Management-IP setzen, DHCP-Serverfunktionen
   ausschließen, Port 1 und Port 2 als ungetaggtes Basis-LAN festlegen.
7. **LAN verkabeln:** Firewall-LAN mit Switch-Port 1 und Laptop mit Switch-Port 2
   verbinden; Links prüfen. WAN bleibt noch getrennt.
8. **LAN-Basistest durchführen:** DHCP-Lease, Gateway, DNS-Adresse,
   Firewall-WebGUI und Switch-Management prüfen.
9. **Backups erstellen:** Firewall- und Switch-Grundkonfiguration gemäß CFG-08
   sichern und Prüfsummen dokumentieren.
10. **WAN umschalten:** Vorhandenes Wohnungskabel vom Netgear Switch lösen und
    an Firewall-WAN anschließen. Keine Speedport-Telefonieeinstellung ändern.
11. **Konnektivität abnehmen:** Tests aus Abschnitt 8 in der festgelegten
    Reihenfolge durchführen.
12. **Ergebnis entscheiden:** Nur bei vollständigem PASS den Testaufbau
    dokumentieren. Bei einem kritischen FAIL sofort Abschnitt 10 ausführen.

## 7. Test Checklist und Messregeln

Vor Testbeginn werden Laptop-Lease, Testzeit und Bediener protokolliert. Ein
Ergebnis ohne beobachteten Istwert ist kein PASS.

| ID | Acceptance Test | Erwartetes Ergebnis | Kritisch |
|---|---|---|---|
| T-01 | Firewall-LAN erreichbar | `10.41.0.1` ist vom Laptop erreichbar. | Ja |
| T-02 | Firewall-WebGUI erreichbar | WebGUI öffnet über `https://10.41.0.1`; Anmeldung mit individuellem Adminzugang gelingt. | Ja |
| T-03 | Switch erreichbar | `10.41.0.2` und lokale Managementoberfläche sind vom Laptop erreichbar. | Ja |
| T-04 | DHCP funktioniert | Laptop erhält genau eine Adresse aus `10.41.0.100–199`, Präfix `/24`, Gateway und DNS `10.41.0.1`. | Ja |
| T-05 | DNS funktioniert | Ein definierter öffentlicher Testname wird aufgelöst; ein absichtlich ungültiger Name liefert einen kontrollierten Fehler. | Ja |
| T-06 | Internet erreichbar | Mindestens ein externer IP-Endpunkt und ein HTTPS-Ziel sind erreichbar. | Ja |
| T-07 | Speedport erreichbar | Speedport ist vom Firewall-WAN aus als Upstream erreichbar; ein Managementzugriff vom Laptop wird nur genutzt, wenn die Baseline-Regel ihn ausdrücklich erlaubt. | Ja |
| T-08 | Pfad bestätigt | Laptop-Gateway und externe Adresssicht belegen den Pfad über OPNsense-NAT und Speedport-NAT. | Ja |
| T-09 | Telefonie unverändert | Eingehender und ausgehender Testanruf funktionieren wie vor dem Umbau. | Ja |
| T-10 | Lokaler Betrieb | Firewall und Switch sind ohne Cloudkonto administrierbar. | Ja |
| T-11 | Backup vorhanden | Beide Konfigurationsexporte, zweite Offline-Kopie, Hash und Restore-Anweisung sind vorhanden. | Ja |
| T-12 | Connectivity fachlich getrennt | Power, Gateway, WAN, Internet und DNS werden getrennt bewertet; ein DNS-Fehler wird nicht pauschal als Strom- oder WAN-Ausfall dokumentiert. | Ja |

Alle Tests T-01 bis T-12 müssen `PASS` sein. `DEGRADED`, `UNKNOWN`, nicht
ausgeführt oder nur teilweise bestanden gelten für das First-Deployment-Gate als
`FAIL`.

## 8. Test-Readiness vor Deployment

`Test Ready = PASS` verlangt bereits vor dem Aufbau:

- benannte Testperson und geplantes Testfenster,
- lokal verfügbare Checkliste T-01 bis T-12,
- bekannte Speedport-Managementadresse und Telefonietestmöglichkeit,
- zwei festgelegte externe Testziele: ein IP-Endpunkt und ein HTTPS-/DNS-Name,
- Werkzeug zur Anzeige von DHCP-Lease, Gateway und DNS auf dem Laptop,
- Vorlage zur Erfassung von Sollwert, Istwert, Zeit und PASS/FAIL,
- definierte Abbruchregel: kritischer FAIL ohne unmittelbare Korrektur führt zum
  Rollback.

## 9. Deployment Gate Definition

| Gate | PASS-Bedingung | Aktueller Status |
|---|---|---|
| Hardware Ready | HW-01 bis HW-08 vorhanden und funktionsgeprüft; Konsolenhilfsmittel final klassifiziert | **FAIL** – Firewall und Managed Switch fehlen |
| Configuration Ready | CFG-01 bis CFG-10 bestätigt; alle sechs offenen Bestätigungen aus Abschnitt 4 geschlossen | **FAIL** – Bestätigungen und konkrete Geräte fehlen |
| Installation Ready | Topologie, Portplan, Reihenfolge, Verantwortlicher und Zeitfenster bestätigt | **FAIL** – Geräte-/Portprüfung und Termin fehlen |
| Test Ready | Testmittel und Protokoll für T-01 bis T-12 vollständig vorbereitet | **FAIL** – konkrete Testziele und Bediener offen |
| Rollback Ready | Ausgangsbelegung, Netgear-Rückbau, Zugangsdaten, Zeitbudget und Verantwortlicher bestätigt | **FAIL** – Vor-Ort-Nachweise offen |
| Architecture Conformity | Abgleich mit Network Design, Connectivity State Model, Asset Lifecycle und PC-0003/PC-0004 ohne Widerspruch | **PASS für den Standard**, vor Start anhand der beschafften Geräte erneut nachzuweisen |

Entscheidungsregel:

```text
Hardware Ready = PASS
AND Configuration Ready = PASS
AND Installation Ready = PASS
AND Test Ready = PASS
AND Rollback Ready = PASS
AND Architecture Conformity = PASS
=> READY_FOR_FIRST_DEPLOYMENT
```

Jede andere Kombination ergibt `NOT_READY`. Rack, Rack-USV, Access Point, NAS,
HDC-OS-Server, Monitoring, Automationen und KI-Komponenten dürfen in dieser
Entscheidung nicht als fehlende Voraussetzungen gewertet werden.

## 10. Rollback Checklist

### 10.1 Auslöser

Rollback erfolgt sofort, wenn ein kritischer Acceptance Test nicht besteht und
nicht innerhalb des vorab festgelegten Testfensters ohne Architektur- oder
Sicherheitsänderung korrigiert werden kann. Telefonieausfall löst unmittelbaren
Rollback aus.

### 10.2 Voraussetzungen

- Ursprünglicher Netgear-Port und Speedport-Kabel sind beschriftet.
- Ausgangsbelegung und funktionierende Baseline sind dokumentiert.
- Speedport-Konfiguration und Telefonie wurden nicht verändert.
- Laptop kann auf seine vorherige Netzkonfiguration zurückgestellt werden.
- Verantwortlicher, Beginn und maximales Rollback-Zeitbudget von 15 Minuten sind
  vor Start benannt.

### 10.3 Verbindlicher Rückbau

1. Test beenden und Fehlerzeitpunkt dokumentieren.
2. Laptop vom Managed Switch trennen.
3. Firewall und Managed Switch ausschalten; keine Konfigurationsdaten löschen.
4. Vorhandenes Wohnungskabel von Firewall-WAN lösen.
5. Dasselbe Kabel wieder mit dem dokumentierten ursprünglichen Port des Netgear
   Switch verbinden.
6. Ursprüngliche Clientverkabelung unverändert wiederherstellen.
7. Laptop auf vorherige DHCP-/WLAN-Nutzung zurückstellen.
8. Internet, DNS, Speedport-Zugang und Telefonie gegen die Baseline prüfen.
9. Rollback-Ergebnis, Dauer und verbleibende Abweichungen dokumentieren.

Der Rollback verändert keine gespeicherten Firewall- oder Switch-Backups und
löscht keine Diagnoseinformationen. Ein fehlgeschlagener Rollback ist ein
Incident; das Deployment bleibt gesperrt.

## 11. Architektur- und Governance-Abgleich

| Referenz | Übernommener Vertrag |
|---|---|
| Network Design v0.1 / WO-0032 | Speedport bleibt DSL-Gateway; OPNsense trennt WAN/LAN; Managed Switch liegt hinter OPNsense; Double NAT; keine neue Wohnungsverkabelung; 15-Minuten-Rollback. |
| Connectivity State Model / WO-0040 | Power, Gateway, WAN, Internet und DNS sind getrennte Zustände; keine Einzelprobe beweist Gesamtkonnektivität. |
| Asset Lifecycle / WO-0035 | Readiness registriert oder akzeptiert keine Assets und leitet keinen Betriebsstatus aus Procurement ab. |
| PC-0003 | Beschaffte Firewall muss OPNsense, getrennte WAN-/LAN-Ports, lokalen Betrieb, Backup und Konsole unterstützen. |
| PC-0004 | Beschaffter Switch muss Managed-Betrieb, lokales Management, Backup/Restore und VLAN-Vorbereitung unterstützen; VLANs bleiben hier inaktiv. |

Dieses Dokument ändert keine der Referenzen. Abweichungen werden nicht während
des Deployments entschieden, sondern blockieren das Gate und benötigen eine
neue Work Order oder einen ADR.

## 12. Offene Nachweise bis zur Startfreigabe

| ID | Offener Nachweis | Verantwortlich / Zeitpunkt | Blockiert |
|---|---|---|---|
| O-01 | Firewall vorhanden, Asset-/Geräteidentität und Ports bestätigt | Project Owner, nach Beschaffung | Hardware, Configuration |
| O-02 | Managed Switch vorhanden, Asset-/Geräteidentität und Ports bestätigt | Project Owner, nach Beschaffung | Hardware, Installation |
| O-03 | Zwei Patchkabel und Wohnungskabel funktionsgeprüft | Deployment-Verantwortlicher, vor Termin | Hardware |
| O-04 | Laptop-RJ45 oder USB-Ethernet-Adapter bestätigt | Deployment-Verantwortlicher, vor Termin | Hardware |
| O-05 | Speedport-Subnetz, Managementadresse und WAN-Zuweisung dokumentiert | Network Owner, vor Konfiguration | Configuration |
| O-06 | DNS-Upstreams und lokale Geheimnisablage festgelegt | Network Owner, vor Konfiguration | Configuration |
| O-07 | Konsolenmethode und erforderliche Hilfsmittel final festgelegt | Deployment-Verantwortlicher, nach Gerätewahl | Hardware, Installation |
| O-08 | Bediener, Testfenster und externe Testziele benannt | Project Owner, vor Termin | Test, Installation |
| O-09 | Ausgangsverkabelung und 15-Minuten-Rollback vor Ort bestätigt | Deployment-Verantwortlicher, unmittelbar vor Start | Rollback |

Es bestehen keine weiteren impliziten Annahmen. Jeder unbekannte Nachweis bleibt
sichtbar offen und verhindert die jeweilige Gate-Freigabe.

## 13. Abschlusskriterium dieser Work Order

WO-0041 ist dokumentarisch abgeschlossen, wenn dieser Standard reviewed und
angenommen ist. Das bedeutet ausdrücklich nicht, dass das Deployment bereits
startbereit ist. Der operative Startstatus bleibt bis zum Schließen von O-01 bis
O-09 und bis zu sechs `PASS`-Gates `NOT_READY`.
