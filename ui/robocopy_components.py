'''
Creates shared controls used by the Robocopy interface.
'''

###############
### Imports ###
###############

import tkinter as tk  # Creates shared Robocopy interface widgets
from tkinter import font as tkfont  # Creates underlined link-style fonts

from utils import theme  # Provides shared fonts and colors


########################################
### Creates a Link-Style UI Control  ###
########################################

def create_link_control(parent, text, command):
    """Creates clickable text styled like a link."""
    # Copies the shared font so underlining does not change every normal label
    link_font = tkfont.Font(font=theme.font_main)
    link_font.configure(underline=True)

    # Creates a label that visually behaves like a hyperlink
    link = tk.Label(
        parent,
        text=text,
        font=link_font,
        bg=theme.light_gray_background,
        fg=theme.primary_blue,
        cursor="hand2",
    )

    # Calls the supplied function when the link is clicked
    link.bind("<Button-1>", lambda event: command())

    # Returns the label so the calling section can place it
    return link


#########################################
### Changes an Entire Checkbox Group  ###
#########################################

def set_checkbox_values(variable_dictionary, selected):
    """Sets every BooleanVar in a checkbox dictionary."""
    # Updates each checkbox variable to the requested selected state
    for variable in variable_dictionary.values():
        variable.set(selected)
