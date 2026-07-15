"""
Creates and reads the top-level and subfolder selection controls.
"""

###############
### Imports ###
###############

import os  # Opens selected Windows folders in File Explorer
import tkinter as tk  # Provides Canvas and BooleanVar for scrolling and state
from pathlib import Path, PurePath  # Builds and compares selected folder paths
from tkinter import messagebox  # Reports folder-opening errors

import customtkinter as ctk  # Creates CustomTkinter folder controls

from ui.robocopy_components import create_link_control  # Creates clickable folder-name links
from utils import helpers, theme  # Provides folder discovery and visual settings


#################################
### Default Folder Selections ###
#################################

# These top-level folders begin selected whenever a Windows user profile is loaded
DEFAULT_SELECTED_FOLDERS = {
    "desktop",
    "favorites",
    "downloads",
    "documents",
}

# Keeps the four default folders in a predictable display order
DEFAULT_FOLDER_ORDER = [
    "Desktop",
    "Favorites",
    "Downloads",
    "Documents",
]


#####################################
### Opens a User Folder for Review ##
#####################################

def open_user_folder(username, relative_folder_path):
    """Opens a selected user folder in Windows File Explorer."""
    # Builds the full path from the user profile and selected relative path
    folder_path = Path("C:/Users") / username / Path(relative_folder_path)

    # Stops with a clear message if the folder no longer exists
    if not folder_path.exists() or not folder_path.is_dir():
        messagebox.showerror(
            "Folder Not Found",
            f"The selected folder could not be found:\n{folder_path}",
        )
        return

    try:
        # Uses the standard Windows folder-opening behavior
        os.startfile(folder_path)
    except OSError as error:
        # Reports Windows or permission errors instead of crashing the page
        messagebox.showerror(
            "Unable to Open Folder",
            f"The folder could not be opened:\n{folder_path}\n\n{error}",
        )


#####################################
### Shared Folder Selection Rules ###
#####################################

def _is_descendant(child_path, parent_path):
    """Returns True when child_path is below parent_path."""
    child_parts = PurePath(child_path).parts
    parent_parts = PurePath(parent_path).parts

    return (
        len(child_parts) > len(parent_parts)
        and child_parts[:len(parent_parts)] == parent_parts
    )


def _has_selected_ancestor(folder_vars, child_path):
    """Returns True when a loaded ancestor already selects this folder."""
    child_parts = PurePath(child_path).parts

    for relative_path, variable in folder_vars.items():
        parent_parts = PurePath(relative_path).parts

        if (
            variable.get()
            and len(parent_parts) < len(child_parts)
            and child_parts[:len(parent_parts)] == parent_parts
        ):
            return True

    return False


def _clear_selected_descendants(folder_vars, parent_path):
    """Clears selected descendants when their parent becomes selected."""
    for relative_path, variable in folder_vars.items():
        if _is_descendant(relative_path, parent_path):
            variable.set(False)


def _clear_selected_ancestors(folder_vars, child_path):
    """Clears selected ancestors when a more specific child is selected."""
    child_parts = PurePath(child_path).parts

    for relative_path, variable in folder_vars.items():
        parent_parts = PurePath(relative_path).parts
        if (
            len(parent_parts) < len(child_parts)
            and child_parts[:len(parent_parts)] == parent_parts
        ):
            variable.set(False)


def _handle_selection_change(folder_vars, relative_path):
    """Keeps loaded folder states synchronized with parent and child choices."""
    variable = folder_vars[relative_path]

    if variable.get():
        # Selecting a child clears any selected ancestors to prevent duplicates
        _clear_selected_ancestors(folder_vars, relative_path)

        # Loaded descendants begin selected because the chosen folder includes them
        for child_path, child_variable in folder_vars.items():
            if _is_descendant(child_path, relative_path):
                child_variable.set(True)
    else:
        # Clearing a nested folder removes selected ancestors so the exclusion works
        _clear_selected_ancestors(folder_vars, relative_path)

        # Clearing a folder also clears all loaded descendants beneath it
        _clear_selected_descendants(folder_vars, relative_path)


##################################
### Scrollable Subfolder Panel ###
##################################

class SubfolderPanel:
    """Displays one top-level folder's expandable subfolder tree on the right."""

    def __init__(self, parent, folder_vars, selection_change_callback=None):
        """Builds the scrollable panel used for nested subfolders."""
        # Stores the outer frame and shared checkbox variables
        self.parent = parent
        self.folder_vars = folder_vars
        self.selection_change_callback = selection_change_callback

        # Tracks the user, active top-level folder, and expanded relative paths
        self.username = ""
        self.root_folder = ""
        self.expanded_paths = set()

        # Tracks the top-level button currently showing a minus sign
        self.active_root_button = None

        # CustomTkinter has no canvas widget, so Tk Canvas provides scrolling only
        self.canvas = tk.Canvas(
            parent,
            bg=theme.light_gray_background,
            highlightthickness=0,
        )
        # Matches the left panel's muted vertical scrollbar styling
        self.vertical_scrollbar = ctk.CTkScrollbar(
            parent,
            orientation="vertical",
            command=self.canvas.yview,
            fg_color=theme.scrollbar_track,
            button_color=theme.scrollbar_thumb,
            button_hover_color=theme.scrollbar_hover,
        )
        # Matches the left panel's muted horizontal scrollbar styling
        self.horizontal_scrollbar = ctk.CTkScrollbar(
            parent,
            orientation="horizontal",
            command=self.canvas.xview,
            fg_color=theme.scrollbar_track,
            button_color=theme.scrollbar_thumb,
            button_hover_color=theme.scrollbar_hover,
        )
        self.content_frame = ctk.CTkFrame(
            self.canvas,
            fg_color=theme.light_gray_background,
            corner_radius=0,
        )

        # Places the scrollable area and its scrollbars
        self.canvas.grid(column=0, row=0, sticky="nsew")
        self.vertical_scrollbar.grid(
            column=1,
            row=0,
            sticky="ns",
            padx=(8, 0),
        )
        self.horizontal_scrollbar.grid(
            column=0,
            row=1,
            sticky="ew",
            pady=(8, 0),
        )

        # Lets the canvas fill the fixed right-side panel
        parent.rowconfigure(0, weight=1)
        parent.columnconfigure(0, weight=1)

        # Connects the inner frame to the canvas
        self.window_id = self.canvas.create_window(
            (0, 0),
            window=self.content_frame,
            anchor="nw",
        )
        self.canvas.configure(
            yscrollcommand=self.vertical_scrollbar.set,
            xscrollcommand=self.horizontal_scrollbar.set,
        )

        # Keeps the visible frame and scroll region synchronized
        self.content_frame.bind("<Configure>", self._update_scroll_region)
        self.canvas.bind("<Configure>", self._resize_content_frame)

        # Enables mouse-wheel support while the pointer is over the panel
        self.canvas.bind("<Enter>", self._bind_mousewheel)
        self.canvas.bind("<Leave>", self._unbind_mousewheel)
        self.content_frame.bind("<Enter>", self._bind_mousewheel)
        self.content_frame.bind("<Leave>", self._unbind_mousewheel)

        # Shows instructions until a top-level folder is expanded
        self._show_placeholder()

    def _update_scroll_region(self, event=None):
        """Updates the canvas scrollable area after rows change."""
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))

    def _resize_content_frame(self, event):
        """Keeps the inner frame at least as wide as the visible panel."""
        requested_width = self.content_frame.winfo_reqwidth()
        self.canvas.itemconfigure(
            self.window_id,
            width=max(event.width, requested_width),
        )

    def _bind_mousewheel(self, event=None):
        """Activates mouse-wheel scrolling for this panel."""
        self.canvas.bind_all("<MouseWheel>", self._on_mousewheel)

    def _unbind_mousewheel(self, event=None):
        """Stops this panel from capturing the wheel outside its area."""
        self.canvas.unbind_all("<MouseWheel>")

    def _on_mousewheel(self, event):
        """Scrolls vertically using the Windows mouse-wheel value."""
        self.canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

    def _show_placeholder(self):
        """Explains how to display subfolders in the right-side panel."""
        helpers.clear_frame(self.content_frame)

        placeholder = ctk.CTkLabel(
            self.content_frame,
            text=(
                "Click the + button beside a folder\n"
                "to view and select its subfolders."
            ),
            font=theme.font_main,
            text_color=theme.dark_blue,
            fg_color="transparent",
            justify="center",
        )
        placeholder.pack(padx=20, pady=40)

        self._update_scroll_region()

    def _root_button_exists(self):
        """Returns True when the stored top-level expand button still exists."""
        if self.active_root_button is None:
            return False

        try:
            return bool(self.active_root_button.winfo_exists())
        except tk.TclError:
            return False

    def prepare_for_root_button_rebuild(self):
        """Drops a button reference before top-level rows are destroyed."""
        self.active_root_button = None

    def register_root_button(self, root_folder, expand_button):
        """Connects a rebuilt top-level button to the active subfolder branch."""
        if self.root_folder == root_folder:
            self.active_root_button = expand_button
            expand_button.configure(text="−")

    def reset(self):
        """Clears the currently displayed subfolder branch."""
        # Restores the previous top-level expand button before clearing the panel
        if self._root_button_exists():
            self.active_root_button.configure(text="+")

        self.active_root_button = None
        self.username = ""
        self.root_folder = ""
        self.expanded_paths.clear()
        self._show_placeholder()

    def _get_children(self, relative_path):
        """Returns accessible immediate subfolders for one relative path."""
        full_path = Path("C:/Users") / self.username / Path(relative_path)

        try:
            return sorted(
                [item.name for item in full_path.iterdir() if item.is_dir()],
                key=str.casefold,
            )
        except (FileNotFoundError, PermissionError, OSError):
            return []

    def _get_or_create_variable(self, relative_path):
        """Returns the shared BooleanVar for one subfolder path."""
        if relative_path not in self.folder_vars:
            # Newly loaded subfolders inherit the selected state of their parent
            starts_selected = _has_selected_ancestor(
                self.folder_vars,
                relative_path,
            )
            self.folder_vars[relative_path] = tk.BooleanVar(
                value=starts_selected
            )

        return self.folder_vars[relative_path]

    def toggle_root(self, username, root_folder, expand_button):
        """Expands or collapses one top-level folder in the right panel."""
        # Clicking the active minus button collapses the entire right-side area
        if (
            self.root_folder == root_folder
            and self.active_root_button is expand_button
        ):
            self.reset()
            return

        # Restores the previously active top-level button before switching folders
        if self._root_button_exists():
            self.active_root_button.configure(text="+")

        # Marks the newly selected top-level folder as expanded
        self.active_root_button = expand_button
        self.active_root_button.configure(text="−")
        self.username = username
        self.root_folder = root_folder
        self.expanded_paths.clear()
        self.render()

    def _toggle_expanded(self, relative_path):
        """Expands or collapses one nested subfolder."""
        if relative_path in self.expanded_paths:
            self.expanded_paths.remove(relative_path)
        else:
            self.expanded_paths.add(relative_path)

        self.render()

    def _on_selection_changed(self, relative_path):
        """Applies parent and child selection rules to one subfolder."""
        _handle_selection_change(self.folder_vars, relative_path)
        if self.selection_change_callback is not None:
            self.selection_change_callback()
        self.render()

    def _add_row(self, relative_path, depth, row_number):
        """Adds one selectable subfolder row to the right-side tree."""
        children = self._get_children(relative_path)
        is_expanded = relative_path in self.expanded_paths
        folder_var = self._get_or_create_variable(relative_path)


        # Holds the expand button, checkbox, and clickable folder name
        row_frame = ctk.CTkFrame(
            self.content_frame,
            fg_color="transparent",
            corner_radius=0,
        )
        row_frame.grid(
            column=0,
            row=row_number,
            sticky="w",
            padx=(8 + (depth * 22), 8),
            pady=2,
        )

        # Shows whether this subfolder can be expanded further
        if children:
            expand_button = ctk.CTkButton(
                row_frame,
                text="−" if is_expanded else "+",
                width=28,
                height=26,
                font=theme.font_main,
                fg_color=theme.white,
                hover_color="#E7ECF2",
                text_color=theme.dark_blue,
                border_color=theme.dark_blue,
                border_width=1,
                corner_radius=4,
                command=lambda path=relative_path: self._toggle_expanded(path),
            )
            expand_button.pack(side="left", padx=(0, 4))
        else:
            spacer = ctk.CTkLabel(
                row_frame,
                text="",
                width=28,
                height=26,
                fg_color="transparent",
            )
            spacer.pack(side="left", padx=(0, 4))

        # Selects this exact relative folder path for the copy job
        checkbox = ctk.CTkCheckBox(
            row_frame,
            text="",
            variable=folder_var,
            width=22,
            height=22,
            checkbox_width=18,
            checkbox_height=18,
            fg_color=theme.primary_blue,
            hover_color=theme.dark_blue,
            border_color=theme.dark_blue,
            command=lambda path=relative_path: self._on_selection_changed(path),
        )
        checkbox.pack(side="left")

        # Opens this exact nested folder in File Explorer
        folder_link = create_link_control(
            row_frame,
            PurePath(relative_path).name,
            lambda path=relative_path: open_user_folder(
                self.username,
                path,
            ),
        )
        folder_link.pack(side="left", padx=(2, 0))

        return children, is_expanded

    def _render_branch(self, relative_path, depth, row_number):
        """Adds one subfolder and any currently expanded descendants."""
        children, is_expanded = self._add_row(
            relative_path,
            depth,
            row_number,
        )
        row_number += 1

        if is_expanded:
            for child_name in children:
                child_path = str(Path(relative_path) / child_name)
                row_number = self._render_branch(
                    child_path,
                    depth + 1,
                    row_number,
                )

        return row_number

    def render(self):
        """Rebuilds the active subfolder branch while preserving selections."""
        helpers.clear_frame(self.content_frame)

        if not self.username or not self.root_folder:
            self._show_placeholder()
            return

        # Labels which top-level folder is currently being inspected
        title_label = ctk.CTkLabel(
            self.content_frame,
            text=f"Subfolders in {self.root_folder}",
            font=theme.font_label,
            text_color=theme.dark_blue,
            fg_color="transparent",
        )
        title_label.grid(column=0, row=0, sticky="w", padx=10, pady=(5, 10))

        # Loads only immediate children until deeper levels are expanded
        children = self._get_children(self.root_folder)
        row_number = 1

        if not children:
            empty_label = ctk.CTkLabel(
                self.content_frame,
                text="No accessible subfolders were found.",
                font=theme.font_main,
                text_color=theme.dark_blue,
                fg_color="transparent",
            )
            empty_label.grid(column=0, row=row_number, sticky="w", padx=10, pady=10)
        else:
            for child_name in children:
                child_path = str(Path(self.root_folder) / child_name)
                row_number = self._render_branch(
                    child_path,
                    depth=0,
                    row_number=row_number,
                )

        self._update_scroll_region()


#####################################
### Creates Top-Level Folder List ###
#####################################

def _get_visible_folders(all_folders, show_all_folders):
    """Returns either the four defaults or the complete folder list."""
    # Shows every folder after the More Folders button is used
    if show_all_folders:
        return all_folders

    # Matches defaults case-insensitively while preserving the requested order
    folder_lookup = {
        folder_name.casefold(): folder_name
        for folder_name in all_folders
    }

    return [
        folder_lookup[default_name.casefold()]
        for default_name in DEFAULT_FOLDER_ORDER
        if default_name.casefold() in folder_lookup
    ]


def _render_top_level_folders(
    selected_user,
    folder_frame,
    subfolder_panel,
    folder_vars,
    folder_display_state,
    selection_change_callback=None,
):
    """Draws the currently visible top-level folder rows."""
    # Drops references to buttons that are about to be destroyed
    subfolder_panel.prepare_for_root_button_rebuild()

    # Removes only the visible folder widgets while preserving checkbox values
    helpers.clear_frame(folder_frame)

    # Reads the complete folder list and current display mode
    all_folders = folder_display_state.get("folders", [])
    show_all_folders = folder_display_state.get("show_all", False)
    visible_folders = _get_visible_folders(
        all_folders,
        show_all_folders,
    )

    # Keeps the existing three-column top-level folder layout
    for column in range(3):
        folder_frame.columnconfigure(column, weight=0)

    # Creates one checkbox, clickable name, and expand button per visible folder
    for count, folder_name in enumerate(visible_folders):
        folder_var = folder_vars[folder_name]

        folder_item_frame = ctk.CTkFrame(
            folder_frame,
            fg_color="transparent",
            corner_radius=0,
        )
        folder_item_frame.grid(
            column=count % 3,
            row=count // 3,
            sticky="w",
            padx=4,
            pady=2,
        )

        # Loads or collapses this folder's subfolders in the right-side panel
        # The expand button stays on the far left to match nested subfolder rows
        expand_button = ctk.CTkButton(
            folder_item_frame,
            text="+",
            width=28,
            height=26,
            font=theme.font_main,
            fg_color=theme.white,
            hover_color="#E7ECF2",
            text_color=theme.dark_blue,
            border_color=theme.dark_blue,
            border_width=1,
            corner_radius=4,
        )
        expand_button.configure(
            command=lambda username=selected_user, path=folder_name, button=expand_button: (
                subfolder_panel.toggle_root(username, path, button)
            )
        )
        expand_button.pack(side="left", padx=(0, 4))
        subfolder_panel.register_root_button(folder_name, expand_button)

        # Selects the complete top-level folder
        checkbox = ctk.CTkCheckBox(
            folder_item_frame,
            text="",
            variable=folder_var,
            width=22,
            height=22,
            checkbox_width=18,
            checkbox_height=18,
            fg_color=theme.primary_blue,
            hover_color=theme.dark_blue,
            border_color=theme.dark_blue,
            command=lambda path=folder_name: (
                _handle_selection_change(
                    folder_vars,
                    path,
                ),
                subfolder_panel.render()
                if subfolder_panel.root_folder == path
                else None,
                selection_change_callback()
                if selection_change_callback is not None
                else None,
            ),
        )
        checkbox.pack(side="left")

        # Opens the top-level folder in File Explorer
        folder_link = create_link_control(
            folder_item_frame,
            folder_name,
            lambda username=selected_user, path=folder_name: open_user_folder(
                username,
                path,
            ),
        )
        folder_link.pack(side="left", padx=(2, 0))


def toggle_additional_folders(
    selected_user,
    folder_frame,
    subfolder_panel,
    folder_vars,
    folder_display_state,
    more_folders_button,
    selection_change_callback=None,
):
    """Switches between the default-only and complete folder lists."""
    # Does nothing until a valid user profile has been loaded
    if not selected_user or not folder_display_state.get("folders"):
        return

    # Flips the display mode while keeping all current checkbox states
    folder_display_state["show_all"] = not folder_display_state.get(
        "show_all",
        False,
    )

    # Updates the button text so the current action is always clear
    more_folders_button.configure(
        text=(
            "Default Folders"
            if folder_display_state["show_all"]
            else "More Folders"
        )
    )

    # Rebuilds only the left list without resetting the right-side panel
    _render_top_level_folders(
        selected_user,
        folder_frame,
        subfolder_panel,
        folder_vars,
        folder_display_state,
        selection_change_callback,
    )


def create_user_folder_checkboxes(
    selected_user,
    folder_frame,
    subfolder_panel,
    folder_vars,
    folder_display_state,
    more_folders_button,
    selection_change_callback=None,
):
    """Loads a user's folders and initially displays only the four defaults."""
    # Removes the previous user's widgets, variables, and subfolder branch
    helpers.clear_frame(folder_frame)
    folder_vars.clear()
    subfolder_panel.reset()

    # Reads every accessible top-level folder for the selected user
    folders = helpers.get_user_folders(selected_user)

    # Stores the full list while starting in default-only display mode
    folder_display_state.clear()
    folder_display_state.update(
        {
            "selected_user": selected_user,
            "folders": folders,
            "show_all": False,
        }
    )

    # Creates variables for every folder, including folders not initially visible
    for folder_name in folders:
        starts_selected = folder_name.casefold() in DEFAULT_SELECTED_FOLDERS
        folder_vars[folder_name] = tk.BooleanVar(value=starts_selected)

    # Resets and enables the button used to reveal the remaining folders
    has_additional_folders = any(
        folder_name.casefold() not in DEFAULT_SELECTED_FOLDERS
        for folder_name in folders
    )
    more_folders_button.configure(
        text="More Folders",
        state="normal" if has_additional_folders else "disabled",
        command=lambda: toggle_additional_folders(
            selected_user,
            folder_frame,
            subfolder_panel,
            folder_vars,
            folder_display_state,
            more_folders_button,
            selection_change_callback,
        ),
    )

    # Draws only Desktop, Favorites, Downloads, and Documents at first
    _render_top_level_folders(
        selected_user,
        folder_frame,
        subfolder_panel,
        folder_vars,
        folder_display_state,
        selection_change_callback,
    )


##########################################
### Gets the Currently Checked Folders ###
##########################################

def get_selected_folders(folder_vars):
    """Returns selected relative paths after removing redundant descendants."""
    # Sorts shortest paths first so selected parents are processed before children
    checked_paths = sorted(
        [
            folder_path
            for folder_path, variable in folder_vars.items()
            if variable.get()
        ],
        key=lambda path: (len(PurePath(path).parts), path.casefold()),
    )

    selected_paths = []

    for folder_path in checked_paths:
        folder_parts = PurePath(folder_path).parts

        # Skips a selected child when one of its selected ancestors already covers it
        has_selected_parent = any(
            folder_parts[:len(PurePath(parent_path).parts)]
            == PurePath(parent_path).parts
            for parent_path in selected_paths
        )

        if not has_selected_parent:
            selected_paths.append(folder_path)

    return selected_paths
