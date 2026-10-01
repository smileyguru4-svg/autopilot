# BUILD INSTRUCTIONS FOR AUTOPILOT.EXE

## Option 1: Build on Your Laptop (Recommended)

### Prerequisites:
1. Install Python 3.10+ from python.org
2. Install Git
3. Clone this repository:
   ```
   git clone https://github.com/smileyguru4-svg/autopilot.git
   cd autopilot
   ```

### Build Steps:
1. Create virtual environment:
   ```
   python -m venv venv
   venv\Scripts\activate
   ```

2. Install dependencies:
   ```
   pip install -r requirements_desktop.txt
   pip install pyinstaller selenium webdriver-manager
   ```

3. Build the EXE:
   ```
   pyinstaller --onefile --windowed --name "Autopilot" autopilot_app.py
   ```

4. Find your EXE in:
   ```
   dist/Autopilot.exe
   ```

## Option 2: Use Pre-Built EXE
We can also provide pre-built EXE files for download.

## Running Autopilot

1. Double-click `Autopilot.exe`
2. Create or select an account
3. Fill in your profile information
4. Select account and click "Start Automation"
5. Watch the logs as it completes surveys

## Features

✅ **Multi-Account Management**
   - Create unlimited survey accounts
   - Save profiles locally
   - Switch between accounts easily
   - Export/import backups

✅ **Human-Like Behavior**
   - Acts like a real person
   - Consistent answers based on profile
   - Realistic delays between answers
   - Handles qualification screens

✅ **Complete Logging**
   - Real-time status updates
   - Detailed activity logs
   - Save logs to file
   - Track completion progress

✅ **Multiple Surveys**
   - Complete multiple surveys in one session
   - Automatic fallback if screened out
   - Batch processing capability

## File Structure

```
autopilot/
├── autopilot_app.py          # Main desktop app (what we build into EXE)
├── autopilot.spec            # PyInstaller spec file
├── core/
│   ├── persona.py            # Human-like personality logic
│   ├── five_survey.py        # Five Survey automation
│   └── agent.py              # Survey agent logic
├── requirements.txt          # Python dependencies
└── README.md                 # Documentation
```

## Troubleshooting

If you get errors when building:

1. **PyInstaller not found:**
   ```
   pip install pyinstaller
   ```

2. **Selenium errors:**
   ```
   pip install selenium webdriver-manager
   ```

3. **Python not found:**
   - Add Python to PATH
   - Or use full path: C:\Python310\python.exe

4. **Permission denied:**
   - Run Command Prompt as Administrator

## Support

For issues or questions, open an issue on GitHub:
https://github.com/smileyguru4-svg/autopilot/issues
