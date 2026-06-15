'''
Creates and reads the folder-selection controls.
'''

###############
### Imports ###
###############

import tkinter as tk  # Creates folder-selection checkboxes

from utils import helpers, theme  # Provides folder discovery and visual settings


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
