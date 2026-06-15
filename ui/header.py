'''
Creates App Header
'''

###############
### Imports ###
###############

import tkinter as tk  # Creates header frames, labels, and buttons
from PIL import Image, ImageTk  # Loads and converts images for Tkinter

from utils import helpers, theme  # Provides image helpers and shared theme values


##########################
### Creates the Header ###
##########################

def create_header(header):
    # Creates a fixed-height header so navigation controls do not shift the logo
    head = tk.Frame(header, bg=theme.white, pady=10, height=95)
    head.grid(row=0, column=0, sticky="ew")
    head.grid_propagate(False)

    # Uses equal outside columns to keep the logo centered when a back button appears
    head.grid_columnconfigure(0, weight=1)
    head.grid_columnconfigure(1, weight=0)
    head.grid_columnconfigure(2, weight=1)

    # Adds the company logo to the center of the header
    add_image(head, theme.long_logo, 75, bgcolor=theme.white)

    # Creates the blue divider line below the header
    bottom_border = tk.Frame(header, bg=theme.dark_blue, pady=5)
    bottom_border.grid(row=1, column=0, sticky="ew")

    # Returns the header frame so other pages can add navigation controls
    return head


#####################################
### Adds the Logo Onto the Screen ###
#####################################

def add_image(header, image, height=None, bgcolor=theme.white):
    """Adds a centered image to the header."""
    # Loads the image with transparency support
    logo = Image.open(image).convert("RGBA")

    # Resizes the image when a target height is supplied
    if height:
        logo = helpers.resize_image(logo, new_height=height)

    # Converts the Pillow image into a Tkinter-compatible image
    logo_image = ImageTk.PhotoImage(logo)

    # Displays the logo over the chosen header background color
    logo_label = tk.Label(header, image=logo_image, bg=bgcolor)

    # Keeps a reference so Python does not remove the image from memory
    logo_label.image = logo_image

    # Places the logo in the exact center of the header
    logo_label.place(relx=0.5, rely=0.5, anchor="center")


#########################################################################
### Creates a Back Button When the User is Not on the Home Screen ###
#########################################################################

def add_back_button(header, body, create_home):
    # Loads and resizes the transparent back-arrow image
    back_arrow = Image.open(theme.back_arrow).convert("RGBA")
    back_arrow = helpers.resize_image(back_arrow, new_height=40)
    back_arrow_image = ImageTk.PhotoImage(back_arrow)

    # Creates the back arrow as a clickable image button
    back_button = tk.Button(
        header,
        image=back_arrow_image,
        command=lambda: create_home(body, header, back_button),
        bg=theme.white,
        activebackground=theme.white,
        borderwidth=0,
        highlightthickness=0,
        relief="flat",
        cursor="hand2",
    )

    # Keeps the image from disappearing after this function finishes
    back_button.image = back_arrow_image

    # Places the button on the left side of the header
    back_button.grid(row=0, column=0, padx=15, sticky="w")
