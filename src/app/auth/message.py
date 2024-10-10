# import requests
# import logging
# import os

# # Load environment variables for sensitive data
# WHATSAPP_API_URL = f"https://graph.facebook.com/v20.0/{os.getenv('PHONE_NUMBER_ID')}/messages"
# WHATSAPP_API_TOKEN = os.getenv('WHATSAPP_API_TOKEN')

# def send_whatsapp_message(phone_number: str, message: str):
#     """
#     Sends a WhatsApp message to the specified phone number using the WhatsApp API.

#     Args:
#         phone_number (str): The phone number to send the message to.
#         message (str): The content of the message to be sent.

#     Returns:
#         bool: True if message was sent successfully, False otherwise.
#     """
#     try:
#         headers = {
#             'Authorization': f'Bearer {WHATSAPP_API_TOKEN}',
#             'Content-Type': 'application/json',
#         }
#         data = {
#             "messaging_product": "whatsapp",
#             "to": phone_number,
#             "type": "template",
#             "template": {
#                 "name": "hello_world",  # Assuming you're using a pre-approved template named 'hello_world'
#                 "language": {"code": "en_US"}
#             }
#         }
        
#         logging.info(f"Sending WhatsApp message to {phone_number} with data: {data} and headers: {headers}")
        
#         response = requests.post(WHATSAPP_API_URL, headers=headers, json=data)
#         response.raise_for_status()  # Raise an exception for HTTP errors
        
#         logging.info(f"WhatsApp message sent successfully to {phone_number}")
#         return True
#     except requests.exceptions.RequestException as e:
#         logging.error(f"Failed to send WhatsApp message to {phone_number}: {e}")
#         if e.response is not None:
#             logging.error(f"Response content: {e.response.content}")
#         return False


import requests
import logging
import os

# Load environment variables for sensitive data
PHONE_NUMBER_ID = os.getenv('PHONE_NUMBER_ID')
WHATSAPP_API_URL = f"https://graph.facebook.com/v20.0/{PHONE_NUMBER_ID}/messages"
WHATSAPP_API_TOKEN = os.getenv('WHATSAPP_API_TOKEN')

logging.info(f"Using PHONE_NUMBER_ID: {PHONE_NUMBER_ID}")

def send_whatsapp_message(phone_number: str, message: str):
    """
    Sends a WhatsApp message to the specified phone number using the WhatsApp API.

    Args:
        phone_number (str): The phone number to send the message to.
        message (str): The content of the message to be sent.

    Returns:
        bool: True if message was sent successfully, False otherwise.
    """
    try:
        headers = {
            'Authorization': f'Bearer {WHATSAPP_API_TOKEN}',
            'Content-Type': 'application/json',
        }
        data = {
            "messaging_product": "whatsapp",
            "to": phone_number,
            "type": "text",
            "text": {
                "body": message
            }
        }
        
        logging.info(f"Sending WhatsApp message to {phone_number} with data: {data} and headers: {headers}")
        
        response = requests.post(WHATSAPP_API_URL, headers=headers, json=data)
        response.raise_for_status()  # Raise an exception for HTTP errors
        
        logging.info(f"WhatsApp message sent successfully to {phone_number}")
        return True
    except requests.exceptions.RequestException as e:
        logging.error(f"Failed to send WhatsApp message to {phone_number}: {e}")
        if e.response is not None:
            logging.error(f"Response content: {e.response.content}")
        return False

