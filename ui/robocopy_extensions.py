"""
Creates the full extension scan and selection popup.
"""

###############
### Imports ###
###############

import tkinter as tk  # Provides Canvas and BooleanVar for scrolling and state
from tkinter import messagebox  # Displays extension-scan validation messages

import customtkinter as ctk  # Creates CustomTkinter popup controls

from ui.robocopy_components import (  # Creates shared popup controls
    apply_window_icon,
    create_link_control,
)
from ui.robocopy_folders import get_selected_folders  # Reads selected source folders
from utils import helpers, theme  # Provides extension scanning and visual settings


########################################
### Default Excluded Extension Types ###
########################################

# These detected file types begin unselected in the popup
DEFAULT_UNSELECTED_EXTENSIONS = {
    ".exe",
    ".bat",
    ".msi",
    ".zip",
}


#####################################################
### Creates a Popup for All Extension Types Found ###
#####################################################

def create_extension_popup(body, selected_user, folder_vars, extension_vars):
    """Scans selected folders and displays extension choices in a popup."""
    # Stops the scan when no Windows user has been selected
    if not selected_user:
        messagebox.showwarning(
            "No User Selected",
            "Select a user before scanning for file types.",
            parent=body.winfo_toplevel(),
        )
        return

    # Collects the folders currently selected on the main page
    selected_folders = get_selected_folders(folder_vars)

    # Stops the scan when no source folders are selected
    if not selected_folders:
        messagebox.showwarning(
            "No Folders Selected",
            "Select at least one folder before scanning for file types.",
            parent=body.winfo_toplevel(),
        )
        return

    # Scans synchronously because this is the stable version used by the project
    extensions = helpers.get_unique_extensions(selected_user, folder_vars)

    # Creates the popup that displays every detected extension
    popup = ctk.CTkToplevel(body, fg_color=theme.light_gray_background)
    popup.title("All File Types")
    popup.geometry("1200x600")
    popup.minsize(750, 400)
    apply_window_icon(popup)

    # Keeps the popup attached to and in front of the main application window
    popup.transient(body.winfo_toplevel())
    popup.grab_set()

    # Adds the popup heading
    popup_title = ctk.CTkLabel(
        popup,
        text="Detected File Types",
        font=theme.font_header,
        text_color=theme.dark_blue,
        fg_color="transparent",
    )
    popup_title.pack(pady=(20, 10))

    # Holds the popup Select All and Deselect All links
    popup_controls_frame = ctk.CTkFrame(
        popup,
        fg_color="transparent",
        corner_radius=0,
    )
    popup_controls_frame.pack(pady=(0, 10))

    # Selects only the extensions displayed in the current popup
    select_all_popup_link = create_link_control(
        popup_controls_frame,
        "Select All",
        lambda: [
            extension_vars[extension].set(True)
            for extension in extensions
            if extension in extension_vars
        ],
    )
    select_all_popup_link.pack(side="left", padx=8)

    # Deselects only the extensions displayed in the current popup
    deselect_all_popup_link = create_link_control(
        popup_controls_frame,
        "Deselect All",
        lambda: [
            extension_vars[extension].set(False)
            for extension in extensions
            if extension in extension_vars
        ],
    )
    deselect_all_popup_link.pack(side="left", padx=8)

    # Holds the scrollable canvas and vertical scrollbar
    scroll_container = ctk.CTkFrame(
        popup,
        fg_color="transparent",
        corner_radius=0,
    )
    scroll_container.pack(fill="both", expand=True, padx=20, pady=(0, 20))
    scroll_container.rowconfigure(0, weight=1)
    scroll_container.columnconfigure(0, weight=1)

    # CustomTkinter has no canvas widget, so Tk Canvas provides scrolling only
    canvas = tk.Canvas(
        scroll_container,
        bg=theme.light_gray_background,
        highlightthickness=0,
    )
    canvas.grid(row=0, column=0, sticky="nsew")

    # Creates and connects the CustomTkinter vertical scrollbar
    scrollbar = ctk.CTkScrollbar(
        scroll_container,
        orientation="vertical",
        command=canvas.yview,
        fg_color=theme.scrollbar_track,
        button_color=theme.scrollbar_thumb,
        button_hover_color=theme.scrollbar_hover,
    )
    scrollbar.grid(row=0, column=1, sticky="ns", padx=(8, 0))
    canvas.configure(yscrollcommand=scrollbar.set)

    # Creates the CustomTkinter frame that contains extension checkboxes
    checkbox_frame = ctk.CTkFrame(
        canvas,
        fg_color=theme.light_gray_background,
        corner_radius=0,
    )

    # Places the checkbox frame inside the canvas as a scrollable window item
    checkbox_window = canvas.create_window(
        (0, 0),
        window=checkbox_frame,
        anchor="nw",
    )

    # Updates the scrollable area whenever checkbox content changes size
    checkbox_frame.bind(
        "<Configure>",
        lambda event: canvas.configure(scrollregion=canvas.bbox("all")),
    )

    # Keeps the inner checkbox frame as wide as the visible canvas
    canvas.bind(
        "<Configure>",
        lambda event: canvas.itemconfigure(checkbox_window, width=event.width),
    )

    ########################################
    ### Handles Popup Mouse-Wheel Scroll ###
    ########################################

    def on_mousewheel(event):
        """Scrolls the extension list with the Windows mouse wheel."""
        # Converts Windows mouse-wheel movement into canvas scrolling
        canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

    def bind_mousewheel(event=None):
        """Enables mouse-wheel scrolling while the popup is active."""
        # Enables wheel scrolling while the cursor is over the canvas
        canvas.bind_all("<MouseWheel>", on_mousewheel)

    def unbind_mousewheel(event=None):
        """Removes the popup mouse-wheel binding when it is not needed."""
        # Removes the global wheel binding when the cursor leaves or popup closes
        canvas.unbind_all("<MouseWheel>")

    # Activates and deactivates wheel scrolling based on cursor location
    canvas.bind("<Enter>", bind_mousewheel)
    canvas.bind("<Leave>", unbind_mousewheel)
    checkbox_frame.bind("<Enter>", bind_mousewheel)
    checkbox_frame.bind("<Leave>", unbind_mousewheel)

    # Converts the current scan result into a set for quick membership checks
    current_extensions = set(extensions)

    # Removes extension values that are no longer present in the current scan
    for extension in list(extension_vars):
        if extension not in current_extensions:
            del extension_vars[extension]

    # Creates a shared CustomTkinter checkbox for every extension found
    for index, extension in enumerate(extensions):
        # Defaults executable and archive types to excluded while including all others
        if extension not in extension_vars:
            starts_selected = (
                extension.casefold() not in DEFAULT_UNSELECTED_EXTENSIONS
            )
            extension_vars[extension] = tk.BooleanVar(value=starts_selected)

        # Creates the checkbox connected to this extension's shared state
        extension_checkbox = ctk.CTkCheckBox(
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
        )

        # Places the full extension list in three columns
        extension_checkbox.grid(
            row=index // 3,
            column=index % 3,
            sticky="w",
            padx=10,
            pady=5,
        )

    # Displays a message when the selected folders contain no file extensions
    if not extensions:
        no_extensions_label = ctk.CTkLabel(
            checkbox_frame,
            text="No file extensions were found.",
            font=theme.font_label,
            text_color=theme.dark_blue,
            fg_color="transparent",
        )
        no_extensions_label.grid(row=0, column=0, padx=20, pady=20)

    ###############################
    ### Closes the Popup Safely ###
    ###############################

    def close_popup():
        """Removes temporary bindings and closes the extension popup."""
        # Removes the wheel binding before destroying the popup
        unbind_mousewheel()
        popup.destroy()

    # Uses the same cleanup function for the window close control
    popup.protocol("WM_DELETE_WINDOW", close_popup)

    # Adds a normal Close button below the scrollable extension area
    close_button = ctk.CTkButton(
        popup,
        text="Close",
        font=theme.font_button,
        fg_color=theme.primary_blue,
        hover_color=theme.dark_blue,
        command=close_popup,
    )
    close_button.pack(side="bottom", pady=20)
