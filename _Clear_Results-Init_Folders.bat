@REM Delete all local subdirectories except for ".git"
@echo off
echo Warning: This script will delete all subfolders except for the ".git" folder.
echo Are you sure you want to continue? (Y/N)
choice /C YN /M "Press Y for Yes or N for No"
if errorlevel 2 goto end
if errorlevel 1 goto proceed

:proceed
for /d %%d in (*) do (
    if /i not "%%d" == ".git" if /i not "%%d" == "_Archive" (
        rmdir /s /q "%%d"
    )
)
echo All subfolders except ".git" have been deleted.

echo Creating output directories...

mkdir "Output_CSV_TSContingency"
mkdir "Output_CSV_TSLimitViolation"
mkdir "Output_CSV_TSResultAnalysisViolation"
mkdir "Output_CSV_TSResultEvent"
mkdir "Output_CSV_TSValidation"

echo Creating directories for each PWB case...
for %%a in (*.pwb) do mkdir "%~dp0%%~na" 

echo Directories have been created successfully.

pause
goto end

:end
echo Exiting script.
