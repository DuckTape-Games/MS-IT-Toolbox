''' Creates App Home Page '''
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
    body.columnconfigure(0, weight=1)
    body.columnconfigure(1, weight=1)
    body.columnconfigure(2, weight=1)
    body.grid_propagate(False) 
    
    # Creates label for user drop down
    select_user_label = tk.Label(
        body, 
        text="Select User", 
        font=theme.font_label, 
        background=theme.light_gray_background, 
        fg=theme.dark_blue
    )
    select_user_label.grid(column=0, row=0, pady=(40, 20), sticky="e")
    
    # Creates a drop down containing users on the system and displays it
    user_combobox = Combobox(
        body, 
        values=helpers.get_windows_users(), 
        font=theme.font_label, 
        state="readonly"
    )
    user_combobox.grid(column=1, row=0, pady=(40, 20), sticky="w", padx=10)
    

    folders_label = tk.Label(
        body, 
        text="Selected Folders\nare included in copy", 
        font=theme.font_label
    )
    folders_label.grid(column=0,row=1)

    extensions_label = tk.Label(
        body, 
        text="Selected Folders\nare included in copy", 
        font=theme.font_label
    )
    extensions_label.grid(column=1,row=1)


    folder_checkbox_frame = tk.Frame(body, bg=theme.light_gray_background)
    folder_checkbox_frame.grid(column=0, row=2, columnspan=3, padx=20, pady=10, sticky="nsw")

    extension_checkbox_frame = tk.Frame(body, bg=theme.light_gray_background)
    extension_checkbox_frame.grid(column=2, row=2, columnspan=3, padx=20, pady=10, sticky="nse")
    
    folder_vars = {}
    extension_vars = {}
    
    # Bind dropdown selection event
    user_combobox.bind(
        "<<ComboboxSelected>>", 
        lambda event: create_user_folder_checkboxes(event, folder_checkbox_frame, folder_vars, extension_checkbox_frame, extension_vars)
    )



#######################################
### Create Folders for User Folders ###
#######################################

def create_user_folder_checkboxes(event, folder_frame, folder_vars, extension_frame, extension_vars):
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
        var = tk.BooleanVar(value=False)
        folder_vars[item] = var
        
        # Build checkbutton instances referencing the updated parent frame
        checkbox = tk.Checkbutton(
            folder_frame, 
            text=item, 
            variable=var,
            bg=theme.light_gray_background,
            fg=theme.dark_blue,
            command=lambda: update_extension_checkboxes(extension_frame, folder_vars, selected_user, extension_vars)
        )
        checkbox.grid(column=count%3, row=count//3)
        count += 1


def update_extension_checkboxes(extension_frame, folder_vars, selected_user, extension_vars):
    helpers.clear_frame(extension_frame)
    extensions = helpers.get_unique_extensions(selected_user, folder_vars)
    
    extension_frame.columnconfigure(0, weight=0)
    extension_frame.columnconfigure(1, weight=0)
    extension_frame.columnconfigure(2, weight=0)
    extension_frame.columnconfigure(3, weight=0)
    extension_frame.columnconfigure(4, weight=0)
    extension_frame.columnconfigure(5, weight=0)
    extension_frame.columnconfigure(6, weight=0)

    count = 0

    for ext in extensions:
        var = tk.BooleanVar(value=False)
        extension_vars[ext] = var

        checkbox = tk.Checkbutton(
            extension_frame,
            text=ext,
            variable=var,
            bg=theme.light_gray_background,
            fg=theme.dark_blue
        )
        checkbox.grid(column=count%7, row=count//7, sticky="nw")
        count += 1
