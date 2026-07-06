"""
Builds the main Robocopy page and connects its controls.
"""

###############
### Imports ###
###############

import tkinter as tk  # Provides Canvas and StringVar for scrolling and status
from tkinter import filedialog  # Selects an existing backup for incremental copies

import customtkinter as ctk  # Creates the CustomTkinter Robocopy page controls

from ui.robocopy_actions import run_copy  # Starts the selected copy operation
from ui.robocopy_components import set_checkbox_values  # Updates checkbox groups
from ui.robocopy_extensions import create_extension_popup  # Opens extension scanning
from ui.robocopy_folders import (  # Builds top-level and subfolder choices
    SubfolderPanel,
    create_user_folder_checkboxes,
)
from utils import helpers, theme  # Provides user discovery and visual settings


#################################
### Creates the Robocopy Menu ###
#################################

def create_robocopy_page(body):
    """Builds the complete Robocopy page without changing its layout."""
    # Removes the previously displayed page from the body frame
    helpers.clear_frame(body)

    # Preserves the wider left and right areas with the smaller center column
    body.columnconfigure(0, weight=0, minsize=620)
    body.columnconfigure(1, weight=0, minsize=220)
    body.columnconfigure(2, weight=0, minsize=520)
    body.grid_propagate(False)
    body.grid_anchor("nw")

    # Stores all top-level, nested-folder, and extension checkbox states
    folder_vars = {}
    extension_vars = {}

    # Tracks whether the left panel is showing defaults or every folder
    folder_display_state = {}

    # Stores the text displayed below the main action buttons
    status_var = tk.StringVar(value="Ready")

    # Stores whether the technician is running an initial or incremental backup
    backup_type_var = tk.StringVar(value="initial")

    # Stores the existing destination selected for an incremental backup
    incremental_destination_var = tk.StringVar(value="")

    # Holds the user selector above all three lower sections
    user_select_frame = ctk.CTkFrame(
        body,
        fg_color="transparent",
        corner_radius=0,
    )
    user_select_frame.grid(
        column=0,
        row=0,
        columnspan=3,
        pady=(30, 15),
    )

    # Labels the Windows user-profile dropdown
    select_user_label = ctk.CTkLabel(
        user_select_frame,
        text="Select User",
        font=theme.font_label,
        text_color=theme.dark_blue,
        fg_color="transparent",
    )
    select_user_label.pack(side="left", padx=(0, 10))

    # Displays valid Windows profiles found under C:/Users
    user_combobox = ctk.CTkComboBox(
        user_select_frame,
        values=helpers.get_windows_users(),
        font=theme.font_label,
        dropdown_font=theme.font_main,
        state="readonly",
        width=220,
        fg_color=theme.white,
        border_color=theme.dark_blue,
        button_color=theme.primary_blue,
        button_hover_color=theme.dark_blue,
        text_color=theme.dark_blue,
    )
    user_combobox.pack(side="left", padx=(0, 30))
    user_combobox.set("")

    # Labels the original top-level folder list on the left
    folders_label = ctk.CTkLabel(
        body,
        text="Selected Folders\nare included in copy",
        font=theme.font_label,
        text_color=theme.dark_blue,
        fg_color="transparent",
    )
    folders_label.grid(column=0, row=1)

    # Labels the expandable nested-folder panel on the right
    subfolders_label = ctk.CTkLabel(
        body,
        text="Selected Subfolders\nare included in copy",
        font=theme.font_label,
        text_color=theme.dark_blue,
        fg_color="transparent",
    )
    subfolders_label.grid(column=2, row=1)

    # Creates a wider scrollable top-level folder area on the left
    folder_panel_frame = ctk.CTkFrame(
        body,
        fg_color=theme.light_gray_background,
        corner_radius=0,
        width=620,
        height=400,
    )
    folder_panel_frame.grid(
        column=0,
        row=3,
        padx=(20, 10),
        pady=10,
        sticky="nw",
    )
    folder_panel_frame.grid_propagate(False)
    folder_panel_frame.rowconfigure(0, weight=1)
    folder_panel_frame.columnconfigure(0, weight=1)

    # CustomTkinter has no canvas widget, so Tk Canvas provides scrolling only
    folder_canvas = tk.Canvas(
        folder_panel_frame,
        bg=theme.light_gray_background,
        highlightthickness=0,
    )
    # Creates the left panel's vertical scrollbar
    folder_vertical_scrollbar = ctk.CTkScrollbar(
        folder_panel_frame,
        orientation="vertical",
        command=folder_canvas.yview,
        fg_color=theme.scrollbar_track,
        button_color=theme.scrollbar_thumb,
        button_hover_color=theme.scrollbar_hover,
    )
    # Creates the left panel's horizontal scrollbar
    folder_horizontal_scrollbar = ctk.CTkScrollbar(
        folder_panel_frame,
        orientation="horizontal",
        command=folder_canvas.xview,
        fg_color=theme.scrollbar_track,
        button_color=theme.scrollbar_thumb,
        button_hover_color=theme.scrollbar_hover,
    )
    # Holds the top-level folder rows inside the scrolling canvas
    folder_checkbox_frame = ctk.CTkFrame(
        folder_canvas,
        fg_color=theme.light_gray_background,
        corner_radius=0,
    )

    # Places the canvas and both scrollbar options around the left panel
    folder_canvas.grid(column=0, row=0, sticky="nsew")
    folder_vertical_scrollbar.grid(
        column=1,
        row=0,
        sticky="ns",
        padx=(8, 0),
    )
    folder_horizontal_scrollbar.grid(
        column=0,
        row=1,
        sticky="ew",
        pady=(8, 0),
    )

    # Connects the inner top-level folder frame to the scrolling canvas
    folder_canvas_window = folder_canvas.create_window(
        (0, 0),
        window=folder_checkbox_frame,
        anchor="nw",
    )
    folder_canvas.configure(
        yscrollcommand=folder_vertical_scrollbar.set,
        xscrollcommand=folder_horizontal_scrollbar.set,
    )

    # Updates the left panel's scrollable area whenever folder rows change
    folder_checkbox_frame.bind(
        "<Configure>",
        lambda event: folder_canvas.configure(
            scrollregion=folder_canvas.bbox("all")
        ),
    )

    # Keeps the folder content at least as wide as the visible canvas
    folder_canvas.bind(
        "<Configure>",
        lambda event: folder_canvas.itemconfigure(
            folder_canvas_window,
            width=max(event.width, folder_checkbox_frame.winfo_reqwidth()),
        ),
    )

    # Enables Windows mouse-wheel scrolling while the pointer is over the left panel
    def scroll_folder_panel(event):
        """Scrolls the left folder panel using the Windows mouse wheel."""
        folder_canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

    def bind_folder_mousewheel(event=None):
        """Enables left-panel mouse-wheel scrolling while hovered."""
        folder_canvas.bind_all("<MouseWheel>", scroll_folder_panel)

    def unbind_folder_mousewheel(event=None):
        """Removes the left-panel mouse-wheel binding after hover ends."""
        folder_canvas.unbind_all("<MouseWheel>")

    folder_canvas.bind("<Enter>", bind_folder_mousewheel)
    folder_canvas.bind("<Leave>", unbind_folder_mousewheel)
    folder_checkbox_frame.bind("<Enter>", bind_folder_mousewheel)
    folder_checkbox_frame.bind("<Leave>", unbind_folder_mousewheel)

    # Creates the middle action area
    middle_frame = ctk.CTkFrame(
        body,
        fg_color=theme.light_gray_background,
        corner_radius=0,
        width=220,
        height=400,
    )
    middle_frame.grid(column=1, row=2, rowspan=2, pady=10, sticky="n")
    middle_frame.grid_propagate(False)

    # Labels the backup mode controls in the middle action area
    backup_type_label = ctk.CTkLabel(
        middle_frame,
        text="Backup Type",
        font=theme.font_label,
        text_color=theme.dark_blue,
        fg_color="transparent",
    )
    backup_type_label.place(relx=0.5, rely=0.08, anchor="center")

    # Groups both backup options so only one can be selected at a time
    backup_type_frame = ctk.CTkFrame(
        middle_frame,
        fg_color="transparent",
        corner_radius=0,
    )
    backup_type_frame.place(relx=0.5, rely=0.18, anchor="center")

    # Finds and displays the newest generated backup for the selected user
    def select_latest_backup():
        """Automatically selects the newest backup for the current user."""
        selected_user = user_combobox.get().strip()

        # Clears the destination until a valid user and backup are found
        incremental_destination_var.set("")

        if not selected_user:
            selected_backup_label.configure(
                text="Select a user to find their latest backup"
            )
            return None

        latest_backup = helpers.find_most_recent_backup(selected_user)

        if latest_backup is None:
            selected_backup_label.configure(
                text="No existing backup found for this user"
            )
            return None

        incremental_destination_var.set(str(latest_backup))
        selected_backup_label.configure(
            text=f"Latest backup: {latest_backup.name}"
        )
        return latest_backup

    # Updates button text and destination controls when the backup type changes
    def update_backup_type_controls():
        """Refreshes controls that depend on the selected backup type."""
        is_incremental = backup_type_var.get() == "incremental"

        # Makes manual backup selection available only for incremental copies
        choose_backup_button.configure(
            state="normal" if is_incremental else "disabled"
        )

        # Keeps the main action text consistent with the selected operation
        run_copy_button.configure(
            text=(
                "Run Incremental Backup"
                if is_incremental
                else "Run Initial Backup"
            )
        )

        if is_incremental:
            # Automatically fills the destination with the user's newest backup
            select_latest_backup()
        else:
            # Clears the incremental destination when returning to initial mode
            incremental_destination_var.set("")
            selected_backup_label.configure(text="No existing backup selected")

    # Allows the technician to override the automatically selected backup
    def choose_incremental_destination():
        """Prompts for a different existing backup folder."""
        selected_folder = filedialog.askdirectory(
            title="Select Existing Backup Folder",
            parent=body.winfo_toplevel(),
        )

        # Keeps the automatically detected value when the dialog is cancelled
        if not selected_folder:
            return

        incremental_destination_var.set(selected_folder)
        selected_backup_label.configure(
            text=f"Selected manually: {selected_folder}"
        )

    # Loads folders and refreshes the latest-backup match after a user change
    def handle_user_selection(selected_user):
        """Updates folder choices and incremental destination for a new user."""
        create_user_folder_checkboxes(
            selected_user,
            folder_checkbox_frame,
            subfolder_panel,
            folder_vars,
            folder_display_state,
            more_folders_button,
        )

        # Re-detects the destination only while incremental mode is active
        if backup_type_var.get() == "incremental":
            select_latest_backup()

    # Selects the normal first-time backup workflow
    initial_backup_radio = ctk.CTkRadioButton(
        backup_type_frame,
        text="Initial",
        variable=backup_type_var,
        value="initial",
        font=theme.font_main,
        text_color=theme.dark_blue,
        fg_color=theme.primary_blue,
        hover_color=theme.dark_blue,
        command=update_backup_type_controls,
    )
    initial_backup_radio.pack(side="left", padx=8)

    # Selects the workflow that updates an existing backup folder
    incremental_backup_radio = ctk.CTkRadioButton(
        backup_type_frame,
        text="Incremental",
        variable=backup_type_var,
        value="incremental",
        font=theme.font_main,
        text_color=theme.dark_blue,
        fg_color=theme.primary_blue,
        hover_color=theme.dark_blue,
        command=update_backup_type_controls,
    )
    incremental_backup_radio.pack(side="left", padx=8)

    # Opens the folder selector for an existing incremental-backup destination
    choose_backup_button = ctk.CTkButton(
        middle_frame,
        text="Choose Different Backup",
        font=theme.font_main,
        width=180,
        height=30,
        fg_color="transparent",
        hover_color="#E7ECF2",
        text_color=theme.primary_blue,
        border_color=theme.primary_blue,
        border_width=1,
        state="disabled",
        command=choose_incremental_destination,
    )
    choose_backup_button.place(relx=0.5, rely=0.28, anchor="center")

    # Displays the selected incremental destination without changing the layout
    selected_backup_label = ctk.CTkLabel(
        middle_frame,
        text="No existing backup selected",
        font=theme.font_main,
        text_color=theme.dark_blue,
        fg_color="transparent",
        wraplength=205,
        justify="center",
    )
    selected_backup_label.place(relx=0.5, rely=0.36, anchor="center")

    # Creates the scrollable subfolder area on the right
    subfolder_frame = ctk.CTkFrame(
        body,
        fg_color=theme.light_gray_background,
        corner_radius=0,
        width=520,
        height=400,
    )
    subfolder_frame.grid(
        column=2,
        row=3,
        padx=(10, 10),
        pady=10,
        sticky="nw",
    )
    subfolder_frame.grid_propagate(False)

    # Manages nested-folder rendering and mouse-wheel scrolling
    subfolder_panel = SubfolderPanel(
        subfolder_frame,
        folder_vars,
    )

    # Adds group controls above the original top-level folder list
    folder_controls_frame = ctk.CTkFrame(
        body,
        fg_color="transparent",
        corner_radius=0,
    )
    folder_controls_frame.grid(column=0, row=2, pady=(5, 0))

    # Selects every currently loaded top-level and nested folder variable
    select_all_folders = ctk.CTkButton(
        folder_controls_frame,
        text="Select All",
        width=75,
        height=24,
        fg_color="transparent",
        hover_color="#E7ECF2",
        text_color=theme.primary_blue,
        cursor="hand2",
        font=theme.font_main,
        command=lambda: set_checkbox_values(folder_vars, True),
    )
    select_all_folders.pack(side="left", padx=8)

    # Clears every currently loaded top-level and nested folder variable
    deselect_all_folders = ctk.CTkButton(
        folder_controls_frame,
        text="Deselect All",
        width=90,
        height=24,
        fg_color="transparent",
        hover_color="#E7ECF2",
        text_color=theme.primary_blue,
        cursor="hand2",
        font=theme.font_main,
        command=lambda: set_checkbox_values(folder_vars, False),
    )
    deselect_all_folders.pack(side="left", padx=8)

    # Reveals or hides the non-default top-level folders
    more_folders_button = ctk.CTkButton(
        folder_controls_frame,
        text="More Folders",
        width=105,
        height=24,
        fg_color="transparent",
        hover_color="#E7ECF2",
        text_color=theme.primary_blue,
        cursor="hand2",
        font=theme.font_main,
        state="disabled",
    )
    more_folders_button.pack(side="left", padx=8)

    # Opens the full extension scan and selection popup
    scan_extensions_button = ctk.CTkButton(
        middle_frame,
        text="Scan Selected Folders\nFor Extensions",
        font=theme.font_button,
        width=190,
        height=54,
        fg_color=theme.primary_blue,
        hover_color=theme.dark_blue,
        command=lambda: create_extension_popup(
            body,
            user_combobox.get(),
            folder_vars,
            extension_vars,
        ),
    )
    scan_extensions_button.place(relx=0.5, rely=0.50, anchor="center")

    # Starts the copy using the current user, folder, and extension choices
    run_copy_button = ctk.CTkButton(
        middle_frame,
        text="Run Initial Backup",
        font=theme.font_button,
        width=140,
        height=38,
        fg_color=theme.primary_blue,
        hover_color=theme.dark_blue,
        command=lambda: run_copy(
            body,
            user_combobox.get(),
            folder_vars,
            extension_vars,
            status_var,
            backup_type_var.get(),
            incremental_destination_var.get(),
        ),
    )
    run_copy_button.place(relx=0.5, rely=0.72, anchor="center")

    # Displays Ready, running, completed, or failed status text
    status_label = ctk.CTkLabel(
        middle_frame,
        textvariable=status_var,
        font=theme.font_main,
        text_color=theme.dark_blue,
        fg_color="transparent",
        wraplength=220,
        justify="center",
    )
    status_label.place(relx=0.5, rely=0.90, anchor="center")

    # Activates user loading after all referenced page controls have been created
    user_combobox.configure(command=handle_user_selection)
