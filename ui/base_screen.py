'''
Creates App Base Screen
'''
#Imports
import tkinter as tk #UI
from utils import theme #Gets the application theme items


def create_screen_base(root):
    body = tk.Frame(root, bg=theme.light_gray_background, pady=10)
    root.grid_rowconfigure(2, weight=1)
    root.grid_columnconfigure(0, weight=1)

    body.grid(row=2, column=0, sticky="nsew")
    return body