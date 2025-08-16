"""
Email Agent - Handles automated email responses based on sender and content
"""

import re
import logging
from datetime import datetime
from typing import Dict, List, Any, Optional
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import smtplib
import imaplib
from email import message_from_bytes

from ..core.config import config
from ..core.database import db
from ..core.utils import setup_logging, parse_email_content, send_email


class EmailAgent:
    """Agent for handling automated email responses"""
    
    def __init__(self):
        self.logger = setup_logging()
        self.email_config = config.get_email_config()
        self.response_templates = self._load_response_templates()
        self.sender_rules = self._load_sender_rules()
    
    def _load_response_templates(self) -> Dict[str, Dict[str, str]]:
        """Load email response templates"""
        templates = {}
        
        # Default templates
        templates["job_application"] = {
            "subject": "Thank you for your application",
            "body": """Dear Hiring Manager,

Thank you for considering my application for the position. I am excited about the opportunity to contribute to your team.

I have attached my updated resume and look forward to discussing how my skills and experience align with your requirements.

Best regards,
[Your Name]"""
        }
        
        templates["interview_request"] = {
            "subject": "Interview Confirmation",
            "body": """Dear [Sender Name],

Thank you for the interview invitation. I confirm my availability for the scheduled interview.

I am looking forward to discussing the opportunity with your team.

Best regards,
[Your Name]"""
        }
        
        templates["rejection"] = {
            "subject": "Thank you for the opportunity",
            "body": """Dear [Sender Name],

Thank you for considering my application and for the opportunity to interview with your company. I appreciate the time you took to meet with me.

I wish you and your team continued success.

Best regards,
[Your Name]"""
        }
        
        templates["offer"] = {
            "subject": "Offer Acceptance",
            "body": """Dear [Sender Name],

Thank you for the offer. I am excited to accept the position and look forward to joining your team.

I will review the offer details and respond with any questions if needed.

Best regards,
[Your Name]"""
        }
        
        return templates
    
    def _load_sender_rules(self) -> Dict[str, Dict[str, Any]]:
        """Load sender-specific response rules"""
        rules = {
            "recruiter": {
                "keywords": ["recruiter", "talent", "hiring", "recruitment"],
                "response_type": "job_application",
                "priority": "high"
            },
            "hr": {
                "keywords": ["hr@", "human.resources", "people.operations"],
                "response_type": "interview_request",
                "priority": "high"
            },
            "hiring_manager": {
                "keywords": ["manager", "director", "head of"],
                "response_type": "interview_request",
                "priority": "high"
            },
            "automated": {
                "keywords": ["noreply", "donotreply", "automated"],
                "response_type": "none",
                "priority": "low"
            }
        }
        return rules
    
    def analyze_sender(self, sender_email: str, sender_name: str = "") -> Dict[str, Any]:
        """Analyze sender to determine response type"""
        sender_info = {
            "type": "unknown",
            "response_type": "none",
            "priority": "medium",
            "confidence": 0.0
        }
        
        sender_lower = (sender_email + " " + sender_name).lower()
        
        for sender_type, rule in self.sender_rules.items():
            keyword_matches = sum(1 for keyword in rule["keywords"] if keyword in sender_lower)
            if keyword_matches > 0:
                confidence = min(keyword_matches / len(rule["keywords"]), 1.0)
                if confidence > sender_info["confidence"]:
                    sender_info.update({
                        "type": sender_type,
                        "response_type": rule["response_type"],
                        "priority": rule["priority"],
                        "confidence": confidence
                    })
        
        return sender_info
    
    def should_respond(self, email_data: Dict[str, Any]) -> bool:
        """Determine if an email should receive an automated response"""
        # Check if it's an automated email
        sender_info = self.analyze_sender(email_data.get("sender", ""))
        if sender_info["response_type"] == "none":
            return False
        
        # Check if it's job-related
        if not email_data.get("job_related", False):
            return False
        
        # Check if we've already responded recently
        recent_responses = db.get_unprocessed_emails()
        for response in recent_responses:
            if response["sender_email"] == email_data.get("sender", ""):
                return False
        
        return True
    
    def generate_response(self, email_data: Dict[str, Any]) -> Dict[str, str]:
        """Generate appropriate response based on email content"""
        sender_info = self.analyze_sender(email_data.get("sender", ""))
        response_type = sender_info["response_type"]
        
        if response_type == "none":
            return {}
        
        template = self.response_templates.get(response_type, {})
        if not template:
            return {}
        
        # Customize template based on email content
        response = {
            "subject": template["subject"],
            "body": template["body"]
        }
        
        # Extract sender name for personalization
        sender_name = self._extract_sender_name(email_data.get("sender", ""))
        if sender_name:
            response["body"] = response["body"].replace("[Sender Name]", sender_name)
        
        # Add specific details based on response type
        if response_type == "interview_request":
            response = self._customize_interview_response(response, email_data)
        elif response_type == "offer":
            response = self._customize_offer_response(response, email_data)
        
        return response
    
    def _extract_sender_name(self, sender: str) -> str:
        """Extract sender name from email address"""
        # Try to extract name from email format like "John Doe <john@example.com>"
        name_match = re.search(r'"([^"]+)"', sender)
        if name_match:
            return name_match.group(1)
        
        # Try to extract from "Name <email>" format
        name_match = re.search(r'([^<]+)<', sender)
        if name_match:
            return name_match.group(1).strip()
        
        # Extract from email username
        email_match = re.search(r'([^@]+)@', sender)
        if email_match:
            username = email_match.group(1)
            # Convert username to readable name
            return username.replace('.', ' ').replace('_', ' ').title()
        
        return "Hiring Manager"
    
    def _customize_interview_response(self, response: Dict[str, str], email_data: Dict[str, Any]) -> Dict[str, str]:
        """Customize interview response with specific details"""
        # Extract interview details from email content
        content = email_data.get("body", "").lower()
        
        # Look for date/time information
        date_patterns = [
            r'(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})',
            r'(\w+ \d{1,2},? \d{4})',
            r'(\d{1,2}:\d{2} (?:AM|PM))'
        ]
        
        for pattern in date_patterns:
            match = re.search(pattern, content)
            if match:
                response["body"] += f"\n\nI have noted the scheduled time: {match.group(1)}"
                break
        
        return response
    
    def _customize_offer_response(self, response: Dict[str, str], email_data: Dict[str, Any]) -> Dict[str, str]:
        """Customize offer response with specific details"""
        # Add acknowledgment of offer details
        response["body"] += "\n\nI will review the offer details and respond within the specified timeframe."
        return response
    
    def send_automated_response(self, to_email: str, response: Dict[str, str]) -> bool:
        """Send automated email response"""
        try:
            success = send_email(
                to_email=to_email,
                subject=response["subject"],
                body=response["body"],
                smtp_config=self.email_config
            )
            
            if success:
                self.logger.info(f"Sent automated response to {to_email}")
                return True
            else:
                self.logger.error(f"Failed to send response to {to_email}")
                return False
                
        except Exception as e:
            self.logger.error(f"Error sending automated response: {e}")
            return False
    
    def process_incoming_emails(self):
        """Process incoming emails and send automated responses"""
        self.logger.info("Processing incoming emails for automated responses")
        
        # Check for new emails
        new_emails = self._fetch_new_emails()
        
        for email_data in new_emails:
            try:
                # Analyze if response is needed
                if not self.should_respond(email_data):
                    continue
                
                # Generate response
                response = self.generate_response(email_data)
                if not response:
                    continue
                
                # Send response
                sender_email = email_data.get("sender", "")
                if self.send_automated_response(sender_email, response):
                    # Log the response
                    db.add_email_response(
                        sender_email=sender_email,
                        subject=email_data.get("subject", ""),
                        content=email_data.get("body", ""),
                        response_type=email_data.get("response_type", "unknown")
                    )
                    
                    self.logger.info(f"Processed and responded to email from {sender_email}")
                
            except Exception as e:
                self.logger.error(f"Error processing email: {e}")
                continue
    
    def _fetch_new_emails(self) -> List[Dict[str, Any]]:
        """Fetch new emails from IMAP server"""
        emails = []
        
        try:
            mail = imaplib.IMAP4_SSL(self.email_config.get('imap_server', 'localhost'))
            mail.login(self.email_config.get('imap_username', ''), 
                      self.email_config.get('imap_password', ''))
            mail.select('INBOX')
            
            # Search for unread emails from the last 24 hours
            _, messages = mail.search(None, 'UNSEEN')
            
            for num in messages[0].split():
                _, msg_data = mail.fetch(num, '(RFC822)')
                email_body = msg_data[0][1]
                email_message = message_from_bytes(email_body)
                
                # Extract email data
                sender = email_message.get('From', '')
                subject = email_message.get('Subject', '')
                
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
                
                email_data = {
                    "sender": sender,
                    "subject": subject,
                    "body": body,
                    "job_related": parsed["job_related"],
                    "response_type": parsed["response_type"]
                }
                
                emails.append(email_data)
            
            mail.close()
            mail.logout()
            
        except Exception as e:
            self.logger.error(f"Error fetching emails: {e}")
        
        return emails
    
    def run_email_monitoring(self):
        """Run continuous email monitoring"""
        self.logger.info("Starting email monitoring service")
        
        while True:
            try:
                self.process_incoming_emails()
                
                # Wait before next check
                import time
                time.sleep(300)  # Check every 5 minutes
                
            except KeyboardInterrupt:
                self.logger.info("Email monitoring stopped by user")
                break
            except Exception as e:
                self.logger.error(f"Error in email monitoring: {e}")
                time.sleep(60)  # Wait 1 minute before retrying


def main():
    """Main function to run email agent"""
    agent = EmailAgent()
    agent.run_email_monitoring()


if __name__ == "__main__":
    main() 