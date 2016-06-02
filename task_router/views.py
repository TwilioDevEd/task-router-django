from django.http import HttpResponse
from django.http import JsonResponse
from django.shortcuts import render
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from twilio import twiml
from twilio.task_router import TaskRouterWorkerCapability
ACCOUNT_SID = settings.TWILIO_ACCOUNT_SID
AUTH_TOKEN = settings.TWILIO_AUTH_TOKEN
WORKSPACE_SID = settings.WORKSPACE_SID
WORKFLOW_SID = settings.WORKFLOW_SID
POST_WORK_ACTIVITY_SID = 'WAdd62089717e804041db4adc2efe4b47f'


def root(request):
    return render(request, 'index.html')


@csrf_exempt
def incoming_call(request):
    resp = twiml.Response()
    with resp.gather(numDigits=1, action="/call/enqueue", method="POST") as g:
        g.say("For ACME Rockets, press one. For ACME TNT, press any other key.")
    return HttpResponse(resp)


@csrf_exempt
def enqueue(request):
    resp = twiml.Response()
    digits = request.POST['Digits']
    selected_product = 'ACMERockets' if digits == '1' else 'ACMETNT'
    with resp.enqueue(None, workflowSid=WORKFLOW_SID) as g:
        g.task('{"selected_product": "%s"}' % selected_product)
    return HttpResponse(resp)


@csrf_exempt
def assignment(request):
    response = {"instruction": "dequeue",
                "post_work_activity_sid": POST_WORK_ACTIVITY_SID}
    return JsonResponse(response)


def agents(request, worker_sid):
    worker_capability = TaskRouterWorkerCapability(ACCOUNT_SID, AUTH_TOKEN, WORKSPACE_SID, worker_sid)
    worker_capability.allow_activity_updates()
    worker_capability.allow_reservation_updates()

    worker_token = worker_capability.generate_token()

    return render(request, 'agent.html', {'worker_token': worker_token})