@REM Open all PowerWorld cases in the local directory. 
@echo off
echo Warning: This script open all local PWB files.
echo Are you sure you want to continue? (Y/N)
choice /C YN /M "Press Y for Yes or N for No"
if errorlevel 2 goto end
if errorlevel 1 goto proceed

:proceed
for %%a in (*.pwb) do start "" "%%a"

echo All local PWB files have been opened.

pause
goto end

:end
echo Exiting script.
