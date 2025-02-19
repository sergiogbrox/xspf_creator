# XSPF_Creator

**XSPF_Creator** is a Python-based tool that generates **XSPF playlists** (compatible with VLC Media Player) from any directory (and its subdirectories) containing video files, **preserving** the folder structure in the playlist.

---

## How It Works

### Video Detection
The tool scans the target folder (and subfolders) for video files (`.mp4`, `.mkv`, `.avi`, `.mov`, `.wmv`, `.flv`, `.mpeg`, `.mpg`).

### Duration Extraction
Each video’s duration is retrieved using **ffprobe**.

### Playlist Generation
The resulting **`.xspf`** file preserves the same folder structure, displayed as hierarchical nodes in VLC.

---

## Using the Portable Executable

### Download the .exe
Go to the **Releases page** (replace with your actual release link) and download **`XSPF_Creator.exe`** (or similarly named file).

### Run It
Double-click the `.exe` or open it via Command Prompt/PowerShell.

### Choose the Folder
When prompted, you can **type a folder path** to scan (e.g., `D:\Videos`) or simply **press Enter** to use your **current folder**.

### Playlist Output
A file named **`Playlist.xspf`** is created in the same folder where you run the executable.

> **Note:** This executable already includes `ffprobe.exe`, so there is **no need** to install anything else.

---

## Example Usage

When asked for the folder path:
- **Press Enter** without typing anything to use the current directory, or
- **Specify a path** like `I:\MyVideos`.
The playlist file (**`Playlist.xspf`**) will be generated in that directory.

---

## Common Issues

### Empty Playlist
If there are no recognized video files, the playlist will be empty.

### VLC Cannot Find Files
If you move or rename videos after the playlist is created, VLC will not be able to locate them unless you regenerate the playlist.

---
**Developed by [SergioGBRox](https://github.com/SergioGBRox).**
Contributions are welcome!