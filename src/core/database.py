"""
Database management for the AI Agent & Productivity Tool
"""

import sqlite3
import json
from datetime import datetime
from typing import Dict, List, Any, Optional
from pathlib import Path
from .config import config


class Database:
    """Database manager for storing application data"""
    
    def __init__(self, db_path: str = None):
        if db_path is None:
            db_config = config.get_database_config()
            db_path = db_config.get("path", "automa.db")
        
        self.db_path = db_path
        self._init_database()
    
    def _init_database(self):
        """Initialize database tables"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Job applications table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS job_applications (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    job_title TEXT NOT NULL,
                    company TEXT NOT NULL,
                    portal TEXT NOT NULL,
                    country TEXT NOT NULL,
                    application_date DATETIME DEFAULT CURRENT_TIMESTAMP,
                    status TEXT DEFAULT 'applied',
                    cv_version TEXT,
                    response_received BOOLEAN DEFAULT FALSE,
                    response_date DATETIME,
                    notes TEXT
                )
            """)
            
            # Email responses table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS email_responses (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    sender_email TEXT NOT NULL,
                    subject TEXT,
                    received_date DATETIME DEFAULT CURRENT_TIMESTAMP,
                    content TEXT,
                    response_type TEXT,
                    job_application_id INTEGER,
                    processed BOOLEAN DEFAULT FALSE,
                    FOREIGN KEY (job_application_id) REFERENCES job_applications (id)
                )
            """)
            
            # Scraped data table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS scraped_data (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    source_url TEXT NOT NULL,
                    business_name TEXT,
                    category TEXT,
                    phone TEXT,
                    email TEXT,
                    address TEXT,
                    city TEXT,
                    country TEXT,
                    scraped_date DATETIME DEFAULT CURRENT_TIMESTAMP,
                    data_json TEXT
                )
            """)
            
            # Scheduled tasks table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS scheduled_tasks (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    task_name TEXT NOT NULL,
                    task_type TEXT NOT NULL,
                    schedule_time TEXT,
                    last_run DATETIME,
                    next_run DATETIME,
                    status TEXT DEFAULT 'active',
                    config_json TEXT,
                    created_date DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            conn.commit()
    
    def add_job_application(self, job_title: str, company: str, portal: str, 
                           country: str, cv_version: str = None, notes: str = None) -> int:
        """Add a new job application"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO job_applications (job_title, company, portal, country, cv_version, notes)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (job_title, company, portal, country, cv_version, notes))
            conn.commit()
            return cursor.lastrowid
    
    def update_job_application_status(self, application_id: int, status: str, 
                                    response_received: bool = False, response_date: datetime = None):
        """Update job application status"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            if response_date:
                cursor.execute("""
                    UPDATE job_applications 
                    SET status = ?, response_received = ?, response_date = ?
                    WHERE id = ?
                """, (status, response_received, response_date, application_id))
            else:
                cursor.execute("""
                    UPDATE job_applications 
                    SET status = ?, response_received = ?
                    WHERE id = ?
                """, (status, response_received, application_id))
            conn.commit()
    
    def get_job_applications(self, status: str = None, country: str = None, 
                           limit: int = 100) -> List[Dict[str, Any]]:
        """Get job applications with optional filters"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            query = "SELECT * FROM job_applications WHERE 1=1"
            params = []
            
            if status:
                query += " AND status = ?"
                params.append(status)
            
            if country:
                query += " AND country = ?"
                params.append(country)
            
            query += " ORDER BY application_date DESC LIMIT ?"
            params.append(limit)
            
            cursor.execute(query, params)
            return [dict(row) for row in cursor.fetchall()]
    
    def add_email_response(self, sender_email: str, subject: str, content: str,
                          response_type: str, job_application_id: int = None) -> int:
        """Add a new email response"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO email_responses (sender_email, subject, content, response_type, job_application_id)
                VALUES (?, ?, ?, ?, ?)
            """, (sender_email, subject, content, response_type, job_application_id))
            conn.commit()
            return cursor.lastrowid
    
    def get_unprocessed_emails(self) -> List[Dict[str, Any]]:
        """Get unprocessed email responses"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute("""
                SELECT * FROM email_responses 
                WHERE processed = FALSE 
                ORDER BY received_date DESC
            """)
            return [dict(row) for row in cursor.fetchall()]
    
    def mark_email_processed(self, email_id: int):
        """Mark email as processed"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE email_responses 
                SET processed = TRUE 
                WHERE id = ?
            """, (email_id,))
            conn.commit()
    
    def add_scraped_data(self, source_url: str, business_name: str, category: str,
                         phone: str = None, email: str = None, address: str = None,
                         city: str = None, country: str = None, data_json: Dict = None) -> int:
        """Add scraped business data"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            data_json_str = json.dumps(data_json) if data_json else None
            cursor.execute("""
                INSERT INTO scraped_data (source_url, business_name, category, phone, email, address, city, country, data_json)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (source_url, business_name, category, phone, email, address, city, country, data_json_str))
            conn.commit()
            return cursor.lastrowid
    
    def get_scraped_data(self, category: str = None, city: str = None, 
                        country: str = None) -> List[Dict[str, Any]]:
        """Get scraped data with optional filters"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            query = "SELECT * FROM scraped_data WHERE 1=1"
            params = []
            
            if category:
                query += " AND category = ?"
                params.append(category)
            
            if city:
                query += " AND city = ?"
                params.append(city)
            
            if country:
                query += " AND country = ?"
                params.append(country)
            
            query += " ORDER BY scraped_date DESC"
            
            cursor.execute(query, params)
            return [dict(row) for row in cursor.fetchall()]
    
    def add_scheduled_task(self, task_name: str, task_type: str, schedule_time: str,
                          config: Dict = None) -> int:
        """Add a new scheduled task"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            config_json = json.dumps(config) if config else None
            cursor.execute("""
                INSERT INTO scheduled_tasks (task_name, task_type, schedule_time, config_json)
                VALUES (?, ?, ?, ?)
            """, (task_name, task_type, schedule_time, config_json))
            conn.commit()
            return cursor.lastrowid
    
    def update_task_run_time(self, task_id: int, last_run: datetime, next_run: datetime):
        """Update task run times"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE scheduled_tasks 
                SET last_run = ?, next_run = ?
                WHERE id = ?
            """, (last_run, next_run, task_id))
            conn.commit()
    
    def get_active_scheduled_tasks(self) -> List[Dict[str, Any]]:
        """Get active scheduled tasks"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute("""
                SELECT * FROM scheduled_tasks 
                WHERE status = 'active' 
                ORDER BY next_run ASC
            """)
            return [dict(row) for row in cursor.fetchall()]


# Global database instance
db = Database() 