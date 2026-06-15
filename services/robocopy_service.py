"""Robocopy execution logic for the M+S IT Acquisition Toolbox."""

import re
import subprocess
from datetime import datetime
from pathlib import Path


ROBOCOPY_SUCCESS_LIMIT = 8


def _safe_log_name(folder_name):
    """Returns a Windows-safe folder name for use in a log filename."""
    return re.sub(r'[^A-Za-z0-9._-]+', '_', folder_name).strip('_') or "folder"


def run_robocopy(username, selected_folders, excluded_extensions):
    """
    Copies each selected top-level folder into a new timestamped folder
    created directly inside the selected Windows user profile.

    Returns a dictionary containing the overall result, destination, and the
    Robocopy exit code/log path for each selected folder.
    """
    source_profile = Path("C:/Users") / username
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    destination_profile = source_profile / f"M+S Acquisition Copy {timestamp}"
    log_folder = destination_profile / "Logs"

    if not source_profile.exists():
        raise FileNotFoundError(f"The selected user profile does not exist: {source_profile}")

    destination_profile.mkdir(parents=True, exist_ok=True)
    log_folder.mkdir(parents=True, exist_ok=True)

    exclusion_patterns = [f"*{extension}" for extension in excluded_extensions]
    results = []

    for folder_name in selected_folders:
        source_folder = source_profile / folder_name

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

        destination_folder = destination_profile / folder_name
        destination_folder.mkdir(parents=True, exist_ok=True)

        log_name = f"{_safe_log_name(folder_name)}_{timestamp}.log"
        log_file = log_folder / log_name

        command = [
            "robocopy",
            str(source_folder),
            str(destination_folder),
            "/E",
            "/R:3",
            "/W:10",
            "/V",
            "/FP",
            f"/LOG:{log_file}",
        ]

        if exclusion_patterns:
            command.append("/XF")
            command.extend(exclusion_patterns)

        try:
            completed_process = subprocess.run(command, check=False)
            returncode = completed_process.returncode

            results.append(
                {
                    "folder": folder_name,
                    "returncode": returncode,
                    "success": returncode < ROBOCOPY_SUCCESS_LIMIT,
                    "log_file": str(log_file),
                    "error": None,
                }
            )
        except FileNotFoundError as error:
            raise RuntimeError(
                "Robocopy could not be found. This feature must be run on Windows."
            ) from error

    overall_success = bool(results) and all(result["success"] for result in results)

    return {
        "success": overall_success,
        "destination": str(destination_profile),
        "log_folder": str(log_folder),
        "results": results,
    }
