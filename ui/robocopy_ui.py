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
    
    # FIX: Initialize the checkbox container on the main layout first
    checkbox_frame = tk.Frame(body, bg=theme.light_gray_background)
    checkbox_frame.grid(column=0, row=1, columnspan=3, padx=20, pady=10, sticky="nsew")
    
    folder_vars = {}
    
    # Bind dropdown selection event
    user_combobox.bind(
        "<<ComboboxSelected>>", 
        lambda event: create_user_folder_checkboxes(event, checkbox_frame, folder_vars)
    )

#######################################
### Create Folders for User Folders ###
#######################################
def create_user_folder_checkboxes(event, frame, folder_vars):
    # Wipe the frame clean of old user widgets
    helpers.clear_frame(frame)
    folder_vars.clear()
    
    selected_user = event.widget.get()
    folders = helpers.get_user_folders(selected_user)
    
    # CRITICAL FIX: Column weights must be assigned AFTER clear_frame runs
    # Otherwise, clear_frame resets cell structures, collapsing widgets to 0 width
    frame.columnconfigure(0, weight=0)
    frame.columnconfigure(1, weight=0)
    frame.columnconfigure(2, weight=0)
    
    count = 0
    for item in folders:
        var = tk.BooleanVar(value=False)
        folder_vars[item] = var
        
        # Build checkbutton instances referencing the updated parent frame
        checkbox = tk.Checkbutton(
            frame, 
            text=item, 
            variable=var,
            bg=theme.light_gray_background,
            fg=theme.dark_blue
        )
        # sticky="w" enforces alignment; padx/pady ensures cells have structural volume
        checkbox.grid(column=count%3, row=count//3)
        count += 1
