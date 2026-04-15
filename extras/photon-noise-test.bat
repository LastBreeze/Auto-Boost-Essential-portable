@echo off
setlocal
pushd "%~dp0"

echo ========================================================
echo          Auto-Boost Photon Noise Test
echo ========================================================
echo.
echo Please ensure you have placed your source AV1 MKV file 
echo into this folder.
echo.
echo This script will:
echo  1. Rename your source file to "0source.mkv"
echo  2. Generate 5 variations with ISO grain levels:
echo     200, 400, 600, 800, 1000.
echo  3. Launch VSPreview for comparison.
echo.
echo Need to generate an av1 mkv sample of your source?
echo 1. Place your mkv in this folder
echo 2. Run create-sample.bat
echo 3. Encode that sample to av1 using a batch script such as batch-anime-25-high.bat
echo 4. Place the output av1 mkv file into this folder and run photon-test.bat
echo The av1 mkv file should be the only mkv in this folder.
echo Press any key to start generation...
pause >nul

:: Find the first .mkv file that isn't already named 0source.mkv and rename it
for %%f in (*.mkv) do (
    if /I not "%%f"=="0source.mkv" (
        ren "%%f" "0source.mkv"
        goto :continue
    )
)
:continue

call ..\tools\av1an\grav1synth.bat
popd
python "..\tools\photon-test.py"
vspreview.bat