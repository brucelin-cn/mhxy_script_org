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

echo [1/6] Stop game
python game_launcher.py stop --target game --json || goto :fail_stop_game
powershell -NoProfile -Command "Start-Sleep -Seconds 1"

echo [2/6] Stop launcher
python game_launcher.py stop --target launcher --json || goto :fail_stop_launcher
powershell -NoProfile -Command "Start-Sleep -Seconds 2"

echo [3/6] Start launcher
python game_launcher.py start --json || goto :fail_start_launcher
powershell -NoProfile -Command "Start-Sleep -Seconds 5"

echo [4/6] Click start-game
python game_launcher_auto.py start-game --json || goto :fail_start_game
powershell -NoProfile -Command "Start-Sleep -Seconds 8"

echo [5/6] Account enter-game
python game_launcher_auto.py account-enter --json --retries 8 || goto :fail_account_enter
powershell -NoProfile -Command "Start-Sleep -Seconds 3"

echo [6/6] Server login-game
python game_launcher_auto.py server-enter --json --retries 8 || goto :fail_server_enter

echo Full start completed successfully.
pause
exit /b 0

:fail_stop_game
echo Full start failed at step 1: stop game
pause
exit /b 1

:fail_stop_launcher
echo Full start failed at step 2: stop launcher
pause
exit /b 1

:fail_start_launcher
echo Full start failed at step 3: start launcher
pause
exit /b 1

:fail_start_game
echo Full start failed at step 4: click start-game
pause
exit /b 1

:fail_account_enter
echo Full start failed at step 5: account enter-game
pause
exit /b 1

:fail_server_enter
echo Full start failed at step 6: server login-game
pause
exit /b 1
