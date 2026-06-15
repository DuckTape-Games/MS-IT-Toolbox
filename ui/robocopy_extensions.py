'''
Creates the common extension controls and full extension popup.
'''

###############
### Imports ###
###############

import tkinter as tk  # Creates extension-selection widgets
from tkinter import messagebox  # Displays extension-scan validation messages

from ui.robocopy_components import create_link_control  # Creates link-style controls
from ui.robocopy_folders import get_selected_folders  # Reads selected source folders
from utils import helpers, theme  # Provides extension scanning and visual settings


###################################
### Common Extension Constants  ###
###################################

# These file types always remain visible on the main Robocopy page
COMMON_EXTENSIONS = [".exe", ".msi", ".bat", ".zip"]

################################################################
### Creates Checkboxes for Commonly Excluded File Extensions ###
################################################################

def default_extension_checkboxes(extension_frame, extension_vars):
    # Removes any old common extension widgets from the frame
    helpers.clear_frame(extension_frame)

    # Resets the shared extension state when the Robocopy page is created
    extension_vars.clear()

    # Creates the four common extensions as selected by default
    for count, extension in enumerate(COMMON_EXTENSIONS):
        extension_var = tk.BooleanVar(value=True)
        extension_vars[extension] = extension_var

        # Connects the main-page checkbox to the shared extension variable
        checkbox = tk.Checkbutton(
            extension_frame,
            text=extension,
            variable=extension_var,
            bg=theme.light_gray_background,
            fg=theme.dark_blue,
        )

        # Places the common extensions in a single vertical column
        checkbox.grid(column=0, row=count, sticky="w")


#####################################################
### Creates a Popup for All Extension Types Found ###
#####################################################

def create_extension_popup(body, selected_user, folder_vars, extension_vars):
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
    popup = tk.Toplevel(body)
    popup.title("All File Types")
    popup.geometry("1200x600")
    popup.minsize(750, 400)
    popup.configure(bg=theme.light_gray_background)
    popup.iconbitmap(theme.app_icon)

    # Keeps the popup attached to and in front of the main application window
    popup.transient(body.winfo_toplevel())
    popup.grab_set()

    # Adds the popup heading
    popup_title = tk.Label(
        popup,
        text="Detected File Types",
        font=theme.font_header,
        bg=theme.light_gray_background,
        fg=theme.dark_blue,
    )
    popup_title.pack(pady=(20, 10))

    # Holds the popup Select All and Deselect All links
    popup_controls_frame = tk.Frame(
        popup,
        bg=theme.light_gray_background,
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
    scroll_container = tk.Frame(popup, bg=theme.light_gray_background)
    scroll_container.pack(fill="both", expand=True, padx=20, pady=(0, 20))

    # Creates the scrollable drawing area for the extension checkbox frame
    canvas = tk.Canvas(
        scroll_container,
        bg=theme.light_gray_background,
        highlightthickness=0,
    )
    canvas.pack(side="left", fill="both", expand=True)

    # Creates and connects the visible vertical scrollbar
    scrollbar = tk.Scrollbar(
        scroll_container,
        orient="vertical",
        command=canvas.yview,
    )
    scrollbar.pack(side="right", fill="y")
    canvas.configure(yscrollcommand=scrollbar.set)

    # Creates the frame that actually contains the extension checkboxes
    checkbox_frame = tk.Frame(canvas, bg=theme.light_gray_background)

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
        # Converts Windows mouse-wheel movement into canvas scrolling
        canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

    def bind_mousewheel(event):
        # Enables wheel scrolling while the cursor is over the canvas
        canvas.bind_all("<MouseWheel>", on_mousewheel)

    def unbind_mousewheel(event=None):
        # Removes the global wheel binding when the cursor leaves or popup closes
        canvas.unbind_all("<MouseWheel>")

    # Activates and deactivates wheel scrolling based on cursor location
    canvas.bind("<Enter>", bind_mousewheel)
    canvas.bind("<Leave>", unbind_mousewheel)

    # Converts the current scan result into a set for quick membership checks
    current_extensions = set(extensions)

    # Removes stale scanned values while preserving the four main-page values
    for extension in list(extension_vars):
        if extension not in COMMON_EXTENSIONS and extension not in current_extensions:
            del extension_vars[extension]

    # Creates a shared checkbox for every extension found during the scan
    for index, extension in enumerate(extensions):
        # Reuses common extension variables so the popup and main page stay synchronized
        if extension not in extension_vars:
            extension_vars[extension] = tk.BooleanVar(value=True)

        extension_checkbox = tk.Checkbutton(
            checkbox_frame,
            text=extension,
            variable=extension_vars[extension],
            bg=theme.light_gray_background,
            fg=theme.dark_blue,
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
        no_extensions_label = tk.Label(
            checkbox_frame,
            text="No file extensions were found.",
            font=theme.font_label,
            bg=theme.light_gray_background,
            fg=theme.dark_blue,
        )
        no_extensions_label.grid(row=0, column=0, padx=20, pady=20)

    ################################
    ### Closes the Popup Safely  ###
    ################################

    def close_popup():
        # Removes the wheel binding before destroying the popup
        unbind_mousewheel()
        popup.destroy()

    # Uses the same cleanup function for the window close control
    popup.protocol("WM_DELETE_WINDOW", close_popup)

    # Adds a normal Close button below the scrollable extension area
    close_button = tk.Button(
        popup,
        text="Close",
        font=theme.font_button,
        command=close_popup,
    )
    close_button.pack(side="bottom", pady=20)
