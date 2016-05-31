from django.conf.urls import include, url
from django.contrib import admin
from django.contrib.auth import views as auth_views

urlpatterns = [
    # Your URLs go here
    url(r'^', include('task_router.urls')),

    # Include the Django admin
    url(r'^admin/', include(admin.site.urls)),
]
