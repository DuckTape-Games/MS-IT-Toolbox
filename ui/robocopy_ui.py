'''
Creates App Home Page
'''
#Imports
import tkinter as tk #UI Elements
from tkinter.ttk import Combobox #Used for the user list
from utils import theme, helpers #Gets the application theme items and helper methods

#Creates the home menu
def create_robocopy_page(body, head):
    helpers.clear_frame(body)
    user_combobox = Combobox(
        body,
        values=helpers.get_windows_users(),
        state="readonly"
    )
    user_combobox.pack()