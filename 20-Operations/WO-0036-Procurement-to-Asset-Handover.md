---
document: WO-0036-Procurement-to-Asset-Handover.md
version: 1.0
status: Accepted
owner: Project Owner
reviewed_by: Lead Architect
last_review: "2026-08-03"
work_order: WO-0036
related_release: knowledge-v1.4.3
classification: Workspace
---

# PC-0001 Closure and Asset Acceptance Handover

## Übergabeentscheidung

PC-0001 ist fachlich abgeschlossen und besitzt den Procurement-Status
`PURCHASED`. Der Case bleibt einschließlich Kandidaten, Preisgrenzen,
Entscheidungsgrundlage, Reports und gespeicherter Beobachtungen erhalten, wird
aber nicht mehr durch den täglichen Portfolio-Watch ausgeführt. Für einen
abgeschlossenen Case erzeugt die Statuslogik ausschließlich `CLOSED` und keine
Kaufempfehlung.

Ab diesem Übergang ist `UPS-RTR-01` in der Asset Registry die führende Quelle für
den Betriebszustand. Procurement darf weder den Assetstatus ableiten noch den
Übergang nach `PRODUCTION` auslösen.

## Bekannte Assetdaten

| Feld | Wert |
|---|---|
| Asset-ID | UPS-RTR-01 |
| Hersteller | Eaton |
| Modell | 3S850D |
| Produktbezeichnung | Eaton 3S 850 DIN |
| Infrastruktur | gateway |
| Im Rack montiert | false |
| Procurement-Herkunft | PC-0001 |
| Lifecycle | ACCEPTANCE |

Seriennummer, Kaufdatum und Garantieende bleiben `PENDING_ACCEPTANCE`; es werden
keine unbekannten Werte ergänzt.

## Reale externe Verbraucher

Die Router-USV versorgt aktuell:

- Speedport Smart 4,
- Telefon,
- Elspet Automatic Litter Box.

Diese drei Verbraucher sind externe Lasten und ausdrücklich keine HDC-OS-Assets.
Sie erscheinen nur als erlaubte externe Relationship-Ziele im Power Graph. Das
Katzenklo wird nicht in der Assetliste registriert.

## Offene Acceptance-Blocker

- Seriennummer dokumentieren,
- Kaufdatum bestätigen,
- Garantie erfassen,
- automatischen Batteriebetrieb erfolgreich testen,
- Rückkehr auf Netzbetrieb erfolgreich testen,
- Acceptance vollständig dokumentieren.

Bis alle Blocker geschlossen sind, bleibt `UPS-RTR-01` in `ACCEPTANCE`; ein
Wechsel nach `PRODUCTION` ist nicht Bestandteil von WO-0036.

## Historien- und Watch-Regel

Nur Cases mit Status `WATCHING` werden ausgewertet und erhalten neue Reports
oder Empfehlungen. Der Reimport eines bereits abgeschlossenen Cases aktualisiert
seinen Abschlussstatus, löscht aber keine vorhandenen Requirements,
Evaluations-, Angebots- oder Preishistorien. PC-0002 bis PC-0005 bleiben
unverändert.
