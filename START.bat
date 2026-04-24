@echo off
title Gaman AI Server
color 0A
echo.
echo ============================================
echo   GAMAN AI - STARTING SERVER
echo ============================================
echo.
cd /d C:\Gamansai\ai
echo Killing old processes...
taskkill /f /im python.exe /fi "WINDOWTITLE eq Gaman*" >nul 2>&1
timeout /t 2 /nobreak >nul
echo.
echo Starting server...
echo.
python -m uvicorn app:app --host 127.0.0.1 --port 8000 --reload
pause
