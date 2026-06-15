'''
M+S IT Acquisition Toolbox application entry point
'''

###############
### Imports ###
###############

import tkinter as tk  # Creates the main application window

from ui import base_screen, header, home  # Builds the shared interface sections
from utils import theme  # Provides shared colors, fonts, and resource paths


###############################
### Starts the Application  ###
###############################

def main():
    # Creates the root window used by every page in the application
    root = tk.Tk()

    # Sets the window title, icon, and starting size
    root.title("M+S IT Acquisition Toolbox")
    root.iconbitmap(theme.app_icon)
    root.geometry("1500x700")

    # Creates the shared header and page body before loading the home page
    head = header.create_header(root)
    body = base_screen.create_screen_base(root)
    home.create_home(body, head)

    # Keeps the application open and listening for user actions
    root.mainloop()


#############################################
### Prevents Startup When File is Imported ###
#############################################

if __name__ == "__main__":
    main()
