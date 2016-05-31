from django.conf.urls import url

from .views import root

urlpatterns = [
    # URLs for searching for and purchasing a new Twilio number
    url(r'^$', root, name='root'),
]
