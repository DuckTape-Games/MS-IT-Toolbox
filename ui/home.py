'''
Creates App Home Page
'''
###############
### Imports ###
###############

import tkinter as tk #UI
from utils import theme, helpers #Gets the application theme items and helper methods
from ui import robocopy_ui #Allows for redirection to the robocopy page
from ui import header #Gives access to the add_back_button command



#############################
### Creates the home menu ###
#############################
def create_home(body, head, back_button=None):
    helpers.clear_frame(body)
    if back_button != None:
        back_button.destroy()
    robocopy_button = tk.Button(
        body, 
        text="Robocopy", 
        relief="raised", 
        font=theme.button_label, 
        fg=theme.dark_blue, 
        bg=theme.white, 
        height=4, 
        width=10,
        command=lambda: go_to_robocopy(body, head) 
    )
    robocopy_button.pack(pady=50)



###########################################
### Sends the user to the robocopy page ###
###########################################

def go_to_robocopy(body, head):
    robocopy_ui.create_robocopy_page(body)
    header.add_back_button(head,body, create_home)