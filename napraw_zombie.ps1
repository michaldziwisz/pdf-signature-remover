# =====================================================================
#  Naprawa: usuniecie pakietow-zombie o tozsamosci UsuwaniePodpisowPDF
#  i ponowna instalacja swiezego MSIX.
#  Przyczyna bledu 0x80070490 (Indexed state handler): dwa osierocone
#  wpisy w rejestrze pakietow (NousResearch.* z certem testowym oraz
#  MichaDziwisz.*) BEZ zawartosci - blokuja kazda nowa instalacje.
#  URUCHOM JAKO ADMINISTRATOR.
# =====================================================================

$ErrorActionPreference = "Continue"
$log = "D:\projekty\pdf_sign_remover\naprawa_zombie.log"
if (Test-Path $log) { Remove-Item $log -Force }
Start-Transcript -Path $log -Force | Out-Null

$czyAdmin = ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
if (-not $czyAdmin) {
    Write-Host "BLAD: uruchom PowerShell JAKO ADMINISTRATOR." -ForegroundColor Red
    Stop-Transcript | Out-Null
    Read-Host "Enter konczy"
    exit 1
}
Write-Host "[1] Uprawnienia administratora: OK"
Write-Host ""

# --- 2. Usun WSZYSTKIE pakiety o tej tozsamosci (biezacy user i AllUsers) ---
Write-Host "[2] Usuwam pakiety-zombie o nazwie *UsuwaniePodpisowPDF* ..."
$do_usuniecia = Get-AppxPackage -AllUsers "*UsuwaniePodpisowPDF*" -ErrorAction SilentlyContinue
if (-not $do_usuniecia) { $do_usuniecia = Get-AppxPackage "*UsuwaniePodpisowPDF*" -ErrorAction SilentlyContinue }
if ($do_usuniecia) {
    foreach ($pkg in $do_usuniecia) {
        Write-Host ("    usuwam: " + $pkg.PackageFullName)
        try {
            Remove-AppxPackage -Package $pkg.PackageFullName -AllUsers -ErrorAction Stop
            Write-Host "      OK (AllUsers)"
        } catch {
            Write-Host ("      AllUsers nie poszlo (" + $_.Exception.Message + "), probuje bez -AllUsers...")
            try {
                Remove-AppxPackage -Package $pkg.PackageFullName -ErrorAction Stop
                Write-Host "      OK"
            } catch {
                Write-Host ("      BLAD usuwania: " + $_.Exception.Message) -ForegroundColor Yellow
            }
        }
    }
} else {
    Write-Host "    (nie znaleziono zadnych - moze juz czysto)"
}

Write-Host ""
Write-Host "[3] Weryfikacja - czy cos jeszcze zostalo:"
$reszta = Get-AppxPackage -AllUsers "*UsuwaniePodpisowPDF*" -ErrorAction SilentlyContinue
if ($reszta) {
    $reszta | ForEach-Object { Write-Host ("    NADAL JEST: " + $_.PackageFullName + " status=" + $_.Status) -ForegroundColor Yellow }
    Write-Host "    Zombie nie zeszly - przerwij i pokaz log agentowi." -ForegroundColor Yellow
} else {
    Write-Host "    Czysto - zaden pakiet tej tozsamosci nie zostal."
}

Write-Host ""
Write-Host "[4] Dodaje certyfikat testowy do zaufanych..."
$cer  = "D:\projekty\pdf_sign_remover\msix_test_cert.cer"
$msix = "D:\projekty\pdf_sign_remover\PDFSignatureRemover.msix"
try {
    Import-Certificate -FilePath $cer -CertStoreLocation "Cert:\LocalMachine\TrustedPeople" | Out-Null
    Write-Host "    Certyfikat OK"
} catch {
    Write-Host ("    Certyfikat - blad lub juz dodany: " + $_.Exception.Message)
}

Write-Host ""
Write-Host "[5] Instaluje swiezy pakiet MSIX..."
try {
    Add-AppxPackage -Path $msix -ErrorAction Stop
    Write-Host "    [SUKCES] Pakiet zainstalowany!" -ForegroundColor Green
} catch {
    Write-Host ("    [BLAD] " + $_.Exception.Message) -ForegroundColor Red
}

Write-Host ""
Write-Host "[6] Stan koncowy pakietu:"
Get-AppxPackage "*UsuwaniePodpisowPDF*" -ErrorAction SilentlyContinue | ForEach-Object {
    Write-Host ("    " + $_.PackageFullName + " status=" + $_.Status)
    Write-Host ("       PackageUserInfo: " + (($_.PackageUserInformation | ForEach-Object { $_.InstallState }) -join ", "))
}

Write-Host ""
Write-Host "===== KONIEC. Log: $log ====="
Stop-Transcript | Out-Null
Read-Host "Nacisnij Enter, aby zakonczyc"
