"""
Creates shared controls used by the Robocopy interface.
"""

###############
### Imports ###
###############

import tkinter as tk  # Handles icon-related Tcl errors

import customtkinter as ctk  # Creates shared CustomTkinter controls

from utils import theme  # Provides shared fonts and colors


########################################
### Creates a Link-Style UI Control  ###
########################################

def create_link_control(parent, text, command):
    """Creates clickable text styled like a link."""
    # Creates an underlined CustomTkinter font without changing normal labels
    link_font = ctk.CTkFont(
        family=theme.font_main[0],
        size=theme.font_main[1],
        underline=True,
    )

    # Creates a label that visually behaves like a hyperlink
    link = ctk.CTkLabel(
        parent,
        text=text,
        font=link_font,
        text_color=theme.primary_blue,
        fg_color="transparent",
        cursor="hand2",
    )

    # Calls the supplied function when the link is clicked
    link.bind("<Button-1>", lambda event: command())

    # Returns the label so the calling section can place it
    return link



############################################
### Applies the Application Window Icon  ###
############################################

def apply_window_icon(window):
    """Applies the application icon after CustomTkinter finishes setup."""
    # Sets the icon immediately when possible
    try:
        window.iconbitmap(theme.app_icon)
    except tk.TclError:
        pass

    # CustomTkinter can replace a Toplevel icon shortly after creation,
    # so the application icon is applied again after initialization
    def apply_icon_again():
        """Reapplies the icon after CustomTkinter initializes the window."""
        try:
            window.iconbitmap(theme.app_icon)
        except tk.TclError:
            pass

    window.after(250, apply_icon_again)


#########################################
### Changes an Entire Checkbox Group  ###
#########################################

def set_checkbox_values(variable_dictionary, selected):
    """Sets every BooleanVar in a checkbox dictionary."""
    # Updates each checkbox variable to the requested selected state
    for variable in variable_dictionary.values():
        variable.set(selected)
