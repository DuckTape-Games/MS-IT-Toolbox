'''
Builds the main Robocopy page and connects its controls.
'''

###############
### Imports ###
###############

import tkinter as tk  # Creates the main Robocopy page widgets
from tkinter.ttk import Combobox  # Displays the Windows user-profile list

from ui.robocopy_actions import run_copy  # Starts the selected copy operation
from ui.robocopy_components import (  # Provides shared link and checkbox controls
    create_link_control,
    set_checkbox_values,
)
from ui.robocopy_extensions import (  # Provides extension controls and scanning
    create_extension_popup,
    default_extension_checkboxes,
)
from ui.robocopy_folders import create_user_folder_checkboxes  # Builds folder choices
from utils import helpers, theme  # Provides user discovery and visual settings


#################################
### Creates the Robocopy Menu ###
#################################

def create_robocopy_page(body):
    # Removes the previously displayed page from the body frame
    helpers.clear_frame(body)

    # Creates the fixed three-column layout used by the Robocopy page
    body.columnconfigure(0, weight=0, minsize=420)
    body.columnconfigure(1, weight=0, minsize=250)
    body.columnconfigure(2, weight=0, minsize=300)
    body.grid_propagate(False)
    body.grid_anchor("nw")

    # Stores the current folder and extension checkbox states
    folder_vars = {}
    extension_vars = {}

    # Stores the text displayed below the main action buttons
    status_var = tk.StringVar(value="Ready")

    # Holds the user selector separately so it does not shift the lower layout
    user_select_frame = tk.Frame(body, bg=theme.light_gray_background)
    user_select_frame.grid(
        column=0,
        row=0,
        columnspan=3,
        pady=(30, 15),
    )

    # Labels the Windows user-profile dropdown
    select_user_label = tk.Label(
        user_select_frame,
        text="Select User",
        font=theme.font_label,
        bg=theme.light_gray_background,
        fg=theme.dark_blue,
    )
    select_user_label.pack(side="left", padx=(0, 10))

    # Displays valid Windows profiles found under C:/Users
    user_combobox = Combobox(
        user_select_frame,
        values=helpers.get_windows_users(),
        font=theme.font_label,
        state="readonly",
        width=22,
    )
    user_combobox.pack(side="left", padx=(0, 30))

    # Explains that checked folders will be included in the copy
    folders_label = tk.Label(
        body,
        text="Selected Folders\nare included in copy",
        font=theme.font_label,
        bg=theme.light_gray_background,
        fg=theme.dark_blue,
    )
    folders_label.grid(column=0, row=1)

    # Explains that checked extensions remain eligible for copying
    extensions_label = tk.Label(
        body,
        text="Selected Extensions\nare included in copy",
        font=theme.font_label,
        bg=theme.light_gray_background,
        fg=theme.dark_blue,
    )
    extensions_label.grid(column=2, row=1)

    # Holds the folder Select All and Deselect All links
    folder_controls_frame = tk.Frame(
        body,
        bg=theme.light_gray_background,
    )
    folder_controls_frame.grid(column=0, row=2, pady=(5, 0))

    # Selects every currently displayed user folder
    select_all_folders_link = create_link_control(
        folder_controls_frame,
        "Select All",
        lambda: set_checkbox_values(folder_vars, True),
    )
    select_all_folders_link.pack(side="left", padx=8)

    # Deselects every currently displayed user folder
    deselect_all_folders_link = create_link_control(
        folder_controls_frame,
        "Deselect All",
        lambda: set_checkbox_values(folder_vars, False),
    )
    deselect_all_folders_link.pack(side="left", padx=8)

    # Holds the extension Select All and Deselect All links
    extension_controls_frame = tk.Frame(
        body,
        bg=theme.light_gray_background,
    )
    extension_controls_frame.grid(column=2, row=2, pady=(5, 0))

    # Selects every known extension in the shared extension dictionary
    select_all_extensions_link = create_link_control(
        extension_controls_frame,
        "Select All",
        lambda: set_checkbox_values(extension_vars, True),
    )
    select_all_extensions_link.pack(side="left", padx=8)

    # Deselects every known extension in the shared extension dictionary
    deselect_all_extensions_link = create_link_control(
        extension_controls_frame,
        "Deselect All",
        lambda: set_checkbox_values(extension_vars, False),
    )
    deselect_all_extensions_link.pack(side="left", padx=8)

    # Creates a fixed-size area for user-folder checkboxes
    folder_checkbox_frame = tk.Frame(
        body,
        bg=theme.light_gray_background,
        width=420,
        height=400,
    )
    folder_checkbox_frame.grid(
        column=0,
        row=3,
        padx=20,
        pady=10,
        sticky="nw",
    )

    # Prevents the folder list from resizing the complete page layout
    folder_checkbox_frame.grid_propagate(False)

    # Creates a fixed-size area for the four common extension checkboxes
    extension_checkbox_frame = tk.Frame(
        body,
        bg=theme.light_gray_background,
        width=300,
        height=400,
    )
    extension_checkbox_frame.grid(
        column=2,
        row=3,
        padx=20,
        pady=10,
        sticky="nw",
    )

    # Prevents the extension list from resizing the complete page layout
    extension_checkbox_frame.grid_propagate(False)

    # Creates the center area that holds the divider and action buttons
    middle_frame = tk.Frame(
        body,
        bg=theme.light_gray_background,
        width=250,
        height=400,
    )
    middle_frame.grid(column=1, row=2, rowspan=2, pady=10, sticky="n")
    middle_frame.grid_propagate(False)

    # Creates the vertical divider between folders and extensions
    divider_line = tk.Frame(middle_frame, bg=theme.dark_blue, width=2)
    divider_line.place(relx=0.5, rely=0, relheight=1, anchor="n")

    # Opens the full extension scan and selection popup
    scan_extensions_button = tk.Button(
        middle_frame,
        text="Scan Selected Folders\nFor Extensions",
        font=theme.font_button,
        command=lambda: create_extension_popup(
            body,
            user_combobox.get(),
            folder_vars,
            extension_vars,
        ),
    )
    scan_extensions_button.place(relx=0.5, rely=0.35, anchor="center")

    # Starts the copy using the current user, folder, and extension choices
    run_copy_button = tk.Button(
        middle_frame,
        text="Run Copy",
        font=theme.font_button,
        command=lambda: run_copy(
            body,
            user_combobox.get(),
            folder_vars,
            extension_vars,
            status_var,
        ),
    )
    run_copy_button.place(relx=0.5, rely=0.70, anchor="center")

    # Displays Ready, running, completed, or failed status text
    status_label = tk.Label(
        middle_frame,
        textvariable=status_var,
        font=theme.font_main,
        bg=theme.light_gray_background,
        fg=theme.dark_blue,
        wraplength=220,
        justify="center",
    )
    status_label.place(relx=0.5, rely=0.88, anchor="center")

    # Rebuilds the folder checkboxes whenever a different user is selected
    user_combobox.bind(
        "<<ComboboxSelected>>",
        lambda event: create_user_folder_checkboxes(
            event,
            folder_checkbox_frame,
            folder_vars,
        ),
    )

    # Adds the four common extension choices when the page first opens
    default_extension_checkboxes(extension_checkbox_frame, extension_vars)
