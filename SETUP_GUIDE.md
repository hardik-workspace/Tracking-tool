# SETUP & INSTALLATION GUIDE

Complete step-by-step guide for setting up and running the Activity Tracking Tool.

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Installation Steps](#installation-steps)
3. [Running the Application](#running-the-application)
4. [Building an Executable](#building-an-executable)
5. [Troubleshooting](#troubleshooting)

## Prerequisites

- **Windows 10/11** (Windows-specific, uses win32api)
- **Python 3.8 or higher** (Download from [python.org](https://www.python.org/downloads/))
- **Administrator privileges** (for system monitoring)
- **Git** (optional, for cloning the repository)

### Verify Python Installation

Open Command Prompt and run:

```bash
python --version
pip --version
```

Both should show version numbers.

## Installation Steps

### Step 1: Download the Project

**Option A - Using Git:**
```bash
git clone <repository-url>
cd Tracking-tool
```

**Option B - Manual Download:**
1. Download as ZIP from GitHub
2. Extract to a folder (e.g., `C:\Users\YourName\Tracking-tool`)
3. Open Command Prompt and navigate to the folder

### Step 2: Create Virtual Environment (Recommended)

Navigate to the project folder and create a virtual environment:

```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate

# You should see (venv) at the beginning of your command prompt
```

**Benefits of virtual environment:**
- Isolates project dependencies
- Prevents conflicts with other Python projects
- Easier to manage versions

### Step 3: Install Dependencies

```bash
# Install all required packages
pip install -r requirements.txt
```

This installs:
- `pynput` - Mouse and keyboard tracking
- `pywin32` - Windows system integration
- `psutil` - System utilities
- `pystray` - System tray icon
- `Pillow` - Image processing

### Step 4: Verify Installation

Run the setup script:

```bash
python setup.py
```

Or run the test suite:

```bash
python test_app.py
```

You should see all components marked as ✓ (passed).

### Common Installation Issues

#### Issue: "Python not found"
- Python is not installed or not in PATH
- Solution: Download from [python.org](https://www.python.org/downloads/)

#### Issue: "pip: command not found"
- pip wasn't installed with Python
- Solution: Re-run Python installer and check "pip" option

#### Issue: "Permission denied"
- Running without administrator privileges
- Solution: Right-click Command Prompt > "Run as administrator"

#### Issue: "pywin32 error"
- Post-install configuration needed
- Solution: Run `python -m pip install --upgrade pywin32`

## Running the Application

### Interactive Mode (with UI)

```bash
python main.py --interactive
```

or

```bash
python main.py -i
```

**What you'll see:**
- Small status window
- Current activity status (Active/Idle)
- Today's statistics
- Controls to minimize or exit

**How to test:**
1. Move your mouse or type on keyboard
2. Keep activity for a moment
3. Stop all activity for the configured idle time (default 5 min)
4. A popup should appear asking for the reason

### Background Mode (no UI)

```bash
python main.py
```

- Runs silently in background
- Still detects activity and shows popups
- No visible window (except popups)
- Use Ctrl+C in Command Prompt to stop

### Enable Auto-Start

```bash
python main.py --autostart
```

The application will:
- Add itself to Windows startup registry
- Automatically launch when Windows starts
- Run in background mode

### Disable Auto-Start

```bash
python main.py --no-autostart
```

### View Application Logs

```bash
# Real-time logs (Windows PowerShell)
Get-Content app_logs.txt -Wait -Tail 10

# Or on Command Prompt
type app_logs.txt

# View last 50 lines
more +50 app_logs.txt
```

## Building an Executable

Convert your Python scripts to a standalone `.exe` file.

### Method 1: Using Build Script (Easiest)

```bash
# Double-click build.bat
# Or run from Command Prompt
build.bat
```

The script will:
1. Check for PyInstaller
2. Verify dependencies
3. Build the executable
4. Place it in `dist\ActivityTracker.exe`

### Method 2: Using PyInstaller Directly

```bash
# Install PyInstaller
pip install pyinstaller

# Build the executable
pyinstaller --onefile --windowed ^
    --name "ActivityTracker" ^
    main.py

# The .exe will be in dist\ folder
```

### Method 3: Using Spec File

```bash
# Build using pre-configured spec file
pyinstaller tracker.spec

# The .exe will be in dist\ folder
```

### Running the Executable

After building:

```bash
# Interactive mode
dist\ActivityTracker.exe --interactive

# Background mode
dist\ActivityTracker.exe

# Enable auto-start
dist\ActivityTracker.exe --autostart
```

**Advantages of .exe:**
- No Python installation needed
- Portable (run from USB drive)
- Can be distributed to others
- Can be added to Start Menu

### Customizing the Build

To add a custom icon or other options:

```bash
# Create icon (convert PNG to ICO)
# Then run:
pyinstaller --onefile --windowed ^
    --name "ActivityTracker" ^
    --icon "path/to/icon.ico" ^
    main.py
```

## Configuration

### Edit Configuration File

The app creates `config.json` on first run. Edit it to customize:

```json
{
    "idle_timeout": 5,          // Minutes before marking as idle
    "check_interval": 2,        // Seconds between activity checks
    "auto_start": false,        // Start with Windows
    "system_tray": true,        // Show system tray icon
    "db_path": "tracking_data.db",
    "log_path": "app_logs.txt",
    "show_notifications": true
}
```

### Common Configuration Changes

**Make idle detection faster (2 minutes instead of 5):**
```json
"idle_timeout": 2
```

**Less frequent activity checks (5 seconds):**
```json
"check_interval": 5
```

**Store database in custom location:**
```json
"db_path": "C:\\Users\\YourName\\Documents\\tracking.db"
```

## Database Access

### Viewing Data with SQLite

Download SQLite DB Browser: [sqlitebrowser.org](https://sqlitebrowser.org/)

Or use command line:

```bash
# List all activities
sqlite3 tracking_data.db "SELECT * FROM activity_logs;"

# List all idle sessions
sqlite3 tracking_data.db "SELECT * FROM idle_sessions;"

# Count today's activities
sqlite3 tracking_data.db "SELECT COUNT(*) FROM activity_logs WHERE date=date('now');"

# Export to CSV
sqlite3 tracking_data.db ".mode csv" ".output activities.csv" "SELECT * FROM activity_logs;"
```

### Query Examples

```sql
-- Total idle time today
SELECT SUM(duration_minutes) as total_idle FROM idle_sessions 
WHERE date = date('now');

-- Idle sessions with reasons
SELECT idle_start, duration_minutes, reason FROM idle_sessions 
WHERE date = date('now') ORDER BY idle_start DESC;

-- Activities from last 7 days
SELECT * FROM activity_logs 
WHERE date >= date('now', '-7 days') ORDER BY start_time DESC;

-- Most common idle reasons
SELECT reason, COUNT(*) as count FROM idle_sessions 
GROUP BY reason ORDER BY count DESC;
```

## Troubleshooting

### Application Doesn't Start

1. Check Python installation:
   ```bash
   python --version
   ```

2. Verify dependencies:
   ```bash
   python test_app.py
   ```

3. Check logs:
   ```bash
   type app_logs.txt
   ```

### No Activity Detected

**Possible causes:**
- Application running in restricted environment
- Keyboard/mouse permissions not granted
- Idle timeout set too high

**Solutions:**
1. Run as administrator
2. Check firewall/antivirus permissions
3. Lower `idle_timeout` in config.json
4. Restart application

### Popup Not Showing

1. Run in interactive mode to check if Tkinter works:
   ```bash
   python main.py --interactive
   ```

2. Install Tkinter if missing:
   ```bash
   pip install tk
   ```

3. Check logs for errors:
   ```bash
   type app_logs.txt | findstr "ERROR"
   ```

### Database Locked Error

1. Close all instances of the application
2. Delete `tracking_data.db` (will be recreated)
3. Restart the application

### .exe Build Fails

1. Install PyInstaller:
   ```bash
   pip install pyinstaller --upgrade
   ```

2. Delete `build/` and `dist/` folders

3. Try again:
   ```bash
   pyinstaller --onefile --windowed main.py
   ```

### High CPU Usage

1. Increase `check_interval` in config.json:
   ```json
   "check_interval": 5
   ```

2. Restart application

### Not Starting with Windows

1. Run this command:
   ```bash
   python main.py --autostart
   ```

2. Verify registry key (run as admin):
   ```bash
   reg query "HKEY_CURRENT_USER\Software\Microsoft\Windows\CurrentVersion\Run" | findstr ActivityTracker
   ```

## Getting Help

### Check Logs

All errors are logged to `app_logs.txt`:

```bash
# View all errors
findstr "ERROR" app_logs.txt

# View recent activity
more /T /E app_logs.txt
```

### Run Tests

```bash
python test_app.py
```

### Reset Configuration

```bash
# Delete config.json - it will be recreated with defaults
del config.json

# Delete database - activity data will be lost
del tracking_data.db

# Restart application
python main.py --interactive
```

## Next Steps

1. **Run the application:**
   ```bash
   python main.py --interactive
   ```

2. **Test functionality:**
   - Move mouse to test activity detection
   - Wait for idle timeout
   - Submit a reason in popup
   - Check `tracking_data.db` for saved data

3. **Configure settings:**
   - Edit `config.json` as needed
   - Adjust idle timeout
   - Customize paths

4. **Create backup:**
   - Copy `tracking_data.db` regularly
   - Back up configuration

5. **Advanced:**
   - Build executable for portable deployment
   - Create installer using NSIS
   - Schedule automated backups

---

**Version**: 1.0.0  
**Status**: Production Ready ✓

For detailed documentation, see README.md
