"""
Validates and identifies backups created by M+S IT Acquisition Toolbox
"""

###############
### Imports ###
###############

import json  # Reads and writes the backup marker file
import re  # Validates timestamped backup folder names
import uuid  # Creates and validates unique backup identifiers
from datetime import datetime, timezone  # Stores ISO-formatted creation dates
from pathlib import Path  # Handles backup and marker file paths


################################
### Backup Marker Constants  ###
################################

BACKUP_MARKER_FILENAME = "MS_BACKUP_INFO.json"
BACKUP_APPLICATION_ID = "M+S IT Acquisition Toolbox"
BACKUP_FORMAT_VERSION = 1
BACKUP_STATUS_IN_PROGRESS = "in_progress"
BACKUP_STATUS_COMPLETED = "completed"
BACKUP_STATUS_COMPLETED_WITH_ERRORS = "completed_with_errors"
VALID_BACKUP_STATUSES = {
    BACKUP_STATUS_IN_PROGRESS,
    BACKUP_STATUS_COMPLETED,
    BACKUP_STATUS_COMPLETED_WITH_ERRORS,
}


########################################
### Validates a Generated Folder Name ###
########################################

def is_generated_backup_name(folder_name, username=None):
    """Returns True only for an exact timestamped M+S backup name."""
    if not folder_name:
        return False

    # Current format ties the folder name directly to the source username
    if username:
        current_match = re.fullmatch(
            rf"MS {re.escape(username)} Copy "
            r"\d{4}-\d{2}-\d{2}_\d{2}-\d{2}-\d{2}",
            folder_name,
            flags=re.IGNORECASE,
        )

        if current_match:
            return True

    # Legacy names are recognized for filtering only, not trusted for updates
    legacy_match = re.fullmatch(
        r"M\+S Acquisition Copy "
        r"\d{4}-\d{2}-\d{2}_\d{2}-\d{2}-\d{2}",
        folder_name,
        flags=re.IGNORECASE,
    )

    return legacy_match is not None


####################################
### Creates a New Backup Marker  ###
####################################

def create_backup_marker(backup_folder, source_username, created_at=None):
    """Writes the identity marker for a newly generated backup."""
    backup_folder = Path(backup_folder)
    marker_path = backup_folder / BACKUP_MARKER_FILENAME
    marker_created_at = created_at or datetime.now(timezone.utc)

    marker_data = {
        "application": BACKUP_APPLICATION_ID,
        "backup_format_version": BACKUP_FORMAT_VERSION,
        "backup_id": str(uuid.uuid4()),
        "source_username": source_username,
        "created_at": marker_created_at.astimezone(timezone.utc).isoformat(),
        "status": BACKUP_STATUS_IN_PROGRESS,
        "completed_at": None,
    }

    marker_path.write_text(
        json.dumps(marker_data, indent=2),
        encoding="utf-8",
    )

    return marker_path


####################################
### Reads a Backup Marker        ###
####################################

def read_backup_marker(backup_folder):
    """Returns valid marker data or None when the marker cannot be trusted."""
    backup_folder = Path(backup_folder)
    marker_path = backup_folder / BACKUP_MARKER_FILENAME

    try:
        marker_data = json.loads(marker_path.read_text(encoding="utf-8"))
    except (
        FileNotFoundError,
        PermissionError,
        OSError,
        json.JSONDecodeError,
    ):
        return None

    if not isinstance(marker_data, dict):
        return None

    if marker_data.get("application") != BACKUP_APPLICATION_ID:
        return None

    if marker_data.get("backup_format_version") != BACKUP_FORMAT_VERSION:
        return None

    source_username = marker_data.get("source_username")
    created_at = marker_data.get("created_at")
    backup_id = marker_data.get("backup_id")
    status = marker_data.get("status")
    completed_at = marker_data.get("completed_at")

    if not all(isinstance(value, str) and value for value in (
        source_username,
        created_at,
        backup_id,
    )):
        return None

    if status not in VALID_BACKUP_STATUSES:
        return None

    if completed_at is not None and not isinstance(completed_at, str):
        return None

    try:
        datetime.fromisoformat(created_at.replace("Z", "+00:00"))
        uuid.UUID(backup_id)

        if completed_at:
            datetime.fromisoformat(completed_at.replace("Z", "+00:00"))
    except (ValueError, TypeError):
        return None

    return marker_data


####################################
### Updates a Backup Status      ###
####################################

def update_backup_status(backup_folder, status):
    """Updates the lifecycle status in an existing backup marker."""
    if status not in VALID_BACKUP_STATUSES:
        raise ValueError(f"Unsupported backup status: {status}")

    backup_folder = Path(backup_folder)
    marker_path = backup_folder / BACKUP_MARKER_FILENAME
    marker_data = read_backup_marker(backup_folder)

    if marker_data is None:
        raise ValueError(
            "The backup marker is missing or invalid and cannot be updated."
        )

    marker_data["status"] = status
    marker_data["completed_at"] = (
        datetime.now(timezone.utc).isoformat()
        if status != BACKUP_STATUS_IN_PROGRESS
        else None
    )

    marker_path.write_text(
        json.dumps(marker_data, indent=2),
        encoding="utf-8",
    )

    return marker_data


####################################
### Validates a Backup Folder    ###
####################################

def validate_backup_folder(
    backup_folder,
    source_username,
    allowed_statuses=None,
):
    """Returns marker data for a matching backup with an allowed status."""
    backup_folder = Path(backup_folder)

    if not backup_folder.exists() or not backup_folder.is_dir():
        return None

    # Incremental backups use the current user-specific naming format only
    if not re.fullmatch(
        rf"MS {re.escape(source_username)} Copy "
        r"\d{4}-\d{2}-\d{2}_\d{2}-\d{2}-\d{2}",
        backup_folder.name,
        flags=re.IGNORECASE,
    ):
        return None

    marker_data = read_backup_marker(backup_folder)

    if marker_data is None:
        return None

    if marker_data["source_username"].casefold() != source_username.casefold():
        return None

    if (
        allowed_statuses is not None
        and marker_data["status"] not in set(allowed_statuses)
    ):
        return None

    return marker_data


####################################
### Gets a Backup Creation Time  ###
####################################

def get_backup_creation_time(
    backup_folder,
    source_username,
    allowed_statuses=None,
):
    """Returns the trusted UTC creation timestamp from an allowed backup."""
    marker_data = validate_backup_folder(
        backup_folder,
        source_username,
        allowed_statuses=allowed_statuses,
    )

    if marker_data is None:
        return None

    try:
        return datetime.fromisoformat(
            marker_data["created_at"].replace("Z", "+00:00")
        ).timestamp()
    except (ValueError, TypeError):
        return None
