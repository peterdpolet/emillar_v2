import uuid
from django.db import models
from django.conf import settings
from django.utils import timezone
from datetime import timedelta


class SalesOrder(models.Model):
    STATUS_CHOICES = [
        ('draft',           'Draft'),
        ('active',          'Active'),
        ('part_fulfilled',  'Part Fulfilled'),
        ('fulfilled',       'Fulfilled'),
        ('cancelled',       'Cancelled'),
    ]

    so_id       = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    reference   = models.CharField(max_length=20, unique=True, blank=True)
    customer    = models.ForeignKey(
        'partners.BusinessPartner',
        on_delete=models.PROTECT,
        related_name='sales_orders',
        limit_choices_to={'bp_type': 'CUST'}
    )
    raised_by   = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name='sales_orders_raised'
    )
    raised_date = models.DateField(auto_now_add=True)
    status      = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    currency    = models.CharField(max_length=3, default='GBP')
    notes            = models.TextField(blank=True)
    customer_po_ref  = models.CharField(max_length=50, blank=True)
    required_by      = models.DateField(null=True, blank=True)
    delivery_address = models.ForeignKey(
        'partners.BusinessPartnerAddress',
        null=True, blank=True,
        on_delete=models.PROTECT,
        related_name='sales_orders'
    )
    created_at  = models.DateTimeField(auto_now_add=True)
    updated_at  = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.reference} — {self.customer.bp_name}"

    def save(self, *args, **kwargs):
        if not self.reference:
            year = timezone.now().year
            count = SalesOrder.objects.filter(
                raised_date__year=year
            ).count() + 1
            self.reference = f"SO-{year}-{count:04d}"
        super().save(*args, **kwargs)


class SalesOrderLine(models.Model):
    STATUS_CHOICES = [
        ('requested',            'Requested'),
        ('rfq_sent',             'RFQ Sent'),
        ('quoted',               'Quoted'),
        ('on_order',             'On Order'),
        ('on_approval',          'On Approval'),
        ('confirmed',            'Confirmed'),
        ('returned',             'Returned'),
        ('returned_to_supplier', 'Returned to Supplier'),
        ('cancelled',            'Cancelled'),
    ]

    ITEM_TYPE_CHOICES = [
        ('certified',   'Certified Stone'),
        ('uncertified', 'Uncertified Stone'),
    ]

    STONE_TYPE_CHOICES = [
        ('diamond',  'Diamond'),
        ('ruby',     'Ruby'),
        ('sapphire', 'Sapphire'),
        ('emerald',  'Emerald'),
        ('pearl',    'Pearl'),
        ('other',    'Other'),
    ]

    CERT_TYPE_CHOICES = [
        ('GIA', 'GIA'),
        ('IGI', 'IGI'),
        ('HRD', 'HRD'),
        ('AGS', 'AGS'),
    ]

    sol_id          = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    sales_order     = models.ForeignKey(SalesOrder, on_delete=models.CASCADE, related_name='lines')
    line_number     = models.PositiveIntegerField(default=1)
    quantity        = models.PositiveIntegerField(default=1)
    stone_type      = models.CharField(max_length=20, choices=STONE_TYPE_CHOICES)
    item_type       = models.CharField(max_length=20, choices=ITEM_TYPE_CHOICES, default='uncertified')
    status          = models.CharField(max_length=30, choices=STATUS_CHOICES, default='requested')

    # Winning supplier — set when a quote is accepted
    supplier        = models.ForeignKey(
        'partners.BusinessPartner',
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='so_lines'
    )
    supplier_sku    = models.CharField(max_length=100, blank=True)

    # Link to stock item — set when fulfilled from stock
    inventory_item  = models.ForeignKey(
        'inventory.Item',
        on_delete=models.PROTECT,
        null=True, blank=True,
        related_name='sales_lines'
    )

    # ── Stone specification fields ──────────────────────────
    min_size        = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True)
    preferred_size  = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True)
    max_size        = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True)

    min_carat       = models.DecimalField(max_digits=8, decimal_places=3, null=True, blank=True)
    preferred_carat = models.DecimalField(max_digits=8, decimal_places=3, null=True, blank=True)
    max_carat       = models.DecimalField(max_digits=8, decimal_places=3, null=True, blank=True)

    colour_spec     = models.CharField(max_length=50, blank=True)
    clarity_spec    = models.CharField(max_length=50, blank=True)

    min_price       = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    max_price       = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)

    # ── Certified stone fields ──────────────────────────────
    certificate_type    = models.CharField(max_length=10, choices=CERT_TYPE_CHOICES, blank=True)
    certificate_number  = models.CharField(max_length=50, blank=True)

    # ── Fulfillment fields ──────────────────────────────────
    agreed_price    = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    notes           = models.TextField(blank=True)

    class Meta:
        ordering = ['line_number']

    def __str__(self):
        return f"{self.sales_order.reference} / Line {self.line_number} — {self.stone_type}"

    @property
    def is_high_conversion(self):
        return self.item_type == 'certified' and bool(self.certificate_number)


class ApprovalNote(models.Model):
    STATUS_CHOICES = [
        ('active',    'Active'),
        ('confirmed', 'Confirmed'),
        ('returned',  'Returned'),
        ('expired',   'Expired'),
    ]

    APPROVAL_DAYS_CHOICES = [
        (14, '14 days'),
        (28, '28 days'),
    ]

    CERT_TYPE_CHOICES = [
        ('GIA', 'GIA'),
        ('IGI', 'IGI'),
        ('HRD', 'HRD'),
        ('AGS', 'AGS'),
    ]

    RETURN_TYPE_CHOICES = [
        ('to_stock',    'Return to Stock'),
        ('to_supplier', 'Return to Supplier'),
    ]

    approval_id         = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    reference           = models.CharField(max_length=20, unique=True, blank=True)
    sales_order_line    = models.OneToOneField(
        SalesOrderLine,
        on_delete=models.PROTECT,
        related_name='approval_note'
    )
    customer            = models.ForeignKey(
        'partners.BusinessPartner',
        on_delete=models.PROTECT,
        related_name='approval_notes'
    )
    issued_by           = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name='approval_notes_issued'
    )
    issued_date         = models.DateField()
    approval_days       = models.IntegerField(choices=APPROVAL_DAYS_CHOICES, default=14)
    expiry_date         = models.DateField(editable=False)
    certificate_type    = models.CharField(max_length=10, choices=CERT_TYPE_CHOICES, blank=True)
    certificate_number  = models.CharField(max_length=50, blank=True)
    agreed_price        = models.DecimalField(max_digits=12, decimal_places=2)
    currency            = models.CharField(max_length=3, default='GBP')
    status              = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    confirmed_date      = models.DateField(null=True, blank=True)
    returned_date       = models.DateField(null=True, blank=True)
    return_type         = models.CharField(max_length=20, choices=RETURN_TYPE_CHOICES, blank=True)
    notes               = models.TextField(blank=True)

    class Meta:
        ordering = ['expiry_date']

    def __str__(self):
        return f"{self.reference} — {self.customer.bp_name}"

    def save(self, *args, **kwargs):
        if not self.reference:
            year = timezone.now().year
            count = ApprovalNote.objects.filter(
                issued_date__year=year
            ).count() + 1
            self.reference = f"AN-{year}-{count:04d}"
        if self.issued_date:
            self.expiry_date = self.issued_date + timedelta(days=self.approval_days)
        super().save(*args, **kwargs)

    @property
    def days_remaining(self):
        return (self.expiry_date - timezone.now().date()).days

    @property
    def is_expiring_soon(self):
        return 0 <= self.days_remaining <= 7

    @property
    def is_expired(self):
        return self.days_remaining < 0