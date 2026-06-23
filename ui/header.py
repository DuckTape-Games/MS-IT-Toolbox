"""
Creates App Header
"""

###############
### Imports ###
###############

import customtkinter as ctk  # Creates CustomTkinter header controls
from PIL import Image  # Loads images for CustomTkinter

from utils import helpers, theme  # Provides image helpers and shared theme values


##########################
### Creates the Header ###
##########################

def create_header(header):
    """Creates the fixed application header and divider."""
    # Creates a fixed-height header so navigation controls do not shift the logo
    head = ctk.CTkFrame(
        header,
        fg_color=theme.white,
        corner_radius=0,
        height=95,
    )
    head.grid(row=0, column=0, sticky="ew")
    head.grid_propagate(False)

    # Uses equal outside columns to keep the logo centered when a back button appears
    head.grid_columnconfigure(0, weight=1)
    head.grid_columnconfigure(1, weight=0)
    head.grid_columnconfigure(2, weight=1)

    # Adds the company logo to the center of the header
    add_image(head, theme.long_logo, 75)

    # Creates the blue divider line below the header
    bottom_border = ctk.CTkFrame(
        header,
        fg_color=theme.dark_blue,
        corner_radius=0,
        height=10,
    )
    bottom_border.grid(row=1, column=0, sticky="ew")
    bottom_border.grid_propagate(False)

    # Returns the header frame so other pages can add navigation controls
    return head


#####################################
### Adds the Logo Onto the Screen ###
#####################################

def add_image(header, image, height=None):
    """Adds a centered image to the header."""
    # Loads the image with transparency support
    logo = Image.open(image).convert("RGBA")

    # Resizes the image when a target height is supplied
    if height:
        logo = helpers.resize_image(logo, new_height=height)

    # Converts the Pillow image into a CustomTkinter-compatible image
    logo_image = ctk.CTkImage(
        light_image=logo,
        dark_image=logo,
        size=logo.size,
    )

    # Displays the logo over the chosen header background color
    logo_label = ctk.CTkLabel(
        header,
        image=logo_image,
        text="",
        fg_color="transparent",
    )

    # Keeps a reference so Python does not remove the image from memory
    logo_label.image = logo_image

    # Places the logo in the exact center of the header
    logo_label.place(relx=0.5, rely=0.5, anchor="center")


#####################################################################
### Creates a Back Button When the User is Not on the Home Screen ###
#####################################################################

def add_back_button(header, body, create_home):
    """Adds the header button used to return to the home page."""
    # Loads and resizes the transparent back-arrow image
    back_arrow = Image.open(theme.back_arrow).convert("RGBA")
    back_arrow = helpers.resize_image(back_arrow, new_height=40)
    back_arrow_image = ctk.CTkImage(
        light_image=back_arrow,
        dark_image=back_arrow,
        size=back_arrow.size,
    )

    # Creates the back arrow as a clickable image button
    back_button = ctk.CTkButton(
        header,
        text="",
        image=back_arrow_image,
        command=lambda: create_home(body, header, back_button),
        width=48,
        height=48,
        fg_color="transparent",
        hover_color=theme.light_gray_background,
        border_width=0,
        corner_radius=0,
        cursor="hand2",
    )

    # Keeps the image from disappearing after this function finishes
    back_button.image = back_arrow_image

    # Places the button on the left side of the header
    back_button.grid(row=0, column=0, padx=15, sticky="w")
