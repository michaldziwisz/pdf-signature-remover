@echo off
setlocal
set SDK=C:\Program Files (x86)\Windows Kits\10\bin\10.0.26100.0\x64
cd /d D:\projekty\pdf_sign_remover

echo === makepri: konfiguracja ===
if exist priconfig.xml del /q priconfig.xml
"%SDK%\makepri.exe" createconfig /cf priconfig.xml /dq pl-PL_en-US /o
echo CFG_EXIT=%errorlevel%

echo === makepri: index (resources.pri) ===
if exist msix_pkg\resources.pri del /q msix_pkg\resources.pri
"%SDK%\makepri.exe" new /pr msix_pkg /cf priconfig.xml /mn msix_pkg\AppxManifest.xml /of msix_pkg\resources.pri /o
echo PRI_EXIT=%errorlevel%

echo === makeappx pack ===
"%SDK%\makeappx.exe" pack /d msix_pkg /p PDFSignatureRemover.msix /o
echo PACK_EXIT=%errorlevel%

echo === signtool sign ===
if "%MSIX_CERT_PASSWORD%"=="" (
  echo BLAD: ustaw zmienna srodowiskowa MSIX_CERT_PASSWORD haslem do msix_test_cert.pfx
  echo Przyklad: set MSIX_CERT_PASSWORD=twoje_haslo
  goto :end
)
"%SDK%\signtool.exe" sign /fd SHA256 /a /f msix_test_cert.pfx /p %MSIX_CERT_PASSWORD% PDFSignatureRemover.msix
echo SIGN_EXIT=%errorlevel%
:end
endlocal
