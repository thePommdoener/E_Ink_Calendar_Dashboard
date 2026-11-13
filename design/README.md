# Design-Mockups

Display: Waveshare 7.5" V2, **800 x 480 px**, schwarz/weiß.

## Raster

Jede Mockup-Datei ist genau **100 Zeichen breit und 30 Zeilen hoch** (inkl. Rahmen).

    1 Zeichen = 8 px breit x 16 px hoch
    Spalte  n -> x = n * 8
    Zeile   m -> y = m * 16

In VS Code unten rechts siehst du "Zeile, Spalte": damit lässt sich jede Position
direkt in Pixel umrechnen. Beim Bearbeiten den **Überschreibmodus** (Taste `Einfg`)
nutzen, dann verrutscht nichts.

## Zeichen-Legende

| Zeichen        | Bedeutung                                         |
|----------------|---------------------------------------------------|
| `+ - \|`        | Rahmen / dünne Linie (1-2 px)                     |
| `====`         | dicke Linie (3-4 px)                              |
| `#`            | schwarz gefüllte Fläche (z. B. große Ziffern)     |
| `[Fr 13.]`     | heutiger Tag, invertiert (weiß auf schwarz)       |
| `[L] [F] [LF]` | Personen-Piktogramm: Frau (Lena), Mann (Fyn), beide nebeneinander (gemeinsam) |
| `#text  #`     | schwarzer Balken mit weißer Schrift über die volle Spaltenbreite (ganztägig) |
| `Messe 2/3`    | mehrtägiger Termin, erscheint an jedem Tag mit Zähler |
| `… / + 2 weitere` | Titel gekürzt / Spalte voll                   |
| GROSSBUCHSTABEN| Überschrift / fett                                |
| normaler Text  | Fließtext, Platzhalter-Inhalt                     |

Text im Mockup ist Beispielinhalt. Schriftgrößen ergeben sich aus der Zeilenhöhe
(1 Zeile ≈ 16 px Schrift); große Elemente einfach über mehrere Zeilen zeichnen.

Anmerkungen gern unterhalb des Rahmens oder in dieser Datei notieren.

## Ansicht

Es gibt nur eine Ansicht: **`ansicht_agenda.txt`**
- links: Wochentag, großes Datum, Monat/KW, Monatskalender (heute markiert), "Stand: …"
- rechts: Terminliste ab heute, Tag für Tag

## Festgelegte Regeln

- Querformat 800 x 480, 4 Graustufen (Weiß, Hellgrau 0xC0, Dunkelgrau 0x80, Schwarz)
  – abschaltbar über `[display] grayscale = false` (dann reines S/W), klare serifenlose Schrift (DejaVu Sans), kein Wetter.
- Aktualisierung alle 15 Minuten.
- Pro Termin nur **Kürzel + Startzeit (oder "ganztägig") + Titel**.
  Personen als Piktogramm (Toilettenschild-Stil): Frau = Lena, Mann = Fyn, beide = gemeinsam.
- Mehrtägige Termine erscheinen **an jedem Tag** erneut, mit Zähler (`Messe 2/3`).
- Tage ohne Termine: kompakter Einzeiler "Mo 16.11.   keine Termine" (ohne Linie).
- **Überlauf:** Es werden nur ganze Tage angezeigt. Passt ein Tag nicht mehr
  vollständig, wird er weggelassen (statt Termine abzuschneiden).
  Ausnahme: Passt schon *heute* nicht komplett, wird heute gekürzt mit "+ X weitere".

## Graustufen-Einsatz

| Element                          | Graustufen-Modus            | S/W-Modus            |
|----------------------------------|-----------------------------|----------------------|
| Tagesüberschrift heute           | schwarzer Balken, weiße Schrift | dicke Linie      |
| Tagesüberschrift andere Tage     | hellgrauer Balken           | dünne Linie          |
| Leere Tage, "ganztägig", KW, Stand | dunkelgrau                | schwarz              |
| Termine von heute, die vorbei sind | dunkelgrau (Icon + Text)  | schwarz              |
| Monatskalender: vergangene Tage  | dunkelgrau                  | schwarz              |
| Monatskalender: aktuelle Woche   | hellgrau hinterlegt         | –                    |

Text immer ohne Kantenglättung (scharf auf E-Paper).
