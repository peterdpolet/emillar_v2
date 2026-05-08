import uuid
from django.db import models
from django.utils import timezone
from phonenumber_field.modelfields import PhoneNumberField



class Supplier(models.Model):
    name         = models.CharField(max_length=255)
    contact_name = models.CharField(max_length=255, blank=True)
    email        = models.EmailField(blank=True)
    phone        = models.CharField(max_length=50, blank=True)
    address      = models.TextField(blank=True)
    notes        = models.TextField(blank=True)
    is_active    = models.BooleanField(default=True)
    created_at   = models.DateTimeField(auto_now_add=True)
    updated_at   = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name

class BusinessPartner(models.Model):
    bp_id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    bp_type = models.CharField(max_length=10, null=True, blank=True)
    bp_int_ref = models.CharField(max_length=10,null=True, blank=True)
    bp_name = models.CharField(max_length=50)     
    bp_desc = models.TextField(max_length=250, null=True, blank=True)
    bp_alias_1 = models.CharField(max_length=30, null=True, blank=True)
    bp_alias_2 = models.CharField(max_length=30, null=True, blank=True)
    bp_comp_name = models.CharField(max_length=30, null=True, blank=True)
    bp_addr_1 = models.CharField(max_length=30, null=True, blank=True)
    bp_addr_2 = models.CharField(max_length=30, null=True, blank=True)
    bp_addr_3 = models.CharField(max_length=30, null=True, blank=True)
    bp_addr_4 = models.CharField(max_length=30, null=True, blank=True)
    bp_city = models.CharField(max_length=30, null=True, blank=True)
    bp_county = models.CharField(max_length=30, null=True, blank=True)
    bp_country = models.CharField(max_length=30, null=True, blank=True)
    bp_pcode = models.CharField(max_length=30, null=True, blank=True)
    bp_email = models.EmailField(max_length=30, null=True, blank=True)
    bp_tel = PhoneNumberField(max_length=30, null=True, blank=True)
    bp_mob = PhoneNumberField(max_length=30, null=True, blank=True)
    bp_fax = PhoneNumberField(max_length=30, null=True, blank=True)
    bp_whatsapp = models.CharField(max_length=30, null=True, blank=True)
    bp_fbook = models.CharField(max_length=30, null=True, blank=True)

    def __str__(self):
        return self.bp_name