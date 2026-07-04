@echo off
cd /d D:\projekty\pdf_sign_remover
"C:\Program Files\Python312\python.exe" -m PyInstaller --onefile --windowed --name "PDF Signature Remover" --noconfirm pdf_sign_remover.py
echo EXITCODE=%errorlevel%
