'''
Creates App Home Page
'''

###############
### Imports ###
###############

import tkinter as tk  # Creates the home-page button

from ui import header, robocopy_ui  # Provides navigation and the Robocopy page
from utils import helpers, theme  # Provides frame helpers and shared theme values


#############################
### Creates the Home Menu ###
#############################

def create_home(body, head, back_button=None):
    # Removes the widgets from the previously displayed page
    helpers.clear_frame(body)

    # Removes the back button when returning to the home page
    if back_button is not None:
        back_button.destroy()

    # Creates the button that opens the Robocopy workflow
    robocopy_button = tk.Button(
        body,
        text="Robocopy",
        relief="raised",
        font=theme.font_button,
        fg=theme.dark_blue,
        bg=theme.white,
        height=4,
        width=10,
        command=lambda: go_to_robocopy(body, head),
    )

    # Places the Robocopy button near the top of the home page
    robocopy_button.pack(pady=50)


###########################################
### Sends the User to the Robocopy Page ###
###########################################

def go_to_robocopy(body, head):
    # Replaces the home page with the Robocopy interface
    robocopy_ui.create_robocopy_page(body)

    # Adds a back arrow to the header after leaving the home page
    header.add_back_button(head, body, create_home)
