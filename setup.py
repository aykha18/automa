#!/usr/bin/env python3
"""
Setup script for AI Agent & Productivity Tool
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path


def check_python_version():
    """Check if Python version is compatible"""
    if sys.version_info < (3, 8):
        print("Error: Python 3.8 or higher is required")
        sys.exit(1)
    print(f"✓ Python {sys.version_info.major}.{sys.version_info.minor} detected")


def install_dependencies():
    """Install required dependencies"""
    print("\n📦 Installing dependencies...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("✓ Dependencies installed successfully")
    except subprocess.CalledProcessError as e:
        print(f"✗ Error installing dependencies: {e}")
        sys.exit(1)


def create_directories():
    """Create necessary directories"""
    print("\n📁 Creating directories...")
    directories = [
        "logs",
        "backups",
        "data",
        "exports",
        "temp"
    ]
    
    for directory in directories:
        Path(directory).mkdir(exist_ok=True)
        print(f"✓ Created directory: {directory}")


def setup_database():
    """Initialize the database"""
    print("\n🗄️ Setting up database...")
    try:
        from src.core.database import db
        print("✓ Database initialized successfully")
    except Exception as e:
        print(f"✗ Error initializing database: {e}")
        sys.exit(1)


def create_config_template():
    """Create configuration template"""
    print("\n⚙️ Creating configuration template...")
    
    config_template = """# AI Agent & Productivity Tool Configuration
# Copy this file to config.yaml and update with your settings

# Email Configuration
email:
  smtp_server: "smtp.gmail.com"
  smtp_port: 587
  smtp_username: "your-email@gmail.com"
  smtp_password: "your-app-password"
  imap_server: "imap.gmail.com"
  imap_port: 993
  imap_username: "your-email@gmail.com"
  imap_password: "your-app-password"

# Job Portal Credentials
job_portals:
  indeed:
    username: "your-indeed-email"
    password: "your-indeed-password"
  linkedin:
    username: "your-linkedin-email"
    password: "your-linkedin-password"
  bayt:
    username: "your-bayt-email"
    password: "your-bayt-password"

# OpenAI Configuration (for CV optimization)
cv_optimization:
  openai_api_key: "your-openai-api-key"

# Scheduler Configuration
scheduler:
  daily_updates:
    time: "09:00"
    timezone: "Asia/Dubai"
  email_monitoring:
    interval: 30  # minutes
  app_launcher:
    applications:
      - name: "Chrome"
        path: "C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe"
        schedule: "08:00"
      - name: "Outlook"
        path: "C:\\Program Files\\Microsoft Office\\root\\Office16\\OUTLOOK.EXE"
        schedule: "08:30"

# Database Configuration
database:
  type: "sqlite"
  path: "automa.db"

# Logging Configuration
logging:
  level: "INFO"
  file: "automa.log"
  max_size: "10MB"
  backup_count: 5
"""
    
    with open("config_template.yaml", "w") as f:
        f.write(config_template)
    
    print("✓ Configuration template created: config_template.yaml")
    print("  Please copy to config.yaml and update with your settings")


def create_startup_scripts():
    """Create startup scripts"""
    print("\n🚀 Creating startup scripts...")
    
    # Windows batch file
    windows_script = """@echo off
echo Starting AI Agent & Productivity Tool...
python main.py --mode interactive
pause
"""
    
    with open("start_automa.bat", "w") as f:
        f.write(windows_script)
    
    # Linux/Mac shell script
    unix_script = """#!/bin/bash
echo "Starting AI Agent & Productivity Tool..."
python3 main.py --mode interactive
"""
    
    with open("start_automa.sh", "w") as f:
        f.write(unix_script)
    
    # Make shell script executable
    if os.name != 'nt':  # Not Windows
        os.chmod("start_automa.sh", 0o755)
    
    print("✓ Startup scripts created:")
    print("  - start_automa.bat (Windows)")
    print("  - start_automa.sh (Linux/Mac)")


def create_web_startup():
    """Create web interface startup script"""
    print("\n🌐 Creating web interface startup...")
    
    web_script = """#!/usr/bin/env python3
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.web.app import app

if __name__ == '__main__':
    print("Starting AI Agent Web Interface...")
    print("Open your browser and go to: http://localhost:5000")
    app.run(debug=True, host='0.0.0.0', port=5000)
"""
    
    with open("start_web.py", "w") as f:
        f.write(web_script)
    
    print("✓ Web interface startup script created: start_web.py")


def create_documentation():
    """Create basic documentation"""
    print("\n📚 Creating documentation...")
    
    readme_content = """# AI Agent & Productivity Tool

## Quick Start

1. **Install Dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Configure Settings:**
   - Copy `config_template.yaml` to `config.yaml`
   - Update with your email and job portal credentials

3. **Run the Application:**
   ```bash
   # Command line interface
   python main.py --mode interactive
   
   # Web interface
   python start_web.py
   ```

## Features

### Simple Tasks
- **Daily Job Portal Updates** - Automatically update random fields across job portals
- **Auto Mailer** - Intelligent email automation based on sender ID and content
- **Scheduled App Launcher** - Launch applications at specific times

### Complex Tasks
- **GCC Job Finder** - Find skills-specific jobs across GCC countries
- **CV Optimizer & Auto-Apply** - Optimize CV based on job requirements
- **Email Response Monitor** - Monitor and track email responses
- **Data Scraper** - Scrape business details from websites

## Usage Examples

### Search for PLSQL jobs in UAE and Saudi Arabia:
```bash
python main.py --mode job_search --skill "PLSQL Developer" --countries AE SA
```

### Scrape business data:
```bash
python main.py --mode scrape --categories tailor mobile_repair --cities Dubai Abu_Dhabi
```

### Run daily updates:
```bash
python main.py --mode daily_updates
```

## Configuration

Edit `config.yaml` to customize:
- Job portal credentials
- Email settings
- GCC country preferences
- Scraping targets
- Schedule settings

## Web Interface

Start the web interface:
```bash
python start_web.py
```

Then open your browser to: http://localhost:5000

## Troubleshooting

1. **Chrome WebDriver Issues:**
   - Download ChromeDriver from: https://chromedriver.chromium.org/
   - Add to PATH or place in project directory

2. **Email Configuration:**
   - Use App Passwords for Gmail
   - Enable IMAP access in email settings

3. **Database Issues:**
   - Delete `automa.db` to reset database
   - Check file permissions

## Support

For issues and questions, please check the logs in the `logs/` directory.
"""
    
    with open("README.md", "w") as f:
        f.write(readme_content)
    
    print("✓ Documentation created: README.md")


def run_tests():
    """Run basic tests"""
    print("\n🧪 Running basic tests...")
    
    try:
        # Test imports
        from src.core.config import config
        from src.core.database import db
        from src.core.utils import setup_logging
        
        print("✓ Core modules imported successfully")
        
        # Test configuration
        job_portals = config.get_job_portals()
        print(f"✓ Configuration loaded: {len(job_portals)} job portals configured")
        
        # Test database
        applications = db.get_job_applications(limit=1)
        print("✓ Database connection successful")
        
        print("✓ All tests passed")
        
    except Exception as e:
        print(f"✗ Test failed: {e}")
        print("  This is normal if configuration is not set up yet")


def main():
    """Main setup function"""
    print("🤖 AI Agent & Productivity Tool Setup")
    print("=" * 50)
    
    # Check Python version
    check_python_version()
    
    # Install dependencies
    install_dependencies()
    
    # Create directories
    create_directories()
    
    # Setup database
    setup_database()
    
    # Create configuration template
    create_config_template()
    
    # Create startup scripts
    create_startup_scripts()
    
    # Create web interface startup
    create_web_startup()
    
    # Create documentation
    create_documentation()
    
    # Run tests
    run_tests()
    
    print("\n" + "=" * 50)
    print("🎉 Setup completed successfully!")
    print("\nNext steps:")
    print("1. Copy config_template.yaml to config.yaml")
    print("2. Update config.yaml with your credentials")
    print("3. Run: python main.py --mode interactive")
    print("4. Or start web interface: python start_web.py")
    print("\nFor help, see README.md")


if __name__ == "__main__":
    main() 