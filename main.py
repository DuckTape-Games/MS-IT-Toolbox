'''
Title: M+S IT Acquisition Toolbox
Purpose: Improve speed for Marshall+Sterling IT Department during acquisitions
Start Date: 5/8/2026
Lead Developer: Chris Herriman Jr (Marshall+Sterling 2026 IT Intern)
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
'''

#Imports
import tkinter as tk #Used for GUI
from utils import theme #Marshall+Sterling Theme
from ui import header, home #Creates the application header and the home page

#Screen Setup
root = tk.Tk()
root.title("M+S IT Acquisition Toolbox")
root.iconbitmap(theme.app_icon)
root.geometry("1200x700")
root.maxsize(1200, 700)
header.create_header(root) #Adds the header to the GUI
home.create_home(root) #Adds the home screen to the GUI

#End Program
root.mainloop()