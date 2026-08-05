---
document: Repository-Documentation-Governance.md
version: 1.0
status: Accepted
owner: Project Owner
reviewed_by: Lead Architect
last_review: "2026-08-05"
release_reference: knowledge-v1.5.4
last_updated: "2026-08-05"
work_order: WO-0042
classification: Historical
---

# Repository Documentation Governance

## 1. Zweck

Diese Governance definiert die verbindliche Dokumentationsprüfung vor jedem
Knowledge Release. Ein Release ist blockiert, sobald eine zentrale Aussage
nicht mit den freigegebenen Repository-Quellen übereinstimmt. Die Regeln ändern
keine Architektur, Runtime oder Fachdomäne.

## 2. Dokumentenklassifizierung

Jedes Repository-Dokument gehört genau einer der folgenden Klassen an.

### 2.1 Living Documents

Living Documents bilden den aktuellen, veröffentlichten Projektstand ab und
werden für jedes Knowledge Release gemeinsam gepflegt:

| Dokument | Verbindlicher Pfad | Zweck |
|---|---|---|
| README | `README.md` | öffentlicher Einstieg und Gesamtstatus |
| Project | `Project.md` | Auftrag, Reifegrad und aktuelle Arbeitsrichtung |
| Project Status | `Project-Status.md` | operative Momentaufnahme und Bottleneck |
| Roadmap | `40-Backlog/Roadmap.md` | aktueller Sprint und nächste Ziele |
| Documentation Consistency Report | `Documentation-Consistency-Report.md` | Nachweis der Release-Prüfung |

Diese fünf Pfade sind die vollständige Living-Document-Liste. Ein weiteres
Living Document darf nur durch Änderung dieser Governance aufgenommen werden.
Alle Living Documents tragen im Front Matter `classification: Living`.

### 2.2 Historical Documents

Alle übrigen Markdown-, Word-, PDF- und Release-Note-Dokumente sind Historical
Documents, insbesondere:

- Work Orders und Review Work Orders (`WO-*`, `RWO-*`),
- ADRs und freigegebene Architekturdesigns,
- Procurement-Entscheidungen und Acceptance-Dokumente,
- Sprintabschlüsse, Knowledge-Recovery-Dokumente und frühere Release Notes,
- Foundation-, Engineering-, Operations- und Backlog-Dokumente, soweit sie
  nicht ausdrücklich in Abschnitt 2.1 aufgeführt sind.

Historical Documents werden nach Freigabe nicht inhaltlich fortgeschrieben.
Eine Korrektur oder fachliche Ablösung erfolgt durch eine neue Work Order, einen
ADR oder ein Nachfolgedokument. Überholte Aussagen werden im neuen Dokument als
`Historical` oder `Superseded` referenziert; die historische Quelle bleibt
unverändert. Nicht-Dokumentdateien wie Code, YAML-Datenquellen und Assets fallen
nicht unter diese Dokumentenklassifizierung.

Ältere Front-Matter-Werte wie `Public`, `Workspace`, `Architecture` oder
`Operations` sind fachliche Ablagekennzeichen und keine dritte Governance-
Klasse. Sofern der exakte Pfad nicht in Abschnitt 2.1 steht, ist das Dokument
für diese Governance eindeutig `Historical`. Diese Regel vermeidet eine
nachträgliche Änderung bereits freigegebener historischer Dokumente.

## 3. Verbindliche Quellenhierarchie

Living Documents erfinden keine Fachstände. Maßgeblich sind:

| Dimension | Primärquelle |
|---|---|
| veröffentlichtes Release | tatsächlich veröffentlichter Git-Tag/GitHub Release |
| Sprint und Projektphase | freigegebene Roadmap und aktuelle Work Orders |
| Architektur | Accepted Architecture Work Orders und ADRs |
| Procurement-Status | `30-Procurement/cases/PC-*.yaml` |
| Asset-Status | `20-Operations/assets/registry.yaml` und referenzierte Asset Records |
| physischer Zustand | freigegebene Acceptance-/Operations-Dokumente |
| Deployment-Status | `20-Operations/WO-0041-First-Deployment-Readiness.md` und spätere Accepted Deployment-Nachweise |

Bei einem Widerspruch bleibt das Release blockiert. Der Konflikt wird nicht
durch Interpretation im Living Document gelöst, sondern an der zuständigen
Primärquelle oder durch eine neue fachliche Entscheidung.

## 4. Einheitlicher Pflichtdatensatz

Jedes Living Document enthält sichtbar und semantisch identisch:

- Release Reference,
- aktuellen Sprint,
- aktuellen Projektstatus,
- Current Bottleneck,
- Current Physical State,
- aktuellen Deployment-Status,
- Lifecycle-Status von PC-0001 bis PC-0005,
- Produktionsstatus aller produktiven Assets.

Zusätzlich müssen Front-Matter-Felder `document`, `status`, `owner`,
`release_reference`, `last_updated` und `classification: Living` vorhanden sein.
Release Reference und Sprint müssen über alle fünf Dokumente exakt gleich sein.

## 5. Release Consistency Checklist

Die Prüfung wird nach Abschluss der fachlichen Release-Änderungen, aber vor Tag
und Veröffentlichung ausgeführt.

### A. Inventar und Metadaten

- [ ] Alle fünf Living Documents existieren an den definierten Pfaden.
- [ ] Alle tragen `classification: Living`.
- [ ] Alle nennen dieselbe vorgesehene Release Reference.
- [ ] Alle nennen denselben Sprint.
- [ ] `last_updated` entspricht dem Prüfdatum.

### B. Projektwahrheit

- [ ] Projektstatus und Horizon sind widerspruchsfrei.
- [ ] Current Bottleneck ist in allen Living Documents identisch.
- [ ] Current Physical State enthält dieselben Geräte und Betriebszustände.
- [ ] Deployment-Status entspricht der freigegebenen Deployment-Quelle.
- [ ] Nur Accepted Architekturentscheidungen werden als verbindlich dargestellt.

### C. Procurement und Assets

- [ ] PC-0001 bis PC-0005 stimmen einzeln mit den Case-Dateien überein.
- [ ] Completed Procurement wird nicht als aktiv dargestellt.
- [ ] Alle produktiven Assets stimmen mit Registry und Asset Record überein.
- [ ] Externe Lasten werden nicht als HDC-OS-Assets dargestellt.

### D. Historie und Qualität

- [ ] Überholte Living-Aussagen wurden aktualisiert.
- [ ] Historische Quellen wurden nicht umgeschrieben.
- [ ] Ablösungen sind als Historical oder Superseded nachvollziehbar.
- [ ] Lokale Links der Living Documents besitzen gültige Ziele.
- [ ] `git diff --check` ist fehlerfrei.
- [ ] Der aktuelle Documentation Consistency Report enthält Dokumente,
      Abweichungen, Korrekturen und Abschlussresultat.

## 6. Documentation Consistency Report

Der Report wird bei jedem Knowledge Release aktualisiert und enthält mindestens:

1. vorgesehene Release Reference und Prüfdatum,
2. Liste aller geprüften Living Documents,
3. verwendete Primärquellen,
4. festgestellte Abweichungen,
5. vorgenommene Korrekturen,
6. Ergebnis jedes Pflichtchecks,
7. eindeutige Gate-Entscheidung `PASS` oder `BLOCKED`.

Ein leerer Abweichungsabschnitt wird ausdrücklich als „keine Abweichungen“
dokumentiert. Implizites Schweigen gilt nicht als Prüfung.

## 7. Release Gate

Ein Knowledge Release darf ausschließlich veröffentlicht werden, wenn alle
Checklist-Punkte `PASS` sind und der Consistency Report `PASS` ausweist.

Blockierende Kriterien sind mindestens:

- fehlendes Living Document,
- abweichende Release Reference oder abweichender Sprint,
- widersprüchlicher Projekt-, Bottleneck-, Physical- oder Deployment-Status,
- Abweichung eines Procurement- oder Asset-Status von seiner Primärquelle,
- nicht freigegebene Architektur als aktuelle Wahrheit,
- unmarkierte überholte Aussage,
- fehlender oder nicht erfolgreicher Consistency Report,
- fehlerhafte lokale Links oder fehlerhaftes `git diff --check`.

Gate-Ausgabe:

```text
alle Pflichtprüfungen PASS  => DOCUMENTATION_READY_FOR_RELEASE
mindestens eine Prüfung FAIL => RELEASE_BLOCKED
```

Es gibt keine Teilfreigabe und keinen automatischen Override. Eine bewusste
Ausnahme benötigt eine neue, freigegebene Governance-Entscheidung.

## 8. Spätere Automatisierbarkeit

Diese Governance implementiert keine Automatisierung. Sie definiert jedoch den
zukünftigen maschinenlesbaren Vertrag:

| Prüfobjekt | Vergleichsfeld / Regel |
|---|---|
| Living-Inventar | fünf exakte Pfade aus Abschnitt 2.1 |
| Front Matter | `classification`, `release_reference`, `last_updated`, `status`, `owner` |
| Sprint | normalisierter Wert `Sprint 4 – First Deployment` beziehungsweise später ein einheitlicher Nachfolger |
| Procurement | `case_id` und `status` aus allen `PC-*.yaml` |
| Assets | `asset_id` aus Registry plus `status` im referenzierten Record |
| Deployment | normierter Gate-Status aus der aktuellen Accepted Deployment-Quelle |
| Links | relative Markdown-Ziele müssen im Repository existieren |
| Report | Gate-Ergebnis muss exakt `PASS` sein |

Eine spätere Prüfung kann diese Felder deterministisch extrahieren und
vergleichen. Freitext darf ergänzen, aber keinen abweichenden normativen Status
enthalten.
