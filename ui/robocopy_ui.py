''' Creates Robocopy Page '''
###############
### Imports ###
###############
import tkinter as tk #UI Elements
from tkinter.ttk import Combobox #Used for the user list
from utils import theme, helpers #Gets the application theme items and helper methods



#################################
### Creates the robocopy menu ###
#################################

def create_robocopy_page(body):
    helpers.clear_frame(body)
    
    # Configures the columns for the main body
    body.columnconfigure(0, weight=0, minsize=420)
    body.columnconfigure(1, weight=0, minsize=250)
    body.columnconfigure(2, weight=0, minsize=300)

    body.grid_propagate(False) 
    body.grid_anchor("nw")
    
    
    # Frame for the user selector so it does not affect the folder/divider/extensions layout
    user_select_frame = tk.Frame(
        body,
        bg=theme.light_gray_background
    )

    user_select_frame.grid(
        column=0,
        row=0,
        columnspan=3,
        pady=(40, 20)
    )

    # Creates label for user drop down
    select_user_label = tk.Label(
        user_select_frame,
        text="Select User",
        font=theme.font_label,
        background=theme.light_gray_background,
        fg=theme.dark_blue
    )

    select_user_label.pack(side="left", padx=(0, 10))

    # Creates a drop down containing users on the system and displays it
    user_combobox = Combobox(
        user_select_frame,
        values=helpers.get_windows_users(),
        font=theme.font_label,
        state="readonly"
    )
    user_combobox.pack(side="left")    

    # Creates a label explaining the folders fpimd
    folders_label = tk.Label(
        body, 
        text="Selected Folders\nare included in copy", 
        font=theme.font_label
    )
    folders_label.grid(column=0,row=1)

    # Creates a label explaining the extensions found
    extensions_label = tk.Label(
        body, 
        text="Selected Extensions\nare included in copy", 
        font=theme.font_label
    )
    extensions_label.grid(column=2,row=1)

    # Creates Folder Checkboxes
    folder_checkbox_frame = tk.Frame(
    body,
    bg=theme.light_gray_background,
    width=420,
    height=400
    )
    folder_checkbox_frame.grid(
        column=0,
        row=2,
        padx=20,
        pady=10,
        sticky="nw"
    )
    folder_checkbox_frame.grid_propagate(False)

    # Creates Extension Checkboxes
    extension_checkbox_frame = tk.Frame(
        body,
        bg=theme.light_gray_background,
        width=300,
        height=400
    )
    extension_checkbox_frame.grid(
        column=2,
        row=2,
        padx=20,
        pady=10,
        sticky="nw"
    )
    extension_checkbox_frame.grid_propagate(False)

    # Creates dictionaries for the two checkbox sets
    folder_vars = {}
    extension_vars = {}

    # Middle section that holds the vertical line and scan button
    middle_frame = tk.Frame(
    body,
    bg=theme.light_gray_background,
    width=250,
    height=400
    )
    middle_frame.grid(
        column=1,
        row=2,
        pady=10,
        sticky="n"
    )
    middle_frame.grid_propagate(False)
    divider_line = tk.Frame(
        middle_frame,
        bg=theme.dark_blue,
        width=2
    )
    divider_line.place(
        relx=0.5,
        rely=0,
        relheight=1,
        anchor="n"
    )

    # Button to scan extensions
    # Goes on top of verticle line
    scan_extensions_button = tk.Button(
        middle_frame,
        text="Scan Selected Folders\nFor Extensions",
        font=theme.font_button,
        command=lambda: create_extension_popup(
            body,
            user_combobox.get(),
            folder_vars,
            extension_vars
        )
    )
    scan_extensions_button.place(
        relx=0.5,
        rely=0.5,
        anchor="center"
    )

    # Bind dropdown selection event
    user_combobox.bind(
        "<<ComboboxSelected>>", 
        lambda event: create_user_folder_checkboxes(event, folder_checkbox_frame, folder_vars)
    )

    # Adds the default extensions to the screen
    default_extension_checkboxes(extension_checkbox_frame, extension_vars)

#######################################
### Create Folders for User Folders ###
#######################################

def create_user_folder_checkboxes(event, folder_frame, folder_vars):
    # Wipe the frame clean of old user widgets
    helpers.clear_frame(folder_frame)
    folder_vars.clear()
    
    selected_user = event.widget.get()
    folders = helpers.get_user_folders(selected_user)
    
    # CRITICAL FIX: Column weights must be assigned AFTER clear_frame runs
    # Otherwise, clear_frame resets cell structures, collapsing widgets to 0 width
    folder_frame.columnconfigure(0, weight=0)
    folder_frame.columnconfigure(1, weight=0)
    folder_frame.columnconfigure(2, weight=0)

    count = 0
    for item in folders:
        var = tk.BooleanVar(value=True)
        folder_vars[item] = var
        
        # Build checkbutton instances referencing the updated parent frame
        checkbox = tk.Checkbutton(
            folder_frame, 
            text=item, 
            variable=var,
            bg=theme.light_gray_background,
            fg=theme.dark_blue,
        )
        checkbox.grid(column=count%3, row=count//3)
        count += 1



################################################################
### Creates Checkboxes for Commonly Excluded File Extensions ###
################################################################

def default_extension_checkboxes(extension_frame, extension_vars):
    helpers.clear_frame(extension_frame)
    extension_vars.clear()

    common_extensions = [".exe", ".msi", ".bat", ".zip"] #Commonly excluded file extensions

    count = 0
    for ext in common_extensions:
        var = tk.BooleanVar(value=True)
        extension_vars[ext] = var
        checkbox = tk.Checkbutton(
            extension_frame,
            text=ext,
            variable=var,
            bg=theme.light_gray_background,
            fg=theme.dark_blue
        )
        checkbox.grid(column=0, row=count, sticky="w")
        count += 1



#####################################################
### Creates a Popup for All Extension Types Found ###
#####################################################

def create_extension_popup(body, selected_user, folder_vars, extension_vars):
# Creates a new popup window
    popup = tk.Toplevel(body)

    extensions = helpers.get_unique_extensions(
    selected_user,
    folder_vars
)

    # Configures the popup window
    popup.title("All File Types")
    popup.geometry("1500x500")
    popup.configure(bg=theme.light_gray_background)
    popup.iconbitmap(theme.app_icon)

    # Keeps the popup associated with the main application
    popup.transient(body.winfo_toplevel())

    # Prevents interaction with the main window until the popup is closed
    popup.grab_set()

    # Adds a heading to the popup
    popup_title = tk.Label(
        popup,
        text="Detected File Types",
        font=theme.font_header,
        bg=theme.light_gray_background,
        fg=theme.dark_blue
    )
    popup_title.pack(pady=20)

        # Frame that holds the canvas and scrollbar
    scroll_container = tk.Frame(
        popup,
        bg=theme.light_gray_background
    )
    scroll_container.pack(
        fill="both",
        expand=True,
        padx=20,
        pady=(0, 20)
    )

    # Canvas used to make the checkbox area scrollable
    canvas = tk.Canvas(
        scroll_container,
        bg=theme.light_gray_background,
        highlightthickness=0
    )
    canvas.pack(
        side="left",
        fill="both",
        expand=True
    )

    # Vertical scrollbar connected to the canvas
    scrollbar = tk.Scrollbar(
        scroll_container,
        orient="vertical",
        command=canvas.yview
    )
    scrollbar.pack(
        side="right",
        fill="y"
    )

    canvas.configure(
        yscrollcommand=scrollbar.set
    )

    # Frame inside the canvas that holds the checkboxes
    checkbox_frame = tk.Frame(
        canvas,
        bg=theme.light_gray_background
    )

    checkbox_window = canvas.create_window(
        (0, 0),
        window=checkbox_frame,
        anchor="nw"
    )

    # Updates the scrollable area whenever checkboxes are added
    def update_scroll_region(event):
        canvas.configure(
            scrollregion=canvas.bbox("all")
        )

    checkbox_frame.bind(
        "<Configure>",
        update_scroll_region
    )

    # Scrolls the canvas with the mouse wheel
    def on_mousewheel(event):
        canvas.yview_scroll(
            int(-1 * (event.delta / 120)),
            "units"
        )


    # Enables mouse-wheel scrolling when the cursor enters the canvas
    def bind_mousewheel(event):
        canvas.bind_all(
            "<MouseWheel>",
            on_mousewheel
        )


    # Disables mouse-wheel scrolling when the cursor leaves the canvas
    def unbind_mousewheel(event):
        canvas.unbind_all("<MouseWheel>")

    canvas.bind("<Enter>", bind_mousewheel)
    canvas.bind("<Leave>", unbind_mousewheel)

    # Makes the inner frame follow the canvas width
    def resize_checkbox_frame(event):
        canvas.itemconfigure(
            checkbox_window,
            width=event.width
        )

    canvas.bind(
        "<Configure>",
        resize_checkbox_frame
    )

    # Temporary test checkboxes
    for index, ext in enumerate(extensions):
    # Reuse existing variables for .exe, .msi, .bat, and .zip
        if ext not in extension_vars:
            extension_vars[ext] = tk.BooleanVar(value=True)

        extension_checkbox = tk.Checkbutton(
            checkbox_frame,
            text=ext,
            variable=extension_vars[ext],
            bg=theme.light_gray_background,
            fg=theme.dark_blue
        )

        extension_checkbox.grid(
            row=index // 3,
            column=index % 3,
            sticky="w",
            padx=10,
            pady=5
        )

    def close_popup():
        canvas.unbind_all("<MouseWheel>")
        popup.destroy()

    # Closes the popup
    close_button = tk.Button(
        popup,
        text="Close",
        font=theme.font_button,
        command=close_popup
    )
    close_button.pack(side="bottom", pady=20)

    