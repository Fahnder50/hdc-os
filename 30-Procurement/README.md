---
document: README.md
version: 1.0
status: Draft
owner: Project Owner
reviewed_by: Lead Architect
last_review: ""
classification: Workspace
---

# Procurement Watch

## Portfolio Operations CLI

Der tägliche Portfolio-Lauf wird mit einem Befehl ausgeführt:

```text
python -m procurement_watch watch live --all
```

Alle Cases mit Status `WATCHING` werden sequentiell verarbeitet. Ein Fehler
eines einzelnen Cases beendet die übrigen Läufe nicht; am Ende erscheint eine
Portfolio-Zusammenfassung und bei Fehlern der Hinweis `Portfolio completed
with warnings.`.

Alle Case-Definitionen lassen sich automatisch importieren:

```text
python -m procurement_watch import --all
```

Der aktuelle Portfolio-Zustand ist abrufbar mit:

```text
python -m procurement_watch portfolio status
```

## Runtime

Die Runtime liegt standardmäßig unter `30-Procurement/runtime/` und wird beim
ersten Initialisieren automatisch angelegt:

```text
runtime/
├── database.sqlite
├── journals/
├── logs/
├── cache/
└── observations/
```

Dieses Verzeichnis enthält ausschließlich lokale Betriebsdaten und ist über
`.gitignore` vollständig vom Repository getrennt. Der Pfad kann mit
`HDC_PROCUREMENT_RUNTIME` überschrieben werden; Datenbank, Logs und Journals
können weiterhin separat über ihre bisherigen Umgebungsvariablen gesetzt
werden.

Für Backups wird die CLI verwendet:

```powershell
python -m procurement_watch backup C:\HDC\Backups\procurement.db
python -m procurement_watch restore C:\HDC\Backups\procurement.db
```

Bei einer leeren Runtime legt `db init` die Verzeichnisse, SQLite-Datenbank
und das aktuelle Schema automatisch an. Ein frischer Clone benötigt keine
manuelle Runtime-Erstellung.

## RWO-0012 – Live Source Activation

PC-0002, PC-0004 und PC-0005 verwenden öffentliche Geizhals-Produktseiten
über den bestehenden `geizhals`-Adapter. Die Beobachtungen werden ausschließlich
lokal in SQLite gespeichert. Die freigegebenen Zielbudgets sind 120 EUR für
PC-0002, 220 EUR für PC-0003, 150 EUR für PC-0004 und 170 EUR für PC-0005;
die bestehenden absoluten Obergrenzen bleiben unverändert.

PC-0003 beobachtet ausschließlich das freigegebene Produktprofil Intel N100
mit mindestens vier Intel-i226-Ports und 2,5-Gigabit-Ethernet. Das Case bleibt
`WATCHING`; die absolute und Zielobergrenze beträgt ausschließlich 220 EUR.
Varianten werden nach Barebone/Komplettsystem, RAM, SSD und Netzteil getrennt
dokumentiert. Andere CPUs, Realtek/i225, weniger als vier Ports und unklare
Controller gelten nicht als passende Angebote.

Aktiviert sind DIGITUS DN-48000/DN-48001/DN-48002 für PC-0002, drei öffentliche
PC-0003-Quellen, TP-Link TL-SG2218 für PC-0004 und CyberPower OR1000ERM1U für
PC-0005. Die Quellen sind öffentlich, loginfrei und secret-frei; automatische
Bestellungen finden nicht statt.

Die konkreten Marktseiten und ihre technische Evidenz sind in
`config/sources.yaml` hinterlegt. Die aktuelle öffentliche Evidenz umfasst
einen Komplettsystem-Treffer bei 169,99 EUR, der ausverkauft ist, einen
Komplettsystem-Treffer ohne auslesbaren Preis sowie Geizhals-Varianten über
220 EUR. Damit bleibt PC-0003 aktiv in `WATCHING`, aber es entsteht keine
Kaufempfehlung außerhalb des freigegebenen Budgets.

## Voraussetzungen

- Windows 11 und Python 3.12
- PowerShell
- lokale Schreibrechte für den konfigurierten Daten-, Log- und Reportpfad

## Installation und Initialisierung

```powershell
.\30-Procurement\scripts\install.ps1
.\30-Procurement\scripts\initialize.ps1
```

Die produktive SQLite-Datenbank liegt standardmäßig unter `C:\HDC\Data\procurement\procurement.db` und wird nicht im Repository erzeugt. Bei der Initialisierung werden Repository-Commit, Repository-Version, Schema-Version und Erstellungszeitpunkt in `runtime_metadata` gespeichert.

## CLI

```powershell
python -m procurement_watch db init
python -m procurement_watch db status
python -m procurement_watch migrate
python -m procurement_watch watch run
python -m procurement_watch watch live PC-0001
python -m procurement_watch watch runs
python -m procurement_watch status
python -m procurement_watch doctor
python -m procurement_watch events
python -m procurement_watch case import 30-Procurement/cases/PC-0001-Router-USV.yaml
python -m procurement_watch product add --product-id PROD-001 --product-name "Router-USV" --case-id PC-0001
python -m procurement_watch offer add --offer-id OFFER-001 --product-id PROD-001 --vendor-id VENDOR-001 --vendor-name "Händler" --price 39.99 --shipping 4.99 --availability in_stock --case-id PC-0001
python -m procurement_watch offers PC-0001
python -m procurement_watch history PC-0001
python -m procurement_watch status PC-0001
python -m procurement_watch report PC-0001
python -m procurement_watch backup C:\HDC\Backups\procurement.db
python -m procurement_watch restore C:\HDC\Backups\procurement.db
```

Ohne konfigurierte Händlerquellen führt `watch run` einen kontrollierten Foundation-Lauf aus. `watch live PC-0001` verwendet die in `config/sources.yaml` hinterlegten öffentlichen Quellen.

Jede manuelle oder strukturierte Angebotserfassung erzeugt eine neue unveränderliche `PriceObservation`. Preis- oder Verfügbarkeitskorrekturen werden als neue Beobachtung gespeichert; die Historie wird nicht überschrieben.

## Lokale Pfade

Der produktive Einstiegspunkt `watch live PC-0001` verwendet die konfigurierten öffentlichen Quellen aus `30-Procurement/config/sources.yaml`. Er beobachtet und empfiehlt nur; Kaufentscheidung und Bestellung bleiben beim Project Owner.

Die Pfade können über `HDC_PROCUREMENT_DB`, `HDC_PROCUREMENT_LOGS` und `HDC_PROCUREMENT_REPORTS` überschrieben werden. Ein Repository-Versionslabel kann über `HDC_REPOSITORY_VERSION` gesetzt werden; ansonsten wird der letzte Git-Tag oder `unreleased` verwendet.

## Tests

```powershell
python -m pytest
```

Tests verwenden ausschließlich temporäre Datenbanken.

Konfigurationstemplates werden mit `load_yaml_config` geladen und validieren eine Mapping-Struktur. Die Foundation führt noch keine Quellen aus.

## Datenschutz und Einschränkungen

Der lokale HTML-Report wird aus `30-Procurement/templates/procurement-report.html` erzeugt. Betriebsabläufe sind in `30-Procurement/operations/Operations-Runbook.md` dokumentiert; Task Scheduler und Backup/Restore haben eigene Anleitungen.

Operative Daten, Logs und Reports bleiben lokal. Keine Secrets werden versioniert. Die Runtime enthält noch keine Live-Händlerabrufe, automatische Kaufentscheidung, Bestellung, Benachrichtigung oder KI-Integration.

## Troubleshooting

## Case-Portfolio

Die initiale Case-Portfoliobeobachtung umfasst `PC-0001` bis `PC-0005`.
`PC-0002` bis `PC-0005` starten mit dem Status `WATCHING` und besitzen eigene
Case-Dateien, Budgets, Journals und Reports. Ein Live-Lauf ohne konfigurierte
Quelle ist ein erfolgreicher Beobachtungslauf ohne Angebote; er erzeugt dennoch
den Journal-Eintrag für den Case.

Das Portfolio-Gesamtbudget ist in `30-Procurement/config/portfolio.yaml`
mit Ziel- und Absolutgrenze von jeweils 2.000 EUR dokumentiert. Die Case-
Budgets werden als Anforderungen an die Rule Engine importiert.

- Fehlt Python, zuerst Python 3.12 installieren und erneut `install.ps1` ausführen.
- Fehlt die virtuelle Umgebung, `install.ps1` erneut ausführen.
- Prüfe bei Datenbankproblemen den Pfad mit `db status` und die Schreibrechte des Zielordners.
- Prüfe die gespeicherte Herkunft einer Datenbank über die Tabelle `runtime_metadata`.
