"""
M+S IT Acquisition Toolbox application entry point
"""

###############
### Imports ###
###############

import customtkinter as ctk  # Creates the CustomTkinter application window

from ui import base_screen, header, home  # Builds the shared interface sections
from ui.robocopy_components import apply_window_icon  # Applies the app icon reliably
from utils import theme  # Provides shared colors, fonts, and resource paths


##############################
### Starts the Application ###
##############################

def main():
    """Creates the application window and starts the interface."""
    # Uses the light appearance so the converted interface matches the prior layout
    ctk.set_appearance_mode("light")
    ctk.set_default_color_theme("blue")

    # Creates the root window used by every page in the application
    root = ctk.CTk(fg_color=theme.light_gray_background)

    # Sets the window title, icon, and starting size
    root.title("M+S IT Acquisition Toolbox")
    apply_window_icon(root)
    root.geometry("1500x700")

    # Creates the shared header and page body before loading the home page
    head = header.create_header(root)
    body = base_screen.create_screen_base(root)
    home.create_home(body, head)

    # Keeps the application open and listening for user actions
    root.mainloop()


##############################################
### Prevents Startup When File is Imported ###
##############################################

if __name__ == "__main__":
    main()
