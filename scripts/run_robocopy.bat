@echo off
setlocal EnableExtensions DisableDelayedExpansion
chcp 65001 >nul
title M+S Robocopy Progress

rem Editable Robocopy settings
set "COPY_SUBDIRECTORIES=/S /XJ"
set "COPY_METADATA=/COPY:DAT /DCOPY:T"
set "RETRY_COUNT=3"
set "WAIT_SECONDS=10"
set "LOG_OPTIONS=/V /FP /NP /TEE /NFL /NDL"

rem Required values from Python
set "JOB_FILE=%~1"
set "RESULT_FILE=%~2"
set "COMBINED_LOG_FILE=%~3"
set "TOTAL_FOLDERS=%~4"

if not defined JOB_FILE (
    set "OVERALL_EXIT_CODE=16"
    goto show_result
)
if not exist "%JOB_FILE%" (
    set "OVERALL_EXIT_CODE=16"
    goto show_result
)
if not defined RESULT_FILE (
    set "OVERALL_EXIT_CODE=16"
    goto show_result
)
if not defined COMBINED_LOG_FILE (
    set "OVERALL_EXIT_CODE=16"
    goto show_result
)
if not defined TOTAL_FOLDERS (
    set "OVERALL_EXIT_CODE=16"
    goto show_result
)

shift
shift
shift
shift
set "EXCLUSION_ARGS="
:collect_exclusions
if "%~1"=="" goto prepare_copy
set "EXCLUSION_ARGS=%EXCLUSION_ARGS% "%~1""
shift
goto collect_exclusions

:prepare_copy
cls
type nul > "%RESULT_FILE%"
type nul > "%COMBINED_LOG_FILE%"
set /a CURRENT_FOLDER=0
set "OVERALL_EXIT_CODE=0"

echo ================================================================
echo                    M+S ROBOCOPY COPY PROCESS
echo ================================================================
echo.
echo Folders selected: %TOTAL_FOLDERS%
echo Combined log: "%COMBINED_LOG_FILE%"
echo Empty folders and junction points will be skipped.
echo.

rem Delayed expansion remains disabled so literal exclamation marks survive.
rem CALL receives no user-controlled arguments, preventing a second CMD parse.
for /f "usebackq tokens=1-3 delims=|" %%A in ("%JOB_FILE%") do (
    set "COPY_SOURCE=%%A"
    set "COPY_DESTINATION=%%B"
    set "COPY_FOLDER_NAME=%%C"
    call :copy_folder
)
goto show_result

:copy_folder
set /a CURRENT_FOLDER+=1
set "JOB_INDEX=%CURRENT_FOLDER%"
set "LOCAL_EXIT_CODE=0"
set "SUBFOLDER_FOUND=0"

echo [%CURRENT_FOLDER%/%TOTAL_FOLDERS%] Copying selected folder...
echo     Main folder: "%COPY_FOLDER_NAME%"
echo.

rem Copies files located directly inside the selected main folder first.
echo     [Root files]
set "RUN_SOURCE=%COPY_SOURCE%"
set "RUN_DESTINATION=%COPY_DESTINATION%"
set "RUN_RECURSIVE_OPTIONS=/XJ"
call :run_robocopy_section

rem Copies each immediate subfolder recursively and displays only its name.
for /d %%D in ("%COPY_SOURCE%\*") do (
    set "SUBFOLDER_FOUND=1"
    set "RUN_SOURCE=%%~fD"
    set "RUN_DESTINATION=%COPY_DESTINATION%\%%~nxD"
    set "RUN_RECURSIVE_OPTIONS=/S /XJ"
    set "CURRENT_SUBFOLDER=%%~nxD"
    call :copy_immediate_subfolder
)

if "%SUBFOLDER_FOUND%"=="0" (
    echo     No immediate subfolders found.
    echo.
)

>> "%RESULT_FILE%" echo(%JOB_INDEX%^|%LOCAL_EXIT_CODE%

if %LOCAL_EXIT_CODE% LSS 8 (
    echo [%CURRENT_FOLDER%/%TOTAL_FOLDERS%] Selected folder completed successfully.
) else (
    echo [%CURRENT_FOLDER%/%TOTAL_FOLDERS%] Selected folder completed with errors.
)
echo ---------------------------------------------------------------
echo.

if %LOCAL_EXIT_CODE% GTR %OVERALL_EXIT_CODE% set "OVERALL_EXIT_CODE=%LOCAL_EXIT_CODE%"
exit /b 0

:copy_immediate_subfolder
echo     [Subfolder] %CURRENT_SUBFOLDER%
call :run_robocopy_section
echo.
exit /b 0

:run_robocopy_section
rem The first Robocopy call creates the combined log; later calls append to it.
if defined LOG_INITIALIZED goto append_section_log

set "LOG_INITIALIZED=1"
if defined EXCLUSION_ARGS goto first_section_with_exclusions
robocopy "%RUN_SOURCE%" "%RUN_DESTINATION%" %RUN_RECURSIVE_OPTIONS% %COPY_METADATA% /R:%RETRY_COUNT% /W:%WAIT_SECONDS% %LOG_OPTIONS% /LOG:"%COMBINED_LOG_FILE%"
goto section_finished

:first_section_with_exclusions
robocopy "%RUN_SOURCE%" "%RUN_DESTINATION%" %RUN_RECURSIVE_OPTIONS% %COPY_METADATA% /R:%RETRY_COUNT% /W:%WAIT_SECONDS% %LOG_OPTIONS% /LOG:"%COMBINED_LOG_FILE%" /XF %EXCLUSION_ARGS%
goto section_finished

:append_section_log
if defined EXCLUSION_ARGS goto append_section_with_exclusions
robocopy "%RUN_SOURCE%" "%RUN_DESTINATION%" %RUN_RECURSIVE_OPTIONS% %COPY_METADATA% /R:%RETRY_COUNT% /W:%WAIT_SECONDS% %LOG_OPTIONS% /LOG+:"%COMBINED_LOG_FILE%"
goto section_finished

:append_section_with_exclusions
robocopy "%RUN_SOURCE%" "%RUN_DESTINATION%" %RUN_RECURSIVE_OPTIONS% %COPY_METADATA% /R:%RETRY_COUNT% /W:%WAIT_SECONDS% %LOG_OPTIONS% /LOG+:"%COMBINED_LOG_FILE%" /XF %EXCLUSION_ARGS%

:section_finished
set "SECTION_EXIT_CODE=%ERRORLEVEL%"
if %SECTION_EXIT_CODE% GTR %LOCAL_EXIT_CODE% set "LOCAL_EXIT_CODE=%SECTION_EXIT_CODE%"
exit /b 0

:show_result
echo.
echo ================================================================
echo                       COPY PROCESS FINISHED
echo ================================================================
echo Overall Robocopy exit code: %OVERALL_EXIT_CODE%
echo Combined log: "%COMBINED_LOG_FILE%"
echo.
if %OVERALL_EXIT_CODE% LSS 8 (
    echo STATUS: All selected folders completed successfully.
) else (
    echo STATUS: One or more selected folders completed with errors.
)
echo.
echo Press any key when you are finished reviewing this window.
pause >nul
exit /b %OVERALL_EXIT_CODE%
