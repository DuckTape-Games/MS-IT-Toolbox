# M+S IT Acquisition Toolbox

A Windows desktop application designed to simplify user-profile data acquisition with a graphical interface for Robocopy.

The toolbox allows technicians to select a Windows user, choose complete folders or specific nested subfolders, review detected file extensions, and run a structured copy job without manually writing Robocopy commands.

## Features

* Modern CustomTkinter interface
* Windows user-profile selection from `C:\Users`
* Direct link to open the Windows Users directory
* Default folder selections for:

  * Desktop
  * Favorites
  * Downloads
  * Documents
* Optional **More Folders** view for every other top-level folder
* Clickable folder names that open the selected location in File Explorer
* Expandable and collapsible subfolder browser
* Select specific nested paths such as:

  * `Pictures\Screenshots`
  * `Desktop\Programming\Prototype`
* Parent and child selection handling to prevent duplicate copy jobs
* Scrollable folder and subfolder panels with mouse-wheel support
* Extension scanning for selected folders
* Extension-selection popup with Select All and Deselect All controls
* `.exe`, `.bat`, `.msi`, and `.zip` start excluded by default when detected
* One visible Command Prompt window for the complete copy process
* Folder-level progress messages without displaying every individual filename
* One combined Robocopy log for the entire job
* Timestamped destination folders
* Protection against recursively copying previous acquisition folders
* Application icon support for the main window and popup windows

## Copy Behavior

Each copy creates a new destination folder inside the selected Windows user profile:

```text
MS Username Copy YYYY-MM-DD_HH-MM-SS
```

Robocopy is configured to:

* Copy file data, attributes, and timestamps with `/COPY:DAT`
* Preserve copied directory timestamps with `/DCOPY:T`
* Copy subfolders while skipping completely empty folders with `/S`
* Retry failed files 3 times with `/R:3`
* Wait 10 seconds between retries with `/W:10`
* Write detailed file information to one combined log

The application does not use `/MIR`, preventing Robocopy from deleting destination files.

## Requirements

* Windows 10 or Windows 11
* Python 3.10 or newer
* Robocopy, included with Windows
* CustomTkinter
* Pillow

Install the Python dependencies with:

```bash
pip install -r requirements.txt
```

## Running From Source

Clone or download the repository, open the project directory, and run:

```bash
python main.py
```

The application must be run on Windows because it uses:

* `C:\Users`
* `os.startfile()`
* `cmd.exe`
* Robocopy
* A Windows batch script

## Building an EXE

The project can be packaged with Auto Py to Exe or PyInstaller.

When using Auto Py to Exe, include these folders as additional folders:

```text
assets
scripts
```

The packaged application must retain this relative path:

```text
scripts\run_robocopy.bat
```

The application uses `helpers.resource_path()` to locate bundled resources in both development and packaged builds.

Recommended Auto Py to Exe settings:

* Script Location: `main.py`
* One Directory
* Window Based
* Icon: `assets\mslogo.ico`
* Additional Folder: `assets`
* Additional Folder: `scripts`

## Project Structure

```text
M+S-IT-Acquisition-Toolbox/
├── assets/
│   ├── back_arrow.png
│   ├── mslogo.ico
│   ├── mslogo_long.png
│   └── mslogo_short.png
├── scripts/
│   └── run_robocopy.bat
├── services/
│   └── robocopy_service.py
├── ui/
│   ├── base_screen.py
│   ├── header.py
│   ├── home.py
│   ├── robocopy_actions.py
│   ├── robocopy_components.py
│   ├── robocopy_extensions.py
│   ├── robocopy_folders.py
│   ├── robocopy_page.py
│   └── robocopy_ui.py
├── utils/
│   ├── helpers.py
│   └── theme.py
├── main.py
└── requirements.txt
```

## How It Works

1. Select a Windows user profile.
2. Review the four default folders or choose **More Folders**.
3. Select complete folders or expand them to choose specific subfolders.
4. Click folder names to inspect their contents in File Explorer.
5. Scan the selected paths for file extensions.
6. Choose which detected extensions should be included.
7. Start the copy and confirm the summary.
8. Review folder-level progress in the Command Prompt window.
9. Review the combined log inside the generated `Logs` folder.

## Notes

* Selecting a parent folder clears redundant selected descendants.
* Selecting a specific subfolder clears its selected parent.
* Previous folders created by the toolbox are excluded from future copy selections.
* Empty folders are skipped.
* Robocopy return codes below 8 are treated as successful.
* Full file-level details are recorded in the combined log rather than displayed in Command Prompt.

## Current Status

The application is under active development and is being refined based on feedback from the Marshall + Sterling IT department.

## Author

Developed by Chris Herriman as part of an Information Systems Department internship project.
