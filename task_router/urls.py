from django.urls import path

from .views import root
from .views import incoming_call
from .views import incoming_sms
from .views import enqueue
from .views import assignment
from .views import events

urlpatterns = [
    # URLs for handling TaskRouter requests
    path('', root, name='root'),
    path('sms/incoming/', incoming_sms, name='incoming_sms'),
    path('call/incoming/', incoming_call, name='incoming_call'),
    path('call/enqueue/', enqueue, name='enqueue'),
    path('assignment/', assignment, name='assignment'),
    path('events/', events, name='events')
]
