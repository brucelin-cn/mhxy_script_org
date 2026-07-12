@echo off
chcp 65001
cd /d "%~dp0"
cd ..

net session >nul 2>&1
if %errorLevel% == 0 (
    echo Administrative permissions confirmed. Continuing...
) else (
    echo Requesting administrative privileges...
    powershell start -verb runas '"%~f0"'
    exit /b
)

powershell -NoProfile -Command "Start-Sleep -Seconds 5"
python game_launcher_auto.py enter-game --json --retries 8
pause
