'''
Helper methods for M+S IT Acquisition Toolbox
'''
#Imports
import os, sys #Used for managing system
from pathlib import Path #Used for finding path to users
import tkinter as tk #Used for the GUI



##############################################
### Makes onefile mode work in pyinstaller ###
##############################################

def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)



########################
### Resizes an image ###
########################

def resize_image(image, new_width=None, new_height=None):
    """
    If neither dimensions are given, original image will be returned
    If both width AND height are given, image will be stretched to fit the new dimensions
    If only width OR height is given, image will be resized with the same ratio
    """
    original_width, original_height = image.size

    #Just image is given
    if not new_width and not new_height:
        return image #Skips the rest of the function by returning the original image
    
    #Just width is given
    if new_width and not new_height:
        ratio = new_width / original_width
        new_height = int(original_height * ratio)

    #Just height is given
    elif new_height and not new_width:
        ratio = new_height / original_height
        new_width = int(original_width * ratio)

    #Returns the resized image with the new ratios
    return image.resize((new_width, new_height))



######################
### Clears a frame ###
######################

def clear_frame(frame):
    #Loops through every widget on a frame and removes it
    for widget in frame.winfo_children():
        widget.destroy()



############################################################
### Creates a list of user profile folders from C:/Users ###
############################################################

def get_windows_users():
    # Stores the path where Windows user profiles are usually located
    users_path = Path("C:/Users")

    # Folders/files that should not appear in the user dropdown
    ignored_users = {
        "Public",
        "Default",
        "Default User",
        "All Users",
        "desktop.ini"
    }

    # Empty list that will store valid user profile names
    users = []

    # Loops through everything inside C:/Users
    for item in users_path.iterdir():

        # Only adds the item if it is a folder and not in the ignored list
        if item.is_dir() and item.name not in ignored_users:
            users.append(item.name)

    # Sends the final list of user folders back to wherever the function was called
    return users



###############################################
### Returns a List of Folders Within a User ###
###############################################

def get_user_folders(username):
    user_path = Path("C:/Users") / username
    try:
        return [
            folder.name
            for folder in user_path.iterdir()
            if folder.is_dir()
        ]
    except:
        return []