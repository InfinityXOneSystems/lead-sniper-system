'''
Lead Sniper - Alert and Notification System

This component is responsible for sending multi-channel notifications for high-priority leads, integrating with Manus Core, Vision Cortex, and Vertex AI.
'''

import os
import json
import requests
import logging
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
from twilio.rest import Client

# Initialize logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Load configuration
with open('config.json', 'r') as config_file:
    config = json.load(config_file)

env = os.environ.get("LEAD_SNIPER_ENV", "development")
app_config = config[env]

# Configuration
SENDGRID_API_KEY = app_config.get("sendgrid_api_key")
TWILIO_ACCOUNT_SID = app_config.get("twilio_account_sid")
TWILIO_AUTH_TOKEN = app_config.get("twilio_auth_token")
TWILIO_PHONE_NUMBER = app_config.get("twilio_phone_number")

class ManusCoreIntegration:
    def __init__(self):
        logging.info("Initializing Manus Core Integration")

    def get_lead_context(self, lead_id):
        logging.info(f"Fetching context for lead {lead_id} from Manus Core")
        # Placeholder for actual Manus Core API call
        return {"manus_core_insight": "This lead is highly engaged."}

class VisionCortexIntegration:
    def __init__(self):
        logging.info("Initializing Vision Cortex Integration")

    def analyze_lead_image(self, image_url):
        logging.info(f"Analyzing image {image_url} with Vision Cortex")
        # Placeholder for actual Vision Cortex API call
        return {"vision_cortex_insight": "Logo detected: Example Corp"}

class VertexAIIntegration:
    def __init__(self):
        logging.info("Initializing Vertex AI Integration")

    def get_lead_score(self, lead_data):
        logging.info(f"Scoring lead with Vertex AI")
        # Placeholder for actual Vertex AI API call
        return {"vertex_ai_score": 0.95}

class AlertAndNotificationSystem:
    def __init__(self):
        '''
        Initializes the Alert and Notification System.
        '''
        self.sendgrid_client = SendGridAPIClient(SENDGRID_API_KEY)
        self.twilio_client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
        self.manus_core = ManusCoreIntegration()
        self.vision_cortex = VisionCortexIntegration()
        self.vertex_ai = VertexAIIntegration()

    def send_email(self, to_email, subject, content):
        '''
        Sends an email notification.
        '''
        message = Mail(
            from_email='alerts@leadsniper.com',
            to_emails=to_email,
            subject=subject,
            html_content=content
        )
        try:
            response = self.sendgrid_client.send(message)
            logging.info(f"Email sent to {to_email} with status code {response.status_code}")
        except Exception as e:
            logging.error(f"Error sending email: {e}")

    def send_sms(self, to_number, message):
        '''
        Sends an SMS notification.
        '''
        try:
            message = self.twilio_client.messages.create(
                body=message,
                from_=TWILIO_PHONE_NUMBER,
                to=to_number
            )
            logging.info(f"SMS sent to {to_number} with SID {message.sid}")
        except Exception as e:
            logging.error(f"Error sending SMS: {e}")

    def send_webhook(self, url, data):
        '''
        Sends a webhook notification.
        '''
        try:
            response = requests.post(url, json=data)
            logging.info(f"Webhook sent to {url} with status code {response.status_code}")
        except Exception as e:
            logging.error(f"Error sending webhook: {e}")

    def process_notification(self, notification_data):
        '''
        Processes a notification request and sends it to the appropriate channels.
        '''
        lead_data = notification_data.get('lead')
        notification_channels = notification_data.get('channels')

        if not lead_data or not notification_channels:
            logging.error("Invalid notification data")
            return

        # Augment lead data with insights from other systems
        lead_data['manus_core_context'] = self.manus_core.get_lead_context(lead_data.get('id'))
        lead_data['vision_cortex_analysis'] = self.vision_cortex.analyze_lead_image(lead_data.get('profile_image_url'))
        lead_data['vertex_ai_score'] = self.vertex_ai.get_lead_score(lead_data)

        subject = f"High-Priority Lead: {lead_data.get('name')}"
        content = f"""
        A new high-priority lead has been identified:
        - Name: {lead_data.get('name')}
        - Email: {lead_data.get('email')}
        - Phone: {lead_data.get('phone')}
        - Company: {lead_data.get('company')}
        - Manus Core Insight: {lead_data['manus_core_context']['manus_core_insight']}
        - Vision Cortex Insight: {lead_data['vision_cortex_analysis']['vision_cortex_insight']}
        - Vertex AI Score: {lead_data['vertex_ai_score']['vertex_ai_score']}
        """

        if "email" in notification_channels:
            self.send_email(notification_channels["email"], subject, content)

        if "sms" in notification_channels:
            self.send_sms(notification_channels["sms"], subject)

        if "webhook" in notification_channels:
            self.send_webhook(notification_channels["webhook"], lead_data)

if __name__ == "__main__":
    # Example usage
    notification_system = AlertAndNotificationSystem()
    example_notification = {
        "lead": {
            "id": "12345",
            "name": "John Doe",
            "email": "john.doe@example.com",
            "phone": "+15551234567",
            "company": "Example Corp",
            "profile_image_url": "https://example.com/profile.jpg"
        },
        "channels": {
            "email": "sales@example.com",
            "sms": "+15557654321",
            "webhook": "https://example.com/webhook-endpoint"
        }
    }
    notification_system.process_notification(example_notification)
