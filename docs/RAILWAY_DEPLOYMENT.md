# 🚂 Railway Deployment Guide

## **Will it Automatically Update on Railway?**

**✅ YES!** With the proper setup, your job portal updates will run automatically on Railway.

## **🚀 Quick Deploy to Railway**

### **Option 1: Automatic Deployment (Recommended)**

1. **Push to GitHub:**
   ```bash
   git add .
   git commit -m "Add Railway deployment configuration"
   git push origin main
   ```

2. **Deploy on Railway:**
   - Go to [Railway.app](https://railway.app)
   - Connect your GitHub repository
   - Railway will automatically detect the configuration
   - Deploy!

### **Option 2: Manual Deployment**

1. **Install Railway CLI:**
   ```bash
   npm install -g @railway/cli
   ```

2. **Login and Deploy:**
   ```bash
   railway login
   railway init
   railway up
   ```

## **⚙️ Configuration Files**

### **railway.json** (Already Created)
```json
{
  "deploy": {
    "startCommand": "python railway_start.py",
    "healthcheckPath": "/",
    "restartPolicyType": "ON_FAILURE"
  }
}
```

### **Environment Variables**
Set these in Railway dashboard:

```bash
# Required
RAILWAY_ENVIRONMENT=production

# Optional (for timezone)
TZ=Asia/Dubai

# Database (if using external)
DATABASE_URL=your_database_url
```

## **🔄 How Automatic Updates Work**

### **✅ What Happens on Railway:**

1. **🚂 Startup Process:**
   - Railway starts your application
   - `railway_start.py` runs automatically
   - Scheduler starts in background thread
   - Web interface starts on main thread

2. **📅 Daily Schedule:**
   - Job portal updates run at 9:00 AM daily
   - Test run happens within 5 minutes of startup
   - All updates are logged to Railway logs

3. **🔄 Persistence:**
   - Railway keeps your app running 24/7
   - Scheduler runs continuously in background
   - Automatic restarts if the app crashes

### **📊 Monitoring:**

1. **Railway Dashboard:**
   - View logs in real-time
   - Monitor deployment status
   - Check resource usage

2. **Web Interface:**
   - Access your app at Railway URL
   - Manual trigger updates
   - View scheduling status

## **🔧 Customization**

### **Change Update Time:**
Edit `src/data/config.yaml`:
```yaml
scheduler:
  daily_updates:
    time: "10:00"  # Change to your preferred time
    timezone: "Asia/Dubai"
```

### **Add More Portals:**
Edit `src/data/job_portals.json`:
```json
{
  "new_portal": {
    "url": "https://new-portal.com",
    "credentials": {
      "username": "your_email",
      "password": "your_password"
    }
  }
}
```

## **🚨 Important Notes**

### **✅ What Works:**
- ✅ Automatic daily updates at 9:00 AM
- ✅ Web interface accessible 24/7
- ✅ Background scheduler runs continuously
- ✅ Automatic restarts on failure
- ✅ Real-time logging and monitoring

### **⚠️ Limitations:**
- ⚠️ Railway may restart containers occasionally
- ⚠️ Free tier has usage limits
- ⚠️ Browser automation requires proper setup

### **🔒 Security:**
- Store sensitive data in Railway environment variables
- Don't commit credentials to GitHub
- Use Railway's built-in secrets management

## **📱 Access Your App**

After deployment:
1. Get your Railway URL from the dashboard
2. Access the web interface
3. Monitor logs for automatic updates
4. Test manual updates via web interface

## **🛠️ Troubleshooting**

### **Common Issues:**

1. **App Not Starting:**
   ```bash
   # Check logs in Railway dashboard
   # Verify all dependencies are installed
   ```

2. **Updates Not Running:**
   ```bash
   # Check scheduler logs
   # Verify timezone settings
   # Test manual updates via web interface
   ```

3. **Browser Automation Issues:**
   ```bash
   # Railway may need additional setup for Playwright
   # Consider using HTTP-only mode for Railway
   ```

### **Support:**
- Check Railway logs in dashboard
- Test locally first: `python railway_start.py`
- Verify configuration files are correct

## **🎯 Summary**

**YES, your job portal updates will run automatically on Railway!**

The setup includes:
- ✅ Background scheduler running 24/7
- ✅ Daily updates at 9:00 AM
- ✅ Web interface for monitoring
- ✅ Automatic restarts and error handling
- ✅ Real-time logging and status updates

Just deploy and your job portals will be updated automatically! 🚀
