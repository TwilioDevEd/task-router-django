from django.http import HttpResponse
from django.http import JsonResponse
from django.shortcuts import render
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from twilio import twiml
from .models import MissedCall
from twilio.rest import TwilioRestClient
import json
WORKFLOW_SID = settings.WORKFLOW_SID
POST_WORK_ACTIVITY_SID = settings.POST_WORK_ACTIVITY_SID
ACCOUNT_SID = settings.TWILIO_ACCOUNT_SID
AUTH_TOKEN = settings.TWILIO_AUTH_TOKEN


def root(request):
    missed_calls = MissedCall.objects.order_by('created')
    return render(request, 'index.html', {
        'missed_calls': missed_calls
    })


@csrf_exempt
def incoming_call(request):
    resp = twiml.Response()
    with resp.gather(numDigits=1, action="/call/enqueue", method="POST") as g:
        g.say("For Programmable SMS, press one. For Voice, press any other key.")
    return HttpResponse(resp)


@csrf_exempt
def enqueue(request):
    resp = twiml.Response()
    digits = request.POST['Digits']
    selected_product = 'ProgrammableSMS' if digits == '1' else 'ProgrammableVoice'
    with resp.enqueue(None, workflowSid=WORKFLOW_SID) as e:
        e.task('{"selected_product": "%s"}' % selected_product)
    return HttpResponse(resp)


@csrf_exempt
def assignment(request):
    response = {"instruction": "dequeue",
                "post_work_activity_sid": POST_WORK_ACTIVITY_SID}
    return JsonResponse(response)


@csrf_exempt
def events(request):
    event_type = request.POST.get('EventType')
    desired_events = ['workflow.timeout', 'task.canceled']

    if event_type in desired_events:
        task_attributes = json.loads(request.POST['TaskAttributes'])
        MissedCall.objects.create(
            phone_number=task_attributes['from'],
            selected_product=task_attributes['selected_product'])
        _hangup_call(task_attributes['call_sid'])

    return HttpResponse('')


def _hangup_call(call_sid):
    client = TwilioRestClient(ACCOUNT_SID, AUTH_TOKEN)
    client.calls.update(call_sid, status="completed")
