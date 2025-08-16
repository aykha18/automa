# Scripts Directory

This directory contains utility scripts for development and deployment.

## Available Scripts

### Railway Deployment
- `railway_start.py` - Main Railway deployment script
- `railway_deployment.py` - Railway-specific deployment utilities

### Documentation
- `RAILWAY_DEPLOYMENT.md` - Complete Railway deployment guide

## Usage

### Local Development
```bash
# Test Railway deployment locally
python scripts/railway_start.py
```

### Railway Deployment
The `railway.json` configuration automatically uses `railway_start.py` as the startup command.

## Notes

- These scripts are for deployment and development purposes
- They should not be modified for production without testing
- Always test locally before deploying to Railway
