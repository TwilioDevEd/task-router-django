import json
from urllib.parse import quote_plus

from django.conf import settings
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt
from twilio.rest import Client
from twilio.twiml.messaging_response import MessagingResponse
from twilio.twiml.voice_response import VoiceResponse

from . import sms_sender, workspace
from .models import MissedCall

if not getattr(settings, 'TESTING', False):
    WORKSPACE_INFO = workspace.setup()
else:
    WORKSPACE_INFO = None

ACCOUNT_SID = settings.TWILIO_ACCOUNT_SID
AUTH_TOKEN = settings.TWILIO_AUTH_TOKEN
TWILIO_NUMBER = settings.TWILIO_NUMBER
EMAIL = settings.MISSED_CALLS_EMAIL_ADDRESS


def root(request):
    """ Renders a missed calls list, with product and phone number """
    missed_calls = MissedCall.objects.order_by('-created')
    return render(request, 'index.html', {
        'missed_calls': missed_calls
    })


@csrf_exempt
def incoming_sms(request):
    """ Changes worker activity and returns a confirmation """
    client = Client(ACCOUNT_SID, AUTH_TOKEN)
    activity = 'Available' if request.POST['Body'].lower().strip() == 'on' else 'Offline'
    activity_sid = WORKSPACE_INFO.activities[activity].sid
    worker_sid = WORKSPACE_INFO.workers[request.POST['From']]
    workspace_sid = WORKSPACE_INFO.workspace_sid

    client.workspaces(workspace_sid)\
          .workers(worker_sid)\
          .update(activity_sid=activity_sid)

    resp = MessagingResponse()
    message = 'Your status has changed to ' + activity
    resp.message(message)
    return HttpResponse(resp)


@csrf_exempt
def incoming_call(request):
    """ Returns TwiML instructions to Twilio's POST requests """
    resp = VoiceResponse()
    gather = resp.gather(numDigits=1, action=reverse('enqueue'), method="POST")
    gather.say("For Programmable SMS, press one. For Voice, press any other key.")

    return HttpResponse(resp)


@csrf_exempt
def enqueue(request):
    """ Parses a selected product, creating a Task on Task Router Workflow """
    resp = VoiceResponse()
    digits = request.POST['Digits']
    selected_product = 'ProgrammableSMS' if digits == '1' else 'ProgrammableVoice'
    task = {'selected_product': selected_product}

    enqueue = resp.enqueue(None, workflowSid=WORKSPACE_INFO.workflow_sid)
    enqueue.task(json.dumps(task))

    return HttpResponse(resp)


@csrf_exempt
def assignment(request):
    """ Task assignment """
    response = {'instruction': 'dequeue',
                'post_work_activity_sid': WORKSPACE_INFO.post_work_activity_sid}
    return JsonResponse(response)


@csrf_exempt
def events(request):
    """ Events callback for missed calls """
    POST = request.POST
    event_type = POST.get('EventType')
    task_events = ['workflow.timeout', 'task.canceled']
    worker_event = 'worker.activity.update'

    if event_type in task_events:
        task_attributes = json.loads(POST['TaskAttributes'])
        _save_missed_call(task_attributes)
        if event_type == 'workflow.timeout':
            _voicemail(task_attributes['call_sid'])
    elif event_type == worker_event and POST['WorkerActivityName'] == 'Offline':
        message = 'Your status has changed to Offline. Reply with '\
            '"On" to get back Online'
        worker_number = json.loads(POST['WorkerAttributes'])['contact_uri']
        sms_sender.send(to=worker_number, from_=TWILIO_NUMBER, body=message)

    return HttpResponse('')


def _voicemail(call_sid):
    msg = 'Sorry, All agents are busy. Please leave a message. We will call you as soon as possible'
    route_url = 'http://twimlets.com/voicemail?Email=' + EMAIL + '&Message=' + quote_plus(msg)
    route_call(call_sid, route_url)


def route_call(call_sid, route_url):
    client = Client(ACCOUNT_SID, AUTH_TOKEN)
    client.api.calls(call_sid).update(url=route_url)


def _save_missed_call(task_attributes):
    MissedCall.objects.create(
            phone_number=task_attributes['from'],
            selected_product=task_attributes['selected_product'])


# Only used by the tests in order to patch requests before any call is made
def setup_workspace():
    global WORKSPACE_INFO
    WORKSPACE_INFO = workspace.setup()
