# PDF Signature Remover

Prosty, w pełni dostępny program dla Windows, który usuwa wszystkie podpisy
cyfrowe z plików PDF, zachowując pełną treść dokumentu i wszystkie strony.

Zaprojektowany z myślą o obsłudze przez czytniki ekranu (NVDA, JAWS) —
natywne kontrolki, pełna obsługa z klawiatury, czytelna lista plików i
komunikaty o postępie.

## Funkcje

- Usuwa wszystkie podpisy cyfrowe z pliku PDF jednym kliknięciem.
- Zachowuje pełną treść dokumentu i wszystkie strony bez zmian.
- Obsługuje wiele plików naraz — pojedyncze pliki lub cały folder.
- Dla każdego pliku tworzy nowy plik obok oryginału (z dopiskiem
  `_bez_podpisow`). Oryginał pozostaje nienaruszony.
- Automatycznie pomija pliki bez podpisów.
- Interfejs dwujęzyczny: automatycznie polski na polskim systemie Windows,
  angielski na pozostałych.

## Jak używać

1. Dodaj pliki PDF (pojedynczo lub cały folder).
2. Kliknij „Usuń podpisy ze wszystkich”.
3. Gotowe pliki znajdziesz obok oryginałów z dopiskiem `_bez_podpisow`.

Możesz też przeciągnąć pliki PDF na ikonę programu lub użyć „Otwórz za
pomocą” w Eksploratorze Windows — zostaną od razu wczytane na listę.

Uwaga: po usunięciu podpisu dokument przestaje być podpisany — czytniki PDF
nie pokażą już informacji „podpisano przez…”. Jest to działanie zamierzone.

## Prywatność

Aplikacja działa w całości lokalnie. Nie zbiera, nie przechowuje ani nie
wysyła żadnych danych. Nie łączy się z internetem. Pełna polityka
prywatności: [strona_prywatnosci/index.html](strona_prywatnosci/index.html)
(publikowana przez GitHub Pages).

## Budowanie ze źródeł (Windows)

Wymagany Python 3.12 oraz Windows SDK (makeappx, makepri, signtool).

```
# instalacja zależności
python -m pip install --user pikepdf wxpython pyinstaller pillow

# build EXE (onedir do pakietu MSIX)
build_msix.bat

# złożenie pakietu MSIX (wymaga certyfikatu i hasła w zmiennej środowiskowej)
set MSIX_CERT_PASSWORD=twoje_haslo
pack_msix.bat
```

Certyfikat testowy (`.pfx`) oraz hasło NIE są częścią repozytorium.
Do publikacji w Microsoft Store pakiet podpisuje sam Microsoft.

## Technologia

- Python 3.12, [wxPython](https://wxpython.org/) (natywne kontrolki Win32).
- [pikepdf](https://github.com/pikepdf/pikepdf) — usuwanie pól `/Sig`,
  widgetów podpisu z AcroForm oraz `/Perms`, z zachowaniem treści i stron.
- Pakowanie: PyInstaller (onedir) + MSIX (Microsoft Store).

## Licencja

Copyright © Michał Dziwisz. Wszelkie prawa zastrzeżone.
