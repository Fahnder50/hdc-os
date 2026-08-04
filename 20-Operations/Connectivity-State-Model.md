---
document: Connectivity-State-Model.md
version: 1.0
status: Accepted
owner: Project Owner
reviewed_by: Lead Architect
last_review: "2026-08-04"
last_updated: "2026-08-04"
work_order: WO-0040
classification: Deployment-relevant Architecture Baseline
---

# Connectivity State Model & Offline Operation Baseline

## 1. Zweck und verbindlicher Grundsatz

Dieses Dokument definiert den providerneutralen fachlichen Vertrag für die
Verfügbarkeit externer Kommunikation in HDC-OS. Ausgangspunkt ist der reale
Stromausfall vom 04.08.2026: Der durch `UPS-RTR-01` versorgte Speedport blieb
in Betrieb, der externe DSL-/WAN-Zugang jedoch nicht, weil außerhalb der
Wohnung liegende Providertechnik nicht verfügbar war.

```text
Gateway mit Strom
  ≠ WAN-Transport-Link vorhanden
  ≠ externe Internetziele erreichbar
  ≠ DNS nutzbar
```

Keine einzelne Ebene und kein einzelnes Gerät darf deshalb den Gesamtzustand
`ONLINE` begründen. Internetabhängige Services konsumieren später den zentralen
Connectivity-State und leiten ihre Onlinefähigkeit nicht aus Router-, Strom-
oder Einzelmesswerten ab.

> Der Ausfall externer Konnektivität ist ein erwartbarer Betriebszustand und
> kein Fehlerzustand des gesamten HDC-OS.

## 2. Systemgrenze und Nichtumfang

Das Modell beschreibt ausschließlich externe Kommunikationsverfügbarkeit. Es
definiert Begriffe, Zustände, Übergänge, Ereignisse und Consumer-Verträge.

Es überwacht oder implementiert ausdrücklich nicht:

- Stromversorgung oder Hardwarezustände,
- Router-, Speedport- oder OPNsense-Konfiguration,
- Providerdiagnose oder konkrete DSL-Auslesung,
- Ping-, DNS-, TCP-, HTTP- oder sonstige aktive Probes,
- Mobilfunk- oder anderes Failover,
- Scheduler, Hintergrunddienst, Queue, Retry oder Backoff,
- Datenbank, Persistierung, CLI, API, Dashboard oder Benachrichtigungen,
- konkrete Zeitfenster, Schwellenwerte oder Stabilitätskriterien,
- Änderungen bestehender Services oder des Procurement Watchers.

WO-0040 ist ausschließlich eine Architektur- und Operations-Baseline. Eine
aktive Zustandsermittlung folgt in späteren Work Orders.

## 3. Providerneutralität

`WAN Transport` bezeichnet den physischen oder logischen Zugang zum Provider.
Das Modell gilt unverändert für DSL, Kabel, Glasfaser, Mobilfunk, Satellit,
mehrere parallele WAN-Verbindungen und zukünftige Failover-Verbindungen. DSL
ist lediglich die aktuelle konkrete Ausprägung am Speedport-Standort.

Primär-/Sekundärpfad, NTP, Captive Portal und externe Dienstabhängigkeiten sind
später als zusätzliche Evidenz vorbereitbar. Sie erweitern nicht den Katalog
der fünf Gesamtzustände.

## 4. Ebenen- und Evidenzmodell

Messwerte beziehungsweise Evidenz und Gesamtzustand sind getrennte fachliche
Objekte. Spätere Ermittler liefern Evidenz; nur der Connectivity State Provider
darf daraus den Gesamtzustand ableiten.

| Ebene | Aussage | Beispielhafte Evidenz |
|---|---|---|
| Power | Sind lokal relevante Komponenten mit Strom versorgt? | `AVAILABLE`, `UNAVAILABLE`, `UNKNOWN` |
| Gateway | Ist das lokale Gateway erreichbar und betriebsbereit? | `AVAILABLE`, `UNAVAILABLE`, `UNKNOWN` |
| WAN Transport | Besteht der physische oder logische Provider-Link? | `AVAILABLE`, `UNAVAILABLE`, `UNKNOWN` |
| Internet Reachability | Sind externe Netzziele tatsächlich erreichbar? | `AVAILABLE`, `UNAVAILABLE`, `DEGRADED`, `UNKNOWN` |
| DNS | Ist die erforderliche Namensauflösung nutzbar? | `AVAILABLE`, `UNAVAILABLE`, `DEGRADED`, `UNKNOWN` |

Evidenz kann zusätzlich Beobachtungszeit, Quelle, Qualität und Detailwerte
tragen. Widersprüchliche, fehlende oder veraltete Evidenz ist keine Bestätigung
für `ONLINE`.

Beispiel des Stromausfalls:

```yaml
power: AVAILABLE
gateway: AVAILABLE
wan_transport: UNAVAILABLE
internet_reachability: UNAVAILABLE
dns: UNKNOWN
```

Dieser Evidenzsatz darf nicht zu `ONLINE` führen. Power ist eine relevante
Evidenzebene, aber das Connectivity-Modell ist keine Stromüberwachung.

## 5. Exakt fünf Connectivity-States

| State | Verbindliche Bedeutung |
|---|---|
| `UNKNOWN` | Der externe Connectivity-Zustand ist nicht belastbar ermittelt. Dies bedeutet weder automatisch `ONLINE` noch `OFFLINE`. Typische Ursachen sind Systemstart, fehlende Messwerte, nicht verfügbare Messkomponente sowie widersprüchliche oder veraltete Evidenz. |
| `ONLINE` | Gateway, erforderlicher WAN-Transport, externe Internet-Reichweite und erforderliche Namensauflösung sind gemeinsam belastbar für den regulären Internetbetrieb verfügbar. Keine einzelne Ebene genügt. |
| `DEGRADED` | Externe Konnektivität ist vorhanden, aber funktional oder qualitativ eingeschränkt, beispielsweise durch DNS-Störung, Teilreichweite, Paketverlust, Instabilität oder einen eingeschränkten Ersatzpfad. `DEGRADED` ist nicht `OFFLINE`. |
| `OFFLINE` | Es besteht keine belastbar nutzbare externe Internetverbindung. Lokales Netzwerk und lokale HDC-OS-Funktionen können trotzdem vollständig oder teilweise weiterlaufen. |
| `RECOVERING` | Nach bestätigtem `OFFLINE` oder `DEGRADED` liegen erste positive Wiederherstellungssignale vor, aber ein stabiler Zustand `ONLINE` ist noch nicht bestätigt. Ein Einzelmesswert reaktiviert keine ausgesetzten Services. |

Andere Gesamtzustände sind nicht zulässig.

## 6. Verbindlicher Transition Contract

| Previous State | Zulässige Current States |
|---|---|
| `UNKNOWN` | `ONLINE`, `DEGRADED`, `OFFLINE` |
| `ONLINE` | `DEGRADED`, `OFFLINE`, `UNKNOWN` |
| `DEGRADED` | `ONLINE`, `OFFLINE`, `RECOVERING`, `UNKNOWN` |
| `OFFLINE` | `RECOVERING`, `UNKNOWN` |
| `RECOVERING` | `ONLINE`, `DEGRADED`, `OFFLINE`, `UNKNOWN` |

Jeder nicht aufgeführte Wechsel ist fachlich unzulässig. Insbesondere ist
`OFFLINE → ONLINE` verboten: Nach einem bestätigten Ausfall muss zunächst
`RECOVERING` durchlaufen werden. WO-0040 legt keine technische Dauer und keine
Anzahl positiver Messwerte für diese Bestätigung fest.

## 7. Ereignismodell

Ein späteres Ereignis entsteht nur bei einem fachlichen Zustandswechsel. Es
muss mindestens folgende Struktur tragen können:

```yaml
event_type: CONNECTIVITY_OFFLINE
previous_state: ONLINE
current_state: OFFLINE
observed_at: <timestamp>
reason_codes: []
evidence_summary: {}
source: <state-provider>
```

| Event | Auslösebedingung |
|---|---|
| `CONNECTIVITY_ONLINE` | Gesamtzustand erreicht erstmals oder nach einer anderen Phase belastbar `ONLINE`. |
| `CONNECTIVITY_DEGRADED` | Wechsel nach `DEGRADED`. |
| `CONNECTIVITY_OFFLINE` | Wechsel nach `OFFLINE`. |
| `CONNECTIVITY_RECOVERING` | Wechsel nach `RECOVERING`, nachdem erste Wiederherstellungsevidenz vorliegt. |
| `CONNECTIVITY_RECOVERED` | Ausschließlich der Wechsel `RECOVERING → ONLINE`. Beschreibt die erfolgreiche Wiederherstellung. |
| `CONNECTIVITY_UNKNOWN` | Wechsel nach `UNKNOWN`, weil kein belastbarer Zustand mehr vorliegt. |

Beim Wechsel `RECOVERING → ONLINE` beschreibt `CONNECTIVITY_ONLINE` den
erreichten Zustand und `CONNECTIVITY_RECOVERED` zusätzlich die bestätigte
Wiederherstellung. `CONNECTIVITY_RECOVERED` darf bei keinem anderen Übergang
entstehen. WO-0040 implementiert weder Erzeugung noch Persistierung oder
Übertragung dieser Ereignisse.

## 8. Eigentümerschaft und spätere Rollen

| Rolle | Darf | Darf nicht |
|---|---|---|
| Ermittler / Probe | Evidenz zu Gateway, WAN Transport, Internet Reachability, DNS und späteren Ebenen liefern | Gesamtzustand selbst setzen oder Serviceentscheidungen treffen |
| Connectivity State Provider | Evidenz aggregieren, Gesamtzustand ableiten, Transition Contract verwalten und Ereignisse erzeugen | Providerdiagnose, Service-Scheduling oder fachfremde Überwachung übernehmen |
| Service Consumer | Zustand lesen, Ereignisse konsumieren und eigene deklarierte Policy anwenden | zentralen Connectivity-State überschreiben |

Der neutrale `Connectivity State Provider` ist später alleiniger Eigentümer des
aktuellen Gesamtzustands.

## 9. Service-Reaktionsvertrag

Jeder internetabhängige Service muss in einer nachgelagerten Work Order genau
eine deklarierte Connectivity-Policy erhalten. Zulässige Reaktionen sind:

| Reaktion | Vertrag |
|---|---|
| `RUN` | Reguläre Ausführung ist erlaubt. |
| `SUSPEND` | Aktive oder geplante internetabhängige Arbeit wird ausgesetzt. |
| `DEFER` | Ausführung wird auf einen späteren Zeitpunkt verschoben. |
| `QUEUE` | Arbeitsauftrag bleibt lokal erhalten und wird nicht verworfen. |
| `RESUME_ON_RECOVERY` | Arbeit wird erst nach bestätigtem `CONNECTIVITY_RECOVERED` kontrolliert wieder aufgenommen. |
| `LOCAL_ONLY` | Nur lokale Teilfunktionen laufen; externe Schritte bleiben ausgesetzt. |

Mindestverhalten internetabhängiger Services:

| Connectivity-State | Standardverhalten |
|---|---|
| `UNKNOWN` | Keine irreversible externe Aktion; abhängig von Policy aussetzen oder verschieben. |
| `ONLINE` | Normale Ausführung. |
| `DEGRADED` | Nur ausdrücklich freigegebene externe Ausführung; sonst verschieben oder lokal weiterarbeiten. |
| `OFFLINE` | Keine externe Ausführung; lokal weiterarbeiten, aufschieben oder einreihen. |
| `RECOVERING` | Keine vollständige automatische Wiederaufnahme, bis `ONLINE` bestätigt ist. |

## 10. Offline Operation und Datenintegrität

Während `OFFLINE` müssen grundsätzlich weiter möglich bleiben:

- lokaler Zugriff auf HDC-OS,
- lokale Asset- und Infrastrukturinformationen,
- lokale Dokumentation und Datenverarbeitung,
- lokale Warteschlangen,
- lokale Entscheidungen ohne Bedarf an aktuellen Internetdaten,
- lokaler Betrieb bestehender Netzwerkkomponenten.

Ein internetabhängiger Service gilt durch `OFFLINE` nicht automatisch als
technisch defekt. Externe Arbeitsaufträge dürfen nicht stillschweigend verloren
gehen. Eine spätere Implementierung muss zwischen `nicht gestartet`,
`verschoben`, `lokal eingereiht`, `nach Wiederherstellung wiederaufgenommen`
und `endgültig fehlgeschlagen` unterscheiden. Dieses Dokument implementiert
keine Queue.

## 11. Spätere Consumer-Abhängigkeiten

Alle internetabhängigen Services werden später Consumer des zentralen Zustands.
Die konkrete Policy-Zuordnung erfolgt ausschließlich in Folge-Work-Orders.

Für den Procurement Watch ist fachlich vorgesehen:

| Connectivity-State | Späteres Procurement-Verhalten |
|---|---|
| `ONLINE` | Regulärer Watch zulässig. |
| `DEGRADED` | Policyabhängig; Ergebnis gegebenenfalls als unvollständig kennzeichnen. |
| `OFFLINE` | Kein externer Watch; Lauf verschieben oder lokal einreihen. |
| `RECOVERING` | Noch keine vollständige Wiederaufnahme. |
| `UNKNOWN` | Keine belastbare externe Bewertung starten. |

WO-0040 verändert den Procurement-Code und bestehende Services ausdrücklich
nicht. Diese Tabelle ist nur eine zukünftige fachliche Abhängigkeit.

## 12. Architekturintegration

Das Connectivity-Modell ergänzt das [Network Design v0.1](Network-Design-v0.1.md),
ohne dessen physische oder logische Topologie zu ändern. Network Design
definiert den Pfad; dieses Dokument definiert, wann externe Kommunikation über
diesen oder einen zukünftigen providerneutralen Pfad fachlich verfügbar ist.

Die Operations-Übersicht verweist auf diesen Vertrag als Deployment-relevante
Baseline. Aktive Ermittlung, Providerintegration und Consumer-Policies benötigen
separate Work Orders beziehungsweise ADRs.
