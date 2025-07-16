import os
import json
import subprocess
import sys
import logging
import tkinter as tk
from tkinter import filedialog

# Import winreg for Windows-specific PATH modification
if sys.platform == "win32":
    try:
        import winreg
    except ImportError:
        winreg = None
        logging.warning("winreg module not found. PATH modification feature will be limited.")
else:
    winreg = None # Not applicable for other OS

# --- Configuration for Data and Log Files ---
def get_app_data_path():
    """Returns the appropriate application data directory based on OS."""
    if sys.platform == "win32":
        # On Windows, use APPDATA for user-specific data
        return os.path.join(os.environ.get('LOCALAPPDATA') or os.environ.get('APPDATA'), 'UrunLauncher')
    elif sys.platform == "darwin":
        # On macOS, use Application Support
        return os.path.join(os.path.expanduser('~'), 'Library', 'Application Support', 'UrunLauncher')
    else:
        # On Linux/Unix, use .local/share
        return os.path.join(os.path.expanduser('~'), '.local', 'share', 'UrunLauncher')

APP_DATA_DIR = get_app_data_path()
os.makedirs(APP_DATA_DIR, exist_ok=True) # Ensure the directory exists

DATA_FILE = os.path.join(APP_DATA_DIR, 'launcher_data.json')
LOG_FILE = os.path.join(APP_DATA_DIR, 'launcher.log')

# --- Logging Setup ---
# Get the root logger
logger = logging.getLogger()
logger.setLevel(logging.INFO) # Set the default level for the logger

# Prevent adding duplicate handlers if the script is run multiple times
if not logger.handlers:
    # File handler for detailed logs
    file_handler = logging.FileHandler(LOG_FILE, mode='a')
    file_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
    logger.addHandler(file_handler)

    # Console handler for user-facing messages
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO) # Show INFO, WARNING, ERROR on console
    console_handler.setFormatter(logging.Formatter('%(message)s')) # Only show message on console
    logger.addHandler(console_handler)

# --- Core Functions ---
def load_executables():
    """Loads the executable mapping from the data file."""
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, 'r') as f:
                executables = json.load(f)
                logging.debug(f"Loaded {len(executables)} executables from '{DATA_FILE}'.")
                return executables
        except json.JSONDecodeError:
            logging.warning(f"Warning: {DATA_FILE} is corrupted. Starting with an empty list.")
            logging.error(f"JSONDecodeError: {DATA_FILE} is corrupted.", exc_info=True)
            return {}
        except Exception as e:
            logging.error(f"Error loading data from {DATA_FILE}: {e}", exc_info=True)
            return {}
    logging.debug(f"No existing data file found at '{DATA_FILE}'. Starting fresh.")
    return {}

def save_executables(executables):
    """Saves the current executable mapping to the data file."""
    try:
        with open(DATA_FILE, 'w') as f:
            json.dump(executables, f, indent=4)
        logging.debug(f"Executables saved to '{DATA_FILE}'.")
    except IOError as e:
        logging.error(f"Error: Could not save data to {DATA_FILE}. Reason: {e}", exc_info=True)
    except Exception as e:
        logging.error(f"An unexpected error occurred while saving data: {e}", exc_info=True)

def add_entry(executables, alias, path, entry_type="file"):
    """
    Adds a new entry (file or folder) to the mapping or updates an existing one.
    Validates path based on entry_type.
    """
    if not os.path.exists(path):
        logging.error(f"Error: The path '{path}' does not exist. Please provide a valid path.")
        return False

    if entry_type == "file":
        if not os.path.isfile(path):
            logging.error(f"Error: The path '{path}' is not a file. Please provide the path to a file.")
            return False
        # General warning for non-typical executable extensions
        if not path.lower().endswith(('.exe', '.bat', '.cmd', '.ps1')):
            logging.warning(f"Warning: The file '{path}' does not have a common executable extension (.exe, .bat, etc.). Ensure it's launchable.")
    elif entry_type == "folder":
        if not os.path.isdir(path):
            logging.error(f"Error: The path '{path}' is not a directory. Please provide the path to a folder.")
            return False
    else:
        logging.error(f"Invalid entry type specified: {entry_type}. Must be 'file' or 'folder'.")
        return False

    alias_lower = alias.lower()
    if alias_lower in executables:
        logging.info(f"Alias '{alias}' already exists. Updating path from '{executables[alias_lower]}' to '{path}'.")
    else:
        logging.info(f"Adding new alias '{alias}' with path '{path}'.")

    executables[alias_lower] = path
    save_executables(executables)
    logging.info(f"'{alias}' added/updated successfully as a {entry_type}.")
    return True

def update_entry(executables, alias, new_path):
    """
    Updates the path for an existing alias.
    Determines if it's a file or folder based on the new path.
    """
    alias_lower = alias.lower()
    if alias_lower not in executables:
        logging.error(f"Error: Alias '{alias}' not found. Use 'add' to create a new entry.")
        return False

    if not os.path.exists(new_path):
        logging.error(f"Error: The new path '{new_path}' does not exist. Please provide a valid path.")
        return False

    entry_type = "file"
    if os.path.isfile(new_path):
        # General warning for non-typical executable extensions
        if not new_path.lower().endswith(('.exe', '.bat', '.cmd', '.ps1')):
            logging.warning(f"Warning: The new file '{new_path}' does not have a common executable extension (.exe, .bat, etc.). Ensure it's launchable.")
    elif os.path.isdir(new_path):
        entry_type = "folder"
    else:
        logging.error(f"Error: The new path '{new_path}' is neither a file nor a directory.")
        return False

    old_path = executables[alias_lower]
    executables[alias_lower] = new_path
    save_executables(executables)
    logging.info(f"Path for '{alias}' updated from '{old_path}' to '{new_path}' (type: {entry_type}).")
    return True

def delete_executable(executables, alias):
    """
    Deletes an executable by its alias with confirmation.
    """
    alias_lower = alias.lower()
    if alias_lower not in executables:
        logging.error(f"Error: Alias '{alias}' not found.")
        return False

    confirm = input(f"Are you sure you want to delete '{alias}' (path: {executables[alias_lower]})? (y/n): ").strip().lower()
    if confirm == 'y':
        del executables[alias_lower]
        save_executables(executables)
        logging.info(f"'{alias}' has been successfully removed.")
        return True
    else:
        logging.info(f"Deletion of '{alias}' cancelled.")
        return False

def rename_alias(executables, old_alias, new_alias):
    """
    Renames an existing alias to a new alias.
    """
    old_alias_lower = old_alias.lower()
    new_alias_lower = new_alias.lower()

    if old_alias_lower not in executables:
        logging.error(f"Error: Old alias '{old_alias}' not found.")
        return False
    if new_alias_lower in executables:
        logging.error(f"Error: New alias '{new_alias}' already exists. Please choose a different name.")
        return False

    executables[new_alias_lower] = executables.pop(old_alias_lower) # Move the value and delete old key
    save_executables(executables)
    logging.info(f"Alias '{old_alias}' successfully renamed to '{new_alias}'.")
    return True


def list_executables(executables):
    """Lists all registered executables."""
    if not executables:
        logging.info("No entries registered yet. Use 'add <alias> <path>' or 'add_folder <alias> <path>' to add one.")
        return

    logging.info("\n--- Registered Entries ---")
    for alias, path in sorted(executables.items()):
        entry_type = "File"
        if os.path.isdir(path):
            entry_type = "Folder"
        elif not os.path.exists(path):
            entry_type = "MISSING"
        logging.info(f"  {alias:<15} -> {path} ({entry_type})")
    logging.info("----------------------------\n")
    logging.info("Listed all entries.")

def launch_entry(executables, alias):
    """
    Launches an entry (file or folder) by its alias.
    For .exe files, uses subprocess.Popen with shell=False and cwd for better compatibility.
    For other files/folders, uses os.startfile.
    """
    path = executables.get(alias.lower())
    if path:
        if os.path.exists(path):
            try:
                logging.info(f"Launching '{alias}' from '{path}'...")
                if os.path.isfile(path) and path.lower().endswith('.exe'):
                    # Set the working directory to the executable's directory
                    working_dir = os.path.dirname(path)
                    # Use subprocess.Popen without shell=True for cleaner process creation
                    # and explicitly set cwd for games that rely on it.
                    subprocess.Popen([path], cwd=working_dir)
                else:
                    # For other files (media, docs) and folders, os.startfile is generally sufficient.
                    os.startfile(path)
                logging.info(f"'{alias}' launched successfully. You can continue using Urun.")
            except OSError as e:
                logging.error(f"Error launching '{alias}': {e}")
                logging.info("Please ensure the path is correct and you have permission to access it.")
            except Exception as e:
                logging.error(f"An unexpected error occurred while launching '{alias}': {e}", exc_info=True)
        else:
            logging.error(f"Error: Path for '{alias}' ('{path}') no longer exists. Consider updating or removing it.")
    else:
        logging.error(f"Error: Alias '{alias}' not found. Use 'list' to see available entries.")

def search_and_launch(executables, query):
    """
    Searches for entries matching the query.
    If a single match, launches it. If multiple, lists them.
    """
    query_lower = query.lower()
    matches = {alias: path for alias, path in executables.items() if query_lower in alias}

    if not matches:
        logging.info(f"No entries found matching '{query}'.")
    elif len(matches) == 1:
        alias = list(matches.keys())[0]
        launch_entry(executables, alias)
    else:
        logging.info(f"Multiple entries found matching '{query}':")
        for alias, path in sorted(matches.items()):
            entry_type = "File"
            if os.path.isdir(path):
                entry_type = "Folder"
            elif not os.path.exists(path):
                entry_type = "MISSING"
            logging.info(f"  - {alias} ({path}) ({entry_type})")
        logging.info(f"Please be more specific, or type the full alias to launch (e.g., '{list(matches.keys())[0]}').")

def browse_for_file():
    """
    Opens a file dialog to allow the user to select any file.
    Returns the selected file path or an empty string if cancelled.
    """
    # Create a Tkinter root window, but hide it
    root = tk.Tk()
    root.withdraw() # Hide the main window

    # Set the window to be always on top and grab focus
    root.attributes("-topmost", True)
    root.lift()
    root.focus_force()

    file_path = filedialog.askopenfilename(
        title="Select File",
        filetypes=[("All files", "*.*"), ("Executable files", "*.exe")]
    )
    root.destroy() # Destroy the root window after selection
    return file_path

def browse_for_folder():
    """
    Opens a folder dialog to allow the user to select a directory.
    Returns the selected folder path or an empty string if cancelled.
    """
    root = tk.Tk()
    root.withdraw() # Hide the main window

    # Set the window to be always on top and grab focus
    root.attributes("-topmost", True)
    root.lift()
    root.focus_force()

    folder_path = filedialog.askdirectory(
        title="Select Folder"
    )
    root.destroy()
    return folder_path

def clear_screen():
    """Clears the console screen."""
    os.system('cls' if os.name == 'nt' else 'clear')
    logging.info("Screen cleared.")

def display_path_troubleshooting(current_exe_dir):
    """Displays detailed instructions for manually adding Urun to PATH."""
    logging.info("\n--- Urun PATH Setup Guide ---")
    logging.info("It seems Urun's directory is not in your system's PATH, or the automatic setup failed.")
    logging.info("This means Windows cannot find 'urun' when you type it in the Run dialog (Win+R).")
    logging.info("\nTo fix this, please follow these simple steps to add Urun to your PATH manually:")
    logging.info(f"1. Copy the path to Urun's folder: '{current_exe_dir}'")
    logging.info("   (You can copy this exact line and paste it into a text editor if needed.)")
    logging.info("2. Press 'Win + R', type 'sysdm.cpl', and press Enter.")
    logging.info("3. In the 'System Properties' window, go to the 'Advanced' tab.")
    logging.info("4. Click the 'Environment Variables...' button.")
    logging.info("5. Under 'User variables for <Your Username>', find and select 'Path', then click 'Edit...'.")
    logging.info("6. Click 'New' and paste the path you copied in step 1.")
    logging.info("7. Click 'OK' on all open windows to save the changes.")
    logging.info("\nIMPORTANT: After these steps, close ALL open Command Prompt/PowerShell windows and Run dialogs.")
    logging.info("Then, open a NEW Run dialog (Win+R) and try typing 'urun' again.")
    logging.info("---------------------------\n")

def add_current_dir_to_path(executables, silent=False):
    """
    Adds the directory of the running executable to the user's PATH environment variable on Windows.
    Asks for user confirmation if not silent.
    Updates 'path_set_attempted' flag in executables.
    """
    if sys.platform != "win32" or winreg is None:
        if not silent:
            logging.error("This feature is only available on Windows and requires the 'winreg' module.")
        return False

    current_exe_dir = os.path.dirname(os.path.abspath(sys.executable))
    
    # Get current user PATH
    try:
        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, 'Environment', 0, winreg.KEY_ALL_ACCESS)
        current_path, _ = winreg.QueryValueEx(key, 'Path')
        winreg.CloseKey(key)
    except FileNotFoundError:
        current_path = "" # Path variable doesn't exist for user, create it
    except Exception as e:
        logging.error(f"Error reading current user PATH: {e}", exc_info=True)
        if not silent:
            logging.info("Could not read user PATH. Please try running as administrator if issues persist.")
        return False # Indicate failure

    # Check if directory is already in PATH
    path_components = [p.strip() for p in current_path.split(';') if p.strip()]
    if current_exe_dir in path_components:
        if not silent:
            logging.info(f"'{current_exe_dir}' is already in your user's PATH.")
            logging.info("No action needed. You can launch Urun from anywhere.")
        # Mark as attempted even if already present
        executables['path_set_attempted'] = True
        save_executables(executables)
        return True # Indicate success

    # If not silent, ask for confirmation
    confirm = 'y' # Default to 'y' for silent mode
    if not silent:
        confirm = input(f"Urun can be launched easily from anywhere by adding '{current_exe_dir}' to your user's system PATH. Do you want to do this now? (y/n): ").strip().lower()

    if confirm == 'y':
        new_path = f"{current_path};{current_exe_dir}" if current_path else current_exe_dir
        try:
            key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, 'Environment', 0, winreg.KEY_SET_VALUE)
            winreg.SetValueEx(key, 'Path', 0, winreg.REG_EXPAND_SZ, new_path) # Use REG_EXPAND_SZ for paths
            winreg.CloseKey(key)

            # Inform other processes about the change (optional but good practice)
            try:
                import ctypes
                ctypes.windll.user32.SendMessageTimeoutA(
                    0xFFFF, # HWND_BROADCAST
                    0x001A, # WM_SETTINGCHANGE
                    0,      # wParam
                    "Environment", # lParam (string "Environment")
                    2,      # SMTO_ABORTIFHUNG
                    1000    # timeout (milliseconds)
                )
            except Exception as e:
                logging.warning(f"Could not send WM_SETTINGCHANGE message: {e}")
                logging.warning("Changes might require a system restart or new console session to take full effect.")

            logging.info(f"Successfully added '{current_exe_dir}' to your user's PATH.")
            logging.info("Please open a NEW Command Prompt or Run dialog (Win+R) for changes to take effect.")
            logging.info("Then you can simply type 'urun' to launch it.")
            executables['path_set_attempted'] = True
            save_executables(executables)
            return True # Indicate success
        except Exception as e:
            logging.error(f"Error adding '{current_exe_dir}' to PATH: {e}", exc_info=True)
            logging.info("Failed to modify PATH. Please try running Urun as administrator if this issue persists.")
            # Even if it fails, we mark it as attempted to avoid re-prompting on next launch
            executables['path_set_attempted'] = True
            save_executables(executables)
            return False # Indicate failure
    else:
        logging.info("Adding to PATH cancelled by user.")
        executables['path_set_attempted'] = True # Mark as attempted to avoid re-prompting
        save_executables(executables)
        return False # Indicate cancellation

def display_help():
    """Displays available commands."""
    logging.info("\n--- Urun Commands ---")
    logging.info("  add <alias> <path>      - Add a new file entry (e.g., .exe, .mp4, .pdf).")
    logging.info("                            Example: add mygame C:\\Games\\MyGame.exe")
    logging.info("                            Example: add mydoc C:\\Docs\\Report.pdf")
    logging.info("  browsify <alias>        - Add a new file entry by browsing for the file.")
    logging.info("                            Example: browsify myimage")
    logging.info("  add_folder <alias> <path> - Add a new folder entry.")
    logging.info("                            Example: add_folder mydocs C:\\Users\\Me\\Documents")
    logging.info("  browsefolder <alias>    - Add a new folder entry by browsing for the folder.")
    logging.info("                            Example: browsefolder myphotos")
    logging.info("  update <alias> <new_path> - Update the path for an existing entry.")
    logging.info("                            Example: update mygame D:\\NewGames\\MyGame.exe")
    logging.info("  delete <alias>          - Remove an existing entry alias (requires confirmation).")
    logging.info("                            Example: delete mygame")
    logging.info("  rename <old_alias> <new_alias> - Rename an existing alias.")
    logging.info("                            Example: rename mygame myfavoritegame")
    logging.info("  list                    - List all registered entries.")
    # Removed "openfolder" from help
    logging.info("  setpath                 - Manually add Urun to your user's system PATH for easy launching.")
    logging.info("  <alias>                 - Launch an entry by its alias.")
    logging.info("                            Example: mygame (launches the executable)")
    logging.info("                            Example: mydocs (opens the folder)")
    logging.info("                            Example: myvideo (opens the video with default player)")
    logging.info("  <partial_alias>         - Search for entries matching the partial alias.")
    logging.info("  clear                   - Clear the console screen.")
    logging.info("  help                    - Display this help message.")
    logging.info("  exit / quit             - Exit the launcher.")
    logging.info("---------------------------\n")

def main():
    """Main function for the CLI launcher."""
    executables = load_executables()
    logging.info("Welcome to Urun - Your Custom Launcher!")

    # --- Automated PATH setup check ---
    if sys.platform == "win32" and winreg is not None:
        current_exe_dir = os.path.dirname(os.path.abspath(sys.executable))
        path_set_attempted = executables.get('path_set_attempted', False)
        
        # Check if current_exe_dir is actually in the current effective PATH
        # os.environ.get('PATH') gives the current process's PATH
        is_in_current_path = current_exe_dir in os.environ.get('PATH', '').split(os.pathsep)

        if not is_in_current_path:
            if not path_set_attempted:
                # First time Urun is run and not in PATH, or previous attempt wasn't marked
                logging.info(f"\nUrun's directory is not currently in your system PATH.")
                # Call add_current_dir_to_path, which will prompt the user and handle saving the flag
                add_current_dir_to_path(executables, silent=False)
            else:
                # PATH setup was attempted/declined before, and it's still not in PATH
                # Provide manual troubleshooting steps
                display_path_troubleshooting(current_exe_dir)
        else:
            # If it's in PATH, ensure the 'path_set_attempted' flag is set for future launches
            if not path_set_attempted:
                executables['path_set_attempted'] = True
                save_executables(executables)
            logging.info(f"Urun's directory '{current_exe_dir}' is already in your PATH.")
    # --- End Automated PATH setup check ---

    display_help()

    while True:
        try:
            command = input("Urun> ").strip()
            if not command:
                continue

            parts = command.split(maxsplit=2) # Split into command, alias, and path (if exists)
            action = parts[0].lower()

            if action == 'exit' or action == 'quit':
                logging.info("Exiting Urun. Goodbye!")
                break
            elif action == 'add':
                if len(parts) == 3:
                    alias = parts[1]
                    path = parts[2].strip('"').strip("'") # Remove potential quotes from path
                    add_entry(executables, alias, path, entry_type="file")
                else:
                    logging.info("Usage: add <alias> <path_to_file>")
                    logging.info("Example: add mygame C:\\Games\\MyGame.exe")
            elif action == 'browsify': # Renamed from add_browse
                if len(parts) == 2:
                    alias = parts[1]
                    logging.info(f"Please select the file for alias '{alias}' in the pop-up window...")
                    selected_path = browse_for_file()
                    if selected_path:
                        add_entry(executables, alias, selected_path, entry_type="file")
                    else:
                        logging.info("File selection cancelled.")
                else:
                    logging.info("Usage: browsify <alias>")
                    logging.info("Example: browsify myimage")
            elif action == 'add_folder':
                if len(parts) == 3:
                    alias = parts[1]
                    path = parts[2].strip('"').strip("'")
                    add_entry(executables, alias, path, entry_type="folder")
                else:
                    logging.info("Usage: add_folder <alias> <path_to_folder>")
                    logging.info("Example: add_folder mydocs C:\\Users\\Me\\Documents")
            elif action == 'browsefolder': # Renamed from add_folder_browse
                if len(parts) == 2:
                    alias = parts[1]
                    logging.info(f"Please select the folder for alias '{alias}' in the pop-up window...")
                    selected_path = browse_for_folder()
                    if selected_path:
                        add_entry(executables, alias, selected_path, entry_type="folder")
                    else:
                        logging.info("Folder selection cancelled.")
                else:
                    logging.info("Usage: browsefolder <alias>")
                    logging.info("Example: browsefolder myphotos")
            elif action == 'update':
                if len(parts) == 3:
                    alias = parts[1]
                    new_path = parts[2].strip('"').strip("'")
                    update_entry(executables, alias, new_path)
                else:
                    logging.info("Usage: update <alias> <new_path>")
                    logging.info("Example: update mygame D:\\NewGames\\MyGame.exe")
            elif action == 'delete':
                if len(parts) == 2:
                    alias = parts[1]
                    delete_executable(executables, alias)
                else:
                    logging.info("Usage: delete <alias>")
                    logging.info("Example: delete mygame")
            elif action == 'rename':
                if len(parts) == 3:
                    old_alias = parts[1]
                    new_alias = parts[2]
                    rename_alias(executables, old_alias, new_alias)
                else:
                    logging.info("Usage: rename <old_alias> <new_alias>")
                    logging.info("Example: rename nfs nfs_shift")
            elif action == 'list':
                list_executables(executables)
            # Removed the openfolder command block
            elif action == 'setpath':
                # Manual setpath call
                add_current_dir_to_path(executables, silent=False)
            elif action == 'clear':
                clear_screen()
            elif action == 'help':
                display_help()
            else:
                # Assume it's an alias or a search query to launch
                search_and_launch(executables, command)
        except KeyboardInterrupt:
            logging.info("\nExiting Urun. Goodbye!")
            break
        except Exception as e:
            logging.error(f"An unexpected error occurred: {e}")
            logging.info("Please try again or restart Urun.")
            logging.critical(f"Unhandled exception in main loop: {e}", exc_info=True)

if __name__ == "__main__":
    # Check if running on Windows, as os.startfile is Windows-specific
    if sys.platform != "win32":
        logging.warning("Warning: Urun uses 'os.startfile' which is primarily for Windows.")
        logging.warning("It might not function as expected on other operating systems for launching files/folders.")
        logging.warning("Consider using 'subprocess.Popen' with platform-specific commands for cross-platform compatibility if needed.")
    main()
