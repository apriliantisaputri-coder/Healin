@echo off
setlocal
cd /d "%~dp0"

echo ============================================
echo   Heal.In - Setup ^& Jalankan Otomatis
echo ============================================
echo.

if not exist ".env" (
    echo [PENTING] File .env belum ada.
    echo Menyalin dari .env.example...
    copy /Y ".env.example" ".env" >nul
    echo.
    echo Silakan buka file .env dengan Notepad, isi DB_PASSWORD
    echo sesuai password PostgreSQL kamu, simpan, lalu jalankan
    echo ulang start.bat ini.
    echo.
    notepad ".env"
    pause
    exit /b 1
)

echo Mengecek/menginstall dependency Python...
pip install -r requirements.txt
if errorlevel 1 (
    echo.
    echo [GAGAL] pip install bermasalah. Pastikan Python ^& pip sudah
    echo ter-install dan bisa diakses dari terminal ini.
    pause
    exit /b 1
)

echo.
echo Menyiapkan database, migrasi, dan seed data...
python run_all.py

echo.
echo Server sudah berhenti.
pause
