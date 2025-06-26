from django.db import models

# Create your models here.

class ParcelInfo(models.Model):
    file_name = models.CharField(max_length=255)
    parcel_number = models.CharField(max_length=100, blank=True, null=True)
    recipient_name = models.CharField(max_length=255, blank=True, null=True)
    recipient_address = models.TextField(blank=True, null=True)
    recipient_phone = models.CharField(max_length=50, blank=True, null=True)
    recipient_postal_code = models.CharField(max_length=20, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.parcel_number or '-'} - {self.recipient_name or '-'}"
