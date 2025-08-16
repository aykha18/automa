# Project Structure

## Overview

```
automa/
├── src/                    # Main source code
│   ├── agents/            # Automation agents
│   ├── core/              # Core functionality
│   ├── data/              # Configuration files
│   └── web/               # Web interface
├── scripts/               # Deployment and utility scripts
├── docs/                  # Documentation
├── config.yaml           # Main configuration (gitignored)
├── config_template.yaml  # Configuration template
├── requirements.txt      # Python dependencies
├── railway.json         # Railway deployment config
├── main.py              # Main application entry point
├── start_web.py         # Web interface entry point
└── README.md            # Project documentation
```

## Directory Details

### `src/` - Main Source Code

#### `src/agents/` - Automation Agents
- `bayt_http_agent.py` - HTTP-based Bayt.com automation
- `bayt_playwright_agent.py` - Playwright-based Bayt.com automation
- `job_portal_agent.py` - Generic job portal automation
- `scheduler_agent.py` - Task scheduling and automation
- `email_agent.py` - Email automation
- `email_monitor.py` - Email monitoring
- `gcc_job_finder.py` - GCC job search
- `cv_optimizer.py` - CV optimization
- `data_scraper.py` - Web scraping

#### `src/core/` - Core Functionality
- `config.py` - Configuration management
- `database.py` - Database operations
- `utils.py` - Utility functions

#### `src/data/` - Configuration Files
- `job_portals.json` - Job portal configurations
- `email_templates.json` - Email templates
- `gcc_countries.json` - GCC country data
- `bayt_cookies.json` - Bayt.com cookies (gitignored)

#### `src/web/` - Web Interface
- `app.py` - Flask application
- `templates/` - HTML templates
- `static/` - Static assets

### `scripts/` - Deployment Scripts
- `railway_start.py` - Railway deployment startup
- `railway_deployment.py` - Railway utilities
- `README.md` - Scripts documentation

### `docs/` - Documentation
- `PROJECT_STRUCTURE.md` - This file
- `RAILWAY_DEPLOYMENT.md` - Railway deployment guide
- `WEB_INTERFACE_README.md` - Web interface documentation

## Key Files

### Configuration Files
- `config.yaml` - Main configuration (contains sensitive data)
- `config_template.yaml` - Configuration template
- `src/data/job_portals.json` - Job portal credentials and settings

### Entry Points
- `main.py` - Command-line interface
- `start_web.py` - Web interface
- `scripts/railway_start.py` - Railway deployment

### Deployment
- `railway.json` - Railway configuration
- `requirements.txt` - Python dependencies
- `.gitignore` - Git ignore rules

## File Naming Conventions

- **Agents**: `*_agent.py` (e.g., `bayt_http_agent.py`)
- **Configuration**: `*.json`, `*.yaml` (e.g., `job_portals.json`)
- **Templates**: `*.html` (in `src/web/templates/`)
- **Scripts**: Descriptive names (e.g., `railway_start.py`)

## Security Considerations

### Gitignored Files
- `config.yaml` - Contains sensitive credentials
- `*.db` - Database files
- `*.log` - Log files
- `*.png` - Screenshots and images
- `*_cookies.json` - Authentication cookies

### Environment Variables
- Store sensitive data in environment variables
- Use Railway's secrets management
- Never commit credentials to Git

## Development Workflow

1. **Local Development**: Use `main.py` or `start_web.py`
2. **Testing**: Create test scripts in temporary files
3. **Deployment**: Use `scripts/railway_start.py`
4. **Documentation**: Update files in `docs/`

## Adding New Features

1. **New Agent**: Add to `src/agents/`
2. **New Configuration**: Add to `src/data/`
3. **New Web Page**: Add to `src/web/templates/`
4. **New Script**: Add to `scripts/`
5. **Documentation**: Update `docs/`
