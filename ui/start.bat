chcp 65001
@echo off
:: 获取管理员权限
net session >nul 2>&1
if %errorLevel% == 0 (
    echo Administrative permissions confirmed. Continuing...
) else (
    echo Requesting administrative privileges...
    powershell start -verb runas '%0'
    exit /b
)

:: 改成绝对目录
start python "D:\work\mhxy\mhxy_script_org\ui\mhxy_pyqt.py"