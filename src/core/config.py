"""
Configuration management for the AI Agent & Productivity Tool
"""

import os
import yaml
from typing import Dict, Any, List
from pathlib import Path


class Config:
    """Configuration manager for the AI Agent"""
    
    def __init__(self, config_path: str = "config.yaml"):
        self.config_path = config_path
        self.config = self._load_config()
    
    def _load_config(self) -> Dict[str, Any]:
        """Load configuration from YAML file"""
        try:
            with open(self.config_path, 'r', encoding='utf-8') as file:
                return yaml.safe_load(file)
        except FileNotFoundError:
            print(f"Config file {self.config_path} not found. Using default configuration.")
            return self._get_default_config()
        except yaml.YAMLError as e:
            print(f"Error parsing config file: {e}")
            return self._get_default_config()
    
    def _get_default_config(self) -> Dict[str, Any]:
        """Return default configuration"""
        return {
            "job_portals": {},
            "email": {},
            "gcc_countries": [],
            "scraping": {},
            "cv_optimization": {},
            "scheduler": {},
            "database": {},
            "logging": {}
        }
    
    def get_job_portals(self) -> Dict[str, Any]:
        """Get job portal configurations"""
        return self.config.get("job_portals", {})
    
    def get_email_config(self) -> Dict[str, Any]:
        """Get email configuration"""
        return self.config.get("email", {})
    
    def get_gcc_countries(self) -> List[Dict[str, Any]]:
        """Get GCC countries configuration"""
        return self.config.get("gcc_countries", [])
    
    def get_scraping_config(self) -> Dict[str, Any]:
        """Get scraping configuration"""
        return self.config.get("scraping", {})
    
    def get_cv_optimization_config(self) -> Dict[str, Any]:
        """Get CV optimization configuration"""
        return self.config.get("cv_optimization", {})
    
    def get_scheduler_config(self) -> Dict[str, Any]:
        """Get scheduler configuration"""
        return self.config.get("scheduler", {})
    
    def get_database_config(self) -> Dict[str, Any]:
        """Get database configuration"""
        return self.config.get("database", {})
    
    def get_logging_config(self) -> Dict[str, Any]:
        """Get logging configuration"""
        return self.config.get("logging", {})
    
    def get_openai_api_key(self) -> str:
        """Get OpenAI API key"""
        return self.config.get("cv_optimization", {}).get("openai_api_key", "")
    
    def reload(self):
        """Reload configuration from file"""
        self.config = self._load_config()


# Global configuration instance
config = Config() 