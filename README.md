# Asynced_AlbotKeinstein
 Asynio used to make this bot

## Installation (Windows)

Albot runs on **Windows 10/11** with these versions:

| Tool | Version | Download |
|---|---|---|
| Python | **3.11.9** (must be 3.11) | https://www.python.org/downloads/release/python-3119/ |
| uv | **0.11.14** | https://docs.astral.sh/uv/getting-started/installation/ |

All other packages and their versions are listed in `requirements.txt` and installed in step 5.

### 1. Install Python 3.11.9
1. Open https://www.python.org/downloads/release/python-3119/
2. Scroll down to **Files** and download **Windows installer (64-bit)**.
3. Run the installer. On the first screen, tick **"Add python.exe to PATH"**, then click **Install Now**.
4. Check it in a new PowerShell window:
   ```powershell
   py -3.11 --version
   ```
   It should say `Python 3.11.9`.

### 2. Install uv 0.11.14
1. Open PowerShell and run:
   ```powershell
   powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/0.11.14/install.ps1 | iex"
   ```
2. Close PowerShell and open a new one, then check:
   ```powershell
   uv --version
   ```
   It should say `uv 0.11.14`.

### 3. Get the code
Either clone it with git:
```powershell
git clone https://github.com/GlenRoger/Asynced_AlbotKeinstein.git
cd Asynced_AlbotKeinstein
```
or download it from GitHub (**Code → Download ZIP**), unzip it and open PowerShell in the folder.

> Tip: keep the folder path short (e.g. `C:\Albot`). Some packages have very long file
> names, and Windows can fail to install them in deep folders.

### 4. Create the virtual environment
In the project folder:
```powershell
uv venv --python 3.11 .venv
```

### 5. Activate it and install the packages
```powershell
.venv\Scripts\activate
uv pip install -r requirements.txt
```
The first install is large (about 700 MB on disk, mostly PySide6), so give it a few minutes.

> If activation fails with *"running scripts is disabled on this system"*, run this once and try again:
> ```powershell
> Set-ExecutionPolicy -Scope CurrentUser RemoteSigned
> ```

### 6. Create the database folder
The database file is created automatically, but the folder must exist:
```powershell
mkdir databases
```

### 7. Tokens
Albot needs its Twitch tokens and API key before it can start. *(Described separately.)*

### 8. Start Albot
With the virtual environment active (step 5):
```powershell
python dashboard.py
```
Click **Start Albot** in the dashboard. The bot opens in its own window, and the button turns
into **Stop Albot** when it's running.

## Starting Albot again later
Each time, open PowerShell in the project folder and run:
```powershell
.venv\Scripts\activate
python dashboard.py
```
If you forget to activate the virtual environment, the dashboard stops with a message telling you to do it.
