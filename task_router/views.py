from django.http import HttpResponse
from django.http import JsonResponse
from django.shortcuts import render
from twilio import twiml
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
WORKFLOW_SID = settings.WORKFLOW_SID
POST_WORK_ACTIVITY_SID = 'WAdd62089717e804041db4adc2efe4b47f'


def root(request):
    return render(request, 'index.html')


@csrf_exempt
def incoming_call(request):
    resp = twiml.Response()
    with resp.gather(numDigits=1, action="/call/enqueue", method="POST") as g:
        g.say("For ACME Rockets, press one. For ACME TNT, press two.")
    return HttpResponse(resp)


@csrf_exempt
def enqueue(request):
    resp = twiml.Response()
    with resp.enqueue(None, workflowSid=WORKFLOW_SID) as g:
        g.task('{"selected_product": "ACMERockets"}')
    return HttpResponse(resp)


@csrf_exempt
def assignment(request):
    response = {"instruction": "dequeue", "from": "+155",
                "post_work_activity_sid": POST_WORK_ACTIVITY_SID}
    return JsonResponse(response)
