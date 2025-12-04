@echo off
cd /d "%~dp0"

pyinstaller PoseScaleConfigEditor.spec --clean

echo.

