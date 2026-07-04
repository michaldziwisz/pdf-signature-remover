# -*- coding: utf-8 -*-
"""
PDF Signature Remover — prosty, dostępny program dla Windows.

Usuwa wszystkie cyfrowe podpisy z plików PDF, zachowując
pełną treść dokumentu i wszystkie strony.

Interfejs dwujęzyczny: automatycznie polski na polskim systemie Windows,
angielski na każdym innym. Zbudowany w wxPython (natywne kontrolki Win32
-> czytelne dla NVDA/JAWS).
"""

import os
import sys
import threading

import wx
import pikepdf


# --------------------------------------------------------------------------
#  Lokalizacja: pl na polskim systemie, en na kazdym innym
# --------------------------------------------------------------------------
def wykryj_jezyk():
    """Zwraca 'pl' gdy jezyk systemu zaczyna sie od 'pl', inaczej 'en'."""
    try:
        import ctypes
        # GetUserDefaultUILanguage -> LANGID; nazwa lokalizacji
        windll = ctypes.windll.kernel32
        buf = ctypes.create_unicode_buffer(85)
        lcid = windll.GetUserDefaultLCID()
        windll.GetLocaleInfoW(lcid, 0x59, buf, 85)  # LOCALE_SISO639LANGNAME
        kod = (buf.value or "").lower()
        if kod.startswith("pl"):
            return "pl"
    except Exception:
        pass
    # zapasowo: zmienne srodowiskowe / locale
    try:
        import locale
        loc = (locale.getdefaultlocale()[0] or "")
        if loc.lower().startswith("pl"):
            return "pl"
    except Exception:
        pass
    return "en"


T = {
    "pl": {
        "app_title": "PDF Signature Remover",
        "add_files": "Dodaj &pliki...",
        "add_files_name": "Dodaj pliki PDF",
        "add_folder": "Dodaj &folder...",
        "add_folder_name": "Dodaj cały folder z plikami PDF",
        "remove_from_list": "Usuń z &listy",
        "remove_from_list_name": "Usuń zaznaczony plik z listy",
        "clear_list": "Wyczyść lis&tę",
        "clear_list_name": "Wyczyść całą listę",
        "list_label": "Lista plików PDF:",
        "list_name": "Lista plików PDF",
        "col_file": "Plik",
        "col_sigs": "Podpisy",
        "col_status": "Status",
        "remove_btn": "&Usuń podpisy ze wszystkich",
        "remove_btn_name": "Usuń podpisy ze wszystkich plików na liście",
        "log_label": "Informacje i postęp:",
        "log_name": "Informacje i postęp",
        "status_ready": "Gotowe. Dodaj pliki PDF, aby rozpocząć.",
        "menu_file": "&Plik",
        "menu_add_files": "Dodaj &pliki...\tCtrl+O",
        "menu_add_folder": "Dodaj &folder...\tCtrl+D",
        "menu_remove": "&Usuń podpisy ze wszystkich\tF5",
        "menu_quit": "&Zakończ\tAlt+F4",
        "menu_help": "P&omoc",
        "menu_about": "&O programie",
        "about_title": "O programie",
        "about_text": (
            "PDF Signature Remover\n\n"
            "Program usuwa wszystkie cyfrowe podpisy z plików PDF, "
            "zachowując pełną treść dokumentów i wszystkie strony.\n\n"
            "Sposób użycia: dodaj pliki PDF (pojedynczo lub cały folder), "
            "kliknij „Usuń podpisy ze wszystkich”. Dla każdego pliku powstaje "
            "nowy plik obok oryginału z dopiskiem „_bez_podpisow”."
        ),
        "dlg_files": "Wybierz pliki PDF",
        "wildcard": "Pliki PDF (*.pdf)|*.pdf",
        "dlg_folder": "Wybierz folder z plikami PDF",
        "added_files": "Dodano plików: {n}.",
        "folder_added": "Folder: {kat} — dodano plików: {n}.",
        "on_list": "Na liście {n} plików.",
        "read_err": "BŁĄD odczytu: {f} — {e}",
        "st_no_sigs": "brak podpisów",
        "st_ready": "gotowy",
        "st_read_err": "błąd odczytu",
        "nothing_selected_t": "Nic nie zaznaczono",
        "nothing_selected": "Najpierw zaznacz plik na liście (strzałkami).",
        "removed_from_list": "Usunięto z listy: {f}",
        "cleared": "Wyczyszczono listę.",
        "list_empty": "Lista pusta. Dodaj pliki PDF.",
        "no_files_t": "Brak plików",
        "no_files": "Najpierw dodaj pliki PDF.",
        "removing": "Usuwam podpisy...",
        "starting": "Rozpoczynam przetwarzanie {n} plików...",
        "skipped_row": "pominięto (brak podpisów)",
        "skipped_log": "Pominięto (brak podpisów): {f}",
        "done_row": "gotowe — zapisano",
        "ok_log": "OK: {a}  ->  {b}",
        "err_row": "BŁĄD",
        "err_log": "BŁĄD: {f} — {e}",
        "summary": "Zakończono. Przetworzono: {ok}, pominięto: {sk}, błędy: {er}.",
        "done_title": "Zakończono",
        "done_extra": (
            "\n\nPliki bez podpisów zapisano obok oryginałów "
            "z dopiskiem „_bez_podpisow”."
        ),
        "suffix": "_bez_podpisow",
    },
    "en": {
        "app_title": "PDF Signature Remover",
        "add_files": "Add &files...",
        "add_files_name": "Add PDF files",
        "add_folder": "Add f&older...",
        "add_folder_name": "Add an entire folder of PDF files",
        "remove_from_list": "Remove from &list",
        "remove_from_list_name": "Remove the selected file from the list",
        "clear_list": "Clear lis&t",
        "clear_list_name": "Clear the entire list",
        "list_label": "PDF file list:",
        "list_name": "PDF file list",
        "col_file": "File",
        "col_sigs": "Signatures",
        "col_status": "Status",
        "remove_btn": "&Remove signatures from all",
        "remove_btn_name": "Remove signatures from all files in the list",
        "log_label": "Information and progress:",
        "log_name": "Information and progress",
        "status_ready": "Ready. Add PDF files to begin.",
        "menu_file": "&File",
        "menu_add_files": "Add &files...\tCtrl+O",
        "menu_add_folder": "Add f&older...\tCtrl+D",
        "menu_remove": "&Remove signatures from all\tF5",
        "menu_quit": "&Quit\tAlt+F4",
        "menu_help": "&Help",
        "menu_about": "&About",
        "about_title": "About",
        "about_text": (
            "PDF Signature Remover\n\n"
            "This program removes all digital signatures from PDF "
            "files, keeping the full document content and all pages.\n\n"
            "How to use: add PDF files (individually or a whole folder), then "
            "click “Remove signatures from all”. For each file a new file is "
            "created next to the original with the “_no_signatures” suffix."
        ),
        "dlg_files": "Select PDF files",
        "wildcard": "PDF files (*.pdf)|*.pdf",
        "dlg_folder": "Select a folder of PDF files",
        "added_files": "Files added: {n}.",
        "folder_added": "Folder: {kat} — files added: {n}.",
        "on_list": "{n} files in the list.",
        "read_err": "READ ERROR: {f} — {e}",
        "st_no_sigs": "no signatures",
        "st_ready": "ready",
        "st_read_err": "read error",
        "nothing_selected_t": "Nothing selected",
        "nothing_selected": "First select a file in the list (arrow keys).",
        "removed_from_list": "Removed from list: {f}",
        "cleared": "List cleared.",
        "list_empty": "List empty. Add PDF files.",
        "no_files_t": "No files",
        "no_files": "First add PDF files.",
        "removing": "Removing signatures...",
        "starting": "Starting to process {n} files...",
        "skipped_row": "skipped (no signatures)",
        "skipped_log": "Skipped (no signatures): {f}",
        "done_row": "done — saved",
        "ok_log": "OK: {a}  ->  {b}",
        "err_row": "ERROR",
        "err_log": "ERROR: {f} — {e}",
        "summary": "Finished. Processed: {ok}, skipped: {sk}, errors: {er}.",
        "done_title": "Finished",
        "done_extra": (
            "\n\nFiles without signatures were saved next to the originals "
            "with the “_no_signatures” suffix."
        ),
        "suffix": "_no_signatures",
    },
}

LANG = wykryj_jezyk()


def tr(klucz, **kw):
    tekst = T[LANG].get(klucz, T["en"].get(klucz, klucz))
    return tekst.format(**kw) if kw else tekst


# --------------------------------------------------------------------------
#  Logika PDF
# --------------------------------------------------------------------------
def policz_podpisy(sciezka):
    """Zwraca liczbę cyfrowych podpisów w pliku PDF (pola /Sig)."""
    pdf = pikepdf.open(sciezka)
    try:
        liczba = 0
        acro = pdf.Root.get("/AcroForm")
        if acro is not None and acro.get("/Fields") is not None:
            for pole in acro.Fields:
                if pole.get("/FT") == "/Sig":
                    liczba += 1
        return liczba
    finally:
        pdf.close()


def usun_podpisy(wejscie, wyjscie):
    """Usuwa wszystkie podpisy cyfrowe z pliku PDF i zapisuje wynik."""
    pdf = pikepdf.open(wejscie)
    try:
        usuniete = 0
        root = pdf.Root

        for strona in pdf.pages:
            annots = strona.get("/Annots")
            if not annots:
                continue
            zachowaj = []
            for a in annots:
                jest_podpisem = (
                    a.get("/Subtype") == "/Widget" and a.get("/FT") == "/Sig"
                )
                rodzic = a.get("/Parent")
                if (
                    not jest_podpisem
                    and a.get("/Subtype") == "/Widget"
                    and rodzic is not None
                    and rodzic.get("/FT") == "/Sig"
                ):
                    jest_podpisem = True
                if jest_podpisem:
                    usuniete += 1
                else:
                    zachowaj.append(a)
            if zachowaj:
                strona.Annots = pikepdf.Array(zachowaj)
            elif "/Annots" in strona:
                del strona.Annots

        acro = root.get("/AcroForm")
        if acro is not None:
            pola = acro.get("/Fields")
            if pola is not None:
                zachowaj = [p for p in pola if p.get("/FT") != "/Sig"]
                if zachowaj:
                    acro.Fields = pikepdf.Array(zachowaj)
                    if "/SigFlags" in acro:
                        del acro.SigFlags
                else:
                    del root.AcroForm

        if "/Perms" in root:
            del root.Perms

        pdf.save(wyjscie)
        return usuniete
    finally:
        pdf.close()


def sciezka_wyjscia(wejscie):
    """Buduje ścieżkę pliku wynikowego z sufiksem zależnym od języka."""
    katalog, nazwa = os.path.split(wejscie)
    rdzen, rozsz = os.path.splitext(nazwa)
    return os.path.join(katalog, rdzen + tr("suffix") + rozsz)


KOL_PLIK = 0
KOL_PODPISY = 1
KOL_STATUS = 2


class Ramka(wx.Frame):
    def __init__(self):
        super().__init__(None, title=tr("app_title"), size=(760, 560))
        self.pliki = []

        panel = wx.Panel(self)
        glowny = wx.BoxSizer(wx.VERTICAL)

        rzad_dodaj = wx.BoxSizer(wx.HORIZONTAL)
        self.btn_dodaj_pliki = wx.Button(panel, label=tr("add_files"))
        self.btn_dodaj_pliki.SetName(tr("add_files_name"))
        self.btn_dodaj_pliki.Bind(wx.EVT_BUTTON, self.na_dodaj_pliki)
        rzad_dodaj.Add(self.btn_dodaj_pliki, 0, wx.RIGHT, 8)

        self.btn_dodaj_folder = wx.Button(panel, label=tr("add_folder"))
        self.btn_dodaj_folder.SetName(tr("add_folder_name"))
        self.btn_dodaj_folder.Bind(wx.EVT_BUTTON, self.na_dodaj_folder)
        rzad_dodaj.Add(self.btn_dodaj_folder, 0, wx.RIGHT, 8)

        self.btn_usun_z_listy = wx.Button(panel, label=tr("remove_from_list"))
        self.btn_usun_z_listy.SetName(tr("remove_from_list_name"))
        self.btn_usun_z_listy.Bind(wx.EVT_BUTTON, self.na_usun_z_listy)
        rzad_dodaj.Add(self.btn_usun_z_listy, 0, wx.RIGHT, 8)

        self.btn_wyczysc = wx.Button(panel, label=tr("clear_list"))
        self.btn_wyczysc.SetName(tr("clear_list_name"))
        self.btn_wyczysc.Bind(wx.EVT_BUTTON, self.na_wyczysc)
        rzad_dodaj.Add(self.btn_wyczysc, 0, wx.RIGHT, 8)

        glowny.Add(rzad_dodaj, 0, wx.LEFT | wx.TOP, 10)

        etykieta_lista = wx.StaticText(panel, label=tr("list_label"))
        glowny.Add(etykieta_lista, 0, wx.LEFT | wx.TOP, 10)

        self.lista = wx.ListCtrl(
            panel, style=wx.LC_REPORT | wx.LC_SINGLE_SEL | wx.BORDER_SUNKEN
        )
        self.lista.SetName(tr("list_name"))
        self.lista.InsertColumn(KOL_PLIK, tr("col_file"), width=380)
        self.lista.InsertColumn(KOL_PODPISY, tr("col_sigs"), width=90)
        self.lista.InsertColumn(KOL_STATUS, tr("col_status"), width=240)
        glowny.Add(self.lista, 1, wx.EXPAND | wx.LEFT | wx.RIGHT | wx.TOP, 10)

        self.btn_usun = wx.Button(panel, label=tr("remove_btn"))
        self.btn_usun.SetName(tr("remove_btn_name"))
        self.btn_usun.Bind(wx.EVT_BUTTON, self.na_usun)
        self.btn_usun.Enable(False)
        glowny.Add(self.btn_usun, 0, wx.LEFT | wx.TOP, 10)

        etykieta_log = wx.StaticText(panel, label=tr("log_label"))
        glowny.Add(etykieta_log, 0, wx.LEFT | wx.TOP, 12)

        self.log = wx.TextCtrl(
            panel, style=wx.TE_MULTILINE | wx.TE_READONLY | wx.TE_RICH2
        )
        self.log.SetName(tr("log_name"))
        self.log.SetMinSize((-1, 120))
        glowny.Add(
            self.log, 0, wx.EXPAND | wx.LEFT | wx.RIGHT | wx.BOTTOM | wx.TOP, 10
        )

        panel.SetSizer(glowny)

        self.CreateStatusBar()
        self.SetStatusText(tr("status_ready"))

        pasek = wx.MenuBar()
        menu_plik = wx.Menu()
        mi_pliki = menu_plik.Append(wx.ID_OPEN, tr("menu_add_files"))
        mi_folder = menu_plik.Append(wx.ID_ANY, tr("menu_add_folder"))
        mi_usun = menu_plik.Append(wx.ID_ANY, tr("menu_remove"))
        menu_plik.AppendSeparator()
        mi_koniec = menu_plik.Append(wx.ID_EXIT, tr("menu_quit"))
        pasek.Append(menu_plik, tr("menu_file"))

        menu_pomoc = wx.Menu()
        mi_info = menu_pomoc.Append(wx.ID_ABOUT, tr("menu_about"))
        pasek.Append(menu_pomoc, tr("menu_help"))
        self.SetMenuBar(pasek)

        self.Bind(wx.EVT_MENU, self.na_dodaj_pliki, mi_pliki)
        self.Bind(wx.EVT_MENU, self.na_dodaj_folder, mi_folder)
        self.Bind(wx.EVT_MENU, self.na_usun, mi_usun)
        self.Bind(wx.EVT_MENU, lambda e: self.Close(), mi_koniec)
        self.Bind(wx.EVT_MENU, self.na_info, mi_info)

        self.Centre()
        self.btn_dodaj_pliki.SetFocus()

    def wczytaj_poczatkowe(self, sciezki):
        """Wczytuje pliki PDF podane jako argumenty wiersza poleceń
        (np. przy 'Otwórz za pomocą' w Eksploratorze Windows)."""
        dodane = 0
        for s in sciezki:
            if os.path.isfile(s) and s.lower().endswith(".pdf"):
                if self.dodaj_do_listy(s):
                    dodane += 1
        if dodane:
            self.aktualizuj_przycisk()
            self.dopisz(tr("added_files", n=dodane))
            self.SetStatusText(tr("on_list", n=len(self.pliki)))

    def dopisz(self, tekst):
        self.log.AppendText(tekst + "\n")

    def aktualizuj_przycisk(self):
        self.btn_usun.Enable(len(self.pliki) > 0)

    def dodaj_do_listy(self, sciezka):
        if sciezka in self.pliki:
            return False
        self.pliki.append(sciezka)
        wiersz = self.lista.InsertItem(self.lista.GetItemCount(), sciezka)
        try:
            liczba = policz_podpisy(sciezka)
            self.lista.SetItem(wiersz, KOL_PODPISY, str(liczba))
            self.lista.SetItem(
                wiersz, KOL_STATUS,
                tr("st_no_sigs") if liczba == 0 else tr("st_ready"),
            )
        except Exception as e:
            self.lista.SetItem(wiersz, KOL_PODPISY, "?")
            self.lista.SetItem(wiersz, KOL_STATUS, tr("st_read_err"))
            self.dopisz(tr("read_err", f=sciezka, e=str(e)))
        return True

    def na_info(self, _evt):
        wx.MessageBox(
            tr("about_text"), tr("about_title"),
            wx.OK | wx.ICON_INFORMATION, self,
        )

    def na_dodaj_pliki(self, _evt):
        with wx.FileDialog(
            self, tr("dlg_files"), wildcard=tr("wildcard"),
            style=wx.FD_OPEN | wx.FD_FILE_MUST_EXIST | wx.FD_MULTIPLE,
        ) as dlg:
            if dlg.ShowModal() == wx.ID_CANCEL:
                return
            sciezki = dlg.GetPaths()
        dodano = sum(1 for s in sciezki if self.dodaj_do_listy(s))
        self.dopisz(tr("added_files", n=dodano))
        self.aktualizuj_przycisk()
        self.SetStatusText(tr("on_list", n=len(self.pliki)))
        if self.pliki:
            self.btn_usun.SetFocus()

    def na_dodaj_folder(self, _evt):
        with wx.DirDialog(
            self, tr("dlg_folder"),
            style=wx.DD_DEFAULT_STYLE | wx.DD_DIR_MUST_EXIST,
        ) as dlg:
            if dlg.ShowModal() == wx.ID_CANCEL:
                return
            katalog = dlg.GetPath()
        znalezione = []
        for korzen, _kat, pliki in os.walk(katalog):
            for nazwa in pliki:
                if nazwa.lower().endswith(".pdf"):
                    if "_bez_podpisow" in nazwa.lower() or "_no_signatures" in nazwa.lower():
                        continue
                    znalezione.append(os.path.join(korzen, nazwa))
        dodano = sum(1 for s in sorted(znalezione) if self.dodaj_do_listy(s))
        self.dopisz(tr("folder_added", kat=katalog, n=dodano))
        self.aktualizuj_przycisk()
        self.SetStatusText(tr("on_list", n=len(self.pliki)))
        if self.pliki:
            self.btn_usun.SetFocus()

    def na_usun_z_listy(self, _evt):
        idx = self.lista.GetFirstSelected()
        if idx < 0:
            wx.MessageBox(
                tr("nothing_selected"), tr("nothing_selected_t"),
                wx.OK | wx.ICON_INFORMATION, self,
            )
            return
        usuwany = self.pliki[idx]
        del self.pliki[idx]
        self.lista.DeleteItem(idx)
        self.dopisz(tr("removed_from_list", f=usuwany))
        self.aktualizuj_przycisk()
        self.SetStatusText(tr("on_list", n=len(self.pliki)))

    def na_wyczysc(self, _evt):
        self.pliki = []
        self.lista.DeleteAllItems()
        self.dopisz(tr("cleared"))
        self.aktualizuj_przycisk()
        self.SetStatusText(tr("list_empty"))

    def na_usun(self, _evt):
        if not self.pliki:
            wx.MessageBox(
                tr("no_files"), tr("no_files_t"),
                wx.OK | wx.ICON_WARNING, self,
            )
            return
        self.blokuj_przyciski(True)
        self.SetStatusText(tr("removing"))
        self.dopisz(tr("starting", n=len(self.pliki)))
        pliki_kopia = list(self.pliki)

        def robota():
            ok = sk = er = 0
            for i, wejscie in enumerate(pliki_kopia):
                wyjscie = sciezka_wyjscia(wejscie)
                try:
                    if policz_podpisy(wejscie) == 0:
                        wx.CallAfter(self.status_wiersza, i, tr("skipped_row"))
                        wx.CallAfter(self.dopisz, tr("skipped_log", f=wejscie))
                        sk += 1
                        continue
                    usun_podpisy(wejscie, wyjscie)
                    wx.CallAfter(self.status_wiersza, i, tr("done_row"))
                    wx.CallAfter(
                        self.dopisz,
                        tr("ok_log", a=os.path.basename(wejscie),
                           b=os.path.basename(wyjscie)),
                    )
                    ok += 1
                except Exception as e:
                    wx.CallAfter(self.status_wiersza, i, tr("err_row"))
                    wx.CallAfter(self.dopisz, tr("err_log", f=wejscie, e=str(e)))
                    er += 1
            wx.CallAfter(self.po_wszystkim, ok, sk, er)

        threading.Thread(target=robota, daemon=True).start()

    def status_wiersza(self, wiersz, tekst):
        if wiersz < self.lista.GetItemCount():
            self.lista.SetItem(wiersz, KOL_STATUS, tekst)

    def blokuj_przyciski(self, blokuj):
        for b in (
            self.btn_dodaj_pliki, self.btn_dodaj_folder,
            self.btn_usun_z_listy, self.btn_wyczysc, self.btn_usun,
        ):
            b.Enable(not blokuj)

    def po_wszystkim(self, ok, sk, er):
        self.blokuj_przyciski(False)
        self.aktualizuj_przycisk()
        podsumowanie = tr("summary", ok=ok, sk=sk, er=er)
        self.dopisz(podsumowanie)
        self.SetStatusText(podsumowanie)
        if not getattr(self, "_tryb_auto", False):
            wx.MessageBox(
                podsumowanie + tr("done_extra"), tr("done_title"),
                wx.OK | wx.ICON_INFORMATION, self,
            )
        self.btn_dodaj_pliki.SetFocus()


def main():
    args = sys.argv[1:]
    auto = "--auto" in args
    pliki_arg = [a for a in args if a != "--auto"]
    app = wx.App(False)
    ramka = Ramka()
    ramka.Show()
    # Pliki podane jako argumenty (np. "Otwórz za pomocą" w Eksploratorze)
    if pliki_arg:
        ramka.wczytaj_poczatkowe(pliki_arg)
        # Tryb automatyczny: od razu uruchom usuwanie (do zrzutów/testów)
        if auto:
            ramka._tryb_auto = True
            wx.CallLater(800, ramka.na_usun, None)
    app.MainLoop()


if __name__ == "__main__":
    main()
