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

python game_launcher_auto.py account-enter --json --retries 8
pause
