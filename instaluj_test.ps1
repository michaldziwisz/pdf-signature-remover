# =====================================================================
#  Instalacja testowa pakietu MSIX "Usuwanie Podpisow PDF"
#  URUCHOM JAKO ADMINISTRATOR (patrz instrukcja obok).
#  Skrypt: (1) sprawdza uprawnienia admina, (2) dodaje certyfikat
#  testowy do zaufanych, (3) instaluje pakiet, (4) zglasza wynik.
# =====================================================================

$ErrorActionPreference = "Stop"

$katalog = "D:\projekty\pdf_sign_remover"
$cer     = Join-Path $katalog "msix_test_cert.cer"
$msix    = Join-Path $katalog "PDFSignatureRemover.msix"

Write-Host ""
Write-Host "=== Instalacja testowa: PDF Signature Remover ==="
Write-Host ""

# --- 1. Sprawdz uprawnienia administratora ---
$czyAdmin = ([Security.Principal.WindowsPrincipal] `
    [Security.Principal.WindowsIdentity]::GetCurrent() `
    ).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)

if (-not $czyAdmin) {
    Write-Host "BLAD: to okno PowerShell NIE ma uprawnien administratora." -ForegroundColor Red
    Write-Host "Zamknij je i uruchom PowerShell 'jako administrator', potem odpal skrypt ponownie."
    Read-Host "Nacisnij Enter, aby zakonczyc"
    exit 1
}
Write-Host "[1/4] Uprawnienia administratora: OK"

# --- 2. Sprawdz czy pliki istnieja ---
if (-not (Test-Path $cer))  { Write-Host "BLAD: brak pliku certyfikatu: $cer" -ForegroundColor Red; Read-Host "Enter konczy"; exit 1 }
if (-not (Test-Path $msix)) { Write-Host "BLAD: brak pliku pakietu: $msix" -ForegroundColor Red; Read-Host "Enter konczy"; exit 1 }
Write-Host "[2/4] Pliki znalezione: certyfikat i pakiet MSIX"

# --- 3. Dodaj certyfikat testowy do zaufanych (LocalMachine\TrustedPeople) ---
try {
    Import-Certificate -FilePath $cer -CertStoreLocation "Cert:\LocalMachine\TrustedPeople" | Out-Null
    Write-Host "[3/4] Certyfikat testowy dodany do zaufanych (TrustedPeople): OK"
} catch {
    Write-Host "BLAD przy dodawaniu certyfikatu: $($_.Exception.Message)" -ForegroundColor Red
    Read-Host "Nacisnij Enter, aby zakonczyc"
    exit 1
}

# --- 4. Zainstaluj pakiet MSIX ---
# Najpierw usun ewentualna wczesniejsza (np. nieudana) wersje o tej nazwie
try {
    $stare = Get-AppxPackage *UsuwaniePodpisowPDF*, *PDFSignatureRemover* -ErrorAction SilentlyContinue
    if ($stare) {
        $stare | Remove-AppxPackage -ErrorAction SilentlyContinue
        Write-Host "      (usunieto wczesniejsza wersje pakietu)"
    }
} catch { }

try {
    Add-AppxPackage -Path $msix
    Write-Host "[4/4] Pakiet zainstalowany: OK" -ForegroundColor Green
} catch {
    Write-Host "BLAD przy instalacji pakietu: $($_.Exception.Message)" -ForegroundColor Red
    Write-Host "Jesli pakiet o tej nazwie juz istnieje, usun go najpierw:"
    Write-Host "   Get-AppxPackage *PDFSignatureRemover* | Remove-AppxPackage"
    Read-Host "Nacisnij Enter, aby zakonczyc"
    exit 1
}

Write-Host ""
Write-Host "=== GOTOWE ==="
Write-Host "Aplikacja 'PDF Signature Remover' jest teraz w menu Start."
Write-Host "Znajdziesz ja wpisujac 'PDF' po nacisnieciu klawisza Windows."
Write-Host ""
Write-Host "Aby ja pozniej ODINSTALOWAC, uruchom w tym oknie:"
Write-Host "   Get-AppxPackage *PDFSignatureRemover* | Remove-AppxPackage"
Write-Host ""
Read-Host "Nacisnij Enter, aby zakonczyc"
