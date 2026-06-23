'''
Theme for M+S IT Acquisition Toolbox
'''

###############
### Imports ###
###############

from utils.helpers import resource_path  # Creates paths that work in development and PyInstaller


########################
### M+S Color Scheme ###
########################

primary_blue = "#174A9C"  # Main company blue used for links and accents
dark_blue = "#0B2F6B"  # Darker blue used for labels, borders, and text
light_gray_background = "#F4F6F8"  # Main application background color
white = "#ffffff"  # Header and button background color
scrollbar_track = "#E9EDF2"  # Soft scrollbar track that blends into the page
scrollbar_thumb = "#B8C1CC"  # Muted gray scrollbar handle
scrollbar_hover = "#9FAAB7"  # Slightly darker gray when hovering


#############
### Fonts ###
#############

font_main = ("Segoe UI", 10)  # Standard text font
font_label = ("Segoe UI", 11)  # Labels and descriptive text
font_button = ("Segoe UI", 11, "bold")  # Main action buttons
font_header = ("Segoe UI", 24, "bold")  # Popup and page headings


############
### Logo ###
############

long_logo = resource_path("assets/mslogo_long.png")  # Main header logo
app_icon = resource_path("assets/mslogo.ico")  # Window and popup icon


#########################
### Other UI Graphics ###
#########################

back_arrow = resource_path("assets/back_arrow.png")  # Header back-button image
