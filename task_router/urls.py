from django.conf.urls import url

from .views import root
from .views import incoming_call

urlpatterns = [
    # URLs for searching for and purchasing a new Twilio number
    url(r'^$', root, name='root'),
    url(r'^call/incoming/?$', incoming_call, name='incoming_call'),
]
