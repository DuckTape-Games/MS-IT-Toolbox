"""
Creates App Home Page
"""

###############
### Imports ###
###############

import os  # Opens the Windows Users directory in File Explorer
from pathlib import Path  # Builds the Windows Users directory path
from tkinter import messagebox  # Reports directory-opening errors

import customtkinter as ctk  # Creates CustomTkinter home-page controls

from ui import defender_ui, header, robocopy_ui  # Provides navigation and app pages
from ui.robocopy_components import create_link_control  # Creates the directory link
from utils import helpers, theme  # Provides frame helpers and shared theme values


#################################
### Opens the Users Directory ###
#################################

def open_users_directory():
    """Opens C:/Users in File Explorer."""
    # Builds the Windows directory that contains every user profile
    users_directory = Path("C:/Users")

    # Stops with a clear message if the directory cannot be found
    if not users_directory.exists() or not users_directory.is_dir():
        messagebox.showerror(
            "Users Directory Not Found",
            f"The Users directory could not be found:\n{users_directory}",
        )
        return

    try:
        # Uses the standard Windows folder-opening behavior
        os.startfile(users_directory)
    except OSError as error:
        # Reports Windows or permission errors instead of crashing the home page
        messagebox.showerror(
            "Unable to Open Users Directory",
            f"The Users directory could not be opened:\n"
            f"{users_directory}\n\n{error}",
        )


#############################
### Creates the Home Menu ###
#############################

def create_home(body, head, back_button=None):
    """Builds the home page and its navigation controls."""
    # Removes the widgets from the previously displayed page
    helpers.clear_frame(body)

    # Removes the back button when returning to the home page
    if back_button is not None:
        back_button.destroy()

    # Holds the main application workflow buttons in one centered row
    home_button_frame = ctk.CTkFrame(
        body,
        fg_color="transparent",
        corner_radius=0,
    )
    home_button_frame.pack(pady=(50, 10))

    # Creates the button that opens the M+S File Copy workflow
    robocopy_button = ctk.CTkButton(
        home_button_frame,
        text="M+S File Copy",
        font=theme.font_button,
        text_color=theme.dark_blue,
        fg_color=theme.white,
        hover_color="#E7ECF2",
        border_color=theme.dark_blue,
        border_width=1,
        corner_radius=6,
        height=80,
        width=160,
        command=lambda: go_to_robocopy(body, head),
    )
    robocopy_button.pack(side="left", padx=10)

    # Creates the button that opens the future Microsoft Defender workflow
    defender_button = ctk.CTkButton(
        home_button_frame,
        text="Microsoft Defender",
        font=theme.font_button,
        text_color=theme.dark_blue,
        fg_color=theme.white,
        hover_color="#E7ECF2",
        border_color=theme.dark_blue,
        border_width=1,
        corner_radius=6,
        height=80,
        width=160,
        command=lambda: go_to_defender(body, head),
    )
    defender_button.pack(side="left", padx=10)

    # Keeps the Users directory link directly below the workflow buttons
    open_directory_link = create_link_control(
        body,
        "Open Users Directory",
        open_users_directory,
    )
    open_directory_link.pack(pady=(0, 50))


###########################################
### Sends the User to the Robocopy Page ###
###########################################

def go_to_robocopy(body, head):
    """Opens the Robocopy page and adds home navigation."""
    # Replaces the home page with the Robocopy interface
    robocopy_ui.create_robocopy_page(body)

    # Adds a back arrow to the header after leaving the home page
    header.add_back_button(head, body, create_home)


##########################################
### Sends the User to Defender Page    ###
##########################################

def go_to_defender(body, head):
    """Opens the Microsoft Defender page and adds home navigation."""
    # Replaces the home page with the future Defender interface
    defender_ui.create_defender_page(body)

    # Adds a back arrow to the header after leaving the home page
    header.add_back_button(head, body, create_home)
