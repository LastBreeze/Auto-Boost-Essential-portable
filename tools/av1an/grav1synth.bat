echo off
cd /d "%~dp0"
echo Generating photon level 2 test file
grav1synth generate ..\..\extras\0source.mkv -o ..\..\extras\temp2.mkv --iso 200
echo Generating photon level 4 test file
grav1synth generate ..\..\extras\0source.mkv -o ..\..\extras\temp4.mkv --iso 400
echo Generating photon level 6 test file
grav1synth generate ..\..\extras\0source.mkv -o ..\..\extras\temp6.mkv --iso 600
echo Generating photon level 8 test file
grav1synth generate ..\..\extras\0source.mkv -o ..\..\extras\temp8.mkv --iso 800
echo Generating photon level 10 test file
grav1synth generate ..\..\extras\0source.mkv -o ..\..\extras\temp10.mkv --iso 1000