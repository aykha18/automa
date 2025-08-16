"""
Utility functions for the AI Agent & Productivity Tool
"""

import logging
import re
import json
import random
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from pathlib import Path
import smtplib
import imaplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email import message_from_bytes
from .config import config


def setup_logging(log_level: str = "INFO", log_file: str = "automa.log"):
    """Setup logging configuration"""
    logging.basicConfig(
        level=getattr(logging, log_level.upper()),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file),
            logging.StreamHandler()
        ]
    )
    return logging.getLogger(__name__)


def parse_email_content(email_content: str) -> Dict[str, Any]:
    """Parse email content to extract relevant information"""
    parsed = {
        "sender": "",
        "subject": "",
        "body": "",
        "job_related": False,
        "response_type": "unknown"
    }
    
    # Extract sender from email headers
    sender_match = re.search(r'From:\s*(.+)', email_content)
    if sender_match:
        parsed["sender"] = sender_match.group(1).strip()
    
    # Extract subject
    subject_match = re.search(r'Subject:\s*(.+)', email_content)
    if subject_match:
        parsed["subject"] = subject_match.group(1).strip()
    
    # Extract body (everything after headers)
    body_start = email_content.find('\n\n')
    if body_start != -1:
        parsed["body"] = email_content[body_start:].strip()
    
    # Determine if job-related
    job_keywords = [
        "application", "interview", "position", "job", "opportunity",
        "resume", "cv", "candidate", "hiring", "recruitment"
    ]
    
    content_lower = (parsed["subject"] + " " + parsed["body"]).lower()
    parsed["job_related"] = any(keyword in content_lower for keyword in job_keywords)
    
    # Determine response type
    if "interview" in content_lower:
        parsed["response_type"] = "interview_request"
    elif "application" in content_lower:
        parsed["response_type"] = "application_response"
    elif "rejection" in content_lower or "unfortunately" in content_lower:
        parsed["response_type"] = "rejection"
    elif "offer" in content_lower or "congratulations" in content_lower:
        parsed["response_type"] = "offer"
    
    return parsed


def generate_random_profile_update() -> Dict[str, Any]:
    """Generate random profile update data for job portals"""
    activities = [
        "Updated profile completion percentage",
        "Added new skill endorsement",
        "Updated job preferences",
        "Enhanced profile visibility",
        "Updated contact information",
        "Added new certification",
        "Updated work experience",
        "Enhanced profile summary"
    ]
    
    skills = [
        "Python", "Java", "SQL", "JavaScript", "React", "Node.js",
        "AWS", "Docker", "Kubernetes", "Machine Learning", "Data Analysis",
        "Project Management", "Agile", "Scrum", "DevOps", "CI/CD"
    ]
    
    return {
        "activity": random.choice(activities),
        "skill": random.choice(skills),
        "completion_percentage": random.randint(85, 100),
        "timestamp": datetime.now().isoformat()
    }


def extract_contact_info(text: str) -> Dict[str, str]:
    """Extract contact information from text"""
    contact_info = {
        "phone": "",
        "email": "",
        "website": ""
    }
    
    # Phone number patterns
    phone_patterns = [
        r'\+971\s*\d{3}\s*\d{3}\s*\d{3}',  # UAE format
        r'\+966\s*\d{3}\s*\d{3}\s*\d{3}',  # Saudi format
        r'\+974\s*\d{4}\s*\d{4}',          # Qatar format
        r'\+965\s*\d{4}\s*\d{4}',          # Kuwait format
        r'\+968\s*\d{4}\s*\d{4}',          # Oman format
        r'\+973\s*\d{4}\s*\d{4}',          # Bahrain format
        r'\d{3}-\d{3}-\d{4}',              # US format
        r'\d{10}',                          # 10 digits
    ]
    
    for pattern in phone_patterns:
        match = re.search(pattern, text)
        if match:
            contact_info["phone"] = match.group()
            break
    
    # Email pattern
    email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
    email_match = re.search(email_pattern, text)
    if email_match:
        contact_info["email"] = email_match.group()
    
    # Website pattern
    website_pattern = r'https?://(?:[-\w.])+(?:[:\d]+)?(?:/(?:[\w/_.])*(?:\?(?:[\w&=%.])*)?(?:#(?:[\w.])*)?)?'
    website_match = re.search(website_pattern, text)
    if website_match:
        contact_info["website"] = website_match.group()
    
    return contact_info


def send_email(to_email: str, subject: str, body: str, 
               smtp_config: Dict = None) -> bool:
    """Send email using SMTP"""
    if smtp_config is None:
        smtp_config = config.get_email_config()
    
    try:
        msg = MIMEMultipart()
        msg['From'] = smtp_config.get('smtp_username', '')
        msg['To'] = to_email
        msg['Subject'] = subject
        
        msg.attach(MIMEText(body, 'plain'))
        
        server = smtplib.SMTP(smtp_config.get('smtp_server', 'localhost'), 
                             smtp_config.get('smtp_port', 587))
        server.starttls()
        server.login(smtp_config.get('smtp_username', ''), 
                    smtp_config.get('smtp_password', ''))
        
        text = msg.as_string()
        server.sendmail(smtp_config.get('smtp_username', ''), to_email, text)
        server.quit()
        
        return True
    except Exception as e:
        logging.error(f"Failed to send email: {e}")
        return False


def check_email_for_responses(imap_config: Dict = None) -> List[Dict[str, Any]]:
    """Check email for new responses"""
    if imap_config is None:
        imap_config = config.get_email_config()
    
    responses = []
    
    try:
        mail = imaplib.IMAP4_SSL(imap_config.get('imap_server', 'localhost'))
        mail.login(imap_config.get('imap_username', ''), 
                  imap_config.get('imap_password', ''))
        mail.select('INBOX')
        
        # Search for unread emails from the last 24 hours
        date = (datetime.now() - timedelta(days=1)).strftime("%d-%b-%Y")
        _, messages = mail.search(None, f'(UNSEEN SINCE "{date}")')
        
        for num in messages[0].split():
            _, msg_data = mail.fetch(num, '(RFC822)')
            email_body = msg_data[0][1]
            email_message = message_from_bytes(email_body)
            
            # Parse email content
            subject = email_message.get('Subject', '')
            sender = email_message.get('From', '')
            
            # Get email body
            body = ""
            if email_message.is_multipart():
                for part in email_message.walk():
                    if part.get_content_type() == "text/plain":
                        body = part.get_payload(decode=True).decode()
                        break
            else:
                body = email_message.get_payload(decode=True).decode()
            
            # Parse content
            parsed = parse_email_content(f"From: {sender}\nSubject: {subject}\n\n{body}")
            
            if parsed["job_related"]:
                responses.append({
                    "sender": sender,
                    "subject": subject,
                    "body": body,
                    "response_type": parsed["response_type"],
                    "received_date": datetime.now()
                })
        
        mail.close()
        mail.logout()
        
    except Exception as e:
        logging.error(f"Failed to check email: {e}")
    
    return responses


def format_cv_for_job(cv_content: str, job_requirements: str, 
                      skills_mapping: Dict = None) -> str:
    """Format CV content based on job requirements"""
    if skills_mapping is None:
        skills_mapping = config.get_cv_optimization_config().get('skills_mapping', {})
    
    # Extract relevant skills from job requirements
    relevant_skills = []
    for skill, keywords in skills_mapping.items():
        if any(keyword.lower() in job_requirements.lower() for keyword in keywords):
            relevant_skills.append(skill)
    
    # Highlight relevant skills in CV
    formatted_cv = cv_content
    for skill in relevant_skills:
        # Add skill highlighting or reordering logic here
        formatted_cv = formatted_cv.replace(skill, f"**{skill}**")
    
    return formatted_cv


def validate_url(url: str) -> bool:
    """Validate URL format"""
    url_pattern = re.compile(
        r'^https?://'  # http:// or https://
        r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?|'  # domain...
        r'localhost|'  # localhost...
        r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # ...or ip
        r'(?::\d+)?'  # optional port
        r'(?:/?|[/?]\S+)$', re.IGNORECASE)
    
    return bool(url_pattern.match(url))


def sanitize_filename(filename: str) -> str:
    """Sanitize filename for safe file operations"""
    # Remove or replace invalid characters
    invalid_chars = '<>:"/\\|?*'
    for char in invalid_chars:
        filename = filename.replace(char, '_')
    
    # Limit length
    if len(filename) > 255:
        filename = filename[:255]
    
    return filename


def create_backup(data: Dict[str, Any], backup_dir: str = "backups") -> str:
    """Create backup of data"""
    backup_path = Path(backup_dir)
    backup_path.mkdir(exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"backup_{timestamp}.json"
    filepath = backup_path / filename
    
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, default=str)
    
    return str(filepath) 