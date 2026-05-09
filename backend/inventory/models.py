import uuid
from django.db import models
from partners.models import BusinessPartner

class Unit(models.Model):
    code = models.CharField(max_length=4, default='xxx')
    desc = models.CharField(max_length=15)  

    def __str__(self):
        return self.desc

class Type(models.Model):
    code_wards = models.CharField(max_length=50, default='xxx')
    code_internal = models.CharField(max_length=50, default='xxx')
    desc = models.CharField(max_length=100)  

    def __str__(self):
        return self.desc

class Cut(models.Model):
    code = models.CharField(max_length=30)
    desc = models.CharField(max_length=30)

    def __str__(self):
        return self.ss_desc

class Color(models.Model):
    code = models.CharField(max_length=30)
    desc = models.CharField(max_length=30)
    
    def __str__(self):
        return self.desc

class Clarity(models.Model):
    class Meta:
        ordering = ['num_code']
        verbose_name_plural = 'Clarities'

    code = models.CharField(max_length=10)
    num_code = models.IntegerField()
    desc = models.CharField(max_length=40)

    def __str__(self):
        return self.desc

class BatchType(models.Model):
    code = models.CharField(max_length=2)
    desc = models.CharField(max_length=15)
    def __str__(self):
        return self.desc

class Status(models.Model):
    code = models.CharField(max_length=5)
    desc = models.CharField(max_length=15)
    def __str__(self):
        return self.desc

class Currency(models.Model):
    code = models.CharField(max_length=5)
    desc = models.CharField(max_length=15)
    def __str__(self):
        return self.desc


class Item(models.Model):

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )   
    sku                  = models.CharField(max_length=100, unique=True, blank=True, null=True )
    name                 = models.CharField(max_length=255, blank=True, null=True )
    description          = models.TextField(blank=True)
    supplier             = models.ForeignKey(BusinessPartner ,related_name='partner', blank=True, null=True,  on_delete=models.PROTECT)
    status               = models.ForeignKey(Status, related_name='status', blank=True, null=True, on_delete=models.PROTECT)
    base_price           = models.DecimalField(max_digits=7, decimal_places=3, blank=True, null=True )
    currency             = models.ForeignKey(Currency, related_name='currency', blank=True, null=True,  on_delete=models.PROTECT)
    created_at           = models.DateTimeField(blank=True, null=True)
    updated_at           = models.DateTimeField(blank=True, null=True)
    def __str__(self):
        return self.sku

class GemDetail(models.Model):
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )
    item                 = models.OneToOneField(Item, related_name='item', on_delete=models.PROTECT)
    certification_number = models.CharField(max_length=30, blank=True, null=True )
    carat_weight         = models.DecimalField(max_digits=7, decimal_places=3, blank=True, null=True )
    origin               = models.CharField(max_length=30, blank=True, null=True )
    cut                  = models.ForeignKey(Cut, related_name='cut', blank=True, null=True, on_delete=models.PROTECT)
    clarity              = models.ForeignKey(Clarity, related_name='clarity', blank=True, null=True,  on_delete=models.PROTECT)
    color                = models.ForeignKey(Color, related_name='color', blank=True, null=True,  on_delete=models.PROTECT)
    def __str__(self):
        return self.item


