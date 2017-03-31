from twilio.rest import Client
from django.conf import settings
ACCOUNT_SID = settings.TWILIO_ACCOUNT_SID
AUTH_TOKEN = settings.TWILIO_AUTH_TOKEN


def send(to, from_, body):
    client = Client(ACCOUNT_SID, AUTH_TOKEN)

    client.api.messages.create(to=to, from_=from_, body=body)
