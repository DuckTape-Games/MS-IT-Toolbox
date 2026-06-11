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

    folders_label = tk.Label(
        body, 
        text="Selected Folders\nare included in copy", 
        font=theme.font_label
    )
    folders_label.grid(column=0,row=1)

    extensions_label = tk.Label(
        body, 
        text="Selected Extensions\nare included in copy", 
        font=theme.font_label
    )
    extensions_label.grid(column=2,row=1)


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

    scan_extensions_button = tk.Button(
        middle_frame,
        text="Scan Selected Folders\nFor Extensions",
        font=theme.font_button
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

    default_extension_checkboxes(extension_checkbox_frame, folder_vars, user_combobox.get(), extension_vars)

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


def default_extension_checkboxes(extension_frame, folder_vars, selected_user, extension_vars, ):
    helpers.clear_frame(extension_frame)


    #extensions = helpers.get_unique_extensions(selected_user, folder_vars)
    extension_vars.clear()

    common_extensions = [".exe", ".msi", ".bat", ".zip"]

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
