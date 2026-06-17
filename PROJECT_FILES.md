# PROJECT STRUCTURE & FILE GUIDE

Complete overview of all files in the Activity Tracking Tool project.

## 📁 File Organization

```
Tracking-tool/
├── Core Application Files
│   ├── main.py                 # Entry point & orchestrator
│   ├── tracker.py              # Activity & system monitoring
│   ├── ui.py                   # GUI components (popups, windows)
│   ├── logger.py               # Database operations
│   ├── config.py               # Configuration management
│   └── utils.py                # Utility functions & logging
│
├── Configuration & Data
│   ├── config.json             # Settings (auto-generated)
│   ├── tracking_data.db        # SQLite database (auto-generated)
│   └── app_logs.txt            # Application logs (auto-generated)
│
├── Build & Setup
│   ├── requirements.txt         # Python dependencies
│   ├── setup.py                # Setup script
│   ├── build.bat               # Windows build script
│   ├── tracker.spec            # PyInstaller configuration
│   └── test_app.py             # Test suite
│
├── Tools & Utilities
│   ├── export_data.py          # Data export & analysis tool
│   └── (future additions)
│
└── Documentation
    ├── README.md               # Main documentation
    ├── SETUP_GUIDE.md          # Installation guide
    ├── ARCHITECTURE.md         # Technical documentation
    ├── PROJECT_FILES.md        # This file
    └── (this folder)
```

## 📄 Core Application Files

### main.py
**Purpose**: Application entry point and orchestrator

**Size**: ~250 lines  
**Language**: Python 3.8+

**Key Components**:
- `TrackingApplication` class - Main orchestrator
- `run_interactive()` - GUI mode
- `run_background()` - Silent mode
- Command-line argument parsing

**Responsibilities**:
- Initialize all components
- Manage thread lifecycle
- Handle events from tracker/monitor
- Show popup dialogs
- Update status display

**Usage**:
```bash
python main.py                    # Background mode
python main.py --interactive      # GUI mode
python main.py --autostart        # Enable startup
python main.py --no-autostart     # Disable startup
```

---

### tracker.py
**Purpose**: Activity and system event monitoring

**Size**: ~350 lines  
**Language**: Python 3.8+

**Key Classes**:
- `ActivityTracker` - Keyboard/mouse monitoring
- `SystemEventMonitor` - System lock/unlock detection

**Key Features**:
- Detects keyboard activity via pynput
- Detects mouse movement via pynput
- Calculates idle duration
- Monitors Windows lock/unlock
- Thread-safe callbacks

**Threading Model**:
- Mouse listener thread
- Keyboard listener thread
- Activity check thread (every 2 seconds)
- System monitor thread (every 2 seconds)

**Usage**:
```python
from tracker import ActivityTracker

tracker = ActivityTracker(callback=on_event)
tracker.start()
# ...
tracker.stop()
```

---

### ui.py
**Purpose**: User interface components

**Size**: ~350 lines  
**Language**: Python 3.8+ with Tkinter

**Key Classes**:
- `InactivityPopup` - Popup for reason input
- `StatusWindow` - Status display window

**UI Components**:
- Dropdown menu (6 predefined reasons)
- Text input for custom reasons
- Submit/Cancel buttons
- Auto-timeout (10 minutes)
- Always-on-top window

**Features**:
- Threaded popup (non-blocking)
- Timeout handling
- User input validation
- Callback support

**Usage**:
```python
from ui import InactivityPopup

popup = InactivityPopup()
popup.show(
    title="Activity Tracker",
    message="Please select reason for inactivity:",
    callback=on_response,
    timeout=600
)
```

---

### logger.py
**Purpose**: SQLite database operations

**Size**: ~300 lines  
**Language**: Python 3.8+

**Key Classes**:
- `ActivityLogger` - Database manager

**Database Tables**:
1. `activity_logs` - Activity records
2. `idle_sessions` - Idle period records
3. `system_events` - System events

**Key Methods**:
- `log_activity()` - Record activity
- `log_idle_session()` - Record idle
- `log_system_event()` - Record system events
- `get_today_stats()` - Daily statistics
- `get_activities()` - Query records

**Features**:
- Thread-safe with locks
- Auto-create tables
- Query optimization
- Data validation

**Usage**:
```python
from logger import ActivityLogger

logger = ActivityLogger()
logger.log_idle_session(idle_start, idle_end, reason)
stats = logger.get_today_stats()
```

---

### config.py
**Purpose**: Configuration management

**Size**: ~100 lines  
**Language**: Python 3.8+

**Key Classes**:
- `Config` - Configuration manager

**Configuration File**: `config.json`

**Default Settings**:
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

**Key Methods**:
- `load_config()` - Load from file
- `save_config()` - Save to file
- `get()` - Get setting value
- `set()` - Set setting value

**Usage**:
```python
from config import config

timeout = config.get("idle_timeout")
config.set("idle_timeout", 10)
```

---

### utils.py
**Purpose**: Utility functions and logging

**Size**: ~250 lines  
**Language**: Python 3.8+

**Key Functions**:
- `get_active_window_name()` - Get current window
- `get_active_application()` - Get active app
- `enable_autostart()` - Setup Windows startup
- `disable_autostart()` - Remove from startup
- `get_system_info()` - CPU, memory, platform
- `format_duration()` - Format seconds to readable
- `log_*()` - Logging functions

**Logging Setup**:
- File logging to `app_logs.txt`
- Console logging (stderr)
- Structured format with timestamp

**Usage**:
```python
from utils import log_info, log_error, get_system_info

log_info("Application started")
info = get_system_info()
enable_autostart()
```

---

## 📋 Configuration & Data Files

### config.json
**Auto-Generated**: Yes (on first run)  
**Format**: JSON  
**Location**: Project root

**Content**:
- Idle timeout setting (minutes)
- Check interval (seconds)
- Database and log paths
- Feature flags

**Editing**: Direct edit possible, restart app to apply

---

### tracking_data.db
**Auto-Generated**: Yes (on first run)  
**Format**: SQLite 3  
**Location**: Project root (configurable)

**Contents**:
- Activity logs
- Idle sessions
- System events

**Size**: Grows with usage (~500KB after 1 week typical)

**Access**:
```bash
sqlite3 tracking_data.db
sqlite3 tracking_data.db "SELECT * FROM idle_sessions;"
```

---

### app_logs.txt
**Auto-Generated**: Yes (on first run)  
**Format**: Plain text log  
**Location**: Project root (configurable)

**Content**:
- Application events
- Errors and warnings
- Debug information
- Timestamps

**Usage**:
```bash
# View logs
type app_logs.txt

# View last 20 lines
powershell -Command "Get-Content app_logs.txt -Tail 20"

# Real-time monitoring
Get-Content app_logs.txt -Tail 1 -Wait
```

---

## 🔧 Build & Setup Files

### requirements.txt
**Purpose**: Python package dependencies  
**Format**: pip requirements format

**Contents**:
```
pynput>=1.7.6           # Keyboard/mouse tracking
pywin32>=305            # Windows integration
psutil>=5.9.0           # System utilities
pystray>=0.19.4         # System tray icon
Pillow>=9.0.0           # Image processing
```

**Usage**:
```bash
pip install -r requirements.txt
```

**Size**: 7 lines

---

### setup.py
**Purpose**: Automated setup and configuration  
**Size**: ~400 lines

**Features**:
- Check Python version
- Install dependencies
- Configure Windows integration
- Create default config
- Test all components
- Setup shortcuts (optional)

**Usage**:
```bash
python setup.py
```

**Output**: Step-by-step setup with verification

---

### build.bat
**Purpose**: Automated executable build  
**Format**: Windows batch script  
**Size**: ~50 lines

**Features**:
- Check PyInstaller
- Verify dependencies
- Build executable
- Report results

**Usage**:
```bash
build.bat
```

**Output**: `dist/ActivityTracker.exe`

---

### tracker.spec
**Purpose**: PyInstaller configuration  
**Format**: Python spec file  
**Size**: ~40 lines

**Configuration**:
- Single executable file
- No console window
- Window app
- Data inclusion

**Usage**:
```bash
pyinstaller tracker.spec
```

---

### test_app.py
**Purpose**: Comprehensive test suite  
**Size**: ~450 lines

**Tests**:
1. Import availability
2. Config loading
3. Database operations
4. Utility functions
5. UI components
6. Tracker functions
7. Main application

**Usage**:
```bash
python test_app.py
```

**Output**: Test results with ✓/✗ indicators

---

## 🛠️ Tools & Utilities

### export_data.py
**Purpose**: Data export and analysis  
**Size**: ~350 lines

**Features**:
- View today's summary
- List idle sessions
- Analyze idle reasons
- Export to CSV
- Export to JSON

**Menu Options**:
1. Today's summary
2. Today's idle sessions
3. Idle reasons (last 7 days)
4. Idle sessions from specific date
5. Export to CSV
6. Export to JSON
7. Exit

**Usage**:
```bash
python export_data.py
```

**Output**: Interactive menu with data views

---

## 📚 Documentation Files

### README.md
**Purpose**: Main project documentation  
**Size**: ~1000 lines

**Sections**:
- Features overview
- System requirements
- Installation guide
- Running instructions
- Configuration guide
- Data storage info
- How it works (with diagrams)
- Module structure
- Troubleshooting
- Future enhancements

**Audience**: General users and developers

---

### SETUP_GUIDE.md
**Purpose**: Detailed installation guide  
**Size**: ~800 lines

**Sections**:
- Prerequisites
- Step-by-step installation
- Virtual environment setup
- Running the application
- Building executable
- Configuration guide
- Database access
- Troubleshooting
- Getting help

**Audience**: First-time users

---

### ARCHITECTURE.md
**Purpose**: Technical design documentation  
**Size**: ~1000 lines

**Sections**:
- System architecture diagrams
- Module breakdown with pseudocode
- Data flow diagrams
- Design patterns used
- Thread management details
- Database schema
- Error handling strategy
- Performance considerations
- Security notes
- Deployment checklist

**Audience**: Developers and maintainers

---

### PROJECT_FILES.md
**Purpose**: This file - file reference guide  
**Size**: ~600 lines

**Content**:
- Complete file listing
- Purpose of each file
- Key components/methods
- Usage examples
- Size and language info

**Audience**: New developers and maintainers

---

## 📊 File Statistics

### By Type

| Type | Count | Total Lines |
|------|-------|-------------|
| Python (core) | 6 | ~1,800 |
| Python (tools) | 4 | ~1,200 |
| Configuration | 3 | Auto-generated |
| Scripts | 2 | ~100 |
| Docs | 4 | ~3,500 |
| **Total** | **23** | **~6,600** |

### By Size Category

| Size | Files | Examples |
|------|-------|----------|
| < 100 lines | 3 | config.py, build.bat |
| 100-300 lines | 5 | utils.py, logger.py |
| 300-500 lines | 5 | tracker.py, ui.py, export_data.py |
| 500+ lines | 4 | setup.py, documentation |

---

## 🚀 Typical Workflows

### First-Time Setup

```
1. git clone / download
2. pip install -r requirements.txt
3. python setup.py
4. python test_app.py
5. python main.py --interactive
```

**Files Used**:
- requirements.txt
- setup.py
- test_app.py
- main.py
- config.py
- All modules

---

### Daily Usage

```
1. python main.py              (background mode)
   or
   python main.py --interactive (interactive mode)
2. App monitors activity
3. Shows popups when needed
4. Data saved to SQLite
```

**Files Used**:
- main.py
- tracker.py
- ui.py
- logger.py

---

### Data Analysis

```
1. python export_data.py
2. Select option from menu
3. View data or export to CSV/JSON
4. Analyze in Excel/Python
```

**Files Used**:
- export_data.py
- tracking_data.db

---

### Build Executable

```
1. pip install pyinstaller
2. build.bat
   or
   pyinstaller --onefile main.py
3. dist\ActivityTracker.exe created
4. Distribute or setup autostart
```

**Files Used**:
- build.bat
- tracker.spec
- All core modules
- requirements.txt

---

## 🔄 File Dependencies

```
main.py
  ├── config.py
  ├── tracker.py
  │   ├── config.py
  │   ├── logger.py
  │   │   └── config.py
  │   └── utils.py
  ├── ui.py
  ├── logger.py
  └── utils.py

export_data.py
  └── sqlite3 (standard library)

setup.py
  ├── config.py
  ├── logger.py
  └── utils.py

test_app.py
  ├── main.py
  ├── config.py
  ├── logger.py
  ├── utils.py
  ├── ui.py
  └── tracker.py
```

---

## 📥 Input Files

| File | Format | Source | Usage |
|------|--------|--------|-------|
| config.json | JSON | Auto-generated/User editable | Settings |
| keyboard input | System event | Windows | Activity detection |
| mouse input | System event | Windows | Activity detection |

---

## 📤 Output Files

| File | Format | Updated | Purpose |
|------|--------|---------|---------|
| tracking_data.db | SQLite | Real-time | Data storage |
| app_logs.txt | Text | Real-time | Application logs |
| export.csv | CSV | On demand | Data export |
| export.json | JSON | On demand | Data export |
| ActivityTracker.exe | Binary | Build time | Distributed executable |

---

## 🔐 File Permissions

### Required Permissions

- **tracking_data.db**: Read/Write
- **app_logs.txt**: Write
- **config.json**: Read/Write
- **All .py files**: Read/Execute

### Administrator Requirements

- System lock/unlock detection (optional)
- Autostart registry modification (optional)
- Registry read (for autostart)

---

## 💾 Storage Growth

### Database Growth Rate

- **Per idle session**: ~200 bytes
- **Per day (typical)**: ~10-20 KB
- **Per week**: ~70-140 KB
- **Per year**: ~4-7 MB

**Estimation**:
- 5 idle sessions/day → 5-6 MB/year
- 10 idle sessions/day → 10-12 MB/year

### Log File Growth

- Per day: 20-50 KB (depends on logging level)
- Per month: 0.6-1.5 MB
- Archive old logs periodically

---

## 🔧 Maintenance Tasks

### Regular Maintenance

```bash
# Check for errors
grep "ERROR" app_logs.txt

# Archive old logs
move app_logs.txt app_logs_backup_$(date +%Y%m%d).txt

# Backup database
copy tracking_data.db tracking_data_backup_$(date +%Y%m%d).db

# Clean old records (older than 1 year)
sqlite3 tracking_data.db "DELETE FROM idle_sessions WHERE date < date('now', '-1 year');"
```

---

## ✅ File Checklist

Before deployment, verify:

- [ ] All .py files present and readable
- [ ] requirements.txt complete and tested
- [ ] README.md accessible
- [ ] Database created on first run
- [ ] Logs being written properly
- [ ] Config file auto-generated
- [ ] All tests passing (test_app.py)
- [ ] Build succeeds (build.bat or pyinstaller)

---

**Version**: 1.0.0  
**Last Updated**: 2024  
**Total Files**: 23  
**Total Lines**: ~6,600  
**Status**: Production Ready ✅
