@echo off
cd /d D:\projekty\pdf_sign_remover
"C:\Program Files\Python312\python.exe" -m PyInstaller --onedir --windowed --name "PDFSignatureRemover" --noconfirm --distpath dist_msix pdf_sign_remover.py
echo EXITCODE=%errorlevel%
