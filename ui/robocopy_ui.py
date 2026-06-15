'''
Public entry point for the reorganized Robocopy interface.
'''

###############
### Imports ###
###############

from ui.robocopy_page import create_robocopy_page  # Builds the complete Robocopy page


############################
### Public Module Exports ###
############################

# Keeps the existing import path working for the home page and older code
__all__ = ["create_robocopy_page"]
