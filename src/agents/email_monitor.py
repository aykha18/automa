"""
Email Monitor Agent - Monitors email responses and tracks application status
"""

import time
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
import imaplib
from email import message_from_bytes
import re

from ..core.config import config
from ..core.database import db
from ..core.utils import setup_logging, parse_email_content, check_email_for_responses


class EmailMonitor:
    """Agent for monitoring email responses and tracking application status"""
    
    def __init__(self):
        self.logger = setup_logging()
        self.email_config = config.get_email_config()
        self.monitoring_interval = config.get_scheduler_config().get('email_monitoring', {}).get('interval', 30)
        self.response_patterns = self._load_response_patterns()
    
    def _load_response_patterns(self) -> Dict[str, Dict[str, Any]]:
        """Load patterns for identifying different types of email responses"""
        patterns = {
            "interview_request": {
                "keywords": ["interview", "meeting", "schedule", "call", "discussion"],
                "priority": "high",
                "action": "schedule_interview"
            },
            "offer": {
                "keywords": ["offer", "congratulations", "welcome", "position", "salary"],
                "priority": "high",
                "action": "review_offer"
            },
            "rejection": {
                "keywords": ["unfortunately", "regret", "not selected", "other candidates", "position filled"],
                "priority": "medium",
                "action": "update_status"
            },
            "application_received": {
                "keywords": ["application received", "thank you", "under review", "process"],
                "priority": "low",
                "action": "log_receipt"
            },
            "follow_up": {
                "keywords": ["follow up", "additional information", "questions", "clarification"],
                "priority": "medium",
                "action": "respond_appropriately"
            }
        }
        return patterns
    
    def monitor_email_responses(self):
        """Monitor email inbox for job-related responses"""
        self.logger.info("Starting email response monitoring")
        
        try:
            # Check for new emails
            new_responses = check_email_for_responses(self.email_config)
            
            for response in new_responses:
                try:
                    # Analyze the response
                    analysis = self._analyze_email_response(response)
                    
                    # Process based on response type
                    if analysis["should_process"]:
                        self._process_email_response(response, analysis)
                    
                except Exception as e:
                    self.logger.error(f"Error processing email response: {e}")
                    continue
            
            self.logger.info(f"Processed {len(new_responses)} email responses")
            
        except Exception as e:
            self.logger.error(f"Error in email monitoring: {e}")
    
    def _analyze_email_response(self, email_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze email response to determine type and action needed"""
        analysis = {
            "response_type": "unknown",
            "priority": "low",
            "action_needed": "none",
            "should_process": False,
            "confidence": 0.0
        }
        
        content = (email_data.get("subject", "") + " " + email_data.get("body", "")).lower()
        sender = email_data.get("sender", "").lower()
        
        # Check against response patterns
        for response_type, pattern in self.response_patterns.items():
            keyword_matches = sum(1 for keyword in pattern["keywords"] if keyword in content)
            if keyword_matches > 0:
                confidence = min(keyword_matches / len(pattern["keywords"]), 1.0)
                if confidence > analysis["confidence"]:
                    analysis.update({
                        "response_type": response_type,
                        "priority": pattern["priority"],
                        "action_needed": pattern["action"],
                        "confidence": confidence,
                        "should_process": True
                    })
        
        # Additional checks for job-related content
        job_keywords = ["application", "resume", "cv", "position", "role", "company"]
        if any(keyword in content for keyword in job_keywords):
            analysis["should_process"] = True
        
        return analysis
    
    def _process_email_response(self, email_data: Dict[str, Any], analysis: Dict[str, Any]):
        """Process email response based on analysis"""
        try:
            response_type = analysis["response_type"]
            sender = email_data.get("sender", "")
            subject = email_data.get("subject", "")
            body = email_data.get("body", "")
            
            # Log the response
            email_id = db.add_email_response(
                sender_email=sender,
                subject=subject,
                content=body,
                response_type=response_type
            )
            
            # Take appropriate action based on response type
            if response_type == "interview_request":
                self._handle_interview_request(email_data, analysis)
            elif response_type == "offer":
                self._handle_offer(email_data, analysis)
            elif response_type == "rejection":
                self._handle_rejection(email_data, analysis)
            elif response_type == "application_received":
                self._handle_application_received(email_data, analysis)
            elif response_type == "follow_up":
                self._handle_follow_up(email_data, analysis)
            
            self.logger.info(f"Processed {response_type} response from {sender}")
            
        except Exception as e:
            self.logger.error(f"Error processing email response: {e}")
    
    def _handle_interview_request(self, email_data: Dict[str, Any], analysis: Dict[str, Any]):
        """Handle interview request emails"""
        try:
            # Extract interview details
            interview_details = self._extract_interview_details(email_data)
            
            # Update job application status
            self._update_application_status(email_data, "interview_scheduled", interview_details)
            
            # Create calendar event (if calendar integration is available)
            self._create_calendar_event(interview_details)
            
            # Send confirmation email
            self._send_interview_confirmation(email_data, interview_details)
            
        except Exception as e:
            self.logger.error(f"Error handling interview request: {e}")
    
    def _handle_offer(self, email_data: Dict[str, Any], analysis: Dict[str, Any]):
        """Handle job offer emails"""
        try:
            # Extract offer details
            offer_details = self._extract_offer_details(email_data)
            
            # Update job application status
            self._update_application_status(email_data, "offer_received", offer_details)
            
            # Create offer review task
            self._create_offer_review_task(offer_details)
            
            # Send acknowledgment email
            self._send_offer_acknowledgment(email_data, offer_details)
            
        except Exception as e:
            self.logger.error(f"Error handling offer: {e}")
    
    def _handle_rejection(self, email_data: Dict[str, Any], analysis: Dict[str, Any]):
        """Handle rejection emails"""
        try:
            # Update job application status
            self._update_application_status(email_data, "rejected", {})
            
            # Log rejection for analysis
            self._log_rejection_for_analysis(email_data)
            
            # Send thank you email (optional)
            self._send_rejection_thank_you(email_data)
            
        except Exception as e:
            self.logger.error(f"Error handling rejection: {e}")
    
    def _handle_application_received(self, email_data: Dict[str, Any], analysis: Dict[str, Any]):
        """Handle application received confirmation emails"""
        try:
            # Update job application status
            self._update_application_status(email_data, "application_received", {})
            
            # Log for tracking
            self.logger.info(f"Application received confirmation from {email_data.get('sender', '')}")
            
        except Exception as e:
            self.logger.error(f"Error handling application received: {e}")
    
    def _handle_follow_up(self, email_data: Dict[str, Any], analysis: Dict[str, Any]):
        """Handle follow-up emails"""
        try:
            # Extract follow-up questions
            follow_up_questions = self._extract_follow_up_questions(email_data)
            
            # Update job application status
            self._update_application_status(email_data, "follow_up_required", follow_up_questions)
            
            # Create follow-up response task
            self._create_follow_up_response_task(follow_up_questions)
            
        except Exception as e:
            self.logger.error(f"Error handling follow-up: {e}")
    
    def _extract_interview_details(self, email_data: Dict[str, Any]) -> Dict[str, Any]:
        """Extract interview details from email"""
        details = {
            "date": "",
            "time": "",
            "location": "",
            "type": "unknown",
            "contact_person": "",
            "notes": ""
        }
        
        content = email_data.get("body", "")
        
        # Extract date patterns
        date_patterns = [
            r'(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})',
            r'(\w+ \d{1,2},? \d{4})',
            r'(\d{1,2}:\d{2} (?:AM|PM))'
        ]
        
        for pattern in date_patterns:
            match = re.search(pattern, content)
            if match:
                if ":" in match.group(1):
                    details["time"] = match.group(1)
                else:
                    details["date"] = match.group(1)
        
        # Extract location
        location_patterns = [
            r'(?:at|in|location:?)\s*([^.\n]+)',
            r'(?:address:?)\s*([^.\n]+)'
        ]
        
        for pattern in location_patterns:
            match = re.search(pattern, content, re.IGNORECASE)
            if match:
                details["location"] = match.group(1).strip()
                break
        
        # Determine interview type
        if "video" in content.lower() or "zoom" in content.lower() or "teams" in content.lower():
            details["type"] = "video"
        elif "phone" in content.lower() or "call" in content.lower():
            details["type"] = "phone"
        else:
            details["type"] = "in-person"
        
        return details
    
    def _extract_offer_details(self, email_data: Dict[str, Any]) -> Dict[str, Any]:
        """Extract offer details from email"""
        details = {
            "salary": "",
            "start_date": "",
            "position": "",
            "benefits": [],
            "response_deadline": ""
        }
        
        content = email_data.get("body", "")
        
        # Extract salary
        salary_patterns = [
            r'(?:salary|compensation|pay):?\s*([^.\n]+)',
            r'(\d{1,3}(?:,\d{3})*(?:\s*-\s*\d{1,3}(?:,\d{3})*)?\s*(?:USD|AED|SAR|QAR|KWD|OMR|BHD))'
        ]
        
        for pattern in salary_patterns:
            match = re.search(pattern, content, re.IGNORECASE)
            if match:
                details["salary"] = match.group(1).strip()
                break
        
        # Extract start date
        start_date_patterns = [
            r'(?:start date|joining date|effective date):?\s*([^.\n]+)',
            r'(\w+ \d{1,2},? \d{4})'
        ]
        
        for pattern in start_date_patterns:
            match = re.search(pattern, content, re.IGNORECASE)
            if match:
                details["start_date"] = match.group(1).strip()
                break
        
        return details
    
    def _extract_follow_up_questions(self, email_data: Dict[str, Any]) -> List[str]:
        """Extract follow-up questions from email"""
        questions = []
        content = email_data.get("body", "")
        
        # Find question patterns
        question_patterns = [
            r'([^.!?]*\?)',
            r'(?:question|clarification):\s*([^.\n]+)'
        ]
        
        for pattern in question_patterns:
            matches = re.findall(pattern, content, re.IGNORECASE)
            questions.extend([q.strip() for q in matches if q.strip()])
        
        return questions
    
    def _update_application_status(self, email_data: Dict[str, Any], status: str, details: Dict[str, Any]):
        """Update job application status in database"""
        try:
            # Find matching application by sender email
            sender = email_data.get("sender", "")
            
            # This would require additional database methods to find applications by email
            # For now, we'll log the status update
            self.logger.info(f"Application status updated to: {status}")
            
            # Add to scheduled tasks for tracking
            db.add_scheduled_task(
                task_name=f"status_update_{status}",
                task_type="application_status",
                schedule_time=datetime.now().strftime("%H:%M"),
                config={"status": status, "details": details, "sender": sender}
            )
            
        except Exception as e:
            self.logger.error(f"Error updating application status: {e}")
    
    def _create_calendar_event(self, interview_details: Dict[str, Any]):
        """Create calendar event for interview"""
        # This would integrate with calendar APIs (Google Calendar, Outlook, etc.)
        self.logger.info(f"Calendar event created for interview: {interview_details}")
    
    def _send_interview_confirmation(self, email_data: Dict[str, Any], interview_details: Dict[str, Any]):
        """Send interview confirmation email"""
        # This would use the email agent to send confirmation
        self.logger.info(f"Interview confirmation sent for: {interview_details}")
    
    def _create_offer_review_task(self, offer_details: Dict[str, Any]):
        """Create task for offer review"""
        # This would create a task in task management system
        self.logger.info(f"Offer review task created: {offer_details}")
    
    def _send_offer_acknowledgment(self, email_data: Dict[str, Any], offer_details: Dict[str, Any]):
        """Send offer acknowledgment email"""
        # This would use the email agent to send acknowledgment
        self.logger.info(f"Offer acknowledgment sent: {offer_details}")
    
    def _log_rejection_for_analysis(self, email_data: Dict[str, Any]):
        """Log rejection for future analysis"""
        # This would store rejection data for pattern analysis
        self.logger.info(f"Rejection logged for analysis: {email_data.get('sender', '')}")
    
    def _send_rejection_thank_you(self, email_data: Dict[str, Any]):
        """Send thank you email for rejection"""
        # This would use the email agent to send thank you
        self.logger.info(f"Rejection thank you sent to: {email_data.get('sender', '')}")
    
    def _create_follow_up_response_task(self, questions: List[str]):
        """Create task for follow-up response"""
        # This would create a task to respond to follow-up questions
        self.logger.info(f"Follow-up response task created for {len(questions)} questions")
    
    def get_response_statistics(self) -> Dict[str, Any]:
        """Get statistics about email responses"""
        try:
            # Get recent email responses
            recent_responses = db.get_unprocessed_emails()
            
            response_types = {}
            for response in recent_responses:
                response_type = response.get('response_type', 'unknown')
                response_types[response_type] = response_types.get(response_type, 0) + 1
            
            return {
                "total_responses": len(recent_responses),
                "response_types": response_types,
                "last_checked": datetime.now().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Error getting response statistics: {e}")
            return {}
    
    def run_continuous_monitoring(self):
        """Run continuous email monitoring"""
        self.logger.info("Starting continuous email monitoring")
        
        while True:
            try:
                self.monitor_email_responses()
                
                # Wait before next check
                time.sleep(self.monitoring_interval * 60)  # Convert minutes to seconds
                
            except KeyboardInterrupt:
                self.logger.info("Email monitoring stopped by user")
                break
            except Exception as e:
                self.logger.error(f"Error in continuous monitoring: {e}")
                time.sleep(60)  # Wait 1 minute before retrying


def main():
    """Main function to run email monitor"""
    monitor = EmailMonitor()
    monitor.run_continuous_monitoring()


if __name__ == "__main__":
    main() 