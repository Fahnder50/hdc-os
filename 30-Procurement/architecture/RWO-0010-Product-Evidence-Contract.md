# RWO-0010 – Product Evidence and Purchase Eligibility

## Kompatible Ergänzung

Der Live-Adapter liefert weiterhin ausschließlich Angebots- und Händlerdaten.
Technische Modelldaten kommen aus dem versionierten lokalen Katalog unter
`catalog/products/`. Der Procurement Service verbindet beide Datenströme über
die exakte Modellnummer; Varianten werden nicht aus Familienbeziehungen
abgeleitet.

## Evidenzvertrag

Jede technische Aussage wird als `verified_true`, `verified_false` oder
`unknown` geführt. `unknown` darf keine positive Regelbewertung erzeugen.
Evidenz wird mit Quelle, Quellentyp, Prüfdatum und Vertrauensstatus gespeichert
und als Snapshot an der Beobachtung erhalten.

USB-Datenschnittstelle, Linux-Monitoring und NUT-Kompatibilität sind getrennte
Merkmale. Ein IEC-C13-Ausgang erzeugt eine sichtbare Kabelbedingung; Schuko ist
bevorzugt, aber keine harte Ausschlussregel.

Unbekannte Versandkosten bleiben unbekannt. Der Endpreis wird nicht als
vollständig ausgegeben; ein Angebot kann nur als `CONDITIONAL_BUY` erscheinen,
wenn Checkout-Preis, Adapterkabel und Laufzeitbedingungen vor dem Kauf geprüft
werden. Bestellungen bleiben außerhalb der Runtime.

Die Case-Annahme für PC-0001 dokumentiert 40 W Designlast und vier Stunden
Wunschlaufzeit. Für diese Laufzeit liegt bei den drei katalogisierten Varianten
noch kein belastbarer Nachweis vor.
