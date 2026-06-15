"""Creates the Robocopy page."""

###############
### Imports ###
###############
import tkinter as tk
from tkinter import messagebox
from tkinter.ttk import Combobox

from services import robocopy_service
from utils import helpers, theme


COMMON_EXTENSIONS = [".exe", ".msi", ".bat", ".zip"]


#################################
### Creates the Robocopy menu ###
#################################

def create_robocopy_page(body):
    helpers.clear_frame(body)

    # Configures the fixed three-column layout.
    body.columnconfigure(0, weight=0, minsize=420)
    body.columnconfigure(1, weight=0, minsize=250)
    body.columnconfigure(2, weight=0, minsize=300)
    body.grid_propagate(False)
    body.grid_anchor("nw")

    folder_vars = {}
    extension_vars = {}
    status_var = tk.StringVar(value="Ready")

    # Holds the user selector without changing the lower layout.
    user_select_frame = tk.Frame(body, bg=theme.light_gray_background)
    user_select_frame.grid(
        column=0,
        row=0,
        columnspan=3,
        pady=(30, 15),
    )

    select_user_label = tk.Label(
        user_select_frame,
        text="Select User",
        font=theme.font_label,
        bg=theme.light_gray_background,
        fg=theme.dark_blue,
    )
    select_user_label.pack(side="left", padx=(0, 10))

    user_combobox = Combobox(
        user_select_frame,
        values=helpers.get_windows_users(),
        font=theme.font_label,
        state="readonly",
        width=22,
    )
    user_combobox.pack(side="left", padx=(0, 30))

    folders_label = tk.Label(
        body,
        text="Selected Folders\nare included in copy",
        font=theme.font_label,
        bg=theme.light_gray_background,
        fg=theme.dark_blue,
    )
    folders_label.grid(column=0, row=1)

    extensions_label = tk.Label(
        body,
        text="Selected Extensions\nare included in copy",
        font=theme.font_label,
        bg=theme.light_gray_background,
        fg=theme.dark_blue,
    )
    extensions_label.grid(column=2, row=1)

    folder_checkbox_frame = tk.Frame(
        body,
        bg=theme.light_gray_background,
        width=420,
        height=400,
    )
    folder_checkbox_frame.grid(
        column=0,
        row=2,
        padx=20,
        pady=10,
        sticky="nw",
    )
    folder_checkbox_frame.grid_propagate(False)

    extension_checkbox_frame = tk.Frame(
        body,
        bg=theme.light_gray_background,
        width=300,
        height=400,
    )
    extension_checkbox_frame.grid(
        column=2,
        row=2,
        padx=20,
        pady=10,
        sticky="nw",
    )
    extension_checkbox_frame.grid_propagate(False)

    middle_frame = tk.Frame(
        body,
        bg=theme.light_gray_background,
        width=250,
        height=400,
    )
    middle_frame.grid(column=1, row=2, pady=10, sticky="n")
    middle_frame.grid_propagate(False)

    divider_line = tk.Frame(middle_frame, bg=theme.dark_blue, width=2)
    divider_line.place(relx=0.5, rely=0, relheight=1, anchor="n")

    scan_extensions_button = tk.Button(
        middle_frame,
        text="Scan Selected Folders\nFor Extensions",
        font=theme.font_button,
        command=lambda: create_extension_popup(
            body,
            user_combobox.get(),
            folder_vars,
            extension_vars,
        ),
    )
    scan_extensions_button.place(relx=0.5, rely=0.35, anchor="center")

    run_copy_button = tk.Button(
        middle_frame,
        text="Run Copy",
        font=theme.font_button,
        command=lambda: run_copy(
            body,
            user_combobox.get(),
            folder_vars,
            extension_vars,
            status_var,
        ),
    )
    run_copy_button.place(relx=0.5, rely=0.70, anchor="center")

    status_label = tk.Label(
        middle_frame,
        textvariable=status_var,
        font=theme.font_main,
        bg=theme.light_gray_background,
        fg=theme.dark_blue,
        wraplength=220,
        justify="center",
    )
    status_label.place(relx=0.5, rely=0.88, anchor="center")

    user_combobox.bind(
        "<<ComboboxSelected>>",
        lambda event: create_user_folder_checkboxes(
            event,
            folder_checkbox_frame,
            folder_vars,
        ),
    )

    default_extension_checkboxes(extension_checkbox_frame, extension_vars)


#######################################
### Creates user-folder checkboxes  ###
#######################################

def create_user_folder_checkboxes(event, folder_frame, folder_vars):
    helpers.clear_frame(folder_frame)
    folder_vars.clear()

    selected_user = event.widget.get()
    folders = helpers.get_user_folders(selected_user)

    folder_frame.columnconfigure(0, weight=0)
    folder_frame.columnconfigure(1, weight=0)
    folder_frame.columnconfigure(2, weight=0)

    for count, item in enumerate(folders):
        folder_var = tk.BooleanVar(value=True)
        folder_vars[item] = folder_var

        checkbox = tk.Checkbutton(
            folder_frame,
            text=item,
            variable=folder_var,
            bg=theme.light_gray_background,
            fg=theme.dark_blue,
        )
        checkbox.grid(
            column=count % 3,
            row=count // 3,
            sticky="w",
            padx=4,
            pady=2,
        )


################################################################
### Creates checkboxes for commonly excluded file extensions ###
################################################################

def default_extension_checkboxes(extension_frame, extension_vars):
    helpers.clear_frame(extension_frame)
    extension_vars.clear()

    for count, extension in enumerate(COMMON_EXTENSIONS):
        extension_var = tk.BooleanVar(value=True)
        extension_vars[extension] = extension_var

        checkbox = tk.Checkbutton(
            extension_frame,
            text=extension,
            variable=extension_var,
            bg=theme.light_gray_background,
            fg=theme.dark_blue,
        )
        checkbox.grid(column=0, row=count, sticky="w")


#####################################################
### Creates a popup for all extension types found ###
#####################################################

def create_extension_popup(body, selected_user, folder_vars, extension_vars):
    if not selected_user:
        messagebox.showwarning(
            "No User Selected",
            "Select a user before scanning for file types.",
            parent=body.winfo_toplevel(),
        )
        return

    selected_folders = get_selected_folders(folder_vars)

    if not selected_folders:
        messagebox.showwarning(
            "No Folders Selected",
            "Select at least one folder before scanning for file types.",
            parent=body.winfo_toplevel(),
        )
        return

    # The existing scanner is intentionally kept synchronous because this is
    # the version that has been stable in the current project.
    extensions = helpers.get_unique_extensions(selected_user, folder_vars)

    popup = tk.Toplevel(body)
    popup.title("All File Types")
    popup.geometry("1200x600")
    popup.minsize(750, 400)
    popup.configure(bg=theme.light_gray_background)
    popup.iconbitmap(theme.app_icon)
    popup.transient(body.winfo_toplevel())
    popup.grab_set()

    popup_title = tk.Label(
        popup,
        text="Detected File Types",
        font=theme.font_header,
        bg=theme.light_gray_background,
        fg=theme.dark_blue,
    )
    popup_title.pack(pady=20)

    scroll_container = tk.Frame(popup, bg=theme.light_gray_background)
    scroll_container.pack(fill="both", expand=True, padx=20, pady=(0, 20))

    canvas = tk.Canvas(
        scroll_container,
        bg=theme.light_gray_background,
        highlightthickness=0,
    )
    canvas.pack(side="left", fill="both", expand=True)

    scrollbar = tk.Scrollbar(
        scroll_container,
        orient="vertical",
        command=canvas.yview,
    )
    scrollbar.pack(side="right", fill="y")

    canvas.configure(yscrollcommand=scrollbar.set)

    checkbox_frame = tk.Frame(canvas, bg=theme.light_gray_background)
    checkbox_window = canvas.create_window(
        (0, 0),
        window=checkbox_frame,
        anchor="nw",
    )

    checkbox_frame.bind(
        "<Configure>",
        lambda event: canvas.configure(scrollregion=canvas.bbox("all")),
    )
    canvas.bind(
        "<Configure>",
        lambda event: canvas.itemconfigure(checkbox_window, width=event.width),
    )

    def on_mousewheel(event):
        canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

    def bind_mousewheel(event):
        canvas.bind_all("<MouseWheel>", on_mousewheel)

    def unbind_mousewheel(event=None):
        canvas.unbind_all("<MouseWheel>")

    canvas.bind("<Enter>", bind_mousewheel)
    canvas.bind("<Leave>", unbind_mousewheel)

    current_extensions = set(extensions)

    # Removes old scanned values while preserving the four main-page values.
    for extension in list(extension_vars):
        if extension not in COMMON_EXTENSIONS and extension not in current_extensions:
            del extension_vars[extension]

    for index, extension in enumerate(extensions):
        if extension not in extension_vars:
            extension_vars[extension] = tk.BooleanVar(value=True)

        extension_checkbox = tk.Checkbutton(
            checkbox_frame,
            text=extension,
            variable=extension_vars[extension],
            bg=theme.light_gray_background,
            fg=theme.dark_blue,
        )
        extension_checkbox.grid(
            row=index // 3,
            column=index % 3,
            sticky="w",
            padx=10,
            pady=5,
        )

    if not extensions:
        no_extensions_label = tk.Label(
            checkbox_frame,
            text="No file extensions were found.",
            font=theme.font_label,
            bg=theme.light_gray_background,
            fg=theme.dark_blue,
        )
        no_extensions_label.grid(row=0, column=0, padx=20, pady=20)

    def close_popup():
        unbind_mousewheel()
        popup.destroy()

    popup.protocol("WM_DELETE_WINDOW", close_popup)

    close_button = tk.Button(
        popup,
        text="Close",
        font=theme.font_button,
        command=close_popup,
    )
    close_button.pack(side="bottom", pady=20)


########################################
### Gets the currently checked folders ###
########################################

def get_selected_folders(folder_vars):
    return [
        folder_name
        for folder_name, variable in folder_vars.items()
        if variable.get()
    ]


###########################################
### Runs Robocopy with the current choices ###
###########################################

def run_copy(
    body,
    selected_user,
    folder_vars,
    extension_vars,
    status_var,
):
    parent_window = body.winfo_toplevel()

    if not selected_user:
        messagebox.showwarning(
            "No User Selected",
            "Select a user before running Robocopy.",
            parent=parent_window,
        )
        return

    selected_folders = get_selected_folders(folder_vars)

    if not selected_folders:
        messagebox.showwarning(
            "No Folders Selected",
            "Select at least one folder to copy.",
            parent=parent_window,
        )
        return

    excluded_extensions = [
        extension
        for extension, variable in extension_vars.items()
        if not variable.get()
    ]

    confirmed = messagebox.askyesno(
        "Confirm Copy",
        (
            f"User: {selected_user}\n"
            f"Folders: {len(selected_folders)} selected\n"
            "Destination: A new folder in the selected user profile\n"
            f"Excluded file types: {len(excluded_extensions)}\n\n"
            "Start Robocopy?"
        ),
        parent=parent_window,
    )

    if not confirmed:
        return

    status_var.set("Robocopy is running...")
    parent_window.update_idletasks()

    try:
        result = robocopy_service.run_robocopy(
            username=selected_user,
            selected_folders=selected_folders,
            excluded_extensions=excluded_extensions,
        )
    except (FileNotFoundError, PermissionError, OSError, RuntimeError) as error:
        status_var.set("Copy failed")
        messagebox.showerror(
            "Robocopy Failed",
            str(error),
            parent=parent_window,
        )
        return

    failed_results = [
        folder_result
        for folder_result in result["results"]
        if not folder_result["success"]
    ]

    if result["success"]:
        status_var.set("Copy completed successfully")
        messagebox.showinfo(
            "Copy Complete",
            (
                "Robocopy completed successfully.\n\n"
                f"Destination: {result['destination']}\n"
                f"Logs: {result['log_folder']}"
            ),
            parent=parent_window,
        )
        return

    status_var.set("Copy completed with errors")
    failed_names = ", ".join(
        folder_result["folder"] for folder_result in failed_results
    )

    messagebox.showwarning(
        "Copy Completed With Errors",
        (
            "One or more folders could not be copied successfully.\n\n"
            f"Failed folders: {failed_names}\n"
            f"Logs: {result['log_folder']}"
        ),
        parent=parent_window,
    )
