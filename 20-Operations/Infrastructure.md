---
document: Infrastructure.md
version: 1.0
status: Accepted
owner: Project Owner
reviewed_by: Lead Architect
last_review: "2026-07-10"
classification: Workspace
---

# Infrastruktur

## Zweck

Dieses Dokument überführt die in Sprint 1 bekannten Infrastruktur-Erkenntnisse in den Workspace.

Es trifft keine neuen Architekturentscheidungen. Festgelegte Grundsätze, diskutierte Inhalte und offene Detailentscheidungen werden getrennt dokumentiert.

---

## Betriebsziel

HDC-OS soll eine sichere, nachvollziehbare und langfristig erweiterbare IT-Infrastruktur unterstützen.

Für Horizon 1 steht eine kleine, nutzbare und verständliche Grundlage im Vordergrund.

Andere Haushaltsmitglieder sollen bei Ausfall der HDC-OS-Infrastruktur möglichst keine sichtbare Einschränkung erfahren.

Angestrebte maximale Ausfalldauer: 15 Minuten.

---

## Grundtopologie

Status: in Sprint 1 festgelegt.

```text
Internet
  ↓
Speedport Smart 4
  ↓
dedizierte OPNsense-Firewall
  ↓
TP-Link Omada SG2218
  ↓
Access Points, kabelgebundene Geräte und spätere Infrastruktur
```

Klarstellungen:

- Die Grundtopologie wurde in Sprint 1 festgelegt.
- Das technische Detaildesign ist noch offen.
- Der Speedport Smart 4 bleibt bestehen.
- OPNsense ist die Zielplattform der Firewall.
- Der Switch SG2218 ist die vorgesehene Horizon-1-Komponente.

---

## Erstes Product Increment

Status: geplanter erster lauffähiger Infrastrukturschritt.

> Ein Asset – voraussichtlich der Laptop des Project Owners – nutzt das Internet hinter der HDC-OS-Firewall.

Dieses Product Increment beschreibt keinen vollständigen Zielbetrieb, sondern den ersten prüfbaren Betriebszustand.

---

## Betriebsbedingungen

Status: bekannte Rahmenbedingungen aus Sprint 1.

- PS5 im Arbeitszimmer bleibt per LAN angebunden.
- Router steht außerhalb des Arbeitszimmers nahe der Eingangstür.
- Arbeitszimmer enthält bestehenden Switch, Laptop und PS5.
- Wohnung umfasst ungefähr 88 m².
- Gemischte Trockenbau- und Ziegelwände sind zu berücksichtigen.
- WLAN soll die gesamte Wohnung zuverlässig versorgen.
- Zwei bis drei Homeoffice-Laptops beziehungsweise Macs müssen stabil arbeiten.
- Andere Haushaltsmitglieder sollen bei Ausfall der HDC-OS-Infrastruktur möglichst keine sichtbare Einschränkung erfahren.
- Angestrebte maximale Ausfalldauer: 15 Minuten.

---

## VLAN-Status

### Festgelegt

- VLANs werden von Beginn an vorgesehen.
- Segmentierung ist ein Sicherheitsgrundsatz.

### Diskutiert, aber nicht freigegeben

- Management
- Trusted/Home
- Work/Homeoffice
- Gaming
- IoT/Smart Home
- Gäste
- Server/Services
- Kameras

### Offen

- VLAN-IDs
- verbindliche Zonennamen
- Gerätezuordnung
- Inter-VLAN-Regeln

---

## IP-Konzept

Status: tatsächlich offen.

Offen sind:

- RFC1918-Adressbereich
- Subnetze
- DHCP-Bereiche
- statische Adressen
- Reservierungen
- DNS-Namen
- Namensschema

---

## Firewall-Grundsätze

### Festgelegt

- OPNsense als Zielplattform
- Speedport bleibt vorgeschaltet
- dedizierte Firewall-Appliance
- segmentierter Zugriff beziehungsweise Default-deny als Sicherheitsprinzip
- VLAN-Unterstützung
- VPN-Unterstützung
- NordVPN optional als ausgehendes Gateway beziehungsweise Policy Route
- NordVPN ersetzt nicht die Firewall
- Homeoffice-Kommunikation darf nicht pauschal durch Consumer-VPN geroutet werden
- direkter Regelbetrieb von Geräten am Speedport ist nicht vorgesehen
- kritische Änderungen bleiben unter menschlicher Kontrolle

### Offen

- Double NAT, Exposed Host oder PPPoE-Passthrough
- konkrete Firewall-Regeln
- DNS-Resolver
- IDS/IPS
- Geo- oder Reputation-Blocking
- NordVPN-Routingregeln
- Fail-open- beziehungsweise Fail-safe-Konzept
- Notfallzugang

---

## Sicherheitsprinzipien

Sicherheit besitzt Vorrang vor Komfort.

Kritische Änderungen bleiben unter menschlicher Kontrolle.

Änderungen an sicherheitsrelevanten Komponenten müssen nachvollziehbar bleiben.

Sicherheit, Nachvollziehbarkeit und Nachhaltigkeit bilden die bekannten Betriebsleitlinien.

---

## Serverrollen und Virtualisierung

Status: langfristig vorgesehene Rollen, noch nicht auf konkrete Hosts verteilt.

- Knowledge Base
- lokale KI
- Monitoring
- Automatisierung
- Ticket- beziehungsweise Work-Management
- NAS/Storage
- Backup
- optional Home Assistant
- Omada Controller
- Dokumentations- und Repository-Dienste

Proxmox wurde als Virtualisierungsplattform diskutiert, aber nicht final beschlossen.

---

## Storage

Status: langfristiges Ziel mit offenen Detailentscheidungen.

Festgehalten:

- eigene NAS ist langfristiges Ziel
- aktueller Speicherbedarf ist noch unbekannt
- Bedarf soll vor einer Hardwareentscheidung ermittelt werden
- kein vorschneller NAS- oder Festplattenkauf

Offen bleiben:

- Nutzkapazität
- RAID/ZFS
- SSD/HDD
- Verschlüsselung
- Snapshots
- Datenklassen
- Aufbewahrung

---

## Backup-Anforderungen

Status: Grundanforderungen bekannt, Detaildesign offen.

Bekannte Anforderungen:

- regelmäßige Backups
- automatisierte Prüfung
- nachgewiesene Wiederherstellbarkeit
- Repository muss unabhängig vom Laptop gesichert sein
- spätere Konfigurationen und Knowledge Base müssen einbezogen werden

Offen:

- 3-2-1-Design
- Backupsoftware
- Backupziele
- Zeitpläne
- Offsite-Ziel
- Restore-Testverfahren
- RPO und RTO je Service

---

## Monitoring-Zielbild

Status: geplante Überwachungsbereiche bekannt, Toolauswahl offen.

Geplante Überwachungsbereiche:

- Internetverfügbarkeit
- Firewall
- Switch
- WLAN
- USV
- Backups
- Updates
- später Server, Storage, Sensoren und Raumwerte

Offen:

- Toolauswahl
- Metriken
- Alarmgrenzen
- Benachrichtigungskanäle
- Dashboards
- Aufbewahrungsdauer

---

## Bekannte Infrastrukturkomponenten

In Sprint 1 wurden folgende Komponenten als relevante Ausgangsbasis benannt:

- Speedport Smart 4
- dedizierte OPNsense-Firewall
- TP-Link Omada SG2218
- Access Points
- kabelgebundene Geräte
- Rack
- Rack-USV
- Router-USV

Diese Liste ist keine finale Beschaffungsliste.

---

## Offene Punkte

Nicht Bestandteil dieses Dokuments sind:

- neues Netzwerkdesign
- Festlegung von VLAN-IDs
- Festlegung eines IP-Konzepts
- Erstellung konkreter Firewall-Regeln
- Auswahl von Monitoring- oder Backupsoftware
- Infrastrukturaufbau

Diese Themen bleiben Folgearbeiten für spätere Work Orders.
