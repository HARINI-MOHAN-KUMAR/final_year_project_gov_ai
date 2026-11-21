@echo off
title GovGuide AI Launcher
where python >nul 2>&1
if %errorlevel% equ 0 (
    python "%~dp0run.py" %*
    goto end
)
where py >nul 2>&1
if %errorlevel% equ 0 (
    py "%~dp0run.py" %*
    goto end
)
echo Python was not found in PATH!
echo Please install Python 3.11+ and add it to PATH.
pause
:end
