from twilio.util import TwilioCapability
from django.conf import settings


def generate(agent_id):
    account_sid = settings.TWILIO_ACCOUNT_SID
    auth_token = settings.TWILIO_AUTH_TOKEN
    capability = TwilioCapability(account_sid, auth_token)
    capability.allow_client_incoming(agent_id)
    return capability.generate()
