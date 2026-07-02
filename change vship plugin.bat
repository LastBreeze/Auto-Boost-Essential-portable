@echo off
cd /d "%~dp0"

if exist "VapourSynth\python.exe" (
    "VapourSynth\python.exe" "tools\changevship.py"
) else (
    python "tools\changevship.py"
)

pause
