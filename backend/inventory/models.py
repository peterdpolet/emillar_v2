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


class StockMovement(models.Model):
    TRANSACTION_TYPES = [
        ('opening',          'Opening stock'),
        ('counted',          'Stock count adjustment'),
        ('appro_in',         'Received from supplier on appro'),
        ('appro_out',        'Issued to customer on appro'),
        ('appro_return_in',  'Returned from customer'),
        ('appro_return_out', 'Returned to supplier'),
        ('purchased',        'Purchased from supplier'),
        ('sold',             'Sold to customer'),
        ('adjustment',       'Manual adjustment'),
    ]

    id               = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    transaction_type = models.CharField(max_length=20, choices=TRANSACTION_TYPES)
    date             = models.DateField()

    # The item — certified stones reference Item, parcels use description
    item             = models.ForeignKey(
                           Item,
                           on_delete=models.PROTECT,
                           null=True, blank=True,
                           related_name='movements'
                       )
    appro_reference  = models.CharField(max_length=50, blank=True, db_index=True)
    parcel_description = models.CharField(max_length=255, blank=True)

    # Quantity — count for certified, weight for parcels
    quantity         = models.PositiveIntegerField(default=0)
    weight_carats    = models.DecimalField(max_digits=10, decimal_places=3, null=True, blank=True)
    price_per_carat  = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)

    # Value
    unit_value       = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    currency         = models.CharField(max_length=3, default='USD')

    # Linked documents
    purchase_order   = models.ForeignKey(
                           'purchasing.PurchaseOrder',
                           on_delete=models.SET_NULL,
                           null=True, blank=True,
                           related_name='stock_movements'
                       )
    customer_memo    = models.ForeignKey(
                           'sales.SalesOrder',
                           on_delete=models.SET_NULL,
                           null=True, blank=True,
                           related_name='stock_movements'
                       )
    supplier         = models.ForeignKey(
                           'partners.BusinessPartner',
                           on_delete=models.SET_NULL,
                           null=True, blank=True,
                           related_name='supplier_movements'
                       )
    customer         = models.ForeignKey(
                           'partners.BusinessPartner',
                           on_delete=models.SET_NULL,
                           null=True, blank=True,
                           related_name='customer_movements'
                       )

    # Audit
    created_by       = models.ForeignKey(
                           'accounts.CustomUser',
                           on_delete=models.SET_NULL,
                           null=True, blank=True,
                           related_name='stock_movements'
                       )
    created_at       = models.DateTimeField(auto_now_add=True)
    notes            = models.TextField(blank=True)

    class Meta:
        ordering = ['-date', '-created_at']

    @classmethod
    def generate_appro_reference(cls):
        from django.utils import timezone
        year = timezone.now().year
        prefix = f'APPRO-{year}-'
        last = cls.objects.filter(
            appro_reference__startswith=prefix
        ).order_by('-appro_reference').first()
        if last:
            try:
                last_num = int(last.appro_reference.split('-')[-1])
            except ValueError:
                last_num = 0
        else:
            last_num = 0
        return f'{prefix}{str(last_num + 1).zfill(3)}'

    def __str__(self):
        item_ref = self.item.sku if self.item else self.parcel_description
        return f'{self.get_transaction_type_display()} — {item_ref} — {self.date}'

    @property
    def value(self):
        """Total value of this movement."""
        if self.weight_carats and self.price_per_carat:
            return self.weight_carats * self.price_per_carat
        if self.unit_value and self.quantity:
            return self.unit_value * self.quantity
        return