from django.http import HttpResponse
from django.shortcuts import render
from twilio import twiml
WORKFLOW_SID = 1

def root(request):
    return render(request, 'index.html')

def incoming_call(request):
    resp = twiml.Response()
    with resp.gather(numDigits=1, action="/call/enqueue", method="POST") as g:
        g.say("For ACME Rockets, press one. For ACME TNT, press two.")
    return HttpResponse(resp)

def enqueue(request):
    resp = twiml.Response()
    with resp.enqueue(None, workflowSid=WORKFLOW_SID) as g:
        g.task('{"selected_product": "ACME Rockets"}')
    return HttpResponse(resp)