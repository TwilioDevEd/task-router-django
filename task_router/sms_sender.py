from twilio.rest import TwilioRestClient
from django.conf import settings
ACCOUNT_SID = settings.TWILIO_ACCOUNT_SID
AUTH_TOKEN = settings.TWILIO_AUTH_TOKEN


def send(to, from_, body):
    client = TwilioRestClient(ACCOUNT_SID, AUTH_TOKEN)

    client.messages.create(to=to, from_=from_, body=body)
