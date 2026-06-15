'''
Creates App Base Screen
'''

###############
### Imports ###
###############

import tkinter as tk  # Creates the application's main content frame
from utils import theme  # Gets the application theme items


###########################################################
### Creates the Base Screen Used By The Rest of the App ###
###########################################################

def create_screen_base(root):
    # Creates the frame where each application page will be displayed
    body = tk.Frame(root, bg=theme.light_gray_background, pady=10)

    # Allows the body row and main column to expand with the window
    root.grid_rowconfigure(2, weight=1)
    root.grid_columnconfigure(0, weight=1)

    # Places the body below the header and stretches it to fill available space
    body.grid(row=2, column=0, sticky="nsew")

    # Returns the frame so other files can place page content inside it
    return body
