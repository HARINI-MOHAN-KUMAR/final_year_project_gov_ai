@echo off
title GovGuide AI - Single-Port Launcher
powershell.exe -NoProfile -ExecutionPolicy Bypass -File "%~dp0run_dev.ps1" -Fast
set "EXIT_CODE=%ERRORLEVEL%"
if not "%EXIT_CODE%"=="0" pause
exit /b %EXIT_CODE%
