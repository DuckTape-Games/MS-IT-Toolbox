'''
Title: M+S IT Acquisition Toolbox
Purpose: Improve speed for Marshall+Sterling IT Department during acquisitions
Start Date: 5/8/2026
'''

#############
### SETUP ###
#############

'''
ALL USED LIBRARIES:

import tkinter as tk            #Used for GUI
import subprocess as sp         #Used for running command prompt
import os, sys                  #Used for managing system
from PIL import Image, ImageTk  #Used for resizing images
from pathlib import Path        #Used for finding path to users
from tkinter import filedialog  #Used for 
'''

#Imports
import tkinter as tk #Used for GUI
from utils import theme #Marshall+Sterling Theme
from ui import header, base_screen as base, home #Creates the application header, the base screen, and the home screen


#Screen Setup
root = tk.Tk()
root.title("M+S IT Acquisition Toolbox")
root.iconbitmap(theme.app_icon)
root.geometry("1200x700")

#Adds widgets and customises the application
head = header.create_header(root) #Adds the header to the GUI
body = base.create_screen_base(root) #Creates the base of the main screen to be used accross menus
home.create_home(body, head) #Adds the home screen to the GUI

#End Program
root.mainloop()


'''
DEVELOPERS:

-> Chris Herriman Jr (ISD Intern)

'''