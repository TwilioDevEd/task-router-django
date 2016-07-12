from django.conf.urls import url

from .views import root
from .views import incoming_call
from .views import incoming_sms
from .views import enqueue
from .views import assignment
from .views import events

urlpatterns = [
    # URLs for handling TaskRouter requests
    url(r'^$', root, name='root'),
    url(r'^sms/incoming/?$', incoming_sms, name='incoming_sms'),
    url(r'^call/incoming/?$', incoming_call, name='incoming_call'),
    url(r'^call/enqueue/?$', enqueue, name='enqueue'),
    url(r'^assignment/?$', assignment, name='assignment'),
    url(r'^events/?$', events, name='events')
]
