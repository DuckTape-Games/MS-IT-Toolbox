'''
Creates App Header
'''
###############
### Imports ###
###############

import tkinter as tk #UI
from utils import theme, helpers #Theme gets the application theme items and helpers gets the helper methods that the project uses
from PIL import Image, ImageTk #Used for resizing images



##########################
### Creates the header ###
##########################

def create_header(header):
    head = tk.Frame(header, bg=theme.white, pady=10, height=95)

    head.grid(row=0, column=0, sticky="ew")
    head.grid_propagate(False)

    head.grid_columnconfigure(0, weight=1)
    head.grid_columnconfigure(1, weight=0)
    head.grid_columnconfigure(2, weight=1)

    add_image(head, theme.long_logo, 75, bgcolor=theme.white)
    bottom_border = tk.Frame(header,bg=theme.dark_blue, padx=600, pady=5)
    bottom_border.grid(row=1, column=0, sticky="ew")
    return head



#####################################
### Adds the logo onto the screen ###
#####################################

def add_image(header, image, height=None, xcor=None, ycor=None, bgcolor=theme.white):
    #Load image
    logo = Image.open(image).convert("RGBA")
    if height: #Checks if a new size was given before resizing
        logo = helpers.resize_image(logo, new_height=height)
    logo_image = ImageTk.PhotoImage(logo)
    #Display image
    logo_label = tk.Label(
        header,
        image=logo_image,
        bg=bgcolor
    )
    #Prevent image from disappearing
    logo_label.image = logo_image
    #Place image
    if xcor == None or ycor == None:
        logo_label.place(
            relx=0.5,
            rely=0.5,
            anchor="center"
        )
    else:
        logo_label.place(x=xcor, y=ycor)



#########################################################################
### Creates a back button for when the user is not on the home screen ###
#########################################################################

def add_back_button(header,body, create_home):
    # Loads the transparent PNG as an actual Tkinter image
    back_arrow = Image.open(theme.back_arrow).convert("RGBA")
    back_arrow = helpers.resize_image(back_arrow, new_height=40)
    back_arrow_image = ImageTk.PhotoImage(back_arrow)

    # Creates the back arrow as a clickable button
    back_button = tk.Button(
        header,
        image=back_arrow_image,
        command=lambda: create_home(body, header, back_button),
        bg=theme.white,
        activebackground=theme.white,
        borderwidth=0,
        highlightthickness=0,
        relief="flat",
        cursor="hand2"
    )

    # Keeps the image from disappearing
    back_button.image = back_arrow_image

    # Places the button on the left side of the header
    back_button.grid(row=0, column=0, padx=15, sticky="w")
    