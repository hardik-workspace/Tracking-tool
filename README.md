# Activity Tracking Tool - Complete Guide

A lightweight, production-quality Windows desktop productivity tracking tool built with Python. Tracks user activity, idle time, system lock/unlock events, and provides popup notifications for activity reasons.

## 🎯 Features

✅ **Background Activity Tracking** - Runs silently in the background
✅ **Keyboard & Mouse Detection** - Detects user activity automatically
✅ **Idle Time Tracking** - Monitors inactivity periods (configurable)
✅ **System Lock/Unlock Detection** - Detects Windows lock/unlock events
✅ **Popup Notifications** - Shows reason dialogs for inactivity
✅ **SQLite Database** - Stores all tracking data efficiently
✅ **Auto-start Support** - Optional startup with Windows
✅ **Lightweight** - Uses Tkinter for minimal overhead
✅ **Error Resilient** - Proper exception handling throughout
✅ **Modular Design** - Clean code structure with separate modules

## 📋 System Requirements

- **OS**: Windows 10/11
- **Python**: 3.8 or higher
- **RAM**: 50-100MB
- **Admin Rights**: Required for system event monitoring

## 📦 Installation

### Step 1: Clone or Download the Repository

```bash
cd Tracking-tool
```

### Step 2: Create Virtual Environment (Optional but Recommended)

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Or if using conda
conda create -n tracker python=3.10
conda activate tracker
```

### Step 3: Install Required Dependencies

```bash
pip install -r requirements.txt
```

If you encounter issues with `pywin32`, run this after installation:

```bash
python -m pip install --upgrade pywin32
python -m PyInstaller.hooks.hookutils
```

### Step 4: Verify Installation

```bash
python -c "import pynput; import pywin32; print('All dependencies installed!')"
```

## 🚀 Running the Application

### Interactive Mode (With Status Window)

```bash
python main.py --interactive
```

or

```bash
python main.py -i
```

This shows a status window where you can:
- See current activity status (Active/Idle)
- View today's statistics
- Minimize or exit the application

### Background Mode (Quiet Mode)

```bash
python main.py
```

The application runs in the background without any visible window.

### Enable Auto-Start

```bash
python main.py --autostart
```

This adds the application to Windows startup registry.

### Disable Auto-Start

```bash
python main.py --no-autostart
```

## ⚙️ Configuration

The application creates a `config.json` file on first run with these settings:

```json
{
    "idle_timeout": 5,
    "check_interval": 2,
    "auto_start": false,
    "system_tray": true,
    "db_path": "tracking_data.db",
    "log_path": "app_logs.txt",
    "show_notifications": true
}
```

### Configuration Options

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `idle_timeout` | int | 5 | Minutes of inactivity before marking as idle |
| `check_interval` | int | 2 | Seconds between activity checks |
| `auto_start` | bool | false | Start on Windows startup |
| `system_tray` | bool | true | Show system tray icon |
| `db_path` | str | tracking_data.db | Database file location |
| `log_path` | str | app_logs.txt | Application log file |
| `show_notifications` | bool | true | Show desktop notifications |

**To modify**: Edit `config.json` directly and restart the application.

## 📊 Data Storage

### Database Schema

The application uses SQLite with three main tables:

#### activity_logs
```
id, start_time, end_time, duration_minutes, activity_type, reason, application_name, date, created_at
```

#### idle_sessions
```
id, idle_start, idle_end, duration_minutes, reason, date, created_at
```

#### system_events
```
id, event_type, timestamp, details, date, created_at
```

### Accessing Data

You can query the database using:

```bash
sqlite3 tracking_data.db "SELECT * FROM activity_logs;"
```

Or use Python:

```python
import sqlite3
conn = sqlite3.connect('tracking_data.db')
cursor = conn.cursor()
cursor.execute("SELECT * FROM activity_logs ORDER BY start_time DESC LIMIT 10")
for row in cursor.fetchall():
    print(row)
conn.close()
```

## 📋 How It Works

### Flow Diagram

```
┌─────────────────────────────────────────┐
│   Application Start                     │
└──────────────┬──────────────────────────┘
               │
       ┌───────┴────────┐
       │                │
       ▼                ▼
┌──────────────┐  ┌──────────────────┐
│Activity      │  │System Event      │
│Tracker       │  │Monitor           │
│(Keyboard/    │  │(Lock/Unlock)     │
│ Mouse)       │  │                  │
└──────┬───────┘  └────────┬─────────┘
       │                   │
       ├───────┬───────────┤
       │       │           │
       ▼       ▼           ▼
   IDLE_START  ACTIVITY_RESUMED  SYSTEM_UNLOCKED
       │            │                  │
       └────────┬───┴──────────────┬───┘
                │                  │
                ▼                  ▼
           ┌─────────────────────────┐
           │  Show Popup Dialog      │
           │  (Reason for inactivity)│
           └────────┬────────────────┘
                    │
          ┌─────────┴─────────┐
          │                   │
          ▼                   ▼
     User Submits         Timeout
          │                   │
          └─────────┬─────────┘
                    │
                    ▼
         ┌──────────────────┐
         │  Log to Database │
         └──────────────────┘
```

### Workflow Steps

1. **Initialization**: App loads config, initializes database
2. **Activity Tracking**: Monitors keyboard/mouse in real-time
3. **Idle Detection**: When no activity for X minutes, marks as idle
4. **Popup Trigger**: Shows popup asking for inactivity reason
5. **User Input**: User selects reason or it times out (10 min)
6. **Data Logging**: Stores activity with reason in SQLite database
7. **Continue Loop**: Resumes monitoring until app stops

## 🎨 Popup Dialog

When idle or system unlock is detected, a popup appears:

```
┌─────────────────────────────────┐
│   Activity Tracker              │
├─────────────────────────────────┤
│                                 │
│  Please select reason for       │
│  inactivity:                    │
│                                 │
│  [Break                      ▼] │
│                                 │
│  Additional details (if Others):│
│  ┌──────────────────────────┐   │
│  │                          │   │
│  │                          │   │
│  └──────────────────────────┘   │
│                                 │
│  [ Submit ]  [ Cancel ]         │
│                                 │
└─────────────────────────────────┘
```

### Reason Options

- **Break** - Taking a break
- **System Issue** - Computer issue or update
- **Internet Issue** - Network connectivity problems
- **Meeting** - In a meeting or call
- **Personal Work** - Personal tasks unrelated to main work
- **Others** - Custom reason with text input

## 🛠️ Module Structure

```
Tracking-tool/
├── main.py              # Entry point & application orchestration
├── tracker.py           # Activity & system event tracking
├── ui.py                # Tkinter UI components (popups, status window)
├── logger.py            # SQLite database operations
├── config.py            # Configuration management
├── utils.py             # Utility functions & logging
├── requirements.txt     # Python dependencies
├── README.md            # This file
├── config.json          # Configuration (auto-generated)
├── tracking_data.db     # SQLite database (auto-generated)
└── app_logs.txt         # Application logs (auto-generated)
```

## 🐛 Error Handling

The application includes comprehensive error handling:

- **Thread Safety**: Database operations use locks
- **Graceful Degradation**: System monitor failures don't crash app
- **Logging**: All errors logged to `app_logs.txt`
- **Recovery**: Auto-recovery from temporary failures

## 📝 Logs

Check `app_logs.txt` for detailed application logs:

```bash
# View recent logs
tail -f app_logs.txt

# Or on Windows
Get-Content app_logs.txt -Tail 20 -Wait
```

## 🔄 Converting to .exe

### Method 1: Using PyInstaller (Recommended)

#### Step 1: Install PyInstaller

```bash
pip install pyinstaller
```

#### Step 2: Create the Executable

```bash
pyinstaller --onefile --windowed --name "ActivityTracker" ^
    --icon=app.ico ^
    --add-data "config.json:." ^
    main.py
```

Or use the provided spec file:

```bash
pyinstaller tracker.spec
```

#### Step 3: Locate the Executable

The `.exe` file will be in:
```
dist/ActivityTracker.exe
```

#### Step 4: Create an Installer (Optional)

Use NSIS or Inno Setup to create an installer.

### Step-by-Step .exe Conversion

```bash
# 1. Install PyInstaller
pip install pyinstaller

# 2. Create a batch file (build.bat)
@echo off
pyinstaller --onefile --windowed ^
    --name "ActivityTracker" ^
    --add-data "requirements.txt:." ^
    main.py
pause

# 3. Run the batch file
build.bat

# 4. The .exe is now in dist/ folder
# dist/ActivityTracker.exe
```

### Running the .exe

```bash
# Run interactively
ActivityTracker.exe --interactive

# Run in background
ActivityTracker.exe

# Enable autostart
ActivityTracker.exe --autostart
```

## 🎓 Learning Points

This project demonstrates:

1. **Threading** - Background monitoring without blocking UI
2. **Event-Driven Programming** - Responding to system events
3. **Database Design** - Normalized SQLite schema
4. **GUI Development** - Tkinter popups and windows
5. **Windows Integration** - Registry access, system events
6. **Error Handling** - Comprehensive try-except patterns
7. **Configuration Management** - JSON-based settings
8. **Logging** - Structured application logging
9. **Process Management** - Managing multiple threads safely
10. **Python Packaging** - Creating distributable executables

## ⚠️ Limitations & Notes

1. **Admin Rights**: System monitor requires admin privileges for full functionality
2. **Active Window Detection**: Currently limited - can be enhanced with additional libraries
3. **Platform Specific**: Built specifically for Windows (uses win32api)
4. **Performance**: Minimal impact on system (~20-50MB RAM)
5. **Privacy**: No screenshots, no spying - pure activity tracking

## 🚀 Future Enhancements

- [ ] Cross-platform support (Linux, macOS)
- [ ] Web-based dashboard for viewing data
- [ ] Real-time analytics and reports
- [ ] Multiple user support
- [ ] Cloud backup option
- [ ] Mobile app for remote monitoring
- [ ] Advanced idle detection (eye tracking)
- [ ] Application usage breakdown

## 📞 Troubleshooting

### Issue: "pynput not found"
```bash
pip install pynput --upgrade
```

### Issue: "pywin32 not working"
```bash
pip install --upgrade pywin32
python -m PyInstaller.hooks.hookutils
```

### Issue: Popup not showing
- Ensure `tkinter` is installed: `pip install tk`
- Check `app_logs.txt` for errors
- Try interactive mode: `python main.py --interactive`

### Issue: Database locked
- Close all instances of the application
- Delete `tracking_data.db` and restart (data will be reset)

### Issue: Not detecting activity
- Ensure the app has keyboard/mouse permissions
- Check if running in a sandboxed environment
- Verify config idle timeout value

## 📄 License

This project is for educational and personal use only.

## 🤝 Contributing

Feel free to modify and extend this project for your needs!

## ✅ Testing Checklist

Before deploying, verify:

- [ ] Activity detection working (move mouse/type)
- [ ] Idle detection triggers after configured time
- [ ] Popup appears and accepts input
- [ ] Data saved to database
- [ ] No memory leaks after long running
- [ ] Logs generated properly
- [ ] Config file creates on startup
- [ ] Exit and restart works cleanly

## 📚 Additional Resources

- [pynput Documentation](https://pynput.readthedocs.io/)
- [pywin32 Documentation](https://github.com/pywin32)
- [SQLite Documentation](https://www.sqlite.org/docs.html)
- [Tkinter Tutorial](https://docs.python.org/3/library/tkinter.html)
- [PyInstaller Guide](https://pyinstaller.org/en/stable/)

## ✨ Quick Start Summary

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Run in interactive mode
python main.py --interactive

# 3. Enable autostart (optional)
python main.py --autostart

# 4. View data
sqlite3 tracking_data.db "SELECT * FROM idle_sessions;"

# 5. Build .exe
pip install pyinstaller
pyinstaller --onefile --windowed main.py
```

---

**Version**: 1.0.0  
**Last Updated**: 2024  
**Status**: Production Ready ✅