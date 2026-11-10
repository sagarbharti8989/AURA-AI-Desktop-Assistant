@echo off
title AURA - AI Desktop Assistant
echo Starting AURA...
python main.py
if %ERRORLEVEL% NEQ 0 (
    echo.
    echo Application exited with an error.
    pause
)

