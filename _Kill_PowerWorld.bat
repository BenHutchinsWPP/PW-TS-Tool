@REM Kills all instances of PowerWorld currently running.
@echo off
echo Warning: This script kill all running copies of PowerWorld.
echo Are you sure you want to continue? (Y/N)
choice /C YN /M "Press Y for Yes or N for No"
if errorlevel 2 goto end
if errorlevel 1 goto proceed

:proceed
taskkill /F /IM pwrworld.exe
taskkill /F /IM pwslsim23.exe
taskkill /F /IM pwslsim22.exe

echo All running instances of PowerWorld have been killed. 

pause
goto end

:end
echo Exiting script.
