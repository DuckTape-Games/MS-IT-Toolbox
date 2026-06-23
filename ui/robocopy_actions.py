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

    # Stops the copy when no source folders are selected
    if not selected_folders:
        messagebox.showwarning(
            "No Folders Selected",
            "Select at least one folder to copy.",
            parent=parent_window,
        )
        return

    # Converts unchecked extension variables into Robocopy exclusions
    excluded_extensions = [
        extension
        for extension, variable in extension_vars.items()
        if not variable.get()
    ]

    # Gives the technician a summary before starting the copy
    confirmed = messagebox.askyesno(
        "Confirm Copy",
        (
            f"User: {selected_user}\n"
            f"Folders: {len(selected_folders)} selected\n"
            "Destination: A new folder in the selected user profile\n"
            f"Excluded file types: {len(excluded_extensions)}\n\n"
            "Start Robocopy?"
        ),
        parent=parent_window,
    )

    # Returns to the page without copying when the confirmation is declined
    if not confirmed:
        return

    # Updates the interface before the synchronous Robocopy process begins
    status_var.set("Robocopy is running...")
    parent_window.update_idletasks()

    try:
        # Sends the selected values into the service and editable batch file
        result = robocopy_service.run_robocopy(
            username=selected_user,
            selected_folders=selected_folders,
            excluded_extensions=excluded_extensions,
        )
    except (FileNotFoundError, PermissionError, OSError, RuntimeError) as error:
        # Displays errors caused by missing files, permissions, or Windows commands
        status_var.set("Copy failed")
        messagebox.showerror(
            "Robocopy Failed",
            str(error),
            parent=parent_window,
        )
        return

    # Collects only the selected folders that Robocopy did not copy successfully
    failed_results = [
        folder_result
        for folder_result in result["results"]
        if not folder_result["success"]
    ]

    # Displays the destination and logs when every selected folder succeeds
    if result["success"]:
        status_var.set("Copy completed successfully")
        messagebox.showinfo(
            "Copy Complete",
            (
                "Robocopy completed successfully.\n\n"
                f"Destination: {result['destination']}\n"
                f"Logs: {result['log_folder']}"
            ),
            parent=parent_window,
        )
        return

    # Changes the status when one or more selected folders fail
    status_var.set("Copy completed with errors")

    # Creates a readable comma-separated list of failed folder names
    failed_names = ", ".join(
        folder_result["folder"] for folder_result in failed_results
    )

    # Displays the failed folders and shared log location for troubleshooting
    messagebox.showwarning(
        "Copy Completed With Errors",
        (
            "One or more folders could not be copied successfully.\n\n"
            f"Failed folders: {failed_names}\n"
            f"Logs: {result['log_folder']}"
        ),
        parent=parent_window,
    )
