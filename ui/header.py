'''
Creates App Header
'''
#Imports
import tkinter as tk #UI
from utils import theme, helpers #Theme gets the application theme items and helpers gets the helper methods that the project uses
from PIL import Image, ImageTk #Used for resizing images

#Creates the header
def create_header(root):
    header = tk.Frame(root, bg=theme.white, pady=10)
    add_image(header, theme.long_logo, 75, bgcolor=theme.white)
    header.pack(fill="x")
    bottom_border = tk.Frame(root,bg=theme.dark_blue, padx=600, pady=5)
    bottom_border.pack(fill="x")


#Adds the logo onto the screen
def add_image(root, image, height=None, xcor=None, ycor=None, bgcolor=theme.white):
    #Load image
    logo = Image.open(image)
    if height: #Checks if a new size was given before resizing
        logo = helpers.resize_image(logo, new_height=height)
    logo_image = ImageTk.PhotoImage(logo)
    #Display image
    logo_label = tk.Label(
        root,
        image=logo_image,
        bg=bgcolor
    )
    #Prevent image from disappearing
    logo_label.image = logo_image
    #Place image
    if xcor == None or ycor == None:
        logo_label.pack(pady=20)
    else:
        logo_label.place(x=xcor, y=ycor)