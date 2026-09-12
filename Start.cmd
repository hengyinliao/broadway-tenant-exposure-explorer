@echo off
start "Broadway Tenant Exposure" /min python "%~dp0scripts\serve.py"
timeout /t 2 /nobreak >nul
start "" http://127.0.0.1:5190
