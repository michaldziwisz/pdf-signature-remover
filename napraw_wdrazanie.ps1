# =====================================================================
#  Naprawa podsystemu wdrazania MSIX
#  Problem: C:\Program Files\WindowsApps\Deleted zawiera osierocone
#  resztki (Microsoft.WindowsAlarms), ktorych system nie moze usunac
#  (blad 0x5) -> KAZDA instalacja MSIX pada na 0x80070490.
#  Ten skrypt przejmuje wlasnosc tego folderu i czysci jego zawartosc.
#  URUCHOM JAKO ADMINISTRATOR.
# =====================================================================

$ErrorActionPreference = "Continue"

Write-Host ""
Write-Host "=== Naprawa folderu WindowsApps\Deleted ==="
Write-Host ""

# --- 1. Sprawdz uprawnienia administratora ---
$czyAdmin = ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
if (-not $czyAdmin) {
    Write-Host "BLAD: brak uprawnien administratora. Uruchom PowerShell jako administrator." -ForegroundColor Red
    Read-Host "Enter konczy"
    exit 1
}
Write-Host "[1/4] Uprawnienia administratora: OK"

$deleted = "C:\Program Files\WindowsApps\Deleted"

if (-not (Test-Path -LiteralPath $deleted)) {
    Write-Host "Folder Deleted nie istnieje - nic do naprawy. Sprobuj od razu instalacji." -ForegroundColor Green
    Read-Host "Enter konczy"
    exit 0
}

# --- 2. Przejmij wlasnosc folderu Deleted (rekurencyjnie) ---
Write-Host "[2/4] Przejmuje wlasnosc folderu (takeown)..."
& takeown.exe /f "$deleted" /r /d y | Out-Null

# --- 3. Nadaj administratorom pelne prawa ---
Write-Host "[3/4] Nadaje uprawnienia (icacls)..."
& icacls.exe "$deleted" /grant "*S-1-5-32-544:(OI)(CI)F" /t /c | Out-Null

# --- 4. Usun zawartosc folderu Deleted ---
Write-Host "[4/4] Usuwam osierocona zawartosc..."
$usuniete = 0
$bledy = 0
$elementy = Get-ChildItem -LiteralPath $deleted -Force -ErrorAction SilentlyContinue
foreach ($el in $elementy) {
    try {
        Remove-Item -LiteralPath $el.FullName -Recurse -Force -ErrorAction Stop
        $usuniete = $usuniete + 1
    } catch {
        $bledy = $bledy + 1
        $nazwa = $el.Name
        $powod = $_.Exception.Message
        Write-Host ("   nie udalo sie usunac: " + $nazwa + " - " + $powod) -ForegroundColor Yellow
    }
}
Write-Host ("   Usunieto elementow: " + $usuniete + ", nieusuniete: " + $bledy)

Write-Host ""
if ($bledy -eq 0) {
    Write-Host "=== GOTOWE. Folder Deleted wyczyszczony. ===" -ForegroundColor Green
    Write-Host "Teraz uruchom ponownie instalacje pakietu:"
    Write-Host '   powershell -ExecutionPolicy Bypass -File "D:\projekty\pdf_sign_remover\instaluj_test.ps1"'
} else {
    Write-Host "=== Czesc plikow pozostala. ===" -ForegroundColor Yellow
    Write-Host "Sprobuj mimo to instalacji; jesli dalej blad 0x80070490 - pomoze restart komputera"
    Write-Host "(zaplanowane usuniecie zawartosci Deleted wykonuje sie przy starcie systemu)."
}
Write-Host ""
Read-Host "Nacisnij Enter, aby zakonczyc"
