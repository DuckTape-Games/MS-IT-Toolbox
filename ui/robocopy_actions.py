'''
Validates selections and starts the Robocopy workflow.
'''

###############
### Imports ###
###############

from tkinter import messagebox  # Displays copy confirmations and results

from services import robocopy_service  # Runs the batch-file Robocopy workflow
from ui.robocopy_folders import get_selected_folders  # Reads selected source folders


##############################################
### Runs Robocopy With the Current Choices ###
##############################################

def run_copy(
    body,
    selected_user,
    folder_vars,
    extension_vars,
    status_var,
    backup_type,
    incremental_destination,
    save_chromium_bookmarks,
):
    """Validates the current choices and starts the Robocopy workflow."""
    # Gets the main application window for message-box ownership
    parent_window = body.winfo_toplevel()

    # Stops the copy when no Windows user is selected
    if not selected_user:
        messagebox.showwarning(
            "No User Selected",
            "Select a user before running Robocopy.",
            parent=parent_window,
        )
        return

    # Collects the folders currently selected for copying
    selected_folders = get_selected_folders(folder_vars)

    # Requires at least one folder or the Chromium bookmark option
    if not selected_folders and not save_chromium_bookmarks:
        messagebox.showwarning(
            "Nothing Selected",
            (
                "Select at least one folder or enable Chromium bookmark "
                "backup before starting."
            ),
            parent=parent_window,
        )
        return

    # Accepts only the two backup modes exposed by the radio buttons
    if backup_type not in {"initial", "incremental"}:
        messagebox.showwarning(
            "Invalid Backup Type",
            "Select either Initial or Incremental backup.",
            parent=parent_window,
        )
        return

    # Incremental copies require an existing destination selected by the technician
    if backup_type == "incremental" and not incremental_destination:
        messagebox.showwarning(
            "No Existing Backup Selected",
            "Choose an existing backup folder before running an incremental backup.",
            parent=parent_window,
        )
        return

    # Converts unchecked extension variables into Robocopy exclusions
    excluded_extensions = [
        extension
        for extension, variable in extension_vars.items()
        if not variable.get()
    ]

    # Builds a mode-specific destination summary for final confirmation
    destination_summary = (
        "A new timestamped folder in the selected user profile"
        if backup_type == "initial"
        else incremental_destination
    )
    backup_type_name = (
        "Initial Backup"
        if backup_type == "initial"
        else "Incremental Backup"
    )

    # Gives the technician a summary before starting the copy
    confirmed = messagebox.askyesno(
        f"Confirm {backup_type_name}",
        (
            f"Backup type: {backup_type_name}\n"
            f"User: {selected_user}\n"
            f"Folders: {len(selected_folders)} selected\n"
            f"Chromium bookmarks: "
            f"{'Included' if save_chromium_bookmarks else 'Not included'}\n"
            f"Destination: {destination_summary}\n"
            f"Excluded file types: {len(excluded_extensions)}\n\n"
            "Start M+S File Copy?"
        ),
        parent=parent_window,
    )

    # Returns to the page without copying when the confirmation is declined
    if not confirmed:
        return

    # Updates the interface before the synchronous Robocopy process begins
    status_var.set(f"{backup_type_name} is running...")
    parent_window.update_idletasks()

    try:
        # Sends the selected values into the service and editable batch file
        result = robocopy_service.run_robocopy(
            username=selected_user,
            selected_folders=selected_folders,
            excluded_extensions=excluded_extensions,
            backup_type=backup_type,
            incremental_destination=incremental_destination,
            save_chromium_bookmarks=save_chromium_bookmarks,
        )
    except (FileNotFoundError, PermissionError, OSError, RuntimeError, ValueError) as error:
        # Displays errors caused by missing files, permissions, or Windows commands
        status_var.set("Copy failed")
        messagebox.showerror(
            "Robocopy Failed",
            str(error),
            parent=parent_window,
        )
        return

    # Collects folder and bookmark failures separately for clear reporting
    failed_results = [
        folder_result
        for folder_result in result["results"]
        if not folder_result["success"]
    ]
    bookmark_failures = result.get("bookmark_failures", [])

    if result["success"]:
        status_var.set(f"{backup_type_name} completed successfully")
        messagebox.showinfo(
            f"{backup_type_name} Complete",
            (
                f"{backup_type_name} completed successfully.\n\n"
                f"Destination: {result['destination']}\n"
                f"Chromium bookmark files saved: "
                f"{result.get('bookmark_files_copied', 0)}\n"
                f"Importable bookmark HTML files created: "
                f"{result.get('bookmark_html_files_created', 0)}\n"
                f"Logs: {result['log_folder']}"
            ),
            parent=parent_window,
        )
        return

    status_var.set(f"{backup_type_name} completed with errors")
    error_sections = []

    if failed_results:
        failed_names = ", ".join(
            folder_result["folder"] for folder_result in failed_results
        )
        error_sections.append(f"Failed folders: {failed_names}")

    if save_chromium_bookmarks and not result.get("bookmarks_found", False):
        error_sections.append(
            "Chromium bookmarks: No supported bookmark files were found."
        )

    if bookmark_failures:
        bookmark_messages = []
        for bookmark_result in bookmark_failures:
            browser_profile = (
                f"{bookmark_result['browser']} / "
                f"{bookmark_result['profile']}"
            )
            if bookmark_result.get("error"):
                detail = bookmark_result["error"]
            elif bookmark_result.get("html_error"):
                detail = (
                    "Original copied, but HTML conversion failed: "
                    f"{bookmark_result['html_error']}"
                )
            else:
                detail = "Bookmark backup did not complete."
            bookmark_messages.append(f"{browser_profile}: {detail}")
        error_sections.append(
            "Bookmark failures:\n- " + "\n- ".join(bookmark_messages)
        )

    if not error_sections:
        error_sections.append("The copy operation did not complete successfully.")

    messagebox.showwarning(
        "Copy Completed With Errors",
        "\n\n".join(error_sections)
        + f"\n\nLogs: {result['log_folder']}",
        parent=parent_window,
    )
