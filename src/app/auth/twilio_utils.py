import os
from twilio.rest import Client
from dotenv import load_dotenv

load_dotenv()  # Load environment variables from the .env file

def send_whatsapp_message(to: str, body: str):
    account_sid = os.getenv('TWILIO_ACCOUNT_SID')
    auth_token = os.getenv('TWILIO_AUTH_TOKEN')
    from_whatsapp = os.getenv('TWILIO_WHATSAPP_FROM')

    client = Client(account_sid, auth_token)
    
    message = client.messages.create(
        from_=from_whatsapp,
        body=body,
        to=f'whatsapp:{to}'
    )

    return message.sid
