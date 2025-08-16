# AI Agent & Productivity Tool - Web Interface

## 🚀 Quick Start

The web interface is now running! You can access it in several ways:

### Option 1: Direct Access
Open your web browser and go to:
```
http://localhost:5000
```

### Option 2: Using the Startup Script
Run the startup script which will automatically open your browser:
```bash
python start_web.py
```

### Option 3: Manual Start
If you need to restart the web interface:
```bash
python src/web/app.py
```

## 🎯 Features Available

The web interface provides access to all the AI Agent features:

### Simple Tasks
1. **Daily Job Portal Updates** - Automatically update job portal profiles
2. **Auto Mailer** - Intelligent email automation
3. **Scheduled App Launcher** - Launch applications at specific times

### Complex Tasks
1. **GCC Job Finder** - Find skills-specific jobs across GCC countries
2. **CV Optimizer** - Optimize CV based on job requirements
3. **Email Response Monitor** - Monitor and track email responses
4. **Data Scraper** - Scrape business details from websites

## 🖥️ Dashboard Overview

The main dashboard shows:
- **Statistics Cards** - Key metrics and activity summary
- **Quick Actions** - One-click access to main features
- **Recent Activity** - Latest job applications and email responses
- **Navigation Sidebar** - Easy access to all features

## 🔧 Configuration

Before using the full features, you'll need to:

1. **Copy the configuration template:**
   ```bash
   copy config_template.yaml config.yaml
   ```

2. **Update config.yaml with your credentials:**
   - Job portal login details
   - Email server settings
   - API keys (for AI features)
   - Database settings

3. **Install additional dependencies (optional):**
   ```bash
   # For AI/ML features
   pip install openai nltk spacy
   
   # For data processing
   pip install pandas numpy
   ```

## 🛠️ Troubleshooting

### If the web interface doesn't start:
1. Check that all dependencies are installed: `pip install -r requirements.txt`
2. Ensure no other application is using port 5000
3. Check the console output for error messages

### If you see import errors:
The web interface uses mock agents for demonstration. To use real functionality:
1. Configure your `config.yaml` file
2. Install additional dependencies as needed
3. Restart the web interface

## 📱 Browser Compatibility

The web interface works best with:
- Chrome (recommended)
- Firefox
- Safari
- Edge

## 🔒 Security Notes

- The web interface runs on `localhost` by default
- For production use, configure proper authentication
- Keep your `config.yaml` file secure with your credentials

## 📞 Support

If you encounter issues:
1. Check the console output for error messages
2. Verify all dependencies are installed
3. Ensure the configuration file is properly set up

---

**Enjoy using your AI Agent & Productivity Tool!** 🎉 