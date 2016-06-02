from django.conf.urls import url

from .views import root
from .views import incoming_call
from .views import enqueue
from .views import assignment
from .views import agents

urlpatterns = [
    # URLs for searching for and purchasing a new Twilio number
    url(r'^$', root, name='root'),
    url(r'^call/incoming/?$', incoming_call, name='incoming_call'),
    url(r'^call/enqueue/?$', enqueue, name='enqueue'),
    url(r'^assignment/?$', assignment, name='assignment'),
    url(r'^agents/(?P<worker_sid>\w+)/?$', agents, name='agents'),
]
