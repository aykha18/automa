# 🤖 AI Agent & Productivity Tool

A comprehensive automation tool for job portal management, email monitoring, and business data scraping.

## 🚀 Features

### **Job Portal Automation**
- ✅ **Bayt.com Integration**: Automated CV refresh and profile updates
- ✅ **Multi-Portal Support**: Indeed, LinkedIn, and other job portals
- ✅ **Cookie Management**: Secure authentication handling
- ✅ **Scheduled Updates**: Daily automatic profile refreshes

### **Web Interface**
- 📊 **Dashboard**: Real-time monitoring and statistics
- 🔧 **Job Portal Management**: Test connections and run updates
- 📧 **Email Monitor**: Track email responses and applications
- 🔍 **GCC Job Finder**: Search jobs across GCC countries
- 📝 **CV Optimizer**: AI-powered CV optimization
- 🗄️ **Data Scraper**: Business data collection

### **Scheduling & Automation**
- ⏰ **Daily Updates**: Automatic job portal refreshes at 9:00 AM
- 🔄 **Background Services**: Continuous monitoring and updates
- 📈 **Statistics Tracking**: Monitor success rates and activity

## 🛠️ Installation

### **Prerequisites**
- Python 3.8+
- Git
- Chrome/Chromium (for browser automation)

### **Quick Start**

1. **Clone the repository:**
   ```bash
   git clone <your-repo-url>
   cd automa
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Install Playwright browsers:**
   ```bash
   playwright install
   ```

4. **Configure settings:**
   ```bash
   cp config_template.yaml config.yaml
   # Edit config.yaml with your credentials
   ```

5. **Run the application:**
   ```bash
   # Web interface
   python start_web.py
   
   # Command line interface
   python main.py --mode interactive
   ```

## ⚙️ Configuration

### **Job Portal Credentials**
Edit `src/data/job_portals.json`:
```json
{
  "bayt": {
    "credentials": {
      "username": "your-email@example.com",
      "password": "your-password"
    }
  }
}
```

### **Scheduler Settings**
Edit `config.yaml`:
```yaml
scheduler:
  daily_updates:
    time: "09:00"
    timezone: "Asia/Dubai"
```

## 🚂 Railway Deployment

### **Automatic Deployment**
1. Push to GitHub
2. Connect repository to Railway
3. Set environment variables
4. Deploy!

### **Environment Variables**
```bash
RAILWAY_ENVIRONMENT=production
TZ=Asia/Dubai
```

## 📖 Usage

### **Web Interface**
- Access at `http://localhost:5000`
- Monitor job portal status
- Run manual updates
- View statistics

### **Command Line**
```bash
# Search for jobs
python main.py --mode job_search --skill "Python Developer" --countries AE SA

# Run daily updates
python main.py --mode daily_updates

# Start background services
python main.py --start-services
```

### **Interactive Mode**
```bash
python main.py --mode interactive
```

## 🔧 Development

### **Project Structure**
```
automa/
├── src/
│   ├── agents/          # Automation agents
│   ├── core/           # Core functionality
│   ├── data/           # Configuration files
│   └── web/            # Web interface
├── config.yaml         # Main configuration
├── requirements.txt    # Dependencies
└── README.md          # This file
```

### **Adding New Job Portals**
1. Add portal configuration to `src/data/job_portals.json`
2. Create agent in `src/agents/`
3. Update scheduler integration

## 🔒 Security

- Store sensitive data in environment variables
- Use Railway's built-in secrets management
- Never commit credentials to Git
- Regular cookie updates for authentication

## 📊 Monitoring

### **Logs**
- Application logs: `automa.log`
- Railway dashboard logs
- Web interface monitoring

### **Statistics**
- Job portal success rates
- Update frequency tracking
- Error monitoring

## 🛠️ Troubleshooting

### **Common Issues**
1. **Browser Automation**: Install Playwright browsers
2. **Authentication**: Update cookies regularly
3. **Scheduling**: Check timezone settings

### **Support**
- Check logs in `automa.log`
- Monitor Railway dashboard
- Test locally before deployment

## 📄 License

This project is licensed under the MIT License.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## 📞 Support

For support and questions:
- Check the documentation
- Review logs and error messages
- Test configurations locally

---

**Made with ❤️ for automated job hunting**
