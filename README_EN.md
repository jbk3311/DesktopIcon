[中文文档](README.md) | English 

---

# Desktop Icon Manager

A tool for managing Windows desktop icons, helping you easily control the display and hiding of desktop icons, with the ability to restore icons to their original positions when toggling visibility.

## Features

- Control desktop icon visibility
- Icon group management for quick batch hide/show
- Save and restore desktop icon positions
- Clean and intuitive graphical user interface
- Administrator privileges support
- Automatic icon position configuration saving
- Group configuration saved in `icon_groups.json`

## Icon Groups

1. Click **Manage Groups** to create groups and assign icons
2. Select a group and click **Select Group** to check icons in that group (without clearing other selections)
3. Use **Hide Selected** or **Show Selected** for batch operations
4. Each icon belongs to at most one group; unassigned icons are **Ungrouped**

## System Requirements

- Windows Operating System
- Python 3.6 or higher
- Administrator privileges (required for full desktop icon control)

## Installation

1. Clone or download this project to your local machine
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Usage

1. Run the main program:
   ```bash
   python main.py
   ```
2. The program will automatically request administrator privileges (required for desktop icon control)
3. Use the graphical interface to manage your desktop icons

## Build exe

This project can be packaged into a Windows executable using [Nuitka](https://nuitka.net/). See [`build.py`](build.py).

### Requirements

- Windows 10 or later
- Python 3.6+ (same as development)
- Network access (Nuitka may download a C compiler on first build)

### Steps

1. Open a terminal in the project root (where `main.py` and `build.py` live):
   ```bash
   cd desktopicon
   ```

2. Install dependencies with the **same** Python you will use to build:
   ```bash
   python -m pip install -r requirements.txt
   ```
   If multiple Python installs exist (e.g. MSYS2 and official CPython), prefer:
   ```bash
   py -3.10 -m pip install -r requirements.txt
   py -3.10 build.py
   ```

3. Run the build script:
   ```bash
   python build.py
   ```

4. After a successful build, find the single-file exe under `dist`:
   ```
   dist/桌面图标管理器v1.0.0.exe
   ```
   The version suffix matches `APP_VERSION` in [`src/config.py`](src/config.py).

5. Double-click the exe to run. UAC will prompt for administrator privileges (`--windows-uac-admin` is enabled at build time); Python is not required on the target machine.

### Notes

- `build.py` cleans old `build`, `dist`, and other intermediate folders before building
- Output is a **one-file exe** with the app icon and `src/resources` bundled
- The first build may take a while; if it fails, ensure a C toolchain is available or run `python -m pip install -U nuitka`

### Common build errors

**`No module named nuitka`**

The Python running `build.py` does not have Nuitka, while `pip install` may have targeted another Python. Check:

```bash
where python
where pip
python -c "import sys; print(sys.executable)"
```

Fix by using one interpreter for both steps, e.g.:

```bash
py -3.10 -m pip install -r requirements.txt
py -3.10 build.py
```

**`No matching distribution found for tkinter`**

`tkinter` is part of the standard library on Windows CPython and cannot be installed via pip. It has been removed from `requirements.txt`.

### Config files

When running the exe, these files are created **next to the executable**:

- `icon_positions.json` — icon position backup
- `icon_groups.json` — icon group configuration

> **Note:** Nuitka `--onefile` executables extract themselves to a temporary directory on each run, which is deleted on exit. This project uses `sys.executable` (instead of `__file__`) to resolve file paths, ensuring both config files are always saved beside the exe and never lost between runs.

Copy both JSON files alongside the exe to back up your layout and group settings.

## Notes

- Administrator privileges are required for full desktop icon control
- Desktop refresh may be needed to see changes
- If icons disappear due to program interruption, simply restart the program and enable display

## License

This project is licensed under the GNU License - see the [LICENSE](LICENSE) file for details

## Author

- Author: [jbk3311]

## Contributing

Issues and Pull Requests are welcome to help improve this project.
