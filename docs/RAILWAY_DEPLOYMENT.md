# Railway Deployment Guide

This guide will help you deploy the Automa job portal automation system to Railway for continuous operation.

## 🚀 Prerequisites

1. **Railway Account**: Sign up at [railway.app](https://railway.app)
2. **GitHub Repository**: Your code should be in a GitHub repository
3. **Railway CLI** (optional): `npm install -g @railway/cli`

## 📋 Step-by-Step Deployment

### 1. Connect Repository to Railway

#### Option A: Via Railway Dashboard
1. Go to [railway.app](https://railway.app)
2. Click "New Project"
3. Select "Deploy from GitHub repo"
4. Choose your repository
5. Railway will automatically detect the Python project

#### Option B: Via Railway CLI
```bash
# Login to Railway
railway login

# Link to your project
railway link

# Deploy
railway up
```

### 2. Configure Environment Variables

In your Railway project dashboard, go to **Variables** tab and add:

#### Required Variables
```bash
PYTHON_VERSION=3.9
PORT=5000
TZ=Asia/Dubai
RAILWAY_ENVIRONMENT=production
```

#### Job Portal Credentials
```bash
# Bayt.com
BAYT_USERNAME=your-email@example.com
BAYT_PASSWORD=your-password

# NaukriGulf.com
NAUKRIGULF_USERNAME=your-email@example.com
NAUKRIGULF_PASSWORD=your-password
```

#### Optional Variables
```bash
# Logging
LOG_LEVEL=INFO
DEBUG=false

# Scheduling
SCHEDULER_ENABLED=true
DAILY_UPDATE_TIME=09:00
```

### 3. Configure Build Settings

Railway will automatically detect the Python project, but you can customize:

#### Build Command
```bash
pip install -r requirements.txt && playwright install chromium
```

#### Start Command
```bash
gunicorn --bind 0.0.0.0:$PORT wsgi:app
```

### 4. Deploy and Monitor

#### Initial Deployment
```bash
# Push your code to GitHub
git add .
git commit -m "Deploy to Railway"
git push origin main

# Railway will automatically deploy
```

#### Monitor Deployment
1. Check Railway dashboard for build status
2. View logs for any errors
3. Test the web interface at your Railway URL

## 🔧 Configuration Files

### Procfile
```
web: gunicorn --bind 0.0.0.0:$PORT wsgi:app
```

### railway.json
```json
{
  "$schema": "https://railway.app/railway.schema.json",
  "build": {
    "builder": "NIXPACKS"
  },
  "deploy": {
    "startCommand": "gunicorn --bind 0.0.0.0:$PORT wsgi:app",
    "healthcheckPath": "/health",
    "healthcheckTimeout": 100,
    "restartPolicyType": "ON_FAILURE",
    "restartPolicyMaxRetries": 10
  }
}
```

### runtime.txt
```
python-3.9.18
```

## 🔒 Security Considerations

### Environment Variables
- Never commit sensitive data to Git
- Use Railway's built-in secrets management
- Rotate credentials regularly

### Cookie Management
- Store cookies as environment variables
- Update cookies periodically
- Monitor authentication status

### Access Control
- Use Railway's access controls
- Limit who can view logs and variables
- Monitor usage and costs

## 📊 Monitoring and Maintenance

### Health Checks
The application includes health check endpoints:
- `/health` - Basic health status
- `/status` - Detailed system status
- `/logs` - Recent log entries

### Logs
- **Railway Dashboard**: View real-time logs
- **Application Logs**: Check `automa.log` in the app
- **Error Monitoring**: Set up alerts for failures

### Performance Monitoring
- Monitor CPU and memory usage
- Track response times
- Watch for failed deployments

## 🚨 Troubleshooting

### Common Issues

#### Build Failures
```bash
# Check build logs
railway logs

# Common fixes:
# 1. Update requirements.txt
# 2. Check Python version compatibility
# 3. Verify all dependencies are listed
```

#### Runtime Errors
```bash
# Check application logs
railway logs

# Common issues:
# 1. Missing environment variables
# 2. Database connection issues
# 3. Authentication problems
```

#### Performance Issues
- Scale up resources if needed
- Optimize code for production
- Monitor resource usage

### Debug Mode
```bash
# Enable debug logging
DEBUG=true
LOG_LEVEL=DEBUG
```

## 🔄 Continuous Deployment

### Automatic Deployments
Railway automatically deploys when you push to your main branch:
```bash
git push origin main
```

### Manual Deployments
```bash
# Deploy specific branch
railway up --branch feature-branch

# Deploy with specific variables
railway up --variable DEBUG=true
```

### Rollback
```bash
# Rollback to previous deployment
railway rollback

# Deploy specific commit
railway up --commit abc123
```

## 💰 Cost Optimization

### Resource Management
- Start with minimal resources
- Scale up based on usage
- Monitor costs regularly

### Free Tier Limits
- Railway offers free tier with limitations
- Monitor usage to avoid charges
- Consider paid plans for production

## 📈 Scaling

### Horizontal Scaling
```bash
# Scale to multiple instances
railway scale web=3
```

### Vertical Scaling
- Upgrade to higher resource tiers
- Monitor performance metrics
- Optimize code efficiency

## 🔐 Production Checklist

Before going live:

- [ ] All environment variables configured
- [ ] Credentials updated and secure
- [ ] Health checks working
- [ ] Logs properly configured
- [ ] Monitoring set up
- [ ] Backup strategy in place
- [ ] Error handling tested
- [ ] Performance optimized
- [ ] Security reviewed
- [ ] Documentation updated

## 📞 Support

### Railway Support
- [Railway Documentation](https://docs.railway.app)
- [Railway Discord](https://discord.gg/railway)
- [Railway Status](https://status.railway.app)

### Application Support
- Check logs for errors
- Review this documentation
- Open issues on GitHub

---

**Note**: This deployment guide is specific to Railway. For other platforms, refer to their respective documentation.
