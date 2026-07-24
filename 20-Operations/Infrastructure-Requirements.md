---
document: Infrastructure-Requirements.md
version: 1.0
status: Draft
owner: Project Owner
reviewed_by: ""
last_review: ""
classification: Workspace
---

# Infrastructure Requirements

## Zweck und Geltungsbereich

Dieses Dokument beschreibt die fachlichen und technischen Anforderungen an die
HDC-OS-Infrastruktur für M2.3. Es beschreibt ausschließlich, **was** die
Infrastruktur leisten und berücksichtigen muss.

Es beschreibt ausdrücklich nicht:

- Netzwerktopologie oder Racklayout
- IP-Adressierung, VLAN-IDs, DNS oder DHCP
- Firewall-Regeln oder OPNsense-Konfiguration
- konkrete Gerätepositionen jenseits des bekannten Ist-Zustands
- eine technische Implementierung

Die Begriffe `Ist-Zustand`, `Anforderung` und `Offene Frage` werden getrennt
verwendet. Eine offene Frage ist keine implizite Entscheidung.

## 1. Physical Environment

### Bekannter Ist-Zustand

- Die Wohnung umfasst ungefähr 88 m².
- Das Arbeitszimmer enthält den bestehenden Switch, den Laptop des Project
  Owners und die PS5.
- Der Router steht außerhalb des Arbeitszimmers nahe der Eingangstür.
- Zwischen den relevanten Bereichen bestehen Trockenbau- und Ziegelwände.
- Die PS5 ist im Arbeitszimmer dauerhaft per LAN angebunden.
- Eine vollständige Vermessung der Räume und Kabelführungen liegt noch nicht vor.

### Anforderungen

- Die Infrastruktur muss in der vorhandenen Wohnumgebung betrieben werden können.
- WLAN muss die gesamte Wohnung zuverlässig versorgen.
- Kabel müssen sicher, wartbar und ohne unnötige Einschränkung der Wohnnutzung
  geführt werden können.
- Stromversorgung und Steckdosen müssen für Router, Netzwerkkomponenten,
  Access Points, Rack-Komponenten und USV-Anforderungen ausreichen.
- Die Infrastruktur darf keine nicht dokumentierten baulichen Eingriffe
  voraussetzen.
- Geräuschentwicklung, Wärmeentwicklung und Platzbedarf müssen für den
  Wohnraumbetrieb akzeptabel sein.

### Offene Fragen

- Wie groß sind die einzelnen Räume und die relevanten Wandabstände genau?
- Wo befinden sich Routerstandort, geplanter Rackstandort und alle benötigten
  Steckdosen präzise?
- Wie viele freie Steckdosen sind an jedem Standort verfügbar?
- Welche Kabelführungen sind vorhanden und welche räumlichen Einschränkungen
  gelten für neue Leitungen?
- Gibt es Vorgaben zu maximaler Geräuschentwicklung, Abwärme oder sichtbarer
  Installation?

## 2. Connected Devices

Die folgende Inventarisierung beschreibt Geräte und Anforderungen, aber keine
Netzwerktopologie.

| Gerät oder Gerätegruppe | Verbindung | Mobilität | Kritikalität | Permanenter Betrieb | Erweiterung |
|---|---|---|---|---|---|
| Speedport Smart 4 | unbekannt | stationär | hoch für Internetzugang | ja | Router bleibt Bestandteil des Ist-Zustands |
| dedizierte Firewall-Plattform | kabelgebunden erforderlich | stationär | hoch | ja | Procurement PC-0003 |
| Managed Switch | kabelgebunden erforderlich | stationär | hoch | ja | Procurement PC-0004; Portreserve erforderlich |
| bestehender Switch im Arbeitszimmer | LAN | stationär | mittel | derzeit ja | genaue Rolle und Weiterverwendung offen |
| Laptop des Project Owners | LAN oder WLAN | mobil | hoch | nein | weitere Arbeitsgeräte möglich |
| zwei bis drei Homeoffice-Laptops oder Macs | LAN oder WLAN | mobil | hoch während Homeoffice | nein | weitere Clients möglich |
| PS5 | LAN | stationär | mittel | nein | keine konkrete Erweiterung festgelegt |
| Access Point(s) | kabelgebunden erforderlich | stationär | hoch für WLAN | ja | Anzahl und Modell offen |
| NAS/Storage | kabelgebunden erforderlich | stationär | hoch für Daten | voraussichtlich ja | Procurement und Kapazität offen |
| Monitoring-Komponenten | LAN oder WLAN | stationär | mittel bis hoch | abhängig vom Dienst | Sensoren und Raumwerte möglich |
| Kameras | LAN oder WLAN | stationär | offen | offen | zukünftige Erweiterung |
| weitere Clients und IoT-Geräte | LAN oder WLAN | offen | offen | offen | zukünftige Erweiterung |

### Inventarisierungsanforderungen

- Für jedes dauerhaft oder regelmäßig verbundene Gerät müssen Verbindungsart,
  Mobilität, Kritikalität und Betriebsbedarf nachvollziehbar dokumentierbar sein.
- Mobile Clients müssen ohne manuelle Infrastrukturänderung nutzbar sein.
- Kritische Geräte müssen bei einem Ausfall anderer, nicht kritischer Geräte
  weiter betrieben werden können.
- Die Infrastruktur muss spätere Geräte und zusätzliche Ports aufnehmen können.
- Gerätezuordnung zu Segmenten und konkrete Adressen bleiben Folgeentscheidungen.

## 3. Functional Requirements

Die Infrastruktur muss folgende fachliche Funktionen unterstützen:

- zuverlässiger Internetzugang für Haushalts- und Arbeitsgeräte
- stabile Homeoffice-Kommunikation für mehrere Laptops oder Macs
- Internetnutzung der PS5
- sicherer Fernzugriff über VPN
- getrennt betreibbare Dienste für Knowledge Base, lokale KI, Monitoring,
  Automatisierung, Work Management, NAS/Storage und Backup
- lokale und nachvollziehbare Überwachung von Internet, Netzwerkkomponenten,
  WLAN, USV, Backups und Updates
- planbare Wartungs- und Updatevorgänge
- regelmäßige Backups und nachweisbare Wiederherstellung
- spätere Unterstützung von Kameras, Sensoren und zusätzlichen Clients
- Betrieb ohne dauerhafte Abhängigkeit von einem täglich genutzten Laptop

Nicht festgelegt wird, welche Software, welches Protokoll oder welches
Konfigurationsmodell diese Funktionen umsetzt.

## 4. Security Requirements

- Gäste müssen von internen und administrativen Ressourcen getrennt werden können.
- IoT- und Smart-Home-Geräte müssen getrennt behandelt werden können.
- Managementzugänge müssen vor normalen Clients geschützt werden können.
- Administrative Zugänge müssen nachvollziehbar und kontrollierbar sein.
- Remotezugriff muss authentifiziert und sicher begrenzbar sein.
- Interne Dienste dürfen nur die für ihren Zweck erforderlichen Zugriffe erhalten.
- Sicherheitsrelevante Änderungen müssen unter menschlicher Kontrolle bleiben.
- Die Infrastruktur muss eine restriktive Zugriffsbasis unterstützen; konkrete
  Regeln werden nicht in diesem Dokument definiert.
- Ausfälle oder Fehlkonfigurationen einzelner Geräte dürfen nicht unnötig den
  Zugriff auf unkritische Haushaltsfunktionen gefährden.
- Betrieb, Änderungen und Wiederherstellungen müssen auditierbar bleiben.

## 5. Availability Requirements

### Bekannte Anforderungen

- Angestrebte maximal akzeptierte Ausfallzeit: 15 Minuten.
- Router, Firewall, zentrale Switching-Komponente und erforderliche WLAN-
  Infrastruktur müssen für den dauerhaften Betrieb ausgelegt sein.
- Kurze Stromausfälle sollen für die Kernkomponenten überbrückbar sein.
- Ein kontrolliertes Herunterfahren muss möglich sein, wenn die Stromversorgung
  länger ausfällt.
- Neustarts und Wartungsfenster müssen planbar und nachvollziehbar sein.
- Wiederanlauf nach Strom- oder Geräteausfall muss ohne manuelle Eingriffe an
  jedem einzelnen Client möglich sein.

### Offene Fragen

- Welche Komponenten dürfen einzeln ausfallen, ohne dass die Zielverfügbarkeit
  verletzt wird?
- Welche Dienste benötigen eigene RPO- und RTO-Werte?
- Muss Internetzugang bei Ausfall eines einzelnen Infrastrukturgeräts erhalten
  bleiben, oder ist ein geplanter Ausfall akzeptabel?
- Welche USV-Laufzeit ist pro Komponentengruppe erforderlich?
- Wie soll ein kontrollierter Shutdown ausgelöst und bestätigt werden?

## 6. Growth Requirements

Die Infrastruktur muss folgende mögliche Erweiterungen berücksichtigen, ohne sie
vorwegzunehmen:

- NAS/Storage mit noch zu ermittelnder Kapazität
- lokale KI und zusätzliche Compute-Ressourcen
- Monitoring, Sensoren und Raumwerte
- Kameras
- ein zweiter Access Point
- ein zweiter Switch
- weitere Server oder Virtualisierungshosts
- zusätzliche Homeoffice- und Haushaltsclients
- zusätzliche Backupziele
- Wachstum bei Kabeln, Ports, Strombedarf und Wärmeabgabe

Für diese Erweiterungen sind ausreichende Kapazitätsreserven bei Ports,
Stromversorgung, Platz, Kühlung und Dokumentation vorzusehen. Konkrete
Dimensionen und Geräteentscheidungen bleiben offen.

## 7. Procurement Dependencies

| Infrastrukturkomponente | Procurement Case | Status | Abhängigkeit | Später ergänzbar |
|---|---|---|---|---|
| Router-USV | PC-0001 | WATCHING | beeinflusst Verfügbarkeit des Internetzugangs | ja |
| rollbarer Netzwerkschrank | PC-0002 | WATCHING | beeinflusst Platz-, Strom- und Erweiterungsanforderungen | ja |
| Firewall Appliance | PC-0003 | WATCHING | beeinflusst Sicherheits- und VPN-Fähigkeit; Produktprofil ist festgelegt | ja, Modellwahl offen |
| Managed Switch | PC-0004 | WATCHING | beeinflusst Portreserve und Segmentierungsfähigkeit | ja |
| Rack-USV | PC-0005 | WATCHING | beeinflusst Stromüberbrückung und kontrollierten Shutdown | ja |
| Access Point(s) | kein Case | offen | beeinflusst WLAN-Abdeckung und Funkkapazität | ja |
| NAS/Storage | kein Case | offen | beeinflusst Speicher-, Backup- und Energieanforderungen | ja |
| Compute/Server | kein Case | offen | beeinflusst Compute-, Platz- und Strombedarf | ja |

Die Procurement-Cases beobachten den Markt unabhängig von dieser
Anforderungsaufnahme. Eine Kaufempfehlung ersetzt keine Infrastrukturfreigabe.
Die Architektur soll soweit möglich ohne konkrete Beschaffung fortschreiten;
offene Modellentscheidungen dürfen jedoch nicht als entschieden angenommen werden.

## 8. Open Questions

- Wie sehen Raummaße, Steckdosen, Leitungswege und der gewünschte Rackstandort
  konkret aus?
- Welche Geräte sind aktuell vollständig inventarisiert, einschließlich
  Hersteller, Modell, MAC/Seriennummer und Verbindungsart?
- Wie viele Access Points werden benötigt?
- Welche WLAN-Abdeckung und Kapazität wird für Homeoffice und Haushaltsnutzung
  konkret akzeptiert?
- Welche NAS-, Server-, Kamera- und Sensorerweiterungen sind verbindlich und in
  welchem Zeitraum zu erwarten?
- Welche RPO/RTO-Werte gelten für Knowledge Base, lokale KI, Monitoring,
  Automatisierung, NAS und Backup?
- Welche USV-Laufzeiten und Shutdown-Zustände sind je Komponente erforderlich?
- Welche administrativen Personen oder Rollen benötigen Zugriff?
- Welche Anforderungen gelten für externe Fernwartung und Notfallzugang?
- Welche Anforderungen gelten für Updates, Wartungsfenster und Rollback?
- Welche Daten müssen dauerhaft lokal bleiben und welche externen Dienste sind
  zulässig?
- Welche Geräusch-, Wärme- und Sichtbarkeitsgrenzen gelten im Wohnraum?
- Welche Teile des bestehenden Ist-Zustands müssen zwingend erhalten bleiben?

## Abgrenzung zu Folgearbeiten

Die folgenden Ergebnisse sind ausdrücklich nicht Teil von WO-0024:

- Netzwerktopologie
- Racklayout
- IP-Plan
- VLAN-IDs und konkrete Zonennamen
- Firewall-Regeln
- DNS- und DHCP-Konfiguration
- OPNsense-Konfiguration
- konkrete Hardwareauswahl oder Kaufentscheidung

Diese Anforderungen bilden die Eingabe für nachfolgende Architektur- und
Infrastruktur-Work-Orders. Eine Freigabe durch den Project Owner ist erforderlich,
bevor daraus ein Infrastructure Blueprint abgeleitet wird.

## Priorisierung der Anforderungen

Eine spätere Revision kann jede Anforderung mit einer Priorität versehen:

- `MUST`: zwingend für die Freigabe oder den sicheren Betrieb
- `SHOULD`: wichtig und nach Möglichkeit umzusetzen
- `COULD`: wünschenswert, aber bei Zielkonflikten nachrangig

Die konkrete Zuordnung wird nicht vorweggenommen. Sie ist eine eigene
Governance-Entscheidung des Project Owners und soll vor der Blueprint-Freigabe
erfolgen.

## Definition of Success

Das Requirements-Dokument ist vollständig, wenn jede spätere
Architekturentscheidung auf mindestens eine dokumentierte Anforderung
zurückgeführt werden kann und jede nicht entschiedene Frage ausdrücklich als
offen erkennbar bleibt.
