@echo off
set "FAST_PARAMS=--enable-dlf 3 --luminance-qp-bias 20"
set "FINAL_PARAMS=--enable-dlf 3 --luminance-qp-bias 20 --photon-noise 200"
set "FAST_SPEED=faster"
set "FINAL_SPEED=slow"
set "AVX512_FLAG="
set "QUALITY=medium"

:: Leave AVX512_FLAG empty unless you are sure your CPU supports AVX-512.
:: You can edit this file with Notepad++.
:: FAST_PARAMS and FINAL_PARAMS must be matching with the exception of photon/film-grain:
:: Only use --photon-noise or --film-grain in FINAL_PARAMS, adding it to FAST_PARAMS will break metrics.

:: FAST_SPEED and FINAL_SPEED take either a named speed or a preset number [-1-13]:
::   slower=2  slow=4  medium=5  fast=6  faster=8
:: Presets without a name are written as the number itself, for example FINAL_SPEED=1.
:: Always set the effort here, never with --preset in FAST_PARAMS or FINAL_PARAMS:
:: SVT-AV1-Essential gives --speed priority over --preset and would discard the preset.

:: crf to quality guide:
:: 40 lower
:: 35 low
:: 30 medium
:: 25 high
:: 20 higher
del tools\bat*.txt
cls
setlocal enableextensions disabledelayedexpansion
cd /d "%~dp0"

:: Create marker
echo. > "tools\bat-used-%~nx0.txt"

:: Call dispatch.py with parameters
"VapourSynth\python.exe" "tools\dispatch.py" %AVX512_FLAG% --quality %QUALITY% --final-speed %FINAL_SPEED% --fast-speed %FAST_SPEED% --fast-params "%FAST_PARAMS%" --final-params "%FINAL_PARAMS%"

echo All tasks finished.
pause