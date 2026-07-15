"""
Creates the full extension scan and selection popup.
"""

###############
### Imports ###
###############

import threading  # Scans large profiles without freezing the interface
import tkinter as tk  # Provides Canvas and BooleanVar for scrolling and state
from tkinter import messagebox  # Displays extension-scan validation messages

import customtkinter as ctk  # Creates CustomTkinter popup controls

from ui.robocopy_components import apply_window_icon, create_link_control
from ui.robocopy_folders import get_selected_folders
from utils import helpers, theme

DEFAULT_UNSELECTED_EXTENSIONS = {".exe", ".bat", ".msi", ".zip"}


def create_extension_popup(body, selected_user, folder_vars, extension_vars):
    """Scans selected folders in the background and displays file types."""
    parent_window = body.winfo_toplevel()

    if not selected_user:
        messagebox.showwarning(
            "No User Selected",
            "Select a user before scanning for file types.",
            parent=parent_window,
        )
        return

    selected_folders = get_selected_folders(folder_vars)
    if not selected_folders:
        messagebox.showwarning(
            "No Folders Selected",
            "Select at least one folder before scanning for file types.",
            parent=parent_window,
        )
        return

    # Takes a snapshot so later checkbox changes cannot alter this active scan
    scan_folder_vars = {
        path: variable.get()
        for path, variable in folder_vars.items()
    }

    popup = ctk.CTkToplevel(body, fg_color=theme.light_gray_background)
    popup.title("All File Types")
    popup.geometry("1200x600")
    popup.minsize(750, 400)
    apply_window_icon(popup)
    popup.transient(parent_window)
    popup.grab_set()

    popup_active = {"value": True}

    def popup_exists():
        try:
            return popup_active["value"] and popup.winfo_exists()
        except tk.TclError:
            return False

    loading_label = ctk.CTkLabel(
        popup,
        text="Scanning selected folders for file types...",
        font=theme.font_header,
        text_color=theme.dark_blue,
    )
    loading_label.pack(expand=True)

    progress_bar = ctk.CTkProgressBar(
        popup,
        width=420,
        mode="indeterminate",
        progress_color=theme.primary_blue,
    )
    progress_bar.pack(pady=(0, 40))
    progress_bar.start()

    def close_popup():
        popup_active["value"] = False
        try:
            popup.grab_release()
        except tk.TclError:
            pass
        popup.destroy()

    popup.protocol("WM_DELETE_WINDOW", close_popup)

    def populate_extensions(extensions):
        if not popup_exists():
            return

        progress_bar.stop()
        for widget in popup.winfo_children():
            widget.destroy()

        title = ctk.CTkLabel(
            popup,
            text="Detected File Types",
            font=theme.font_header,
            text_color=theme.dark_blue,
        )
        title.pack(pady=(20, 10))

        controls = ctk.CTkFrame(popup, fg_color="transparent")
        controls.pack(pady=(0, 10))

        current_extensions = set(extensions)
        for extension in list(extension_vars):
            if extension not in current_extensions:
                del extension_vars[extension]

        for extension in extensions:
            if extension not in extension_vars:
                extension_vars[extension] = tk.BooleanVar(
                    value=extension.casefold() not in DEFAULT_UNSELECTED_EXTENSIONS
                )

        create_link_control(
            controls,
            "Select All",
            lambda: [extension_vars[item].set(True) for item in extensions],
        ).pack(side="left", padx=8)
        create_link_control(
            controls,
            "Deselect All",
            lambda: [extension_vars[item].set(False) for item in extensions],
        ).pack(side="left", padx=8)

        container = ctk.CTkFrame(popup, fg_color="transparent")
        container.pack(fill="both", expand=True, padx=20, pady=(0, 10))
        container.rowconfigure(0, weight=1)
        container.columnconfigure(0, weight=1)

        canvas = tk.Canvas(
            container,
            bg=theme.light_gray_background,
            highlightthickness=0,
        )
        canvas.grid(row=0, column=0, sticky="nsew")
        scrollbar = ctk.CTkScrollbar(
            container,
            orientation="vertical",
            command=canvas.yview,
            fg_color=theme.scrollbar_track,
            button_color=theme.scrollbar_thumb,
            button_hover_color=theme.scrollbar_hover,
        )
        scrollbar.grid(row=0, column=1, sticky="ns", padx=(8, 0))
        canvas.configure(yscrollcommand=scrollbar.set)

        checkbox_frame = ctk.CTkFrame(
            canvas,
            fg_color=theme.light_gray_background,
            corner_radius=0,
        )
        window_id = canvas.create_window((0, 0), window=checkbox_frame, anchor="nw")
        checkbox_frame.bind(
            "<Configure>",
            lambda event: canvas.configure(scrollregion=canvas.bbox("all")),
        )
        canvas.bind(
            "<Configure>",
            lambda event: canvas.itemconfigure(window_id, width=event.width),
        )

        def on_mousewheel(event):
            canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

        canvas.bind("<Enter>", lambda event: canvas.bind_all("<MouseWheel>", on_mousewheel))
        canvas.bind("<Leave>", lambda event: canvas.unbind_all("<MouseWheel>"))

        if extensions:
            for index, extension in enumerate(extensions):
                ctk.CTkCheckBox(
                    checkbox_frame,
                    text=extension,
                    variable=extension_vars[extension],
                    font=theme.font_main,
                    text_color=theme.dark_blue,
                    fg_color=theme.primary_blue,
                    hover_color=theme.dark_blue,
                    border_color=theme.dark_blue,
                    checkbox_width=18,
                    checkbox_height=18,
                ).grid(
                    row=index // 3,
                    column=index % 3,
                    sticky="w",
                    padx=10,
                    pady=5,
                )
        else:
            ctk.CTkLabel(
                checkbox_frame,
                text="No file extensions were found.",
                font=theme.font_label,
                text_color=theme.dark_blue,
            ).grid(row=0, column=0, padx=20, pady=20)

        ctk.CTkButton(
            popup,
            text="Close",
            font=theme.font_button,
            fg_color=theme.primary_blue,
            hover_color=theme.dark_blue,
            command=close_popup,
        ).pack(side="bottom", pady=20)

    def handle_scan_error(error_message):
        if not popup_exists():
            return
        close_popup()
        messagebox.showerror(
            "Extension Scan Failed",
            error_message,
            parent=parent_window,
        )

    def scan_worker():
        try:
            extensions = helpers.get_unique_extensions(
                selected_user,
                scan_folder_vars,
            )
        except (PermissionError, FileNotFoundError, OSError) as error:
            error_message = str(error)
            if popup_exists():
                popup.after(
                    0,
                    lambda message=error_message: handle_scan_error(message),
                )
            return

        if popup_exists():
            popup.after(
                0,
                lambda found_extensions=extensions: populate_extensions(
                    found_extensions
                ),
            )

    threading.Thread(target=scan_worker, daemon=True).start()
