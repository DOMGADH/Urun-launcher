# Urun-launcher

A minimalist, open-source CLI launcher for Windows (and soon Linux!) that lets you define custom aliases to instantly launch any application, game, or file type.

---

## ✨ Why Urun-launcher?

Are you tired of cluttered desktops, slow-loading game launchers, or constantly navigating through folders to find that one specific file or application? Urun-launcher is designed to solve exactly that.

It provides a blazing-fast, command-line interface to access everything you need. It gets out of your way and dedicates your system's resources to what truly matters – your applications and games.

## 🚀 Features

* **Instant Launching:** Define simple, memorable aliases for any application (`.exe`), game, document (PDFs, Word docs), media file, or even specific folders. Just type `urun <alias>` and hit Enter!
* **Feather-light:** Urun-launcher is incredibly resource-efficient, consuming only ~24MB RAM during its brief execution and then exiting completely, ensuring zero ongoing overhead.
* **Universal Compatibility:** Launch virtually anything on your system, regardless of its type or location.
* **User-Friendly Setup:** Includes an automated Windows PATH integration command (`urun setpath`) for hassle-free installation and instant access from `Win + R` or any terminal.
* **Customizable:** All aliases are managed via a straightforward configuration file, allowing for easy viewing and direct editing for advanced users.
* **Open Source:** Built with transparency in mind, inviting community feedback and contributions.

## 📦 Installation (Windows)

Urun-launcher is designed for a quick and easy setup.

### For End-Users (Recommended - using pre-built executable)

1.  **Download Urun:** Download the latest `urun.exe` file from the [Releases page](https://github.com/DOMGADH/Urun-launcher/releases).
2.  **Place Urun.exe:** Create a new folder on your system (e.g., `C:\Urun`) and place the downloaded `urun.exe` inside it.
3.  **Add to PATH:** Open **Command Prompt** or **PowerShell** (you can use `Win + R`, type `cmd` or `powershell`, and press Enter).
    Navigate to the directory where you placed `urun.exe`:
    ```bash
    cd C:\Urun
    ```
    Then, run the setup command:
    ```bash
    urun setpath
    ```
    This command will automatically add `C:\Urun` (or your chosen path) to your system's environment variables, allowing you to run `urun` from anywhere.
4.  **Restart Terminal/System:** For the PATH changes to take full effect, it's recommended to restart any open Command Prompt/PowerShell windows, or even your system.

### For Developers / Running from Source

1.  **Prerequisites:**
    * [Python 3.8+](https://www.python.org/downloads/)
    * `pip` (usually comes with Python)
2.  **Clone the Repository:**
    ```bash
    git clone [https://github.com/DOMGADH/Urun-launcher.git](https://github.com/DOMGADH/Urun-launcher.git)
    ```
3.  **Navigate to Directory:**
    ```bash
    cd Urun-launcher
    ```
4.  **Install Dependencies:**
    ```bash
    pip install -r requirements.txt
    ```
5.  **Run from Source:** You can now run Urun directly using:
    ```bash
    python urun.py [command]
    ```

## 💡 Usage

Urun-launcher is controlled entirely via simple commands.

### Launching an Item

To launch an aliased item, simply type `urun` followed by your alias name:

```bash
urun <your_alias_name>
````

**Examples:**

  * Launch VLC media player:
    ```bash
    urun vlc
    ```
  * Launch your favorite game:
    ```bash
    urun cyberpunk
    ```
  * Open a specific project folder:
    ```bash
    urun mydevproject
    ```
  * Open a PDF document:
    ```bash
    urun thesis
    ```

### Managing Aliases

Urun provides commands to easily manage your custom aliases.

  * **`urun add <alias_name>`**
    Adds a new alias. You will be prompted to enter the full path to the executable, file, or folder.

      * **Using Browse Dialogs:** When prompted for a path, you can type `browsify` to open a file selection dialog or `browsefolder` to open a folder selection dialog, making it easy to pick paths graphically.

    <!-- end list -->

    ```bash
    # Example to add a game alias
    urun add mygame
    # Follow prompts for path (e.g., C:\Games\MyGame\game.exe) and working directory (optional)
    ```

  * **`urun list`**
    Displays all your currently configured aliases and their associated paths.

    ```bash
    urun list
    ```

  * **`urun remove <alias_name>`**
    Deletes an existing alias.

    ```bash
    urun remove mygame
    ```

  * **`urun help`**
    Shows a list of available commands and their usage.

    ```bash
    urun help
    ```

## ⚙️ Configuration

Urun stores its aliases in a simple Python dictionary within a `config.py` file. This file is automatically created inside an `urun_data` folder (located in your user's home directory, e.g., `C:\Users\YourUser\urun_data\config.py`).

For advanced users, you can directly edit this `config.py` file to quickly manage many aliases at once.

## 🛠️ Building the Executable

If you're running from source and wish to compile your own standalone `urun.exe`:

1.  **Install PyInstaller:**
    ```bash
    pip install pyinstaller
    ```
2.  **Navigate to Project Root:**
    Change your directory to the `Urun-launcher` folder where `urun.py` is located.
3.  **Run PyInstaller:**
    ```bash
    pyinstaller --onefile --name urun urun.py
    ```
    The compiled executable will be found in the newly created `dist` folder.

## 🚧 Known Issues / Future Enhancements

We are continuously working to improve Urun-launcher. Here are some points we are aware of or planning:

### Known Issues:

  * **Tkinter File/Folder Dialog Blurriness on High-DPI Displays (Windows):** Users on high-resolution monitors might experience the file/folder selection pop-up windows (`browsify`, `browsefolder`) appearing slightly blurry. This is a known limitation with Tkinter's default DPI scaling on Windows. A fix is planned for a future update if significant user feedback indicates it's a major pain point.

### Future Enhancements:

  * **Linux Compatibility:** Full support for Linux environments using platform-appropriate commands (e.g., `xdg-open` for launching files/folders).
  * **Enhanced Error Handling:** More robust error messages and graceful handling of edge cases (e.g., invalid paths, missing files).
  * **Advanced Alias Options:** Considering features like alias grouping or more complex argument passing.

## 👋 Contributing

Contributions are what make the open-source community such an amazing place to learn, inspire, and create. Any contributions you make are **greatly appreciated**.

If you have a suggestion that would make Urun better, please fork the repo and create a pull request. You can also simply open an issue with the tag "enhancement."

1.  Fork the Project
2.  Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
3.  Commit your Changes (`git commit -m 'Add some AmazingFeature'`)
4.  Push to the Branch (`git push origin feature/AmazingFeature`)
5.  Open a Pull Request

## 📄 License

Distributed under the MIT License. See `LICENSE` for more information.

```
```
