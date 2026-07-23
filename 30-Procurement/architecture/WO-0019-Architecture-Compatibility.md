---
document: WO-0019-Architecture-Compatibility.md
version: 1.0
status: Draft
owner: Project Owner
reviewed_by: Lead Architect
last_review: ""
classification: Workspace
---

# WO-0019 – Architekturkompatibilität

## Festgestellte Konflikte

Die bestehende Runtime kennt nur die Watch-Run-Status `succeeded` und `failed`. Die Live-Quellenisolierung benötigt zusätzlich eine Warnung bei teilweise erfolgreichen Quellen. Der bestehende Statusvertrag bleibt deshalb unverändert: Ein Lauf mit mindestens einer erfolgreichen Quelle bleibt `succeeded`; Quellenfehler werden in `watch_run_results`, Logs und `SOURCE_FAILED`-Events gespeichert.

Das bestehende Datenmodell speichert Preise und Verfügbarkeit, aber noch keine Lieferfenster, Abholung oder Lieferkonfidenz. Diese Daten sind für WO-0019 fachlich erforderlich. Die kleinste kompatible Lösung ist eine additive SQLite-Migration mit Lieferfeldern auf Angeboten und unveränderlichen Beobachtungen. Bestehende Tabellen und Persistenzverantwortlichkeiten bleiben erhalten.

Der bestehende Evaluator bewertet bereits Preis, Verfügbarkeit und technische Nachweise. WO-0019 ergänzt Liefer-, Budget- und USV-Anforderungsregeln im Evaluator; Adapter bleiben auf Abruf und Normalisierung beschränkt.

## Kompatible Umsetzung

`watch live PC-0001` lädt ausschließlich konfigurierte, öffentliche Quellen, normalisiert deren Ergebnisse und übergibt sie an den bestehenden Service- und Repository-Pfad. Es gibt keine automatische Bestellung, keine Login-Automation, keine kostenpflichtige API und keine Secret-Konfiguration.

Die Quellenkonfiguration liegt außerhalb der Python-Logik. Der erste Lauf verwendet zwei öffentliche Geizhals-Produktseiten für zwei konkrete APC-Modellvarianten. Händlerangebote werden einzeln erfasst; Modellfamilien allein gelten nicht als technische Freigabe.

Lieferangaben werden relativ zum Beobachtungszeitpunkt normalisiert. `Auf Lager` ohne belastbares Datum bleibt `unknown` und erzeugt `DELIVERY_UNKNOWN`.
