# M+S IT Acquisition Toolbox

M+S IT Acquisition Toolbox is a Python/Tkinter desktop utility built to support internal IT workflows at Marshall+Sterling.

The first version focuses on simplifying Robocopy-based user data copying from `C:\Users` through a graphical interface. The goal is to reduce the need for manual Command Prompt usage and make common IT copy tasks faster, safer, and more consistent.

## Project Purpose

This project was created as part of a Summer 2026 IT internship at Marshall+Sterling.

The tool is designed to help improve internal IT workflows, especially tasks related to user data copying, workstation setup, and future acquisition or migration processes.

## Current Features

- Python/Tkinter desktop interface
- Marshall+Sterling themed UI
- Modular project structure
- Reusable helper methods
- Asset path handling for development and PyInstaller
- Image resizing helper for consistent logo/image scaling
- Early UI structure for future Robocopy tools

## Planned Features

- User profile selection from `C:\Users`
- Destination folder selection
- Robocopy command preview
- Robocopy execution through the GUI
- Live output/status display
- Saved log files
- Copy presets for common IT workflows
- PyInstaller packaging as a Windows `.exe`

## Tech Stack

- Python
- Tkinter
- Pillow
- Robocopy
- PyInstaller

## Project Structure

```text
M+S IT Acquisition Toolbox/
│
├── main.py
│
├── assets/
│   ├── mslogo.ico
│   └── mslogo_long.png
│
├── ui/
│   ├── __init__.py
│   ├── header.py
│   └── home.py
│
├── utils/
│   ├── __init__.py
│   ├── helpers.py
│   └── theme.py
│
└── README.md
```

Development Notes

This project is being built in stages.

The first version focuses on the basic application structure, reusable UI components, and the starting layout. Later versions will add Robocopy functionality, command previews, logs, and workflow presets.

The project is intentionally organized across multiple files to practice a cleaner, more maintainable project structure instead of using a single-file script.

Status

In development.

Current focus: building the basic UI and preparing the first user data copy feature.
