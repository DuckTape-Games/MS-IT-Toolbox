'''
Creates the Robocopy Page
'''

###############
### Imports ###
###############

import tkinter as tk  # Creates the Robocopy page widgets
from tkinter import font as tkfont  # Creates underlined link-style fonts
from tkinter import messagebox  # Displays validation and result messages
from tkinter.ttk import Combobox  # Displays the Windows user-profile list

from services import robocopy_service  # Runs the batch-file Robocopy workflow
from utils import helpers, theme  # Provides shared helpers and visual settings


###################################
### Common Extension Constants  ###
###################################

# These file types always remain visible on the main Robocopy page
COMMON_EXTENSIONS = [".exe", ".msi", ".bat", ".zip"]


########################################
### Creates a Link-Style UI Control  ###
########################################

def create_link_control(parent, text, command):
    """Creates clickable text styled like a link."""
    # Copies the shared font so underlining does not change every normal label
    link_font = tkfont.Font(font=theme.font_main)
    link_font.configure(underline=True)

    # Creates a label that visually behaves like a hyperlink
    link = tk.Label(
        parent,
        text=text,
        font=link_font,
        bg=theme.light_gray_background,
        fg=theme.primary_blue,
        cursor="hand2",
    )

    # Calls the supplied function when the link is clicked
    link.bind("<Button-1>", lambda event: command())

    # Returns the label so the calling section can place it
    return link


#########################################
### Changes an Entire Checkbox Group  ###
#########################################

def set_checkbox_values(variable_dictionary, selected):
    """Sets every BooleanVar in a checkbox dictionary."""
    # Updates each checkbox variable to the requested selected state
    for variable in variable_dictionary.values():
        variable.set(selected)


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


########################################
### Creates User-Folder Checkboxes   ###
########################################

def create_user_folder_checkboxes(event, folder_frame, folder_vars):
    # Removes the previous user's folder checkboxes
    helpers.clear_frame(folder_frame)

    # Removes the previous user's stored checkbox variables
    folder_vars.clear()

    # Reads the selected username and retrieves that profile's top-level folders
    selected_user = event.widget.get()
    folders = helpers.get_user_folders(selected_user)

    # Configures the three checkbox columns used by the folder list
    folder_frame.columnconfigure(0, weight=0)
    folder_frame.columnconfigure(1, weight=0)
    folder_frame.columnconfigure(2, weight=0)

    # Creates a selected checkbox for every accessible top-level user folder
    for count, item in enumerate(folders):
        folder_var = tk.BooleanVar(value=True)
        folder_vars[item] = folder_var

        # Connects the displayed checkbox to its saved BooleanVar
        checkbox = tk.Checkbutton(
            folder_frame,
            text=item,
            variable=folder_var,
            bg=theme.light_gray_background,
            fg=theme.dark_blue,
        )

        # Wraps each fourth folder onto the next row
        checkbox.grid(
            column=count % 3,
            row=count // 3,
            sticky="w",
            padx=4,
            pady=2,
        )


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


###########################################
### Gets the Currently Checked Folders  ###
###########################################

def get_selected_folders(folder_vars):
    # Returns only folder names whose BooleanVar is currently True
    return [
        folder_name
        for folder_name, variable in folder_vars.items()
        if variable.get()
    ]


#############################################
### Runs Robocopy With the Current Choices ###
#############################################

def run_copy(
    body,
    selected_user,
    folder_vars,
    extension_vars,
    status_var,
):
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
