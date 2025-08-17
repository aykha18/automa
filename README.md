# Automa - Job Portal Automation System

A comprehensive automation system for managing job portal profiles and CV updates across multiple platforms including Bayt.com, NaukriGulf.com, and more.

## 🚀 Features

### ✅ Working Automations
- **Bayt.com**: Full automation with CV refresh and profile updates
- **NaukriGulf.com**: CV headline updates and profile management
- **Cookie-based authentication**: Secure session management
- **Scheduled updates**: Daily automated profile refreshes
- **Web interface**: User-friendly dashboard for monitoring

### 🔧 Technical Features
- **Playwright automation**: Robust browser automation
- **Multi-platform support**: Windows, Linux, macOS
- **Railway deployment**: Cloud-ready configuration
- **Background scheduling**: Continuous operation
- **Error handling**: Comprehensive logging and recovery

## 📋 Prerequisites

- Python 3.8+
- Playwright browsers
- Git
- Railway account (for deployment)

## 🛠️ Installation

### 1. Clone the Repository
```bash
git clone <your-repo-url>
cd automa
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
playwright install chromium
```

### 3. Configure the System
```bash
# Copy configuration template
cp config_template.yaml config.yaml

# Edit configuration with your credentials
# See Configuration section below
```

## ⚙️ Configuration

### Job Portal Credentials
Edit `src/data/job_portals.json` to configure your job portal accounts:

```json
{
  "bayt": {
    "enabled": true,
    "credentials": {
      "username": "your-email@example.com",
      "password": "your-password"
    },
    "update_fields": ["cv_refresh", "profile_completion"]
  },
  "naukrigulf": {
    "enabled": true,
    "credentials": {
      "username": "your-email@example.com", 
      "password": "your-password"
    },
    "update_fields": ["cv_refresh"]
  }
}
```

### Cookie Management
For enhanced security and bypassing login issues, the system uses cookie-based authentication:

1. **Extract cookies manually** from your browser after logging in
2. **Store cookies** in `src/data/[portal]_cookies.json` files
3. **System automatically loads** cookies for authentication

## 🚀 Usage

### Local Development

#### Start the Web Interface
```bash
python start_web.py
# Access at http://localhost:5000
```

#### Run Manual Updates
```bash
python main.py --portal bayt --action refresh_cv
python main.py --portal naukrigulf --action update_headline
```

#### Start Background Scheduler
```bash
python main.py --scheduler
```

### Railway Deployment

#### 1. Deploy to Railway
```bash
# Connect to Railway
railway login
railway link

# Deploy
railway up
```

#### 2. Configure Environment Variables
Set the following in Railway dashboard:
- `PYTHON_VERSION`: 3.9
- `PORT`: 5000
- Add your credentials as environment variables

#### 3. Start the Service
```bash
railway start
```

## 📁 Project Structure

```
automa/
├── src/
│   ├── agents/           # Automation agents for each portal
│   │   ├── bayt_playwright_agent.py
│   │   ├── naukrigulf_playwright_agent.py
│   │   └── scheduler_agent.py
│   ├── core/            # Core functionality
│   │   ├── config.py
│   │   ├── database.py
│   │   └── utils.py
│   ├── data/            # Configuration and data files
│   │   ├── job_portals.json
│   │   ├── bayt_cookies.json
│   │   └── naukrigulf_cookies.json
│   └── web/             # Web interface
│       ├── app.py
│       ├── static/
│       └── templates/
├── scripts/             # Utility scripts
├── docs/               # Documentation
├── main.py             # Main application entry point
├── start_web.py        # Web interface starter
├── requirements.txt    # Python dependencies
├── Procfile           # Railway deployment
├── railway.json       # Railway configuration
└── README.md          # This file
```

## 🔧 Development

### Adding New Job Portals

1. **Create agent file**: `src/agents/[portal]_playwright_agent.py`
2. **Add configuration**: Update `src/data/job_portals.json`
3. **Implement methods**: 
   - `login()` - Authentication
   - `refresh_cv()` - CV updates
   - `update_profile()` - Profile management
4. **Test automation**: Create test scripts
5. **Add to scheduler**: Update `scheduler_agent.py`

### Testing

```bash
# Test specific portal
python -m pytest scripts/tests/test_[portal].py

# Test all automations
python main.py --test-all
```

## 📊 Monitoring

### Web Dashboard
Access the web interface at `http://localhost:5000` to:
- Monitor automation status
- View logs and errors
- Trigger manual updates
- Configure settings

### Logs
- **Application logs**: `automa.log`
- **Portal-specific logs**: `logs/[portal].log`
- **Scheduler logs**: `logs/scheduler.log`

## 🔒 Security

### Cookie Management
- Cookies are stored locally in JSON format
- Never commit cookies to version control
- Rotate cookies regularly for security

### Credentials
- Store credentials in environment variables
- Use Railway secrets for production
- Never hardcode passwords in code

## 🚨 Troubleshooting

### Common Issues

#### Connection Timeouts
- Check internet connectivity
- Verify portal URLs are accessible
- Increase timeout values in configuration

#### Authentication Failures
- Update cookies manually
- Verify credentials are correct
- Check for CAPTCHA or 2FA requirements

#### Browser Automation Issues
- Update Playwright browsers: `playwright install`
- Check for portal UI changes
- Review error logs for specific selectors

### Debug Mode
```bash
# Enable debug logging
python main.py --debug --portal bayt --action refresh_cv
```

## 📈 Performance

### Optimization Tips
- Use headless mode for production
- Implement retry mechanisms
- Cache successful operations
- Monitor resource usage

### Scaling
- Deploy multiple instances
- Use load balancing
- Implement queue systems for high volume

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Implement your changes
4. Add tests
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

For support and questions:
- Check the documentation in `docs/`
- Review the troubleshooting section
- Open an issue on GitHub
- Contact the development team

## 🔄 Changelog

### Version 1.0.0
- ✅ Bayt.com automation working
- ✅ NaukriGulf.com automation working
- ✅ Cookie-based authentication
- ✅ Web interface
- ✅ Railway deployment
- ✅ Background scheduling
- ✅ Comprehensive error handling

---

**Note**: This automation system is designed for personal use. Please respect the terms of service of each job portal and use responsibly.
