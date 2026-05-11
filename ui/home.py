'''
Creates App Home Page
'''
#Imports
import tkinter as tk #UI
from utils import theme #Gets the application theme items


def create_home(root):
    body = tk.Frame(root, bg=theme.light_gray_background, pady=10)
    body.pack(fill="both", expand=True)