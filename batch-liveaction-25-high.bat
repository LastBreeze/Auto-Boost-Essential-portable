@echo off
set "FAST_PARAMS=--ac-bias 1.0 --tx-bias 3 --luminance-qp-bias 20 --enable-alt-dlf 1 --qp-scale-compress-strength 3"
set "FINAL_PARAMS=--ac-bias 1.0 --tx-bias 3 --luminance-qp-bias 20 --enable-alt-dlf 1 --qp-scale-compress-strength 3 --complex-hvs 1 --photon-noise 200"
set "FAST_SPEED=faster"
set "FINAL_SPEED=slow"
set "QUALITY=high"

:: Only use --photon-noise or --film-grain in FINAL_PARAMS, adding it to FAST_PARAMS will break metrics.

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
"VapourSynth\python.exe" "tools\dispatch.py" --quality %QUALITY% --ssimu2 --final-speed %FINAL_SPEED% --fast-speed %FAST_SPEED% --fast-params "%FAST_PARAMS%" --final-params "%FINAL_PARAMS%"

echo All tasks finished.
pause