# ARCHITECTURE & DESIGN DOCUMENTATION

Comprehensive technical documentation for the Activity Tracking Tool.

## Table of Contents

1. [System Architecture](#system-architecture)
2. [Module Breakdown](#module-breakdown)
3. [Data Flow](#data-flow)
4. [Design Patterns](#design-patterns)
5. [Thread Management](#thread-management)
6. [Database Schema](#database-schema)
7. [Error Handling](#error-handling)
8. [Performance Considerations](#performance-considerations)

## System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                        Main Process                         │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌────────────────────────────────────────────────────┐    │
│  │  TrackingApplication (main.py)                     │    │
│  │  - Orchestrates all components                    │    │
│  │  - Manages threads                                │    │
│  │  - Handles events                                 │    │
│  └────────────────────────────────────────────────────┘    │
│                     │                                       │
│     ┌───────────────┼───────────────┐                      │
│     │               │               │                       │
│     ▼               ▼               ▼                       │
│  ┌────────────┐  ┌────────────┐  ┌────────────────┐        │
│  │ActivityTrk │  │SystemEvent │  │UI Components  │        │
│  │   acker    │  │  Monitor   │  │(Popup/Window) │        │
│  └────────────┘  └────────────┘  └────────────────┘        │
│     │               │               │                       │
│     └───────────────┼───────────────┘                      │
│                     │                                       │
│     ┌───────────────┴────────────────┐                     │
│     │                                │                     │
│     ▼                                ▼                     │
│  ┌──────────────┐            ┌────────────────────┐       │
│  │ActivityLogger│            │Configuration      │       │
│  │ (SQLite DB) │            │(config.json)       │       │
│  └──────────────┘            └────────────────────┘       │
│                                                             │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│                   System Resources                         │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  Windows Keyboard     Windows Mouse       Windows System   │
│    (pynput)            (pynput)           (pywin32)        │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

## Module Breakdown

### main.py - Application Orchestrator
**Purpose**: Entry point and main application controller

**Key Classes**:
- `TrackingApplication` - Main orchestrator

**Key Methods**:
- `initialize()` - Setup components
- `start()` - Start tracking
- `stop()` - Cleanup
- `run_interactive()` - UI mode
- `run_background()` - Silent mode

**Responsibilities**:
- Coordinate tracker and monitor
- Handle events from components
- Manage popup dialogs
- Thread lifecycle management

### tracker.py - Activity Tracking
**Purpose**: Detect and monitor user activity and system events

**Key Classes**:
- `ActivityTracker` - Keyboard/mouse monitoring
- `SystemEventMonitor` - Lock/unlock detection

**Key Methods**:
- `start()` / `stop()` - Control tracking
- `_on_activity()` - Mouse/keyboard callback
- `_check_activity_loop()` - Idle detection thread
- `_monitor_loop()` - System event monitoring thread

**Responsibilities**:
- Monitor keyboard and mouse via pynput
- Detect idle periods
- Monitor system lock/unlock
- Trigger callbacks when state changes

**Threading**:
- Mouse listener thread (pynput)
- Keyboard listener thread (pynput)
- Activity check thread
- System monitor thread

### ui.py - User Interface
**Purpose**: Display popups and status windows

**Key Classes**:
- `InactivityPopup` - Popup for reason input
- `StatusWindow` - Status display window

**Key Features**:
- Tkinter-based GUI
- Non-blocking popup display
- Dropdown with predefined reasons
- Text input for custom reasons
- Auto-dismiss timeout

**Threading**:
- Popup runs in separate thread
- Prevents blocking main application

### logger.py - Data Storage
**Purpose**: Persistent data storage and retrieval

**Key Classes**:
- `ActivityLogger` - Database manager

**Database Tables**:
- `activity_logs` - All activity records
- `idle_sessions` - Idle period records
- `system_events` - Lock/unlock events

**Key Methods**:
- `log_activity()` - Record activity
- `log_idle_session()` - Record idle time
- `log_system_event()` - Record system events
- `get_today_stats()` - Daily statistics
- `get_activities()` - Query records

**Thread Safety**:
- Uses database locks (threading.Lock)
- Prevents concurrent access issues

### config.py - Configuration Management
**Purpose**: Load and manage application settings

**Key Classes**:
- `Config` - Configuration manager

**Features**:
- JSON-based configuration
- Default values
- Runtime modification
- Persistent storage

**Configuration Keys**:
- `idle_timeout` - Idle detection threshold
- `check_interval` - Activity check frequency
- `auto_start` - Windows startup
- `db_path` - Database location
- `log_path` - Log file location

### utils.py - Utility Functions
**Purpose**: Helper functions and cross-cutting concerns

**Key Functions**:
- `get_active_window_name()` - Get current window
- `get_system_info()` - System metrics
- `enable_autostart()` - Setup auto-start
- `log_*()` - Logging functions
- `format_duration()` - Time formatting

**Logging Setup**:
- File logging to `app_logs.txt`
- Console logging
- Structured format with timestamp

## Data Flow

### Activity Detection Flow

```
Keyboard Event / Mouse Event
    │
    ▼
pynput Listener Detects Event
    │
    ▼
_on_activity() Called
    │
    ├─ Check if was idle
    │  │
    │  ├─ Yes: Log idle session
    │  │       Trigger ACTIVITY_RESUMED event
    │  │
    │  └─ No: Continue
    │
    └─ Update last_activity timestamp
```

### Idle Detection Flow

```
_check_activity_loop() Thread (runs every 2 sec)
    │
    ▼
Calculate time since last activity
    │
    ├─ >= idle_threshold (5 min default)?
    │  │
    │  ├─ Yes & not already idle:
    │  │     │
    │  │     ├─ Set is_idle = True
    │  │     ├─ Log idle start
    │  │     └─ Trigger IDLE_START event
    │  │         │
    │  │         ▼
    │  │     Callback to main app
    │  │         │
    │  │         ▼
    │  │     Show popup dialog
    │  │         │
    │  │         ▼
    │  │     User selects reason
    │  │         │
    │  │         ▼
    │  │     Log to database
    │  │
    │  └─ No: Continue monitoring
    │
    └─ Sleep 2 seconds, repeat
```

### System Lock/Unlock Flow

```
System Lock State Change
    │
    ▼
Monitor Thread Detects Change
    │
    ├─ LOCKED:
    │  ├─ Log system event
    │  └─ Update internal state
    │
    └─ UNLOCKED:
       ├─ Calculate lock duration
       ├─ Log system event with details
       └─ Trigger SYSTEM_UNLOCKED event
           │
           ▼
       Callback to main app
           │
           ▼
       Show popup dialog
           │
           ▼
       User provides reason
           │
           ▼
       Log to database
```

## Design Patterns

### Observer Pattern
**Used for**: Event handling between components

**Implementation**:
```python
# Callback registration
tracker = ActivityTracker(callback=self._on_tracker_event)

# Event notification
if self.activity_callback:
    self.activity_callback({"type": "IDLE_START", ...})
```

### Singleton-like Pattern
**Used for**: Global config instance

```python
# In config.py
config = Config()  # Single instance

# Usage anywhere
from config import config
idle_time = config.get("idle_timeout")
```

### Thread Pool Pattern
**Used for**: Multiple monitoring threads

**Components**:
- Main thread (orchestration)
- Activity check thread
- Mouse listener thread
- Keyboard listener thread
- System monitor thread
- Popup UI thread

### Database Connection Pool
**Concept**: Thread-safe database operations with locks

```python
db_lock = threading.Lock()

with db_lock:
    conn = sqlite3.connect(self.db_path)
    # Perform operations
    conn.close()
```

## Thread Management

### Thread Overview

| Thread | Purpose | Daemon | Blocking |
|--------|---------|--------|----------|
| Main | Orchestration | No | Program lifetime |
| Activity Check | Idle detection | Yes | Loop with sleep |
| Mouse Listener | pynput | Yes | Event-driven |
| Keyboard Listener | pynput | Yes | Event-driven |
| System Monitor | Lock/unlock | Yes | Loop with sleep |
| Popup UI | User input | Yes | Event loop |

### Thread Safety Mechanisms

1. **Database Locks**
   ```python
   db_lock = threading.Lock()
   with db_lock:
       # Database operations
   ```

2. **Event Callbacks**
   - Loose coupling between components
   - No direct thread access

3. **Thread-Safe Data Structures**
   - Timestamps (immutable)
   - Strings (immutable)
   - Simple booleans/integers

4. **Daemon Threads**
   - Don't prevent program exit
   - Cleaned up automatically

## Database Schema

### activity_logs Table
```sql
CREATE TABLE activity_logs (
    id INTEGER PRIMARY KEY,           -- Unique identifier
    start_time TEXT NOT NULL,         -- ISO format timestamp
    end_time TEXT,                    -- ISO format timestamp
    duration_minutes INTEGER,         -- Calculated duration
    activity_type TEXT NOT NULL,      -- ACTIVE, IDLE, etc.
    reason TEXT,                      -- User-provided reason
    application_name TEXT,            -- Active app name
    date TEXT NOT NULL,               -- YYYY-MM-DD
    created_at TIMESTAMP              -- Creation timestamp
);
```

### idle_sessions Table
```sql
CREATE TABLE idle_sessions (
    id INTEGER PRIMARY KEY,           -- Unique identifier
    idle_start TEXT NOT NULL,         -- ISO format timestamp
    idle_end TEXT,                    -- ISO format timestamp
    duration_minutes INTEGER,         -- Calculated duration
    reason TEXT,                      -- User reason: "Break", "Meeting", etc.
    date TEXT NOT NULL,               -- YYYY-MM-DD
    created_at TIMESTAMP              -- Creation timestamp
);
```

### system_events Table
```sql
CREATE TABLE system_events (
    id INTEGER PRIMARY KEY,           -- Unique identifier
    event_type TEXT NOT NULL,         -- SYSTEM_LOCKED, SYSTEM_UNLOCKED
    timestamp TEXT NOT NULL,          -- ISO format timestamp
    details TEXT,                     -- Additional info
    date TEXT NOT NULL,               -- YYYY-MM-DD
    created_at TIMESTAMP              -- Creation timestamp
);
```

### Key Design Decisions

1. **TEXT for Timestamps**: ISO format for cross-platform compatibility
2. **Separate Tables**: Logical separation of concerns
3. **Date Field**: Enables efficient daily queries
4. **Thread-Safe**: Lock-based access

## Error Handling

### Error Handling Strategy

1. **Top-Level Exception Handling**
   ```python
   try:
       app.start()
   except Exception as e:
       utils.log_error(f"Fatal error: {e}", exc_info=True)
   ```

2. **Component-Level Handling**
   ```python
   try:
       self.activity_tracker.start()
   except Exception as e:
       utils.log_error(f"Tracker error: {e}")
       # Continue with other components
   ```

3. **Thread-Level Handling**
   ```python
   def _monitor_loop(self):
       while self.is_running:
           try:
               # Monitoring logic
           except Exception as e:
               utils.log_debug(f"Monitor error: {e}")
               time.sleep(2)  # Retry
   ```

### Graceful Degradation

```
System Monitor fails → App continues
Database unavailable → Errors logged, app continues
Popup fails → Event logged, no crash
Config missing → Use defaults
```

### Logging Levels

- **INFO**: Important events (start, stop, idle detected)
- **WARNING**: Non-critical issues (autostart failed)
- **ERROR**: Recoverable errors (component initialization)
- **DEBUG**: Detailed information for troubleshooting

## Performance Considerations

### Memory Usage

**Typical**:
- Idle application: 30-50 MB
- With popup: 50-80 MB
- Database: Size grows with time

**Optimization**:
- Listener threads are lightweight
- Database uses indexes
- Old data can be archived

### CPU Usage

**Monitoring**: ~0.1% CPU (idle)
**Activity Check Loop**: ~0.2% CPU (checking every 2 sec)
**Listeners**: Event-driven (minimal when inactive)

**Optimization**:
- Increase `check_interval` to reduce checks
- Listeners are efficient (pynput optimized)

### Database Performance

**Optimization**:
- Indexes on `date` field for queries
- Locks prevent concurrent writes
- Batch operations recommended

**Query Performance**:
```sql
-- Efficient (indexed)
SELECT * FROM activity_logs WHERE date = '2024-01-15'

-- Less efficient (table scan)
SELECT * FROM activity_logs WHERE reason LIKE '%break%'
```

### Startup Time

- Config load: ~10ms
- Database init: ~50-100ms
- Listeners start: ~100-200ms
- Total: ~300-400ms

## Security Considerations

### Data Privacy

1. **Local Storage Only**
   - No cloud sync (unless configured)
   - Database on local machine
   - No external API calls

2. **Activity Data**
   - Contains timestamps only
   - No screenshots
   - No keystrokes
   - No passwords

3. **User Reasons**
   - User-entered text
   - Stored in database
   - Not encrypted by default

### Autostart Security

- Registry key set only when explicitly requested
- User can disable anytime
- Runs as current user (no elevation required)

## Configuration Best Practices

### Performance Tuning

```json
{
    "idle_timeout": 10,      // Longer timeout = fewer popups
    "check_interval": 5      // Longer interval = less CPU
}
```

### Storage Management

```json
{
    "db_path": "/mnt/data/tracking.db"  // Custom location
}
```

## Deployment Checklist

- [ ] Test on target Windows version
- [ ] Verify all dependencies installed
- [ ] Test autostart (if needed)
- [ ] Check database permissions
- [ ] Test popup display
- [ ] Verify logging
- [ ] Check registry (for autostart)
- [ ] Test .exe build (if distributing)

---

**Version**: 1.0.0  
**Last Updated**: 2024
