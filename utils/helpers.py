'''
Helper methods for M+S IT Acquisition Toolbox
'''
#Imports
import os, sys #Used for managing system

### Makes onefile mode work in pyinstaller
def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)


### Resizes an image
def resize_image(image, new_width=None, new_height=None):
    """
    If neither dimensions are given, original image will be returned
    If both width AND height are given, image will be stetched to fit the new dimensions
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