@echo off
setlocal EnableExtensions DisableDelayedExpansion
chcp 65001 >nul
title M+S Robocopy Progress

rem Editable Robocopy settings
set "COPY_SUBDIRECTORIES=/S /XJ"
set "COPY_METADATA=/COPY:DAT /DCOPY:T"
set "RETRY_COUNT=3"
set "WAIT_SECONDS=10"
set "LOG_OPTIONS=/V /FP /NP"

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

echo [%CURRENT_FOLDER%/%TOTAL_FOLDERS%] Copying selected folder...
echo     Source and destination are recorded in the combined log.
echo.

if "%CURRENT_FOLDER%"=="1" goto first_log

goto append_log

:first_log
if defined EXCLUSION_ARGS goto first_log_with_exclusions
robocopy "%COPY_SOURCE%" "%COPY_DESTINATION%" %COPY_SUBDIRECTORIES% %COPY_METADATA% /R:%RETRY_COUNT% /W:%WAIT_SECONDS% %LOG_OPTIONS% /LOG:"%COMBINED_LOG_FILE%"
goto copy_finished

:first_log_with_exclusions
robocopy "%COPY_SOURCE%" "%COPY_DESTINATION%" %COPY_SUBDIRECTORIES% %COPY_METADATA% /R:%RETRY_COUNT% /W:%WAIT_SECONDS% %LOG_OPTIONS% /LOG:"%COMBINED_LOG_FILE%" /XF %EXCLUSION_ARGS%
goto copy_finished

:append_log
if defined EXCLUSION_ARGS goto append_log_with_exclusions
robocopy "%COPY_SOURCE%" "%COPY_DESTINATION%" %COPY_SUBDIRECTORIES% %COPY_METADATA% /R:%RETRY_COUNT% /W:%WAIT_SECONDS% %LOG_OPTIONS% /LOG+:"%COMBINED_LOG_FILE%"
goto copy_finished

:append_log_with_exclusions
robocopy "%COPY_SOURCE%" "%COPY_DESTINATION%" %COPY_SUBDIRECTORIES% %COPY_METADATA% /R:%RETRY_COUNT% /W:%WAIT_SECONDS% %LOG_OPTIONS% /LOG+:"%COMBINED_LOG_FILE%" /XF %EXCLUSION_ARGS%

:copy_finished
set "LOCAL_EXIT_CODE=%ERRORLEVEL%"
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
