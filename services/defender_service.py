"""
Runs Microsoft Defender scans and creates scan logs
"""

###############
### Imports ###
###############

import json  # Reads structured scan results returned by PowerShell
import re  # Extracts Windows paths from Defender resource strings
import subprocess  # Runs Microsoft Defender PowerShell commands
from datetime import datetime  # Creates timestamps and scan durations
from pathlib import Path  # Validates scan targets and creates log folders

from utils import helpers  # Locates PowerShell scripts in source and packaged builds


#######################################
### Gets the Defender Log Directory ###
#######################################

def get_defender_log_directory():
    """Returns the user-accessible folder used for Defender scan logs."""
    # Keeps scan reports in the current Windows user's Documents folder
    return (
        Path.home()
        / "Documents"
        / "M+S IT Acquisition Toolbox Logs"
        / "Microsoft Defender"
    )


###################################
### Formats Defender Severities ###
###################################

def _get_severity_name(severity_id):
    """Returns a readable Microsoft Defender severity name."""
    # Converts Defender's numeric severity identifiers into technician labels
    severity_names = {
        0: "Unknown",
        1: "Low",
        2: "Moderate",
        4: "High",
        5: "Severe",
    }

    try:
        normalized_severity = int(severity_id)
    except (TypeError, ValueError):
        return "Unknown"

    return severity_names.get(normalized_severity, str(normalized_severity))


######################################
### Normalizes Defender Detections ###
######################################

def _normalize_detections(detections):
    """Returns Defender detections in a consistent Python structure."""
    detections = detections or []

    # PowerShell returns one object instead of a list for one detection
    if isinstance(detections, dict):
        detections = [detections]

    normalized_detections = []

    for detection in detections:
        resources = detection.get("Resources") or []

        if isinstance(resources, str):
            resources = [resources]

        normalized_detections.append(
            {
                "threat_id": detection.get("ThreatID"),
                "threat_name": (
                    detection.get("ThreatName")
                    or "Unknown Threat"
                ),
                "severity": _get_severity_name(
                    detection.get("SeverityID")
                ),
                "category_id": detection.get("CategoryID"),
                "is_active": detection.get("IsActive"),
                "did_execute": detection.get("DidThreatExecute"),
                "initial_detection_time": detection.get(
                    "InitialDetectionTime"
                ),
                "last_status_change_time": detection.get(
                    "LastThreatStatusChangeTime"
                ),
                "resources": resources,
            }
        )

    return normalized_detections


################################
### Runs a Defender Scan     ###
################################

def _run_defender_scan(scan_type, scan_path=None):
    """Runs one supported Defender scan and returns structured results."""
    # Validates custom scan targets before PowerShell is started
    if scan_type == "Custom Scan":
        if not scan_path:
            raise ValueError("A custom scan target is required.")

        scan_target = Path(scan_path).expanduser()

        if not scan_target.exists():
            raise FileNotFoundError(
                f"The selected scan target does not exist: {scan_target}"
            )

        scan_path = str(scan_target.resolve())

    # Selects the external PowerShell script for the requested scan type
    if scan_type == "Quick Scan":
        script_path = Path(
            helpers.resource_path(
                "scripts/defender_quick_scan.ps1"
            )
        )
        script_arguments = []
    elif scan_type == "Full Scan":
        script_path = Path(
            helpers.resource_path(
                "scripts/defender_full_scan.ps1"
            )
        )
        script_arguments = []
    elif scan_type == "Custom Scan":
        script_path = Path(
            helpers.resource_path(
                "scripts/defender_custom_scan.ps1"
            )
        )
        script_arguments = [
            "-ScanPath",
            scan_path,
        ]
    else:
        raise ValueError(
            f"Unsupported Microsoft Defender scan type: {scan_type}"
        )

    # Stops before launching PowerShell when the required script is missing
    if not script_path.exists():
        raise FileNotFoundError(
            f"Microsoft Defender script was not found: {script_path}"
        )

    python_start_time = datetime.now()

    try:
        completed_process = subprocess.run(
            [
                "powershell.exe",
                "-NoProfile",
                "-NonInteractive",
                "-ExecutionPolicy",
                "Bypass",
                "-File",
                str(script_path),
                *script_arguments,
            ],
            capture_output=True,
            text=True,
            check=False,
            creationflags=getattr(
                subprocess,
                "CREATE_NO_WINDOW",
                0,
            ),
        )
    except FileNotFoundError as error:
        raise RuntimeError(
            "Windows PowerShell could not be found on this computer."
        ) from error
    except OSError as error:
        raise RuntimeError(
            f"Microsoft Defender could not be started: {error}"
        ) from error

    python_end_time = datetime.now()

    # Reports PowerShell and Defender errors without hiding their details
    if completed_process.returncode != 0:
        error_text = (
            completed_process.stderr.strip()
            or completed_process.stdout.strip()
            or "Microsoft Defender returned an unknown error."
        )
        raise RuntimeError(error_text)

    output_text = completed_process.stdout.strip()

    if not output_text:
        raise RuntimeError(
            "Microsoft Defender completed without returning scan results."
        )

    try:
        scan_data = json.loads(output_text)
    except json.JSONDecodeError as error:
        raise RuntimeError(
            "Microsoft Defender returned results that could not be read."
        ) from error

    detections = _normalize_detections(
        scan_data.get("Detections")
    )
    duration_seconds = max(
        0,
        int((python_end_time - python_start_time).total_seconds()),
    )

    result = {
        "scan_type": scan_type,
        "scan_path": scan_path,
        "status": "Completed",
        "start_time": scan_data.get("ScanStartTime"),
        "end_time": scan_data.get("ScanEndTime"),
        "duration_seconds": duration_seconds,
        "antivirus_enabled": scan_data.get("AntivirusEnabled"),
        "real_time_protection_enabled": scan_data.get(
            "RealTimeProtectionEnabled"
        ),
        "quick_scan_start_time": scan_data.get("QuickScanStartTime"),
        "quick_scan_end_time": scan_data.get("QuickScanEndTime"),
        "quick_scan_age": scan_data.get("QuickScanAge"),
        "detections": detections,
        "threat_count": len(detections),
    }

    # Creates the technician-readable scan report before returning
    result["log_file"] = str(_write_scan_log(result))

    return result


#################################
### Runs a Defender Quick Scan ###
#################################

def run_quick_scan():
    """Runs a Microsoft Defender quick scan."""
    return _run_defender_scan("Quick Scan")


def run_full_scan():
    """Runs a Microsoft Defender full-system scan."""
    return _run_defender_scan("Full Scan")


##################################
### Runs a Defender Custom Scan ###
##################################

def run_custom_scan(scan_path):
    """Runs a Microsoft Defender scan against one file or folder."""
    return _run_defender_scan(
        "Custom Scan",
        scan_path=scan_path,
    )


########################################
### Extracts a Defender File Path    ###
########################################

def _extract_detected_file_path(resource):
    """Returns the outer local Windows file path in a Defender resource."""
    if not resource:
        return None

    resource_text = str(resource).strip()

    # Recognizes Defender's file:_ and containerfile:_ resource prefixes
    resource_match = re.search(
        r"(?:^|;)(?:containerfile|file):_"
        r"(?P<path>[A-Za-z]:\\[^\r\n]+)",
        resource_text,
        flags=re.IGNORECASE,
    )

    if resource_match:
        detected_path = resource_match.group("path").strip()
    else:
        # Supports plain Windows paths returned without a Defender prefix
        windows_path_match = re.search(
            r"[A-Za-z]:\\[^\r\n]+",
            resource_text,
        )

        if not windows_path_match:
            return None

        detected_path = windows_path_match.group(0).strip()

    # Stops at nested Defender resources while preserving normal semicolons
    detected_path = re.split(
        r";(?=(?:containerfile|file):_)",
        detected_path,
        maxsplit=1,
        flags=re.IGNORECASE,
    )[0].strip()

    # Keeps the outer container for other archive-member notations
    for separator in ("->", "!", "|"):
        if separator in detected_path:
            detected_path = detected_path.split(separator, 1)[0].strip()

    return Path(detected_path)


########################################
### Removes Flagged Backup Files     ###
########################################

def remove_flagged_files(scan_result):
    """Deletes flagged files that are safely inside a custom-scanned folder."""
    if scan_result.get("scan_type") != "Custom Scan":
        raise ValueError(
            "Flagged-file removal is only available after a custom scan."
        )

    scan_path = scan_result.get("scan_path")

    if not scan_path:
        raise ValueError("The completed scan does not include a scan target.")

    scanned_root = Path(scan_path).expanduser()

    if not scanned_root.exists() or not scanned_root.is_dir():
        raise ValueError(
            "Flagged-file removal requires a custom folder scan."
        )

    scanned_root = scanned_root.resolve()
    cleanup_results = []
    processed_paths = set()

    # Reviews every affected resource reported by Defender
    for detection in scan_result.get("detections", []):
        threat_name = detection.get("threat_name") or "Unknown Threat"

        for resource in detection.get("resources", []):
            detected_path = _extract_detected_file_path(resource)

            if detected_path is None:
                cleanup_results.append(
                    {
                        "threat_name": threat_name,
                        "resource": str(resource),
                        "path": None,
                        "status": "skipped",
                        "reason": "No local file path could be read.",
                    }
                )
                continue

            normalized_path = str(detected_path).casefold()

            # Prevents duplicate deletion attempts for the same file
            if normalized_path in processed_paths:
                continue

            processed_paths.add(normalized_path)

            try:
                resolved_path = detected_path.resolve(strict=False)
            except OSError as error:
                cleanup_results.append(
                    {
                        "threat_name": threat_name,
                        "resource": str(resource),
                        "path": str(detected_path),
                        "status": "failed",
                        "reason": str(error),
                    }
                )
                continue

            # Never removes anything outside the folder that was explicitly scanned
            try:
                is_inside_scan = resolved_path.is_relative_to(scanned_root)
            except AttributeError:
                is_inside_scan = (
                    scanned_root == resolved_path
                    or scanned_root in resolved_path.parents
                )

            if not is_inside_scan:
                cleanup_results.append(
                    {
                        "threat_name": threat_name,
                        "resource": str(resource),
                        "path": str(resolved_path),
                        "status": "skipped",
                        "reason": "The file is outside the scanned folder.",
                    }
                )
                continue

            if not resolved_path.exists():
                cleanup_results.append(
                    {
                        "threat_name": threat_name,
                        "resource": str(resource),
                        "path": str(resolved_path),
                        "status": "skipped",
                        "reason": (
                            "The file no longer exists or Defender already "
                            "removed or quarantined it."
                        ),
                    }
                )
                continue

            if not resolved_path.is_file():
                cleanup_results.append(
                    {
                        "threat_name": threat_name,
                        "resource": str(resource),
                        "path": str(resolved_path),
                        "status": "skipped",
                        "reason": "Only files can be removed automatically.",
                    }
                )
                continue

            try:
                resolved_path.unlink()
                cleanup_results.append(
                    {
                        "threat_name": threat_name,
                        "resource": str(resource),
                        "path": str(resolved_path),
                        "status": "removed",
                        "reason": None,
                    }
                )
            except (PermissionError, OSError) as error:
                cleanup_results.append(
                    {
                        "threat_name": threat_name,
                        "resource": str(resource),
                        "path": str(resolved_path),
                        "status": "failed",
                        "reason": str(error),
                    }
                )

    summary = {
        "scan_path": str(scanned_root),
        "results": cleanup_results,
        "removed_count": sum(
            1 for item in cleanup_results if item["status"] == "removed"
        ),
        "skipped_count": sum(
            1 for item in cleanup_results if item["status"] == "skipped"
        ),
        "failed_count": sum(
            1 for item in cleanup_results if item["status"] == "failed"
        ),
    }
    summary["log_file"] = str(_write_cleanup_log(summary))

    return summary


########################################
### Writes a Backup Cleanup Log      ###
########################################

def _write_cleanup_log(summary):
    """Writes a report for flagged files removed from a scanned backup."""
    log_directory = get_defender_log_directory()
    log_directory.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    log_file = log_directory / f"defender_backup_cleanup_{timestamp}.txt"

    log_lines = [
        "M+S IT Acquisition Toolbox",
        "Microsoft Defender Backup Cleanup Report",
        "",
        f"Scanned folder: {summary['scan_path']}",
        f"Files removed: {summary['removed_count']}",
        f"Files skipped: {summary['skipped_count']}",
        f"Removal failures: {summary['failed_count']}",
        "",
    ]

    if not summary["results"]:
        log_lines.append("No removable flagged file paths were reported.")
    else:
        for item in summary["results"]:
            log_lines.extend(
                [
                    f"Status: {item['status'].upper()}",
                    f"Threat: {item['threat_name']}",
                    f"Path: {item['path'] or 'Not available'}",
                    f"Resource: {item['resource']}",
                ]
            )

            if item["reason"]:
                log_lines.append(f"Reason: {item['reason']}")

            log_lines.append("")

    log_file.write_text("\n".join(log_lines), encoding="utf-8")
    return log_file


#################################
### Writes a Defender Scan Log ###
#################################

def _write_scan_log(result):
    """Writes one timestamped Microsoft Defender scan report."""
    log_directory = get_defender_log_directory()
    log_directory.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    scan_slug = result["scan_type"].casefold().replace(" ", "_")
    log_file = log_directory / f"defender_{scan_slug}_{timestamp}.txt"

    log_lines = [
        "M+S IT Acquisition Toolbox",
        f"Microsoft Defender {result['scan_type']} Report",
        "",
        f"Status: {result['status']}",
        f"Scan type: {result['scan_type']}",
        (
            f"Scan target: {result['scan_path']}"
            if result.get("scan_path")
            else (
                "Scan target: Full system"
                if result["scan_type"] == "Full Scan"
                else "Scan target: Microsoft Defender quick-scan locations"
            )
        ),
        f"Start time: {result.get('start_time') or 'Not reported'}",
        f"End time: {result.get('end_time') or 'Not reported'}",
        f"Duration: {result['duration_seconds']} seconds",
        f"Antivirus enabled: {result.get('antivirus_enabled')}",
        (
            "Real-time protection enabled: "
            f"{result.get('real_time_protection_enabled')}"
        ),
        f"Threats detected during scan: {result['threat_count']}",
        "",
    ]

    if not result["detections"]:
        log_lines.append(
            f"No new threats were reported during this "
            f"{result['scan_type'].casefold()}."
        )
    else:
        for count, detection in enumerate(
            result["detections"],
            start=1,
        ):
            log_lines.extend(
                [
                    f"Detection {count}",
                    f"Threat: {detection['threat_name']}",
                    f"Severity: {detection['severity']}",
                    f"Threat ID: {detection['threat_id']}",
                    f"Active: {detection['is_active']}",
                    f"Executed: {detection['did_execute']}",
                    (
                        "Initial detection: "
                        f"{detection['initial_detection_time']}"
                    ),
                    "Affected resources:",
                ]
            )

            if detection["resources"]:
                for resource in detection["resources"]:
                    log_lines.append(f"  - {resource}")
            else:
                log_lines.append("  - No resource path was reported")

            log_lines.append("")

    log_file.write_text(
        "\n".join(log_lines),
        encoding="utf-8",
    )

    return log_file
