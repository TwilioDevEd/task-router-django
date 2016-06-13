from django.db import models
import phonenumbers
from phonenumbers import PhoneNumberFormat


class MissedCall(models.Model):
    """ A missed call from a customer, lets call them back! """

    selected_product = models.CharField(max_length=30)
    phone_number = models.CharField(max_length=30)
    created = models.DateTimeField(auto_now_add=True)

    @property
    def international_phone_number(self):
        """ Represents the number as +99 9999999 """
        parsed_number = phonenumbers.parse(self.phone_number)
        return phonenumbers.format_number(parsed_number,
                                          PhoneNumberFormat.INTERNATIONAL)
