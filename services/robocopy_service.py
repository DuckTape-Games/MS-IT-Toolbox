"""
Robocopy execution logic for the M+S IT Acquisition Toolbox
"""

###############
### Imports ###
###############

import subprocess  # Opens the editable batch file in Command Prompt
import sys  # Locates files beside a packaged executable when needed
from datetime import datetime  # Creates timestamped copy folders and log files
from pathlib import Path  # Creates and validates Windows folder paths

from utils import helpers  # Locates bundled files in development and packaged builds


################################
### Robocopy Return Code Rule ###
################################

# Robocopy return codes below 8 represent success or success with differences
ROBOCOPY_SUCCESS_LIMIT = 8


########################################
### Locates the Editable Batch File  ###
########################################

def _get_batch_file_path():
    """Returns the Robocopy batch file in source and packaged applications."""
    # resource_path handles the project root and PyInstaller's temporary _MEIPASS folder
    bundled_script = Path(
        helpers.resource_path("scripts/run_robocopy.bat")
    )

    # Uses the correctly bundled scripts folder whenever it exists
    if bundled_script.exists():
        return bundled_script

    # Supports builds where Auto Py to Exe placed the file at the bundle root
    bundled_root_script = Path(
        helpers.resource_path("run_robocopy.bat")
    )
    if bundled_root_script.exists():
        return bundled_root_script

    # Supports an editable scripts folder stored beside the generated executable
    if getattr(sys, "frozen", False):
        executable_folder = Path(sys.executable).resolve().parent

        external_script = executable_folder / "scripts" / "run_robocopy.bat"
        if external_script.exists():
            return external_script

        external_root_script = executable_folder / "run_robocopy.bat"
        if external_root_script.exists():
            return external_root_script

    # Returns the intended resource path so any error message shows the proper location
    return bundled_script


# Stores the batch-file path once so every copy operation can reuse it
ROBOCOPY_BATCH_FILE = _get_batch_file_path()


#####################################################
### Checks for Previously Generated Copy Folders ###
#####################################################

def _is_generated_copy_folder(folder_name, username):
    """Returns True when a folder is one of this tool's generated copies."""
    # Builds the current copy-folder prefix for the selected user
    current_prefix = f"MS {username} Copy "

    # Supports both the current and older project naming formats
    return (
        folder_name.startswith(current_prefix)
        or folder_name.startswith("M+S Acquisition Copy ")
    )


#########################################
### Builds the Batch File Command     ###
#########################################

def _build_batch_command(job_file, result_file, combined_log_file, folder_count, excluded_extensions):
    """Builds the single command used to run the complete copy job."""
    # Converts extensions such as .exe into Robocopy patterns such as *.exe
    exclusion_patterns = [f"*{extension}" for extension in excluded_extensions]

    # Sends the manifest, result path, folder count, and exclusions to the batch file
    return [
        "cmd.exe",
        "/d",
        "/c",
        str(ROBOCOPY_BATCH_FILE),
        str(job_file),
        str(result_file),
        str(combined_log_file),
        str(folder_count),
        *exclusion_patterns,
    ]


#########################################
### Reads Batch File Folder Results   ###
#########################################

def _read_folder_results(result_file):
    """Returns folder-level Robocopy results written by the batch file."""
    results = []

    # Returns an empty result list when the batch file did not create the file
    if not result_file.exists():
        return results

    # Reads each folder name, exit code, and log path from the result file
    for line in result_file.read_text(encoding="utf-8", errors="replace").splitlines():
        parts = line.split("|", 2)
        if len(parts) != 3:
            continue

        folder_name, returncode_text, log_file = parts

        try:
            returncode = int(returncode_text)
        except ValueError:
            continue

        results.append(
            {
                "folder": folder_name,
                "returncode": returncode,
                "success": returncode < ROBOCOPY_SUCCESS_LIMIT,
                "log_file": log_file,
                "error": None,
            }
        )

    return results


########################################
### Runs the Robocopy Copy Operation ###
########################################

def run_robocopy(username, selected_folders, excluded_extensions):
    """
    Copies every selected top-level folder into one timestamped folder created
    directly inside the selected Windows user profile.

    One editable batch-file process handles the complete copy job, so only one
    Command Prompt window opens. Robocopy uses /E, so empty folders are copied.
    """
    # Builds the source profile and unique destination for the current run
    source_profile = Path("C:/Users") / username
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    destination_profile = source_profile / f"MS {username} Copy {timestamp}"
    log_folder = destination_profile / "Logs"
    batch_file = Path(ROBOCOPY_BATCH_FILE)
    combined_log_file = log_folder / f"robocopy_{timestamp}.log"

    # Stops if the selected Windows profile cannot be found
    if not source_profile.exists():
        raise FileNotFoundError(
            f"The selected user profile does not exist: {source_profile}"
        )

    # Stops if the editable batch file is missing from the scripts folder
    if not batch_file.exists():
        raise FileNotFoundError(
            "The Robocopy batch file could not be found. "
            "Add scripts/run_robocopy.bat to Auto Py to Exe with the destination "
            f"folder set to scripts. Expected path: {batch_file}"
        )

    # Creates the main destination and shared log folder before copying
    destination_profile.mkdir(parents=True, exist_ok=True)
    log_folder.mkdir(parents=True, exist_ok=True)

    # Stores invalid selections before the valid folders are sent to the batch file
    results = []
    jobs = []

    # Validates every selected folder and prepares its source, destination, and log paths
    for folder_name in selected_folders:
        # Blocks folders previously generated by this tool to prevent recursive copies
        if _is_generated_copy_folder(folder_name, username):
            results.append(
                {
                    "folder": folder_name,
                    "returncode": None,
                    "success": False,
                    "log_file": None,
                    "error": "Generated acquisition-copy folders cannot be copied.",
                }
            )
            continue

        source_folder = source_profile / folder_name

        # Records a failure if the source disappeared or cannot be used
        if not source_folder.exists() or not source_folder.is_dir():
            results.append(
                {
                    "folder": folder_name,
                    "returncode": None,
                    "success": False,
                    "log_file": None,
                    "error": "Source folder does not exist or cannot be accessed.",
                }
            )
            continue

        # Creates a matching folder under the new acquisition-copy destination
        destination_folder = destination_profile / folder_name
        destination_folder.mkdir(parents=True, exist_ok=True)

        # Adds the validated folder to the single multi-folder copy job
        jobs.append(
            {
                "folder": folder_name,
                "source": source_folder,
                "destination": destination_folder,
            }
        )

    # Returns validation failures without opening Command Prompt when no jobs are valid
    if not jobs:
        return {
            "success": False,
            "destination": str(destination_profile),
            "log_folder": str(log_folder),
            "results": results,
        }

    # Creates files used to pass the full multi-folder job into one batch process
    job_file = log_folder / f"copy_job_{timestamp}.txt"
    result_file = log_folder / f"copy_results_{timestamp}.txt"

    # Writes one pipe-separated source, destination, and display name per line
    manifest_lines = [
        f"{job['source']}|{job['destination']}|{job['folder']}"
        for job in jobs
    ]
    job_file.write_text("\n".join(manifest_lines), encoding="utf-8")

    # Builds one cmd.exe call for the entire selected-folder job
    command = _build_batch_command(
        job_file=job_file,
        result_file=result_file,
        combined_log_file=combined_log_file,
        folder_count=len(jobs),
        excluded_extensions=excluded_extensions,
    )

    try:
        # Opens one visible Command Prompt window and waits until its final pause closes
        creation_flags = getattr(subprocess, "CREATE_NEW_CONSOLE", 0)
        subprocess.run(
            command,
            check=False,
            creationflags=creation_flags,
        )
    except FileNotFoundError as error:
        raise RuntimeError(
            "Command Prompt or the Robocopy batch file could not be started. "
            "This feature must be run on Windows."
        ) from error

    # Adds every folder-level result produced by the batch file
    results.extend(_read_folder_results(result_file))

    # Adds failures for jobs that never received a batch-file result
    completed_names = {result["folder"] for result in results}
    for job in jobs:
        if job["folder"] not in completed_names:
            results.append(
                {
                    "folder": job["folder"],
                    "returncode": None,
                    "success": False,
                    "log_file": str(combined_log_file),
                    "error": "No result was returned by the batch file.",
                }
            )

    # Removes temporary coordination files after their values have been read
    job_file.unlink(missing_ok=True)
    result_file.unlink(missing_ok=True)

    # The complete operation only succeeds when every selected folder succeeds
    overall_success = bool(results) and all(result["success"] for result in results)

    return {
        "success": overall_success,
        "destination": str(destination_profile),
        "log_folder": str(log_folder),
        "results": results,
    }
