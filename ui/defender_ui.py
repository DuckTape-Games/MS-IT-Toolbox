"""
Creates the Microsoft Defender UI Page
"""

###############
### Imports ###
###############

import threading  # Runs Defender without freezing the application
from pathlib import Path  # Checks whether a custom target is a folder
import tkinter as tk  # Stores scan choices and paths
from tkinter import filedialog, messagebox  # Selects targets and displays dialogs

import customtkinter as ctk  # Creates the Defender page controls

from services import defender_service  # Runs Microsoft Defender scans
from utils import helpers, theme  # Provides frame helpers and shared theme values


#####################################
### Formats a Scan Time Duration  ###
#####################################

def _format_duration(duration_seconds):
    """Returns a readable scan duration."""
    minutes, seconds = divmod(max(0, duration_seconds), 60)

    if minutes:
        return f"{minutes} minute(s), {seconds} second(s)"

    return f"{seconds} second(s)"


#####################################
### Formats Defender Scan Results ###
#####################################

def _format_scan_results(result):
    """Returns technician-readable Microsoft Defender scan results."""
    result_lines = [
        f"{result['scan_type'].upper()} COMPLETED",
        "",
        f"Threats detected during this scan: {result['threat_count']}",
        f"Duration: {_format_duration(result['duration_seconds'])}",
    ]

    if result.get("scan_path"):
        result_lines.append(f"Scan target: {result['scan_path']}")

    result_lines.extend(
        [
            (
                "Real-time protection enabled: "
                f"{result.get('real_time_protection_enabled')}"
            ),
            f"Log: {result['log_file']}",
        ]
    )

    if not result["detections"]:
        result_lines.extend(
            [
                "",
                f"No new threats were reported during this "
                f"{result['scan_type'].casefold()}.",
            ]
        )
        return "\n".join(result_lines)

    result_lines.extend(["", "DETECTIONS"])

    for count, detection in enumerate(
        result["detections"],
        start=1,
    ):
        result_lines.extend(
            [
                "",
                f"{count}. {detection['threat_name']}",
                f"Severity: {detection['severity']}",
            ]
        )

        if detection["resources"]:
            result_lines.append("Affected resources:")

            for resource in detection["resources"]:
                result_lines.append(f"  - {resource}")

    return "\n".join(result_lines)


########################################
### Creates the Defender UI Branch   ###
########################################

def create_defender_page(body):
    """Builds the Microsoft Defender scan interface."""
    # Removes widgets from the previously displayed page
    helpers.clear_frame(body)

    # Stores the active scan type and custom file or folder selection
    scan_type_var = tk.StringVar(value="quick")
    custom_scan_path_var = tk.StringVar(value="")

    # Stores the last completed scan for optional backup cleanup
    last_scan_result = {"value": None}

    # Creates the main page heading
    page_title = ctk.CTkLabel(
        body,
        text="Microsoft Defender",
        font=theme.font_header,
        text_color=theme.dark_blue,
        fg_color="transparent",
    )
    page_title.pack(pady=(22, 3))

    # Explains which Defender features are currently available
    page_description = ctk.CTkLabel(
        body,
        text=(
            "Run a Microsoft Defender quick scan, full scan, or scan "
            "one selected file or folder."
        ),
        font=theme.font_label,
        text_color=theme.dark_blue,
        fg_color="transparent",
        wraplength=700,
        justify="center",
    )
    page_description.pack(pady=(0, 12))

    # Holds scan controls and the result report side by side
    page_content = ctk.CTkFrame(
        body,
        fg_color="transparent",
        corner_radius=0,
    )
    page_content.pack(fill="both", expand=True, padx=35, pady=(0, 12))

    # Gives this page instance a unique identity for background callbacks
    page_token = object()
    body._defender_page_token = page_token

    def page_is_active():
        """Returns True while this exact Defender page is still displayed."""
        # This function is called only from Tkinter's main thread
        if getattr(body, "_defender_page_token", None) is not page_token:
            return False

        try:
            return bool(page_content.winfo_exists())
        except tk.TclError:
            return False

    def run_if_page_active(callback, *callback_args):
        """Runs one UI callback only while this page still exists."""
        if page_is_active():
            callback(*callback_args)

    def schedule_page_callback(callback, *callback_args):
        """Schedules a guarded UI callback from a background thread."""
        try:
            body.after(
                0,
                lambda: run_if_page_active(
                    callback,
                    *callback_args,
                ),
            )
        except (RuntimeError, tk.TclError):
            # The application was closed before the callback was scheduled
            pass

    page_content.grid_columnconfigure(0, weight=1)
    page_content.grid_columnconfigure(1, weight=1)
    page_content.grid_rowconfigure(0, weight=1)

    # Contains scan configuration controls
    scan_panel = ctk.CTkFrame(
        page_content,
        fg_color=theme.white,
        border_color=theme.dark_blue,
        border_width=1,
        corner_radius=8,
    )
    scan_panel.grid(
        row=0,
        column=0,
        sticky="nsew",
        padx=(0, 10),
    )

    # Displays scan results and threat details
    results_panel = ctk.CTkFrame(
        page_content,
        fg_color=theme.white,
        border_color=theme.dark_blue,
        border_width=1,
        corner_radius=8,
    )
    results_panel.grid(
        row=0,
        column=1,
        sticky="nsew",
        padx=(10, 0),
    )
    results_panel.grid_rowconfigure(1, weight=1)
    results_panel.grid_rowconfigure(2, weight=0)
    results_panel.grid_columnconfigure(0, weight=1)

    # Labels the available Defender scan choices
    scan_type_label = ctk.CTkLabel(
        scan_panel,
        text="Scan Type",
        font=theme.font_button,
        text_color=theme.dark_blue,
        fg_color="transparent",
    )
    scan_type_label.pack(pady=(24, 12))

    # Displays current scan state above the progress bar
    status_var = tk.StringVar(value="Ready to run a quick scan")
    status_label = ctk.CTkLabel(
        scan_panel,
        textvariable=status_var,
        font=theme.font_label,
        text_color=theme.dark_blue,
        fg_color="transparent",
        wraplength=420,
        justify="center",
    )

    # Shows indeterminate activity while Defender is running
    progress_bar = ctk.CTkProgressBar(
        scan_panel,
        width=360,
        height=12,
        mode="indeterminate",
        progress_color=theme.primary_blue,
    )

    # Holds references needed before every widget has been created
    scan_controls = {}

    # Refreshes button states for the currently selected scan type
    def update_scan_controls():
        """Updates controls for the selected scan type."""
        selected_scan_type = scan_type_var.get()
        custom_selected = selected_scan_type == "custom"
        full_selected = selected_scan_type == "full"

        custom_file_button.configure(
            state="normal" if custom_selected else "disabled"
        )
        custom_folder_button.configure(
            state="normal" if custom_selected else "disabled"
        )
        clear_custom_button.configure(
            state=(
                "normal"
                if custom_selected and custom_scan_path_var.get()
                else "disabled"
            )
        )

        if full_selected:
            run_scan_button.configure(
                state="normal",
                text="Run Full Scan",
            )
            status_var.set(
                "Ready to run a full system scan."
            )
        elif custom_selected:
            has_target = bool(custom_scan_path_var.get())
            run_scan_button.configure(
                state="normal" if has_target else "disabled",
                text="Run Custom Scan",
            )
            status_var.set(
                "Ready to scan the selected file or folder."
                if has_target
                else "Choose a file or folder to scan."
            )
        else:
            run_scan_button.configure(
                state="normal",
                text="Run Quick Scan",
            )
            status_var.set("Ready to run a quick scan")

    # Selects the implemented quick-scan workflow
    quick_scan_radio = ctk.CTkRadioButton(
        scan_panel,
        text="Quick Scan",
        variable=scan_type_var,
        value="quick",
        font=theme.font_label,
        text_color=theme.dark_blue,
        fg_color=theme.primary_blue,
        hover_color=theme.dark_blue,
        command=update_scan_controls,
    )
    quick_scan_radio.pack(anchor="w", padx=70, pady=7)

    # Selects the future full-system scan workflow
    full_scan_radio = ctk.CTkRadioButton(
        scan_panel,
        text="Full Scan",
        variable=scan_type_var,
        value="full",
        font=theme.font_label,
        text_color=theme.dark_blue,
        fg_color=theme.primary_blue,
        hover_color=theme.dark_blue,
        command=update_scan_controls,
    )
    full_scan_radio.pack(anchor="w", padx=70, pady=7)

    # Selects the implemented custom file or folder scan workflow
    custom_scan_radio = ctk.CTkRadioButton(
        scan_panel,
        text="Custom File or Folder Scan",
        variable=scan_type_var,
        value="custom",
        font=theme.font_label,
        text_color=theme.dark_blue,
        fg_color=theme.primary_blue,
        hover_color=theme.dark_blue,
        command=update_scan_controls,
    )
    custom_scan_radio.pack(anchor="w", padx=70, pady=7)

    # Stores and displays one selected custom scan target
    def set_custom_scan_path(selected_path):
        """Stores one selected custom scan file or folder."""
        if not selected_path:
            return

        custom_scan_path_var.set(selected_path)
        custom_path_label.configure(
            text=f"Selected: {selected_path}"
        )
        update_scan_controls()

    # Opens the file picker for a custom Defender scan
    def choose_custom_file():
        """Prompts for one file to scan."""
        selected_file = filedialog.askopenfilename(
            title="Select File to Scan",
            parent=body.winfo_toplevel(),
        )
        set_custom_scan_path(selected_file)

    # Opens the folder picker for a custom Defender scan
    def choose_custom_folder():
        """Prompts for one folder to scan."""
        selected_folder = filedialog.askdirectory(
            title="Select Folder to Scan",
            parent=body.winfo_toplevel(),
        )
        set_custom_scan_path(selected_folder)

    # Clears the pending custom scan target
    def clear_custom_target():
        """Clears the selected custom scan path."""
        custom_scan_path_var.set("")
        custom_path_label.configure(
            text="No custom scan target selected"
        )
        update_scan_controls()

    # Holds custom target buttons in one row
    custom_button_frame = ctk.CTkFrame(
        scan_panel,
        fg_color="transparent",
        corner_radius=0,
    )
    custom_button_frame.pack(pady=(15, 5))

    # Selects one file for a custom scan
    custom_file_button = ctk.CTkButton(
        custom_button_frame,
        text="Choose File",
        font=theme.font_main,
        width=125,
        height=32,
        fg_color="transparent",
        hover_color="#E7ECF2",
        text_color=theme.primary_blue,
        border_color=theme.primary_blue,
        border_width=1,
        state="disabled",
        command=choose_custom_file,
    )
    custom_file_button.pack(side="left", padx=5)

    # Selects one folder for a custom scan
    custom_folder_button = ctk.CTkButton(
        custom_button_frame,
        text="Choose Folder",
        font=theme.font_main,
        width=125,
        height=32,
        fg_color="transparent",
        hover_color="#E7ECF2",
        text_color=theme.primary_blue,
        border_color=theme.primary_blue,
        border_width=1,
        state="disabled",
        command=choose_custom_folder,
    )
    custom_folder_button.pack(side="left", padx=5)

    # Displays the selected custom target
    custom_path_label = ctk.CTkLabel(
        scan_panel,
        text="No custom scan target selected",
        font=theme.font_main,
        text_color=theme.dark_blue,
        fg_color="transparent",
        wraplength=420,
        justify="center",
    )
    custom_path_label.pack(pady=(2, 3))

    # Removes the selected custom target
    clear_custom_button = ctk.CTkButton(
        scan_panel,
        text="Clear Selection",
        font=theme.font_main,
        width=130,
        height=25,
        fg_color="transparent",
        hover_color="#E7ECF2",
        text_color=theme.dark_blue,
        state="disabled",
        command=clear_custom_target,
    )
    clear_custom_button.pack(pady=(0, 8))

    # Labels the scan report panel
    results_title = ctk.CTkLabel(
        results_panel,
        text="Scan Results",
        font=theme.font_button,
        text_color=theme.dark_blue,
        fg_color="transparent",
    )
    results_title.grid(row=0, column=0, pady=(20, 8))

    # Displays scan summaries and detection details
    results_textbox = ctk.CTkTextbox(
        results_panel,
        font=theme.font_main,
        fg_color=theme.light_gray_background,
        text_color=theme.dark_blue,
        border_color=theme.scrollbar_thumb,
        border_width=1,
        corner_radius=6,
        wrap="word",
        state="disabled",
    )
    results_textbox.grid(
        row=1,
        column=0,
        sticky="nsew",
        padx=18,
        pady=(0, 10),
    )

    # Removes Defender-flagged files only from a custom-scanned folder
    remove_flagged_button = ctk.CTkButton(
        results_panel,
        text="Remove Flagged Files From Scanned Folder",
        font=theme.font_main,
        width=270,
        height=34,
        fg_color=theme.primary_blue,
        hover_color=theme.dark_blue,
        text_color=theme.white,
        state="disabled",
    )
    remove_flagged_button.grid(
        row=2,
        column=0,
        pady=(0, 16),
    )

    # Replaces visible results while keeping the text box read-only
    def display_results(result_text):
        """Displays one scan report in the results panel."""
        results_textbox.configure(state="normal")
        results_textbox.delete("1.0", "end")
        results_textbox.insert("1.0", result_text)
        results_textbox.configure(state="disabled")

    # Restores controls after a background scan has finished
    def finish_scan():
        """Restores the Defender page after a completed scan."""
        progress_bar.stop()
        progress_bar.pack_forget()
        status_label.pack_forget()

        quick_scan_radio.configure(state="normal")
        full_scan_radio.configure(state="normal")
        custom_scan_radio.configure(state="normal")
        update_scan_controls()

    # Handles successful Defender results on the Tkinter thread
    def handle_scan_success(result):
        """Displays successful Defender scan results."""
        if not page_is_active():
            return

        finish_scan()
        last_scan_result["value"] = result
        display_results(_format_scan_results(result))

        # Cleanup is limited to detected files inside a custom-scanned folder
        can_remove_flagged_files = (
            result["scan_type"] == "Custom Scan"
            and result["threat_count"] > 0
            and result.get("scan_path")
            and Path(result["scan_path"]).is_dir()
        )
        remove_flagged_button.configure(
            state="normal" if can_remove_flagged_files else "disabled"
        )

        if result["threat_count"]:
            messagebox.showwarning(
                f"{result['scan_type']} Complete",
                (
                    f"Microsoft Defender reported "
                    f"{result['threat_count']} new detection(s).\n\n"
                    "Review the Scan Results panel and log."
                ),
                parent=body.winfo_toplevel(),
            )
        else:
            messagebox.showinfo(
                f"{result['scan_type']} Complete",
                (
                    "No new threats were reported during this "
                    f"{result['scan_type'].casefold()}."
                ),
                parent=body.winfo_toplevel(),
            )

    # Handles scan failures on the Tkinter thread
    def handle_scan_error(scan_name, error_message):
        """Displays Microsoft Defender errors and restores controls."""
        if not page_is_active():
            return

        finish_scan()
        status_var.set(f"{scan_name} failed")
        display_results(
            f"{scan_name.upper()} FAILED\n\n"
            f"{error_message}"
        )
        messagebox.showerror(
            "Microsoft Defender Scan Failed",
            error_message,
            parent=body.winfo_toplevel(),
        )

    # Runs one selected Defender scan away from the UI thread
    def scan_worker(scan_type, scan_path):
        """Runs the Defender service and schedules the UI result."""
        try:
            if scan_type == "custom":
                result = defender_service.run_custom_scan(scan_path)
            elif scan_type == "full":
                result = defender_service.run_full_scan()
            else:
                result = defender_service.run_quick_scan()
        except (
            FileNotFoundError,
            PermissionError,
            OSError,
            RuntimeError,
            ValueError,
        ) as error:
            if scan_type == "custom":
                scan_name = "Custom Scan"
            elif scan_type == "full":
                scan_name = "Full Scan"
            else:
                scan_name = "Quick Scan"

            schedule_page_callback(
                handle_scan_error,
                scan_name,
                str(error),
            )
            return

        schedule_page_callback(
            handle_scan_success,
            result,
        )

    # Starts the currently selected implemented scan
    def start_selected_scan():
        """Starts Quick Scan or Custom Scan in the background."""
        selected_scan_type = scan_type_var.get()

        selected_path = custom_scan_path_var.get()

        if selected_scan_type == "custom" and not selected_path:
            messagebox.showwarning(
                "No Scan Target Selected",
                "Choose a file or folder before running a custom scan.",
                parent=body.winfo_toplevel(),
            )
            return

        if selected_scan_type == "custom":
            scan_name = "Custom Scan"
        elif selected_scan_type == "full":
            scan_name = "Full Scan"
        else:
            scan_name = "Quick Scan"
        target_summary = (
            f"\n\nTarget: {selected_path}"
            if selected_scan_type == "custom"
            else ""
        )

        confirmation_message = (
            f"Start a Microsoft Defender {scan_name.casefold()} now?"
            f"{target_summary}\n\n"
            "The application will remain open while Defender scans."
        )

        # Full scans can take much longer than quick or custom scans
        if selected_scan_type == "full":
            confirmation_message += (
                "\n\nA full scan may take a long time and can use "
                "significant system resources."
            )

        confirmed = messagebox.askyesno(
            f"Run {scan_name}",
            confirmation_message,
            parent=body.winfo_toplevel(),
        )

        if not confirmed:
            return

        last_scan_result["value"] = None
        remove_flagged_button.configure(state="disabled")

        quick_scan_radio.configure(state="disabled")
        full_scan_radio.configure(state="disabled")
        custom_scan_radio.configure(state="disabled")
        custom_file_button.configure(state="disabled")
        custom_folder_button.configure(state="disabled")
        clear_custom_button.configure(state="disabled")
        run_scan_button.configure(
            state="disabled",
            text=f"{scan_name} Running...",
        )

        status_var.set(
            f"Microsoft Defender is running a {scan_name.casefold()}."
        )
        status_label.pack(pady=(6, 4))
        progress_bar.pack(pady=(0, 10))
        progress_bar.start()

        progress_details = (
            f"Target: {selected_path}"
            if selected_scan_type == "custom"
            else "Waiting for Microsoft Defender to complete..."
        )
        display_results(
            f"{scan_name.upper()} IN PROGRESS\n\n"
            f"{progress_details}"
        )

        scan_thread = threading.Thread(
            target=scan_worker,
            args=(selected_scan_type, selected_path),
            daemon=True,
        )
        scan_thread.start()

    # Formats the result of removing flagged backup files
    def format_cleanup_results(summary):
        """Returns technician-readable backup cleanup results."""
        lines = [
            "BACKUP CLEANUP COMPLETED",
            "",
            f"Scanned folder: {summary['scan_path']}",
            f"Files removed: {summary['removed_count']}",
            f"Files skipped: {summary['skipped_count']}",
            f"Removal failures: {summary['failed_count']}",
            f"Log: {summary['log_file']}",
        ]

        if summary["results"]:
            lines.extend(["", "FILE RESULTS"])

            for item in summary["results"]:
                lines.extend(
                    [
                        "",
                        f"{item['status'].upper()}: "
                        f"{item['path'] or item['resource']}",
                    ]
                )

                if item["reason"]:
                    lines.append(f"Reason: {item['reason']}")

        return "\n".join(lines)

    # Displays completed backup cleanup results
    def handle_cleanup_success(summary):
        """Displays the cleanup summary and restores the cleanup button."""
        if not page_is_active():
            return

        remove_flagged_button.configure(
            state="disabled",
            text="Remove Flagged Files From Scanned Folder",
        )
        display_results(format_cleanup_results(summary))

        if summary["failed_count"]:
            messagebox.showwarning(
                "Backup Cleanup Completed With Errors",
                (
                    f"Removed {summary['removed_count']} flagged file(s).\n"
                    f"Failed to remove {summary['failed_count']} file(s).\n\n"
                    "Review the cleanup report for details."
                ),
                parent=body.winfo_toplevel(),
            )
        else:
            messagebox.showinfo(
                "Backup Cleanup Complete",
                (
                    f"Removed {summary['removed_count']} flagged file(s) "
                    "from the scanned folder."
                ),
                parent=body.winfo_toplevel(),
            )

    # Displays backup cleanup errors
    def handle_cleanup_error(error_message):
        """Displays a cleanup failure without deleting additional files."""
        if not page_is_active():
            return

        remove_flagged_button.configure(
            state="normal",
            text="Remove Flagged Files From Scanned Folder",
        )
        messagebox.showerror(
            "Backup Cleanup Failed",
            error_message,
            parent=body.winfo_toplevel(),
        )

    # Removes flagged files away from the Tkinter thread
    def cleanup_worker(scan_result):
        """Runs flagged-file removal and schedules the UI result."""
        try:
            summary = defender_service.remove_flagged_files(scan_result)
        except (
            FileNotFoundError,
            PermissionError,
            OSError,
            RuntimeError,
            ValueError,
        ) as error:
            schedule_page_callback(
                handle_cleanup_error,
                str(error),
            )
            return

        schedule_page_callback(
            handle_cleanup_success,
            summary,
        )

    # Confirms and starts removal of flagged files from the scanned folder
    def remove_flagged_files_from_backup():
        """Removes detected files only from the completed custom folder scan."""
        scan_result = last_scan_result["value"]

        if not scan_result:
            return

        confirmed = messagebox.askyesno(
            "Remove Flagged Files",
            (
                f"Microsoft Defender reported "
                f"{scan_result['threat_count']} detection(s).\n\n"
                f"Scanned folder:\n{scan_result['scan_path']}\n\n"
                "Remove the flagged files that are confirmed to be inside "
                "this scanned folder?\n\n"
                "Files outside this folder and the original files on another "
                "computer will not be touched. This cannot be undone."
            ),
            parent=body.winfo_toplevel(),
        )

        if not confirmed:
            return

        remove_flagged_button.configure(
            state="disabled",
            text="Removing Flagged Files...",
        )

        cleanup_thread = threading.Thread(
            target=cleanup_worker,
            args=(scan_result,),
            daemon=True,
        )
        cleanup_thread.start()

    remove_flagged_button.configure(
        command=remove_flagged_files_from_backup,
    )

    # Runs Quick Scan, Full Scan, or Custom Scan
    run_scan_button = ctk.CTkButton(
        scan_panel,
        text="Run Quick Scan",
        font=theme.font_button,
        width=230,
        height=42,
        fg_color=theme.primary_blue,
        hover_color=theme.dark_blue,
        text_color=theme.white,
        command=start_selected_scan,
    )
    run_scan_button.pack(pady=(12, 8))
    scan_controls["run_button"] = run_scan_button

    # Starts the page with a clear empty-state report
    display_results(
        "No scan has been run yet.\n\n"
        "Choose Quick Scan, Full Scan, or Custom File or Folder Scan."
    )
