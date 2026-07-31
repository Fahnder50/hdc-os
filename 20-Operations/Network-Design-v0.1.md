---
document: Network-Design-v0.1.md
work_order: WO-0032
version: 0.1
status: Accepted
owner: Project Owner
reviewed_by: Lead Architect
last_review: "2026-07-31"
classification: Workspace
---

# HDC-OS Network Design v0.1

## 1. Zweck, Geltung und Erfolgskriterium

Dieses Dokument ist das erste vollständige Infrastrukturdesign für HDC-OS. Es
beschreibt den bekannten Ist-Zustand, die verbindliche Zielarchitektur und einen
reversiblen Migrationspfad. Nach Annahme ist es die Referenz für
Infrastrukturentscheidungen und für die Bewertung der Procurement Cases PC-0002
bis PC-0005. Produkt-, Hersteller- und Preisentscheidungen sind nicht enthalten.

Das primäre Erfolgskriterium lautet:

> Ein Laptop ist per LAN oder WLAN an ein von OPNsense geschütztes Netz
> angeschlossen, erhält automatisch eine gültige Netzkonfiguration und erreicht
> das Internet über Managed Switch, OPNsense, Speedport Smart 4 und Telekom DSL.
> Die Telefonie am Speedport bleibt dabei unverändert funktionsfähig.

### 1.1 Normative Begriffe

- **Entscheidung:** Bestandteil des Zielbilds und gegenwärtig verbindlich.
- **Designvorgabe:** Muss eine spätere Detailentscheidung oder Beschaffung
  erfüllen.
- **Annahme:** Für v0.1 verwendete, noch zu bestätigende Aussage; sie wird nicht
  als Tatsache behandelt.
- **Offene Frage:** Vor Umsetzung des betroffenen Schritts zu klärender Punkt.
- **Produktiver Client:** Ein Gerät, das regulär Haushalts-, Arbeits- oder
  HDC-OS-Dienste nutzt. Telefonie-Endgeräte am Speedport sind hiervon ausgenommen.

### 1.2 Architekturentscheidungen und Begründungen

| ID | Entscheidung | Begründung |
|---|---|---|
| ND-01 | Der Speedport Smart 4 bleibt DSL-Gateway und Telefonie-Plattform. | Erfüllt die Randbedingungen und vermeidet Eingriffe in die funktionierende Telefonie. |
| ND-02 | OPNsense wird als Router und Sicherheitsgrenze zwischen Speedport und allen produktiven Clients betrieben. | Nur so gelten Firewall-Regeln, Protokollierung, VPN und spätere Segmentierung einheitlich für LAN und WLAN. |
| ND-03 | Der Zielbetrieb verwendet zunächst geroutetes IPv4 mit NAT auf OPNsense und dem weiterhin bestehenden NAT des Speedport (Double NAT). | Der Speedport bleibt Router; das Design benötigt weder Bridge Mode noch PPPoE-Passthrough. Double NAT ist lokal und mit der vorhandenen Leitung realisierbar. Eingehende Dienste erfordern gesonderte Freigaben. |
| ND-04 | Das vorhandene Kabel Speedport–Arbeitszimmer wird ausschließlich als WAN-Uplink der OPNsense verwendet. | Es gibt nur dieses Kabel und neue Wohnungsverkabelung ist ausgeschlossen. Eine Vermischung von WAN und internem LAN auf derselben unkontrollierten Verbindung wird vermieden. |
| ND-05 | Der Managed Switch bildet den zentralen LAN-Verteiler hinter OPNsense. | Er ermöglicht Portkontrolle, VLAN-Vorbereitung, Monitoring und spätere Segmentierung ohne Austausch der Grundtopologie. |
| ND-06 | Der Access Point wird ausschließlich hinter OPNsense am Managed Switch betrieben. | WLAN-Clients erhalten dadurch dieselbe Sicherheitsgrenze wie kabelgebundene Clients. |
| ND-07 | Im Zielzustand verbleiben am Speedport-Netz nur der Speedport selbst, seine Telefoniefunktion und der OPNsense-WAN-Port. | Direkte produktive Clients würden die zentrale Firewall umgehen. Temporäre Migrations- oder Notfallzugänge sind zeitlich begrenzt, dokumentiert und kein Regelbetrieb. |
| ND-08 | VLANs werden vorbereitet, aber erst nach stabilem unsegmentiertem Basisbetrieb aktiviert. | Das erste Erfolgskriterium bleibt klein und prüfbar; die Architektur bleibt dennoch ohne Austausch von Firewall, Switch oder AP segmentierbar. |
| ND-09 | HDC-OS wird lokal hinter OPNsense betrieben und erhält keine Voraussetzung für einen Cloud-Control-Plane-Dienst. | Erfüllt die Randbedingung „vollständig lokal betreibbar“ und erhält Diagnosefähigkeit bei externen Ausfällen. |
| ND-10 | Router-USV und Rack-USV bleiben getrennte Stromdomänen. | Die räumliche Trennung wird eingehalten; ein Fehler oder eine Überlastung einer USV betrifft nicht automatisch beide Standorte. |

## 2. Current State

### 2.1 Geräte und Standorte

| Standort | Gerät | Bekannte Rolle | Stromversorgung |
|---|---|---|---|
| Außerhalb des Arbeitszimmers, nahe Eingangstür | Telekom-DSL-Anschluss | Internetzugang | passiv |
| Außerhalb des Arbeitszimmers | Speedport Smart 4 | DSL-Modem/Router, NAT, bestehendes LAN/WLAN, Telefonie | Router-USV PC-0001 |
| Außerhalb des Arbeitszimmers | Telefonie-Endgerät(e) bzw. Speedport-Telefoniefunktion | Bestehende Telefonie | Zuordnung/Anschlussart noch zu inventarisieren |
| Außerhalb des Arbeitszimmers | Router-USV | Überbrückung der Stromversorgung des Speedport-Standorts | Netzstrom |
| Zwischen den Standorten | Ein vorhandenes Ethernet-Kabel | Speedport-Uplink in das Arbeitszimmer | keine |
| Arbeitszimmer | Unmanaged Netgear Switch | Verteilung des Speedport-LAN | Netzstrom; keine bekannte USV |
| Arbeitszimmer | PS5 | Kabelgebundener Client | Netzstrom |
| Arbeitszimmer | Sky Box | Client; Verbindungsart ist zu bestätigen | Netzstrom |
| Arbeitszimmer | Laptop des Project Owners | Mobiler produktiver Client; aktuelle Anbindung ist nicht vollständig dokumentiert | Akku/Netzteil |

### 2.2 Verkabelung und Internetpfad

Der bekannte kabelgebundene Pfad lautet:

```text
Telekom DSL
  -> Speedport Smart 4
  -> vorhandenes Ethernet-Kabel in das Arbeitszimmer
  -> unmanaged Netgear Switch
  -> PS5 und weitere angeschlossene Geräte
```

Der aktuelle WLAN-Pfad des Laptops und anderer Geräte ist nicht vollständig
inventarisiert. Soweit Geräte das Speedport-WLAN nutzen, umgehen sie keine
separate Firewall, da OPNsense heute noch nicht im Pfad steht.

### 2.3 Grenzen des bekannten Ist-Zustands

Nicht bestätigt sind insbesondere Portbelegung und Modell des Netgear Switch,
Verbindungsart der Sky Box, aktuelle Laptop-Anbindung, Telefonie-Anschlussart,
Speedport-Netz und DHCP-Bereich, WLAN-SSID(s), Kabelkategorie und Linkrate sowie
Steckdosen- und Leistungsdaten. Diese Lücken werden in Abschnitt 10 geführt.

## 3. Target Architecture

### 3.1 Zielbild

```text
Telekom DSL
  -> Speedport Smart 4
       -> Telefonie unverändert
       -> OPNsense WAN über vorhandenes Kabel
            -> OPNsense LAN
                 -> Managed Switch im Rack
                      -> Laptop per LAN
                      -> Access Point -> Laptop per WLAN
                      -> PS5
                      -> Sky Box, sofern netzwerkgebunden
                      -> lokale HDC-OS-Systeme
                      -> spätere Server, Storage und Infrastruktur
```

Der Speedport stellt weiterhin die DSL-Sitzung, Telefonie, sein eigenes
Managementnetz und die äußere NAT-Grenze bereit. OPNsense bezieht auf WAN eine
Adresse aus einem eigenen Speedport-Subnetz, verwendet auf LAN ein davon
verschiedenes privates Subnetz und ist Default Gateway, DHCP- und DNS-Endpunkt
für das interne Netz. Der Managed Switch verteilt dieses LAN. Der Access Point
transportiert das interne Netz und später mehrere VLANs als WLAN-SSIDs.

### 3.2 Komponenten und Beziehungen

| Komponente | Zweck im Zielbild | Beziehung |
|---|---|---|
| Speedport Smart 4 | DSL-Gateway, äußeres NAT, Telefonie | WAN-seitig Telekom; LAN-seitig nur OPNsense-WAN im Regelbetrieb |
| OPNsense Firewall | Zentrale Sicherheitsgrenze, internes Routing, NAT, DHCP, DNS, VPN-Endpunkt/-Gateway | WAN zum Speedport; LAN/Trunk zum Managed Switch |
| Managed Switch | Zentraler interner LAN-Verteiler und VLAN-Transport | Uplink zu OPNsense; Ports zu AP, Clients und HDC-OS |
| Access Point | WLAN hinter der Firewall | Kabel zum Managed Switch; Verwaltung intern; SSID-/VLAN-Zuordnung später |
| Rack | Physischer, geordneter Aufnahmeort für Rack-Komponenten | Im Arbeitszimmer; genaue Position offen |
| Router-USV | Versorgung des Speedport-Standorts | Bleibt außerhalb des Arbeitszimmers; versorgt mindestens Speedport gemäß PC-0001 |
| Rack-USV | Versorgung ausschließlich direkt angeschlossener Rack-Komponenten | Versorgt Firewall, Managed Switch und definierte HDC-OS-Rack-Komponenten; keine Haushaltsgeräte |
| HDC-OS | Lokal betriebene Operations-, Dokumentations-, Monitoring- und spätere Service-Plattform | Als interne Systeme am Managed Switch; kein Routing-Bypass |
| Laptop | Referenzclient für das Product Increment | Wahlweise Switch-Port oder WLAN des internen AP |
| PS5 / Sky Box | Haushaltsclients | Im Zielzustand hinter OPNsense; Segmentzuordnung später |

Der Access Point soll vorzugsweise per PoE vom Managed Switch versorgt werden.
Dabei ist nur der Switch direkt an die Rack-USV angeschlossen; die PoE-Abgabe ist
eine Netzwerkfunktion des Rack-Switches und kein separater Verbraucher an der
USV. Ob diese Auslegung der Randbedingung entspricht, ist vor PC-0004/PC-0005
durch den Project Owner zu bestätigen. Alternativ erhält der AP lokale
Netzversorgung ohne USV-Anspruch.

### 3.3 Erfolgspfad des Laptops

**LAN:** Laptop -> Access-Port des Managed Switch -> OPNsense-LAN ->
OPNsense-NAT -> Speedport-NAT -> Telekom DSL -> Internet.

**WLAN:** Laptop -> interne SSID des Access Point -> Managed Switch ->
OPNsense-LAN -> OPNsense-NAT -> Speedport-NAT -> Telekom DSL -> Internet.

In beiden Fällen vergibt OPNsense die Clientkonfiguration. DNS-Anfragen gehen an
OPNsense; OPNsense löst lokal bzw. über konfigurierte externe Resolver auf.
Unaufgeforderte eingehende Verbindungen werden an beiden NAT-Grenzen verworfen,
sofern keine ausdrücklich dokumentierte Freigabe existiert.

## 4. Physical Topology

### 4.1 Netzwerk- und Stromverbindungen

```text
STANDORT A – außerhalb Arbeitszimmer

  Netzstrom
     |
  Router-USV (PC-0001)
     |
  Speedport Smart 4 ---- Telefonie-Endgerät(e) / Telefoniefunktion
     |
     | vorhandenes Ethernet-Kabel, dedizierter WAN-Uplink
     +==========================================================+

STANDORT B – Arbeitszimmer

     +==========================================================+
     |
  OPNsense-WAN
  [Rack: OPNsense Firewall]
     |
  OPNsense-LAN
     |
  [Rack: Managed Switch] ---- LAN ---- Laptop
     |        |               LAN ---- PS5
     |        |               LAN ---- Sky Box (falls netzwerkgebunden)
     |        +--------------- LAN ---- lokale HDC-OS-Systeme
     |
     +---- Ethernet/PoE oder Ethernet + lokale Versorgung ---- Access Point
                                                               )) WLAN Laptop

  Netzstrom
     |
  Rack-USV (PC-0005)
     +---- OPNsense Firewall
     +---- Managed Switch
     +---- ausdrücklich definierte HDC-OS-Rack-Komponenten
```

### 4.2 Physische Designvorgaben

- Zwischen Speedport und Arbeitszimmer wird kein zusätzliches Netzwerkkabel
  vorausgesetzt.
- Das vorhandene Kabel endet im Zielzustand am OPNsense-WAN-Port, nicht am
  internen Switch.
- WAN- und LAN-Kabel im Rack sind eindeutig und dauerhaft zu kennzeichnen.
- Der OPNsense-LAN-Port verbindet sich direkt mit dem Managed Switch.
- Der Netgear Switch wird im Zielbetrieb nicht als zentraler Verteiler verwendet.
  Eine spätere Nutzung hinter dem Managed Switch ist nur für ein einzelnes,
  unsegmentiertes Access-Netz und nach dokumentierter Freigabe zulässig; für
  Trunks, Management oder Sicherheitszonengrenzen ist er ungeeignet.
- Rack, Rack-USV, Firewall und Switch müssen hinsichtlich Platz, Gewicht,
  Belüftung, Kabelführung, Steckern und Wartungszugang kompatibel sein.
- Der AP-Standort wird durch Funkmessung festgelegt; das Design erzwingt keinen
  Einbau des AP in das Rack.

### 4.3 USV-Zuordnung

| Stromdomäne | Direkt versorgte Komponenten | Nicht versorgt |
|---|---|---|
| Router-USV | Speedport; weitere Telefonie-Komponenten nur nach bestätigter PC-0001-Auslegung | Rack, Firewall, Switch, HDC-OS-Compute |
| Rack-USV | Firewall, Managed Switch, ausdrücklich freigegebene Rack-Komponenten | Speedport, PS5, Sky Box, Laptop-Netzteil, sonstige Haushaltsgeräte |
| Lokaler Netzstrom | AP, falls kein PoE; Clients und Haushaltsgeräte | Kein zugesicherter USV-Betrieb |

## 5. Logical Topology

### 5.1 Zonen und Schnittstellen

| Zone/Schnittstelle | Funktion | Adressvergabe | Vertrauensniveau |
|---|---|---|---|
| Internet/DSL | Externes Telekom-Netz | Provider | nicht vertrauenswürdig |
| Speedport-LAN / OPNsense-WAN | Transitnetz zwischen den Routern | Speedport-DHCP-Reservierung oder statische, konfliktfreie Adresse | Transit, nicht für produktive Clients |
| OPNsense-LAN | Internes Basisnetz für Migration und erstes Product Increment | OPNsense-DHCP | intern; noch unsegmentiert |
| Management (vorbereitet) | Administration von Firewall, Switch, AP, USV und Infrastruktur | später eigenes Subnetz/VLAN | hoch privilegiert |
| Trusted/Home (vorbereitet) | Vertrauenswürdige private Clients | später eigenes Subnetz/VLAN | intern |
| Work (vorbereitet) | Homeoffice-Geräte | später eigenes Subnetz/VLAN | intern, isolierbar |
| Gaming/Media (vorbereitet) | PS5, Sky und ähnliche Geräte | später eigenes Subnetz/VLAN | eingeschränkt |
| IoT (vorbereitet) | Smart-Home-/IoT-Geräte | später eigenes Subnetz/VLAN | gering |
| Guest (vorbereitet) | Gäste-WLAN | später eigenes Subnetz/VLAN | untrusted, Internet-only |
| Server/Services (vorbereitet) | HDC-OS, Storage und lokale Dienste | später eigenes Subnetz/VLAN | dienstabhängig |
| Cameras (vorbereitet) | Zukünftige Kameras | später eigenes Subnetz/VLAN | stark eingeschränkt |
| VPN (vorbereitet) | Authentifizierter Fernzugriff oder definierte ausgehende Policy Routes | eigenes Tunnelnetz | regelbasiert |

Zonennamen sind Funktionsbezeichnungen der Vorbereitung, noch keine Freigabe
konkreter VLAN-Namen, IDs oder Subnetze.

### 5.2 WAN, Routing und NAT

- OPNsense-WAN wird an einen LAN-Port des Speedport angeschlossen.
- Speedport-LAN und OPNsense-LAN müssen unterschiedliche, nicht überlappende
  RFC1918-Netze verwenden.
- OPNsense verwendet den Speedport als IPv4-Default-Gateway.
- Interne Clients verwenden ausschließlich OPNsense als Default-Gateway.
- OPNsense führt Source NAT für interne Netze auf seine WAN-Adresse aus.
- Der Speedport führt Source NAT von seinem LAN zum Telekom-Anschluss aus.
- Es wird kein produktives Routing zwischen Speedport-Clients und OPNsense-LAN
  vorausgesetzt.
- Für eingehendes VPN oder andere veröffentlichte Dienste ist eine gezielte
  Speedport-Weiterleitung auf OPNsense und dort eine zweite, eng begrenzte Regel
  erforderlich. Exposed Host ist nicht Standard und bedarf einer separaten
  Sicherheitsentscheidung.
- IPv6 wird erst nach Bestätigung von Präfixdelegation, Firewall-Verhalten und
  Zielsegmenten produktiv aktiviert. Bis dahin darf es nicht unbeabsichtigt die
  IPv4-Sicherheitsgrenze umgehen.

### 5.3 DHCP

- Im Speedport-Transitnetz vergibt der Speedport nur die OPNsense-WAN-
  Konfiguration; eine feste DHCP-Reservierung ist gegenüber einer unkoordinierten
  dynamischen Adresse vorzuziehen.
- Im internen Basisnetz ist ausschließlich OPNsense DHCP-Server.
- Der Managed Switch und der AP dürfen im Zielbetrieb keinen konkurrierenden
  DHCP-Server betreiben.
- Spätere VLANs erhalten getrennte DHCP-Bereiche auf OPNsense.
- Infrastrukturkomponenten erhalten dokumentierte Reservierungen oder statische
  Adressen außerhalb dynamischer Pools.

### 5.4 DNS

- Interne Clients verwenden OPNsense als DNS-Endpunkt.
- OPNsense stellt lokale Namen bereit bzw. leitet rekursiv oder an ausdrücklich
  konfigurierte Resolver weiter.
- DNS-Verhalten, Upstream-Resolver, DNSSEC und Blocklisten werden in einem
  Detaildesign festgelegt; v0.1 setzt keinen externen Anbieter voraus.
- Direkter Client-DNS-Verkehr kann später segmentbezogen eingeschränkt werden.
  Eine solche Regel wird erst nach Kompatibilitätstests aktiviert.

### 5.5 VLAN-Vorbereitung

- Firewall, Managed Switch und Access Point müssen IEEE 802.1Q unterstützen.
- Der Link OPNsense–Switch muss als VLAN-Trunk nutzbar sein.
- Der Link Switch–AP muss mehrere getaggte Client-VLANs und ein eindeutig
  bestimmtes Managementnetz transportieren können.
- Clientports werden später als Access-Ports einem Segment zugeordnet.
- Das Basis-LAN bleibt während des ersten Product Increments untagged bzw. als
  explizit dokumentiertes natives Migrationsnetz bestehen.
- VLAN-IDs, Subnetze, SSID-Zuordnung und Inter-VLAN-Regeln werden durch einen
  Folge-ADR oder eine Work Order freigegeben. Ihre Einführung erfordert keinen
  Austausch der in diesem Design beschafften Kernkomponenten.

### 5.6 VPN-Integrationspunkt

OPNsense ist der vorgesehene VPN-Endpunkt für authentifizierten Fernzugriff und
der mögliche Policy-Routing-Punkt für einen externen VPN-Anbieter. Homeoffice-
Verkehr wird nicht pauschal über einen Consumer-VPN geleitet. Protokoll, Port,
Authentisierung, erlaubte Zielnetze und Notfallzugang bleiben Folgeentscheidungen.

## 6. Security Model

### 6.1 Sicherheitsgrenze

Die primäre Sicherheitsgrenze liegt auf OPNsense. Das Speedport-Transitnetz gilt
nicht als internes Clientnetz. Der Managed Switch und der AP erweitern nur Netze,
die OPNsense kontrolliert; sie schaffen keinen alternativen Internetpfad.

### 6.2 Geräte am Speedport

Im Ziel-Regelbetrieb dürfen direkt am Speedport verbleiben:

- OPNsense-WAN,
- die integrierte Telefoniefunktion und erforderliche Telefonie-Endgeräte,
- ein zeitlich begrenzter, dokumentierter Notfall-Adminclient nur während
  Störung oder Rollback.

Nicht dauerhaft am Speedport verbleiben: Laptop, PS5, Sky Box, HDC-OS-Systeme,
IoT-, Gäste- oder sonstige produktive Clients. Das Speedport-WLAN wird nach
erfolgreicher WLAN-Migration deaktiviert oder ausschließlich als dokumentierter,
nicht regulär verwendeter Break-Glass-Zugang betrieben. Welche Variante gilt,
ist vor Abschluss der Migration festzulegen.

### 6.3 Geräte hinter der Firewall

Alle produktiven kabelgebundenen und drahtlosen Clients, Managementoberflächen,
HDC-OS-Systeme, Server, Storage, Access Points und zukünftigen
Infrastrukturkomponenten werden hinter OPNsense betrieben.

### 6.4 Regelprinzipien

- WAN-seitig gilt: eingehend verweigern, sofern nicht ausdrücklich freigegeben.
- Ausgehend gilt im Basisnetz zunächst ein minimaler, protokollierter
  Internetzugang, der für das Product Increment erforderlich ist.
- Nach Segmentierung gilt zwischen Zonen Default-deny; Freigaben werden nach
  Quelle, Ziel, Dienst und Zweck dokumentiert.
- Managementzugriff ist auf definierte Admin-Geräte und Managementnetze begrenzt.
- Guest erhält ausschließlich Internetzugang und keinen Zugriff auf interne Netze.
- IoT, Gaming/Media und Cameras erhalten nur erforderliche interne Ziele.
- HDC-OS-Dienste erhalten Least-Privilege-Zugriff und bleiben lokal betreibbar.
- Konfigurationsänderungen, Backups und Wiederherstellungen werden
  nachvollziehbar dokumentiert.
- UPnP ist kein impliziter Bestandteil des Designs; eine Aktivierung erfordert
  eine begründete Folgeentscheidung und begrenzte Geltung.

### 6.5 Zukunftsfähige Segmentierung

Die vorbereiteten Zonen Management, Trusted/Home, Work, Gaming/Media, IoT,
Guest, Server/Services, Cameras und VPN verhindern eine Sackgasse. Ihre konkrete
Aktivierung folgt risikobasiert. Bis dahin stellt das unsegmentierte Basis-LAN
einen bewusst zeitlich begrenzten Migrationszustand dar, nicht den langfristigen
Sicherheitsendzustand.

## 7. Migration Plan

Jeder Schritt ist einzeln validierbar und reversibel. Vor jedem Eingriff werden
Ist-Fotos, Portbelegung, Konfiguration und Zeitpunkt dokumentiert. Änderungen
erfolgen in einem angekündigten Wartungsfenster.

### Schritt 1 – Ist-Zustand verifizieren und Baseline sichern

**Ziel:** Vollständige, belastbare Ausgangsbasis für Verkabelung, Adressen,
Telefonie und Internetfunktion.

**Voraussetzungen:** Zugang zu Speedport, Switch und Clients; keine Änderung der
Verkabelung.

**Durchführung:** Geräte, Ports, Kabel, SSIDs, Speedport-LAN/DHCP, Telefonie-
Anschlussart, Linkrate und Steckdosen erfassen. Speedport-Konfiguration sichern,
soweit technisch möglich. Internet, DNS und Telefonie als Baseline testen.

**Validierung:** Inventarliste ist vollständig; Internet und ein eingehender sowie
ausgehender Telefonietest funktionieren; Sicherung ist lesbar.

**Rollback:** Keine Betriebsänderung. Fehlerhafte Dokumentation wird verworfen
und aus der unveränderten Umgebung neu erhoben.

### Schritt 2 – Rack und getrennte Stromdomäne bereitstellen

**Ziel:** Sichere physische Aufnahme und Stromversorgung der Rack-Komponenten.

**Voraussetzungen:** PC-0002 und PC-0005 erfüllen Abschnitt 9; Standort,
Steckdose, Last, Belüftung und Schutzleiter sind geprüft.

**Durchführung:** Rack und Rack-USV ohne Netzwerkumschaltung installieren;
Firewall und Managed Switch montieren, beschriften und zunächst ausgeschaltet
bzw. ohne produktive Verbindung prüfen.

**Validierung:** Rack ist standsicher und zugänglich; USV-Selbsttest und
Lastprüfung sind erfolgreich; Router-USV bleibt unverändert.

**Rollback:** Rack-Komponenten ausschalten und vom Netz trennen; bestehender
Netzwerkpfad und Router-USV bleiben unberührt.

### Schritt 3 – OPNsense offline grundkonfigurieren

**Ziel:** Sichere, konfliktfreie Firewall-Basiskonfiguration.

**Voraussetzungen:** PC-0003 erfüllt Abschnitt 9; bestätigtes Speedport-Subnetz;
gewähltes, nicht überlappendes internes Basisnetz; lokaler Konsolenzugang.

**Durchführung:** WAN/LAN eindeutig zuordnen; Adminzugang absichern; WAN per
Reservierung oder konfliktfreier Adresse vorbereiten; LAN, DHCP, DNS, NAT und
minimale Ausgangsregel konfigurieren; Konfigurationsbackup erzeugen. IPv6 bleibt
bis zur Klärung kontrolliert deaktiviert oder vollständig gefiltert.

**Validierung:** Ein direkt am LAN angeschlossener Test-Laptop erhält DHCP/DNS,
erreicht die OPNsense-Administration und kann keine WAN-seitige Administration
öffnen. Konfigurationsbackup lässt sich prüfen.

**Rollback:** OPNsense ausschalten; keine produktive Verkabelung wurde geändert.
Bei Bedarf Werkszustand herstellen und gesichertes Basisprofil neu einspielen.

### Schritt 4 – Managed Switch offline vorbereiten

**Ziel:** Kontrollierter interner Verteiler ohne konkurrierende Dienste.

**Voraussetzungen:** PC-0004 erfüllt Abschnitt 9; lokaler Adminzugang; definierte
Portrollen.

**Durchführung:** Managementzugang absichern; DHCP-Serverfunktionen deaktivieren;
Ports für OPNsense-LAN, Test-Laptop, AP, PS5, Sky und HDC-OS dokumentieren.
VLAN-Fähigkeit prüfen, aber Basis-LAN zunächst unsegmentiert betreiben.

**Validierung:** Verwaltung ist nur intern erreichbar; Portstatus und Linkraten
sind sichtbar; Test-Laptop kommuniziert über OPNsense-LAN.

**Rollback:** Switch vom Netz trennen; Test-Laptop wieder direkt mit OPNsense-LAN
verbinden oder bestehende Umgebung unverändert weiterbetreiben.

### Schritt 5 – OPNsense-WAN hinter dem Speedport aktivieren

**Ziel:** End-to-End-Internetpfad durch beide Router herstellen, ohne bestehende
Clients umzuschalten.

**Voraussetzungen:** Schritte 1–4 erfolgreich; Wartungsfenster; beschriftete
Kabel; Zugriff auf beide Router.

**Durchführung:** Vorhandenes Kabel im Arbeitszimmer temporär vom Netgear Switch
an OPNsense-WAN anschließen. OPNsense-LAN mit Managed Switch verbinden. Einen
Test-Laptop am Managed Switch anschließen. Sonstige Bestandsclients bleiben für
diesen Test getrennt oder nutzen vorübergehend dokumentiertes Speedport-WLAN.

**Validierung:** OPNsense-WAN erhält die erwartete Adresse und erreicht den
Speedport; Laptop erhält OPNsense-DHCP/DNS, erreicht Internet und zeigt den
erwarteten Pfad; unerwarteter WAN-Adminzugriff ist blockiert; Telefonietest ist
erfolgreich.

**Rollback:** Vorhandenes Kabel von OPNsense-WAN lösen und wieder am Netgear
Switch anschließen. Ursprüngliche Clientverkabelung wiederherstellen. OPNsense
und Managed Switch aus dem Produktivpfad nehmen.

### Schritt 6 – Kabelgebundene Clients migrieren

**Ziel:** Laptop, PS5 und netzwerkgebundene Sky Box hinter OPNsense betreiben.

**Voraussetzungen:** Schritt 5 über ein vereinbartes Beobachtungsfenster stabil;
ausreichende Switch-Ports; dokumentierte Ausgangsbelegung.

**Durchführung:** Clients einzeln auf den Managed Switch umstecken. Nach jedem
Gerät DHCP-Lease, DNS, Internet und gerätespezifische Funktion prüfen.

**Validierung:** Laptop erfüllt das LAN-Erfolgskriterium; PS5-Netzwerktest und
Sky-Funktion sind erfolgreich; kein produktiver kabelgebundener Client hängt
direkt am Speedport.

**Rollback:** Betroffenes Gerät an den dokumentierten ursprünglichen Netgear-Port
zurückstecken. Bei systemischem Fehler vollständigen Rollback aus Schritt 5
ausführen.

### Schritt 7 – WLAN hinter OPNsense bereitstellen

**Ziel:** Laptop und spätere WLAN-Clients nutzen einen internen Access Point.

**Voraussetzungen:** AP erfüllt Abschnitt 9; Standort und Stromversorgung sind
geklärt; sichere Admin-Zugangsdaten und SSID-Konzept liegen vor.

**Durchführung:** AP am Managed Switch anschließen, Management absichern, interne
SSID mit moderner Verschlüsselung bereitstellen und Laptop verbinden. Funk- und
Roaming-Abdeckung in den relevanten Räumen messen.

**Validierung:** Laptop erfüllt das WLAN-Erfolgskriterium; OPNsense vergibt DHCP
und DNS; interne Verwaltungsoberflächen sind nicht aus einem unzulässigen Netz
erreichbar; Telefonie funktioniert; Abdeckung erfüllt die noch festzulegenden
Messkriterien.

**Rollback:** Interne SSID deaktivieren und AP trennen. Laptop nutzt für das
Wartungsfenster wieder die dokumentierte vorherige Verbindung; falls nötig
Rollback aus Schritt 5.

### Schritt 8 – Zielbetrieb konsolidieren

**Ziel:** Speedport-Bypässe entfernen und den stabilen Basisbetrieb dokumentieren.

**Voraussetzungen:** LAN und WLAN über ein festgelegtes Beobachtungsfenster
stabil; alle produktiven Clients inventarisiert; Break-Glass-Entscheidung
getroffen.

**Durchführung:** Speedport-WLAN deaktivieren oder als dokumentierten
Break-Glass-Zugang isolieren; Netgear Switch außer Betrieb nehmen oder seine
freigegebene nachgelagerte Rolle dokumentieren; Backups von OPNsense, Switch und
AP erstellen; Betriebs- und Wiederanlaufreihenfolge dokumentieren.

**Validierung:** Am Speedport befindet sich regulär nur OPNsense-WAN plus
Telefonie; alle produktiven Clients liegen hinter OPNsense; Neustarttest und
Strompfadprüfung sind erfolgreich; Laptop besteht LAN- und WLAN-Test.

**Rollback:** Vorherige Speedport-WLAN-Konfiguration wieder aktivieren und bei
Bedarf ursprünglichen Netgear-Pfad gemäß Schritt 5 wiederherstellen. Gesicherte
Konfigurationen zurückspielen.

### Schritt 9 – VLAN-Segmentierung einführen

**Ziel:** Vorbereitete Sicherheitszonen ohne Austausch der Kernarchitektur
aktivieren.

**Voraussetzungen:** Basisbetrieb abgenommen; VLAN-IDs, Subnetze, SSIDs,
Gerätezuordnung und Regelmatrix durch Folge-ADR/Work Order freigegeben;
Konfigurationsbackups und lokaler Konsolenzugang vorhanden.

**Durchführung:** Zonen zunächst auf OPNsense anlegen, Trunks auf Switch und AP
aktivieren, danach Clients segmentweise migrieren. Managementzugang zuletzt
verschärfen, damit kein Lockout entsteht.

**Validierung:** Pro Zone DHCP, DNS, Internet und erlaubte interne Dienste testen;
verbotene Inter-Zonen-Pfade negativ testen; LAN- und WLAN-Erfolgskriterium bleibt
erfüllt.

**Rollback:** Betroffene Ports/SSID auf das dokumentierte Basis-LAN zurücksetzen,
neue VLAN-Regeln deaktivieren und letzte bekannte Konfigurationen wiederherstellen.

## 8. Risks

| ID | Risiko | Auswirkung | Eintritt | Behandlung / Nachweis |
|---|---|---|---|---|
| R-01 | Double NAT beeinträchtigt eingehende VPNs, Portfreigaben, Spiele oder spezielle Protokolle. | Mittel bis hoch | Mittel | Ausgehenden Basisbetrieb zuerst testen; eingehende Dienste doppelt und minimal weiterleiten; Exposed Host nur per Folgeentscheidung. |
| R-02 | Speedport- und OPNsense-Netz überlappen. | Kein Routing oder schwer diagnostizierbare Fehler | Mittel | Subnetze vor Schritt 3 inventarisieren und konfliktfrei festlegen. |
| R-03 | IPv6 umgeht das beabsichtigte IPv4-Modell oder funktioniert hinter dem Speedport nicht wie erwartet. | Sicherheitslücke oder Konnektivitätsfehler | Mittel | IPv6 nicht implizit aktivieren; Präfixdelegation und Regeln separat testen und freigeben. |
| R-04 | Das einzige Kabel oder seine Linkqualität ist unzureichend. | Gesamter interner Internetpfad fällt aus oder ist langsam | Mittel | Kategorie, Länge, Linkrate und Fehlerzähler vor Umschaltung prüfen; Ersatzpatchkabel nur an Endpunkten bereithalten. |
| R-05 | Firewall-Ausfall trennt langfristig alle produktiven Clients vom Internet. | Hohe Verfügbarkeitseinbuße | Mittel | Getesteter 15-Minuten-Rollback auf Netgear/Speedport, Konfigurationsbackup und Konsolenzugang. |
| R-06 | Rack-USV ist unterdimensioniert oder inkompatibel. | Ungeplanter Shutdown, Brand-/Betriebsrisiko | Mittel | PC-0005 gegen Last, Anschlüsse, Laufzeit, Shutdown und Rack-Kompatibilität prüfen. |
| R-07 | Router-USV und Telefonie-Last sind nicht vollständig erfasst. | Telefonie fällt bei Stromausfall aus | Mittel | PC-0001-Zweck, Lasten und Telefonie-Anschlussart bestätigen; separaten Telefonietest durchführen. |
| R-08 | AP-Position deckt die ca. 88 m² mit Trockenbau- und Ziegelwänden nicht ausreichend ab. | WLAN-Erfolgskriterium nur lokal erfüllt | Hoch | Funkmessung am vorgesehenen Standort; Erweiterbarkeit für zweiten AP vorsehen. |
| R-09 | AP ohne PoE benötigt am optimalen Standort eine freie Steckdose. | Standort nicht realisierbar | Mittel | PoE-Fähigkeit/PoE-Budget in PC-0004 prüfen oder Steckdose vor Standortfreigabe bestätigen. |
| R-10 | PoE-Auslegung kollidiert mit der Interpretation „Rack-USV nur für Rack-Komponenten“. | Governance-Konflikt | Mittel | Interpretation vor PC-0004/PC-0005 ausdrücklich bestätigen. |
| R-11 | Unmanaged Netgear Switch wird versehentlich in einem Trunk oder über Zonengrenzen eingesetzt. | VLAN-Leak oder Fehlfunktion | Mittel | Nicht für Trunks/Management verwenden; Zielrolle beschriften oder außer Betrieb nehmen. |
| R-12 | Speedport-WLAN bleibt unkontrollierter produktiver Bypass. | Clients umgehen OPNsense | Hoch | Nach WLAN-Migration deaktivieren oder Break-Glass-Betrieb ausdrücklich begrenzen und überwachen. |
| R-13 | Telefonie wird durch Speedport-Neustart oder Fehlkonfiguration beeinträchtigt. | Business Goal verletzt | Niedrig bis mittel | Telefoniekonfiguration nicht ändern; nach jedem WAN-/Stromschritt testen; Speedport-Backup vorhalten. |
| R-14 | OPNsense-, Switch- oder AP-Management wird ausgesperrt. | Betrieb nicht administrierbar | Mittel | Lokale Konsole, dokumentierte Managementports, gestufte Regeln und Backups. |
| R-15 | Geräte benötigen UPnP, Multicast oder Discovery über spätere Segmente. | PS5/Sky/IoT teilweise funktionslos | Mittel | Basisbetrieb erfassen; segmentbezogene Ausnahmen nur nach konkretem Test und Least Privilege. |
| R-16 | HDC-OS-Dienste werden zu früh als kritischer Teil von DHCP/DNS/Internetpfad eingeführt. | Ausfall eines Dienstes legt Netzwerk lahm | Mittel | Basisfunktionen zunächst auf OPNsense lokal halten; HDC-OS integriert Monitoring und Dokumentation additiv. |
| R-17 | Thermik, Geräusch, Platz oder Rollbarkeit des Racks sind unzureichend. | Wohnraumbetrieb oder Hardwarezuverlässigkeit beeinträchtigt | Mittel | PC-0002 gegen Standort, Luftstrom, Last, Kabelzug und Wartungszugang prüfen. |
| R-18 | Konfigurationen sind nicht gesichert oder Backups nicht wiederherstellbar. | Rollback scheitert | Mittel | Vor jedem Schritt versioniertes Export- und Restore-Verfahren testen. |
| R-19 | Unvollständiges Geräteinventar lässt einen Client direkt am Speedport zurück. | Sicherheitsmodell unvollständig | Mittel | Lease-, WLAN- und Portlisten vor Abschluss abgleichen. |
| R-20 | Der 15-Minuten-Rollback ist praktisch nicht erreichbar. | Verfügbarkeitsziel wird verfehlt | Mittel | Rückbau physisch proben, Kabel beschriften und Zeit messen. |

## 9. Procurement Architecture Gates

Jeder Kandidat wird zusätzlich zu seinen Case-Anforderungen gegen diese
Architekturgates bewertet. `PASS` bedeutet architekturkompatibel, nicht
automatisch kaufwürdig.

### PC-0002 – Rollbarer Netzwerkschrank

- Nimmt Firewall, Managed Switch, Rack-USV und geplante HDC-OS-
  Rack-Komponenten mit dokumentierter Reserve auf.
- Trägt Gesamtgewicht und erlaubt sicheren, rollbaren und standsicheren Betrieb.
- Ermöglicht Belüftung, Wartungszugang, Zugentlastung und klare WAN/LAN-Trennung.
- Passt an den bestätigten Standort und benötigt keine neue Wohnungsverkabelung.

### PC-0003 – Firewall Appliance

- Unterstützt OPNsense und mindestens getrennte physische WAN-/LAN-Schnittstellen.
- Bewältigt die bestätigte DSL-Rate mit Firewall, NAT und vorgesehenem VPN mit
  Reserve.
- Unterstützt 802.1Q, mehrere interne Netze, lokale Konsole und
  Konfigurationsbackup/-restore.
- Ist dauerhaft lokal und ohne Hersteller-Cloud betreibbar.
- Ist mechanisch und elektrisch mit Rack und Rack-USV kompatibel.

### PC-0004 – Managed Switch

- Unterstützt 802.1Q-Trunks, Access-Ports, sicheres lokales Management und
  ausreichende Portreserve.
- Bietet ausreichende Uplink-/Portleistung für Firewall, AP, Laptop, PS5, Sky,
  HDC-OS und geplante Erweiterungen.
- Falls PoE vorgesehen ist: Standard, Gesamtbudget und Einzelportleistung decken
  AP und Reserve; PoE-Verhalten an USV ist dokumentiert.
- Ist ohne Cloud-Zwang betreibbar und mit Rack/Rack-USV kompatibel.

### PC-0005 – Rack-USV

- Versorgt ausschließlich die definierten direkten Rack-Komponenten.
- Deckt bestätigte Dauer-, Spitzen- und Anlaufleistung mit Reserve.
- Erreicht die festzulegende Mindestlaufzeit und unterstützt den vorgesehenen
  kontrollierten Shutdown bzw. Alarmweg.
- Passt mechanisch in das Rack; Steckertypen, Schutz, Batteriewechsel,
  Wärmeabgabe und lokales Management sind kompatibel.
- Ist unabhängig von der Router-USV; kein standortübergreifendes Stromkabel wird
  vorausgesetzt.

### Querschnittsgate für PC-0002 bis PC-0005

Kein Kandidat darf einen Hersteller-Cloud-Zwang, neue Wohnungsverkabelung, einen
Bypass um OPNsense, eine Änderung der Speedport-Telefonie oder den Austausch
einer Kernkomponente allein für die spätere VLAN-/VPN-Einführung erzwingen.

## 10. Open Questions and Assumptions Register

### 10.1 Offene Fragen

| ID | Offene Frage | Blockiert spätestens |
|---|---|---|
| OQ-01 | Welches IPv4-Subnetz und welcher DHCP-Bereich werden aktuell am Speedport verwendet? | Migration Schritt 3 |
| OQ-02 | Welches interne RFC1918-Basisnetz, welcher DHCP-Pool und welches Namensschema werden freigegeben? | Migration Schritt 3 |
| OQ-03 | Unterstützt bzw. benötigt der Speedport eine feste DHCP-Reservierung für OPNsense-WAN, und wie wird sie konfiguriert? | Migration Schritt 5 |
| OQ-04 | Welche IPv6-Funktionen und Präfixdelegation stellt der Telekom-/Speedport-Anschluss bereit? | Produktive IPv6-Aktivierung |
| OQ-05 | Wie sind Telefonie-Endgeräte angeschlossen und welche davon benötigen bei Stromausfall eigene Versorgung? | PC-0001-Abnahme / Schritt 1 |
| OQ-06 | Modell, Portzahl, Linkrate und aktuelle Belegung des Netgear Switch? | Schritt 1 |
| OQ-07 | Ist die Sky Box per LAN, WLAN oder gar nicht verbunden, und welche Netzwerkfunktionen benötigt sie? | Schritt 6 |
| OQ-08 | Welche Geräte und SSIDs nutzen aktuell direkt den Speedport? | Schritt 1 und 8 |
| OQ-09 | Kategorie, Länge, Endpunkte und gemessene Linkqualität des vorhandenen Kabels? | Schritt 5 |
| OQ-10 | Exakter Rackstandort, Steckdosen, Tragfähigkeit, Maße, Luftstrom, Geräusch- und Wärmegrenzen? | PC-0002/PC-0005 |
| OQ-11 | Welche Firewall-, Switch- und AP-Modelle bzw. Leistungsdaten werden in den Procurement Cases bewertet? | Procurement-Freigabe |
| OQ-12 | Wird der AP per PoE oder lokal versorgt, und gilt PoE aus dem USV-versorgten Rack-Switch als zulässig? | PC-0004/PC-0005 / Schritt 7 |
| OQ-13 | Wo kann der AP ohne neue Wohnungsverkabelung aufgestellt werden, und welche Messwerte definieren ausreichende WLAN-Abdeckung? | Schritt 7 |
| OQ-14 | Wird ein oder werden mehrere APs für ca. 88 m² und die Wandtypen benötigt? | AP-Beschaffung |
| OQ-15 | Wird das Speedport-WLAN im Zielbetrieb deaktiviert oder als Break-Glass-Zugang behalten? | Schritt 8 |
| OQ-16 | Welche Mindest-USV-Laufzeit, Maximallast und Shutdown-Reihenfolge gelten je Stromdomäne? | PC-0001/PC-0005 |
| OQ-17 | Welche HDC-OS-Komponenten werden in Horizon 1 physisch im Rack betrieben? | PC-0002/PC-0005 |
| OQ-18 | Welche VLAN-IDs, Subnetze, SSIDs, Gerätezuordnungen und Inter-Zonen-Regeln werden freigegeben? | Schritt 9 |
| OQ-19 | Welches VPN-Szenario ist zuerst umzusetzen: Fernzugriff, Site-to-Site oder ausgehendes Policy Routing? | VPN-Umsetzung |
| OQ-20 | Sind eingehende Dienste erforderlich; falls ja, genügen Portweiterleitungen oder wird eine andere Speedport-Betriebsart benötigt? | Veröffentlichung/VPN |
| OQ-21 | Welches Beobachtungsfenster definiert Stabilität nach den Schritten 5, 7 und 8? | jeweilige Abnahme |
| OQ-22 | Welche Person/Rolle darf Infrastruktur administrieren, und welches Notfallzugangsverfahren gilt? | Schritt 3/8 |
| OQ-23 | Welche maximale Ausfallzeit gilt verbindlich: die bekannte Zielgröße von 15 Minuten oder ein anderer Wert? | Migrationsfreigabe |
| OQ-24 | Soll der Netgear Switch nach Migration entfernt, als Ersatzteil gelagert oder unsegmentiert nachgelagert weiterverwendet werden? | Schritt 8 |
| OQ-25 | Welche Anforderungen gelten für DNS-Upstream, DNSSEC, Filterung und lokale Domain? | DNS-Detaildesign |

### 10.2 Gekennzeichnete Annahmen

| ID | Annahme für v0.1 | Konsequenz bei Widerlegung |
|---|---|---|
| A-01 | Das vorhandene Ethernet-Kabel kann eine stabile Verbindung vom Speedport zum OPNsense-WAN herstellen. | Zieltopologie ist unter „keine neuen Kabel“ nicht umsetzbar; Randbedingung oder Übertragungsweg muss per neuer Architekturentscheidung geändert werden. |
| A-02 | Der Speedport kann OPNsense als normalen LAN-Client mit Internetzugang versorgen. | Speedport-Konfiguration oder Anschlussfähigkeit muss geklärt werden; Schritt 5 blockiert. |
| A-03 | Die bestehende Telefonie hängt nicht davon ab, dass Clients oder der Netgear Switch direkt am Speedport-LAN verbleiben. | Betroffene Telefoniekomponente bleibt als ausdrücklich begründete Ausnahme am Speedport oder benötigt ein Folge-Design. |
| A-04 | Im Arbeitszimmer kann LAN-seitig ohne neue Wohnungsverkabelung zwischen Firewall, Switch, Rack-Geräten und mindestens einem AP-Standort verbunden werden. | AP-Standort, lokale Patchführung oder WLAN-Ziel muss neu entschieden werden. |
| A-05 | Ein unsegmentiertes Basis-LAN ist für das zeitlich begrenzte Product Increment akzeptabel. | VLAN-Detaildesign muss vor der ersten produktiven Clientmigration abgeschlossen werden. |
| A-06 | Double NAT ist für ausgehenden Internetzugang des ersten Laptops funktionsfähig. | Speedport-Betriebsart oder Routingmodell benötigt einen ADR; v0.1-Erfolgspfad kann nicht abgenommen werden. |

## 11. Acceptance and Review Matrix

| Akzeptanzkriterium | Nachweis in diesem Dokument |
|---|---|
| IST-Zustand vollständig dokumentiert | Abschnitt 2; unbekannte Werte explizit in Abschnitt 10 |
| Zielarchitektur vollständig dokumentiert | Abschnitt 3 |
| Physische Topologie vollständig dokumentiert | Abschnitt 4 |
| Logische Topologie vollständig dokumentiert | Abschnitt 5 |
| Sicherheitsmodell dokumentiert | Abschnitt 6 |
| Migrationsplan vollständig vorhanden | Abschnitt 7 |
| Rollback für jeden Migrationsschritt definiert | Jeder Schritt in Abschnitt 7 |
| Alle bekannten Risiken dokumentiert | Abschnitt 8 |
| Alle offenen Fragen dokumentiert | Abschnitt 10 |
| PC-0002 bis PC-0005 bewertbar | Abschnitt 9 |
| Laptop per LAN oder WLAN sicher im Internet | Abschnitte 1.3, 3.3 und Validierungen in 7 |

Ein Review dieses Dokuments beantwortet ausschließlich:

1. Wurde jeder Deliverable vollständig erstellt?
2. Sind alle Acceptance Criteria erfüllt?
3. Enthält das Dokument Widersprüche?
4. Sind Risiken oder Annahmen unvollständig?

Neue Architekturideen sind nicht Teil des Reviews. Nach Annahme erfolgen
Designänderungen ausschließlich über neue Work Orders oder ADRs.

## 12. Abnahmezustand

Version 0.1 ist **Accepted**. Das Review von WO-0032 wurde am 31.07.2026 durch
den Lead Architect ohne offene Beanstandung abgeschlossen. Blockierende offene
Fragen bleiben vor dem jeweils in Abschnitt 10 genannten Umsetzungsschritt zu
klären; sie ändern den angenommenen Architekturstatus nicht.
