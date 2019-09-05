from django.urls import include, path
from django.contrib import admin

urlpatterns = [
    # Your URLs go here
    path('', include('task_router.urls')),

    # Include the Django admin
    path('admin/', admin.site.urls),
]
