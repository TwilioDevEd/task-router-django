from django.db import models


class MissedCall(models.Model):

    selected_product = models.CharField(max_length=30)
    phone_number = models.CharField(max_length=30)
    created = models.DateTimeField(auto_now_add=True)
