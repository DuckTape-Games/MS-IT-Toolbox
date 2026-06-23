rem ##########################
rem ### Command Line Setup ###
rem ##########################

rem Hides each command so the window only shows useful status messages.
@echo off

rem Starts a local environment and allows variables inside loops to update.
setlocal EnableExtensions EnableDelayedExpansion

rem Gives the single copy window a clear title.
title M+S Robocopy Progress


rem ##################################
rem ### Editable Robocopy Settings ###
rem ##################################

rem /S copies subfolders but skips folders that are completely empty.
rem Do not replace /S with /MIR because /MIR can delete destination files.
set "COPY_SUBDIRECTORIES=/S"

rem /COPY:DAT copies file data, attributes, and timestamps.
rem /DCOPY:T preserves directory timestamps for copied folders.
set "COPY_METADATA=/COPY:DAT /DCOPY:T"

rem Sets how many times Robocopy retries a failed file.
set "RETRY_COUNT=3"

rem Sets how many seconds Robocopy waits between retries.
set "WAIT_SECONDS=10"

rem /V and /FP keep detailed file information inside the combined log.
rem Filenames are not displayed in Command Prompt because /TEE is not used.
set "LOG_OPTIONS=/V /FP"


rem ###################################
rem ### Values Received From Python ###
rem ###################################

rem %%1 = job manifest file
rem %%2 = result file written by this batch file
rem %%3 = one combined log file for the entire copy job
rem %%4 = total number of folders in the job
rem %%5 and later = optional file patterns to exclude
set "JOB_FILE=%~1"
set "RESULT_FILE=%~2"
set "COMBINED_LOG_FILE=%~3"
set "TOTAL_FOLDERS=%~4"


rem #############################
rem ### Required Value Checks ###
rem #############################

if not defined JOB_FILE (
    echo ERROR: No copy-job file was provided.
    set "OVERALL_EXIT_CODE=16"
    goto show_result
)

if not exist "%JOB_FILE%" (
    echo ERROR: The copy-job file could not be found.
    set "OVERALL_EXIT_CODE=16"
    goto show_result
)

if not defined RESULT_FILE (
    echo ERROR: No result file was provided.
    set "OVERALL_EXIT_CODE=16"
    goto show_result
)

if not defined COMBINED_LOG_FILE (
    echo ERROR: No combined log file was provided.
    set "OVERALL_EXIT_CODE=16"
    goto show_result
)

if not defined TOTAL_FOLDERS (
    echo ERROR: No folder count was provided.
    set "OVERALL_EXIT_CODE=16"
    goto show_result
)


rem ##################################
rem ### File Exclusion Preparation ###
rem ##################################

rem Removes the first four required arguments.
shift
shift
shift
shift

rem Holds every optional /XF pattern passed by Python.
set "EXCLUSION_ARGS="

:collect_exclusions
if "%~1"=="" goto prepare_copy
set "EXCLUSION_ARGS=!EXCLUSION_ARGS! "%~1""
shift
goto collect_exclusions


rem ############################
rem ### Prepare the Copy Job ###
rem ############################

:prepare_copy
cls

rem Clears old result and combined-log data before the new run starts.
type nul > "%RESULT_FILE%"
type nul > "%COMBINED_LOG_FILE%"

rem Tracks the current folder and highest Robocopy return code.
set /a CURRENT_FOLDER=0
set "OVERALL_EXIT_CODE=0"

echo ================================================================
echo                    M+S ROBOCOPY COPY PROCESS
echo ================================================================
echo.
echo Folders selected: %TOTAL_FOLDERS%
echo Combined log: "%COMBINED_LOG_FILE%"
echo Empty folders will be skipped because Robocopy uses /S.

if defined EXCLUSION_ARGS (
    echo Excluded file patterns: !EXCLUSION_ARGS!
) else (
    echo Excluded file patterns: None
)

echo.
echo Individual filenames will not be displayed in this window.
echo Full details for every folder are being appended to one log file.
echo ================================================================
echo.


rem ##################################
rem ### Copy Every Selected Folder ###
rem ##################################

rem Each manifest line contains:
rem source path ^| destination path ^| display folder name
for /f "usebackq tokens=1-3 delims=|" %%A in ("%JOB_FILE%") do (
    set /a CURRENT_FOLDER+=1

    echo [!CURRENT_FOLDER!/%TOTAL_FOLDERS%] Copying %%C...
    echo     Source:      "%%A"
    echo     Destination: "%%B"
    echo.

    rem The first folder creates the combined log with /LOG.
    rem Later folders append to the same file with /LOG+.
    if !CURRENT_FOLDER! EQU 1 (
        if defined EXCLUSION_ARGS (
            robocopy "%%A" "%%B" %COPY_SUBDIRECTORIES% %COPY_METADATA% /R:%RETRY_COUNT% /W:%WAIT_SECONDS% %LOG_OPTIONS% /LOG:"%COMBINED_LOG_FILE%" /XF !EXCLUSION_ARGS!
        ) else (
            robocopy "%%A" "%%B" %COPY_SUBDIRECTORIES% %COPY_METADATA% /R:%RETRY_COUNT% /W:%WAIT_SECONDS% %LOG_OPTIONS% /LOG:"%COMBINED_LOG_FILE%"
        )
    ) else (
        if defined EXCLUSION_ARGS (
            robocopy "%%A" "%%B" %COPY_SUBDIRECTORIES% %COPY_METADATA% /R:%RETRY_COUNT% /W:%WAIT_SECONDS% %LOG_OPTIONS% /LOG+:"%COMBINED_LOG_FILE%" /XF !EXCLUSION_ARGS!
        ) else (
            robocopy "%%A" "%%B" %COPY_SUBDIRECTORIES% %COPY_METADATA% /R:%RETRY_COUNT% /W:%WAIT_SECONDS% %LOG_OPTIONS% /LOG+:"%COMBINED_LOG_FILE%"
        )
    )

    rem Saves the folder-level return code immediately.
    set "FOLDER_EXIT_CODE=!ERRORLEVEL!"

    rem Writes the folder result so Python can display a final summary.
    >> "%RESULT_FILE%" echo %%C^|!FOLDER_EXIT_CODE!^|%COMBINED_LOG_FILE%

    rem Keeps the highest return code as the overall result.
    if !FOLDER_EXIT_CODE! GTR !OVERALL_EXIT_CODE! (
        set "OVERALL_EXIT_CODE=!FOLDER_EXIT_CODE!"
    )

    if !FOLDER_EXIT_CODE! LSS 8 (
        echo [!CURRENT_FOLDER!/%TOTAL_FOLDERS%] %%C completed successfully.
    ) else (
        echo [!CURRENT_FOLDER!/%TOTAL_FOLDERS%] %%C completed with errors.
    )

    echo ---------------------------------------------------------------
    echo.
)


rem #################################
rem ### Display Completion Result ###
rem #################################

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


rem ##############################
rem ### Return Robocopy Result ###
rem ##############################

exit /b %OVERALL_EXIT_CODE%
