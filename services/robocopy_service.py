"""
Robocopy execution logic for the M+S IT Acquisition Toolbox
"""

###############
### Imports ###
###############

import html  # Escapes bookmark names and URLs for HTML output
import json  # Reads Chromium bookmark data
import shutil  # Copies Chromium bookmark files while preserving metadata
import subprocess  # Opens the editable batch file in Command Prompt
import sys  # Locates files beside a packaged executable when needed
from datetime import datetime, timezone  # Creates timestamps and converts Chromium dates
from pathlib import Path  # Creates and validates Windows folder paths

from utils import backup_metadata, helpers  # Validates backups and locates resources


#################################
### Robocopy Return Code Rule ###
#################################

# Robocopy return codes below 8 represent success or success with differences
ROBOCOPY_SUCCESS_LIMIT = 8


#######################################
### Locates the Editable Batch File ###
#######################################

def _get_batch_file_path():
    """Returns the Robocopy batch file in source and packaged applications."""
    # Supports an editable scripts folder stored beside the generated executable
    if getattr(sys, "frozen", False):
        executable_folder = Path(sys.executable).resolve().parent

        external_script = executable_folder / "scripts" / "run_robocopy.bat"
        if external_script.exists():
            return external_script

        external_root_script = executable_folder / "run_robocopy.bat"
        if external_root_script.exists():
            return external_root_script

    # resource_path handles the project root and PyInstaller's temporary folder
    bundled_script = Path(
        helpers.resource_path("scripts/run_robocopy.bat")
    )
    if bundled_script.exists():
        return bundled_script

    bundled_root_script = Path(
        helpers.resource_path("run_robocopy.bat")
    )
    if bundled_root_script.exists():
        return bundled_root_script

    # Returns the intended path so any error shows the correct location
    return bundled_script


# Stores the batch-file path once so every copy operation can reuse it
ROBOCOPY_BATCH_FILE = _get_batch_file_path()


####################################################
### Checks for Previously Generated Copy Folders ###
####################################################

def _is_generated_copy_folder(folder_name, username):
    """Returns True when a folder uses an exact generated-backup name."""
    return backup_metadata.is_generated_backup_name(
        folder_name,
        username,
    )


#####################################
### Builds the Batch File Command ###
#####################################

def _build_batch_command(
    job_file,
    result_file,
    combined_log_file,
    folder_count,
    excluded_extensions,
):
    """Builds one safely quoted cmd.exe command for the complete copy job."""
    # Converts extensions such as .exe into Robocopy patterns such as *.exe
    exclusion_patterns = [
        f"*{extension}"
        for extension in excluded_extensions
    ]

    # cmd.exe /c has special quote handling for batch paths containing spaces.
    # list2cmdline quotes every batch argument, then the extra outer quote keeps
    # the quoted script path attached to the complete command passed to /c.
    batch_arguments = [
        str(ROBOCOPY_BATCH_FILE),
        str(job_file),
        str(result_file),
        str(combined_log_file),
        str(folder_count),
        *exclusion_patterns,
    ]
    quoted_batch_command = subprocess.list2cmdline(batch_arguments)

    return (
        'cmd.exe /d /s /c '
        f'"{quoted_batch_command}"'
    )


#########################################
### Reads Batch File Folder Results   ###
#########################################

def _read_folder_results(result_file, jobs, combined_log_file):
    """Returns batch results while restoring names and log paths in Python."""
    results = []

    # Returns an empty result list when the batch file did not create the file
    if not result_file.exists():
        return results

    # Batch output contains only a numeric job index and Robocopy exit code
    for line in result_file.read_text(
        encoding="utf-8",
        errors="replace",
    ).splitlines():
        parts = line.split("|", 1)

        if len(parts) != 2:
            continue

        job_index_text, returncode_text = parts

        try:
            job_index = int(job_index_text)
            returncode = int(returncode_text)
            job = jobs[job_index - 1]
        except (ValueError, IndexError):
            continue

        results.append(
            {
                "folder": job["folder"],
                "returncode": returncode,
                "success": returncode < ROBOCOPY_SUCCESS_LIMIT,
                "log_file": str(combined_log_file),
                "error": None,
            }
        )

    return results


########################################
### Converts Chromium Bookmarks      ###
########################################

def _chromium_time_to_unix(timestamp):
    """Converts Chromium microseconds since 1601 into a Unix timestamp."""
    try:
        chromium_microseconds = int(timestamp)
    except (TypeError, ValueError):
        return 0

    # Chromium timestamps begin on January 1, 1601 UTC
    chromium_epoch = datetime(1601, 1, 1, tzinfo=timezone.utc)
    bookmark_time = chromium_epoch.timestamp() + (
        chromium_microseconds / 1_000_000
    )

    return max(0, int(bookmark_time))


def _write_bookmark_html_node(node, output_lines, indent_level=1):
    """Writes one Chromium bookmark node into Netscape bookmark HTML."""
    indentation = "    " * indent_level
    node_type = node.get("type")
    node_name = html.escape(node.get("name", "Unnamed"))

    # Writes a normal bookmark link
    if node_type == "url":
        bookmark_url = html.escape(node.get("url", ""), quote=True)
        date_added = _chromium_time_to_unix(node.get("date_added"))

        output_lines.append(
            f'{indentation}<DT><A HREF="{bookmark_url}" '
            f'ADD_DATE="{date_added}">{node_name}</A>'
        )
        return

    # Writes a bookmark folder and recursively includes all of its children
    if node_type == "folder":
        date_added = _chromium_time_to_unix(node.get("date_added"))

        output_lines.append(
            f'{indentation}<DT><H3 ADD_DATE="{date_added}">'
            f'{node_name}</H3>'
        )
        output_lines.append(f'{indentation}<DL><p>')

        for child in node.get("children", []):
            _write_bookmark_html_node(
                child,
                output_lines,
                indent_level + 1,
            )

        output_lines.append(f'{indentation}</DL><p>')


def _convert_chromium_bookmarks_to_html(bookmark_file, output_file):
    """Converts one Chromium Bookmarks JSON file into importable HTML."""
    with Path(bookmark_file).open("r", encoding="utf-8") as file:
        bookmark_data = json.load(file)

    output_lines = [
        "<!DOCTYPE NETSCAPE-Bookmark-file-1>",
        "<!-- Automatically generated by M+S IT Acquisition Toolbox. -->",
        '<META HTTP-EQUIV="Content-Type" CONTENT="text/html; charset=UTF-8">',
        "<TITLE>Bookmarks</TITLE>",
        "<H1>Bookmarks</H1>",
        "<DL><p>",
    ]

    # Keeps the standard Chromium root folders in a predictable order
    bookmark_roots = bookmark_data.get("roots", {})
    for root_name in ("bookmark_bar", "other", "synced"):
        root_node = bookmark_roots.get(root_name)

        if root_node:
            _write_bookmark_html_node(
                root_node,
                output_lines,
                indent_level=1,
            )

    output_lines.append("</DL><p>")

    output_file = Path(output_file)
    output_file.parent.mkdir(parents=True, exist_ok=True)
    output_file.write_text("\n".join(output_lines), encoding="utf-8")


########################################
### Finds Chromium Bookmark Files    ###
########################################

def _get_chromium_browser_roots(source_profile):
    """Returns supported Chromium browser data folders for one user."""
    # Maps browser names to their standard Windows user-data locations
    return {
        "Google Chrome": (
            source_profile
            / "AppData"
            / "Local"
            / "Google"
            / "Chrome"
            / "User Data"
        ),
        "Microsoft Edge": (
            source_profile
            / "AppData"
            / "Local"
            / "Microsoft"
            / "Edge"
            / "User Data"
        ),
        "Brave": (
            source_profile
            / "AppData"
            / "Local"
            / "BraveSoftware"
            / "Brave-Browser"
            / "User Data"
        ),
        "Opera": (
            source_profile
            / "AppData"
            / "Roaming"
            / "Opera Software"
            / "Opera Stable"
        ),
        "Opera GX": (
            source_profile
            / "AppData"
            / "Roaming"
            / "Opera Software"
            / "Opera GX Stable"
        ),
    }


def _find_chromium_bookmark_files(source_profile):
    """Returns browser, profile, and bookmark paths found for one user."""
    bookmark_files = []

    # Checks every supported Chromium browser location
    for browser_name, browser_root in _get_chromium_browser_roots(
        source_profile
    ).items():
        if not browser_root.exists() or not browser_root.is_dir():
            continue

        # Opera stores bookmarks directly in its browser folder
        if browser_name in {"Opera", "Opera GX"}:
            profile_folders = [browser_root]
        else:
            try:
                profile_folders = [
                    folder
                    for folder in browser_root.iterdir()
                    if folder.is_dir()
                    and (
                        folder.name == "Default"
                        or folder.name.startswith("Profile ")
                    )
                ]
            except (PermissionError, FileNotFoundError, OSError):
                continue

        # Saves both the active bookmark file and Chromium's backup when present
        for profile_folder in profile_folders:
            profile_name = (
                profile_folder.name
                if profile_folder != browser_root
                else "Default"
            )

            for bookmark_name in ("Bookmarks", "Bookmarks.bak"):
                bookmark_path = profile_folder / bookmark_name

                try:
                    if bookmark_path.is_file():
                        bookmark_files.append(
                            {
                                "browser": browser_name,
                                "profile": profile_name,
                                "name": bookmark_name,
                                "source": bookmark_path,
                            }
                        )
                except (PermissionError, FileNotFoundError, OSError):
                    continue

    return bookmark_files


def _copy_chromium_bookmarks(
    source_profile,
    destination_profile,
    timestamp,
):
    """Copies Chromium bookmark files and creates importable HTML versions."""
    original_root = (
        destination_profile
        / "Browser Bookmarks"
        / "Original"
    )
    importable_root = (
        destination_profile
        / "Browser Bookmarks"
        / "Importable"
    )
    bookmark_log = (
        destination_profile
        / "Logs"
        / f"chromium_bookmarks_{timestamp}.txt"
    )
    bookmark_results = []

    # Groups discovered files by browser and profile so Bookmarks.bak can be
    # preserved without producing duplicate HTML exports
    discovered_files = _find_chromium_bookmark_files(source_profile)

    for bookmark in discovered_files:
        original_destination = (
            original_root
            / bookmark["browser"]
            / bookmark["profile"]
            / bookmark["name"]
        )

        result = {
            "browser": bookmark["browser"],
            "profile": bookmark["profile"],
            "name": bookmark["name"],
            "source": str(bookmark["source"]),
            "destination": str(original_destination),
            "html_destination": None,
            "success": False,
            "html_created": False,
            "error": None,
            "html_error": None,
        }

        try:
            original_destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(bookmark["source"], original_destination)
            result["success"] = True
        except (PermissionError, FileNotFoundError, OSError) as error:
            result["error"] = str(error)
            bookmark_results.append(result)
            continue

        # Converts only the active Bookmarks file into a browser-importable file
        if bookmark["name"] == "Bookmarks":
            safe_browser_name = bookmark["browser"].replace("/", "-")
            safe_profile_name = bookmark["profile"].replace("/", "-")
            html_destination = (
                importable_root
                / bookmark["browser"]
                / f"{safe_browser_name} - {safe_profile_name} Bookmarks.html"
            )
            result["html_destination"] = str(html_destination)

            try:
                _convert_chromium_bookmarks_to_html(
                    bookmark["source"],
                    html_destination,
                )
                result["html_created"] = True
            except (
                json.JSONDecodeError,
                KeyError,
                TypeError,
                PermissionError,
                FileNotFoundError,
                OSError,
            ) as error:
                # The original JSON remains preserved even when conversion fails
                result["html_error"] = str(error)

        bookmark_results.append(result)

    # Records original copies and HTML conversion results for technician review
    log_lines = [
        "M+S Chromium Bookmark Backup",
        f"Source user profile: {source_profile}",
        f"Original files: {original_root}",
        f"Importable files: {importable_root}",
        "",
    ]

    if not bookmark_results:
        log_lines.append("No supported Chromium bookmark files were found.")
    else:
        for result in bookmark_results:
            copy_status = "COPIED" if result["success"] else "FAILED"
            log_lines.append(
                f"{copy_status} | {result['browser']} | {result['profile']} | "
                f"{result['source']} | {result['destination']}"
            )

            if result["error"]:
                log_lines.append(f"COPY ERROR | {result['error']}")

            if result["html_destination"]:
                html_status = (
                    "HTML CREATED"
                    if result["html_created"]
                    else "HTML FAILED"
                )
                log_lines.append(
                    f"{html_status} | {result['html_destination']}"
                )

            if result["html_error"]:
                log_lines.append(f"HTML ERROR | {result['html_error']}")

    bookmark_log.write_text("\n".join(log_lines), encoding="utf-8")

    return bookmark_results


########################################
### Runs the Robocopy Copy Operation ###
########################################

def run_robocopy(
    username,
    selected_folders,
    excluded_extensions,
    backup_type="initial",
    incremental_destination="",
    save_chromium_bookmarks=False,
):
    """
    Copies selected folders into either a new timestamped destination or an
    existing backup folder chosen for an incremental update.

    One editable batch-file process handles the complete copy job, so only one
    Command Prompt window opens. Robocopy uses /S, so empty folders are skipped.
    """
    # Builds the source profile and timestamp used for folders and log files
    source_profile = Path("C:/Users") / username
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    batch_file = Path(ROBOCOPY_BATCH_FILE)

    # Creates a new destination for initial mode or reuses an existing backup
    if backup_type == "initial":
        destination_profile = source_profile / f"MS {username} Copy {timestamp}"
    elif backup_type == "incremental":
        destination_profile = Path(incremental_destination).expanduser()
    else:
        raise ValueError(
            "Backup type must be either 'initial' or 'incremental'."
        )

    # Stores each run's log inside the chosen backup destination
    log_folder = destination_profile / "Logs"
    combined_log_file = log_folder / f"robocopy_{timestamp}.log"

    # Stops if the selected Windows profile cannot be found
    if not source_profile.exists():
        raise FileNotFoundError(
            f"The selected user profile does not exist: {source_profile}"
        )

    # Incremental mode requires an existing destination directory
    if backup_type == "incremental":
        if not destination_profile.exists():
            raise FileNotFoundError(
                f"The selected backup folder does not exist: {destination_profile}"
            )

        if not destination_profile.is_dir():
            raise NotADirectoryError(
                f"The selected incremental destination is not a folder: "
                f"{destination_profile}"
            )

        resolved_destination = destination_profile.resolve()
        resolved_profile = source_profile.resolve()

        # Prevents the user profile itself from becoming its own destination
        if resolved_destination == resolved_profile:
            raise ValueError(
                "The Windows user profile itself cannot be used as the "
                "incremental backup destination."
            )

        # Blocks drive roots, C:\Users, and other ancestors of the live profile
        try:
            profile_inside_destination = resolved_profile.is_relative_to(
                resolved_destination
            )
        except AttributeError:
            profile_inside_destination = (
                resolved_profile == resolved_destination
                or resolved_destination in resolved_profile.parents
            )

        if profile_inside_destination:
            raise ValueError(
                "The incremental destination cannot contain the selected "
                "Windows user profile. Choose the generated M+S backup folder."
            )

        # Requires a marker proving this tool created the backup for this user
        backup_marker = backup_metadata.validate_backup_folder(
            destination_profile,
            username,
            allowed_statuses={
                backup_metadata.BACKUP_STATUS_IN_PROGRESS,
                backup_metadata.BACKUP_STATUS_COMPLETED,
                backup_metadata.BACKUP_STATUS_COMPLETED_WITH_ERRORS,
            },
        )

        if backup_marker is None:
            raise ValueError(
                "The incremental destination is not a marker-validated M+S "
                "backup for the selected user. Backups created before marker "
                "support must be handled as legacy backups rather than selected "
                "automatically."
            )

        # Prevents a backup from being placed inside any selected source folder
        for folder_name in selected_folders:
            selected_source = (source_profile / folder_name).resolve()
            try:
                destination_inside_source = resolved_destination.is_relative_to(
                    selected_source
                )
            except AttributeError:
                destination_inside_source = (
                    resolved_destination == selected_source
                    or selected_source in resolved_destination.parents
                )

            if destination_inside_source:
                raise ValueError(
                    "The incremental destination cannot be the same as or "
                    "inside a selected source folder. Choose an existing "
                    "backup outside the selected data."
                )

    # Stops if the editable batch file is missing from the scripts folder
    if not batch_file.exists():
        raise FileNotFoundError(
            "The Robocopy batch file could not be found. "
            "Add scripts/run_robocopy.bat to Auto Py to Exe with the destination "
            f"folder set to scripts. Expected path: {batch_file}"
        )

    # Creates and identifies a new initial destination before copying data
    if backup_type == "initial":
        destination_profile.mkdir(parents=True, exist_ok=True)
        backup_metadata.create_backup_marker(
            destination_profile,
            username,
        )

    log_folder.mkdir(parents=True, exist_ok=True)

    # Stores invalid selections before the valid folders are sent to the batch file
    results = []
    jobs = []

    # Validates every selected relative folder path and prepares its source and destination paths
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

        # Defines the matching destination path without creating it in advance
        destination_folder = destination_profile / folder_name

        # Adds the validated folder to the single multi-folder copy job
        jobs.append(
            {
                "folder": folder_name,
                "source": source_folder,
                "destination": destination_folder,
            }
        )

    # Stores Chromium bookmark copy results separately from folder results
    bookmark_results = []

    # Copies bookmarks before or without the Robocopy folder operation
    if save_chromium_bookmarks:
        bookmark_results = _copy_chromium_bookmarks(
            source_profile,
            destination_profile,
            timestamp,
        )

    # Returns when no valid folder jobs remain and only bookmark work was requested
    if not jobs:
        bookmark_failures = [
            result
            for result in bookmark_results
            if (
                not result["success"]
                or (
                    result["name"] == "Bookmarks"
                    and not result["html_created"]
                )
            )
        ]
        bookmark_files_copied = sum(
            1 for result in bookmark_results if result["success"]
        )
        bookmark_html_files_created = sum(
            1 for result in bookmark_results if result["html_created"]
        )
        bookmarks_found = bool(bookmark_results)
        overall_success = (
            save_chromium_bookmarks
            and bookmarks_found
            and not bookmark_failures
            and not results
        )

        # Initial backups are finalized only after all requested work is known
        if backup_type == "initial":
            backup_metadata.update_backup_status(
                destination_profile,
                (
                    backup_metadata.BACKUP_STATUS_COMPLETED
                    if overall_success
                    else backup_metadata.BACKUP_STATUS_COMPLETED_WITH_ERRORS
                ),
            )

        return {
            "success": overall_success,
            "backup_type": backup_type,
            "destination": str(destination_profile),
            "log_folder": str(log_folder),
            "results": results,
            "bookmark_results": bookmark_results,
            "bookmark_files_copied": bookmark_files_copied,
            "bookmark_html_files_created": bookmark_html_files_created,
            "bookmarks_found": bookmarks_found,
            "bookmark_failures": bookmark_failures,
        }

    # Creates files used to pass the full multi-folder job into one batch process
    job_file = log_folder / f"copy_job_{timestamp}.txt"
    result_file = log_folder / f"copy_results_{timestamp}.txt"

    # Writes one pipe-separated source, destination, and display name per line
    manifest_lines = [
        f"{job['source']}|{job['destination']}|{job['folder']}"
        for job in jobs
    ]
    job_file.write_text(
        "\n".join(manifest_lines),
        encoding="utf-8",
        newline="\n",
    )

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
            shell=False,
            creationflags=creation_flags,
        )
    except FileNotFoundError as error:
        raise RuntimeError(
            "Command Prompt or the Robocopy batch file could not be started. "
            "This feature must be run on Windows."
        ) from error

    # Adds every folder-level result produced by the batch file
    results.extend(_read_folder_results(result_file, jobs, combined_log_file))

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

    # The complete operation succeeds when all folder and bookmark copies succeed
    folder_success = bool(results) and all(
        result["success"]
        for result in results
    )
    bookmark_failures = [
        result
        for result in bookmark_results
        if (
            not result["success"]
            or (
                result["name"] == "Bookmarks"
                and not result["html_created"]
            )
        )
    ]
    bookmark_success = (
        not save_chromium_bookmarks
        or (bool(bookmark_results) and not bookmark_failures)
    )
    overall_success = folder_success and bookmark_success

    # Initial backups are finalized only after folder and bookmark work ends
    if backup_type == "initial":
        backup_metadata.update_backup_status(
            destination_profile,
            (
                backup_metadata.BACKUP_STATUS_COMPLETED
                if overall_success
                else backup_metadata.BACKUP_STATUS_COMPLETED_WITH_ERRORS
            ),
        )

    return {
        "success": overall_success,
        "backup_type": backup_type,
        "destination": str(destination_profile),
        "log_folder": str(log_folder),
        "results": results,
        "bookmark_results": bookmark_results,
        "bookmark_files_copied": sum(
            1
            for result in bookmark_results
            if result["success"]
        ),
        "bookmark_html_files_created": sum(
            1
            for result in bookmark_results
            if result["html_created"]
        ),
        "bookmarks_found": bool(bookmark_results),
        "bookmark_failures": bookmark_failures,
    }
