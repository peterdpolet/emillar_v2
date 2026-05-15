# purchasing/models.py
import uuid
from django.db import models
from django.conf import settings


class PurchaseOrder(models.Model):
    STATUS_CHOICES = [
        ('draft',     'Draft'),
        ('sent',      'Sent to Supplier'),
        ('partial',   'Partially Received'),
        ('complete',  'Complete'),
        ('cancelled', 'Cancelled'),
    ]

    id           = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    supplier     = models.ForeignKey(
                       'partners.BusinessPartner',
                       on_delete=models.PROTECT,
                       related_name='purchase_orders'
                   )
    # Link back to originating Sales Order (RFQ) — optional (speculative buying)
    sales_order  = models.ForeignKey(
                       'sales.SalesOrder',
                       on_delete=models.SET_NULL,
                       null=True, blank=True,
                       related_name='purchase_orders'
                   )
    reference    = models.CharField(max_length=100, blank=True)   # our PO ref
    supplier_ref = models.CharField(max_length=100, blank=True)   # their ref
    status       = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    raised_by    = models.ForeignKey(
                       settings.AUTH_USER_MODEL,
                       on_delete=models.SET_NULL,
                       null=True, blank=True,
                       related_name='purchase_orders_raised'
                   )
    raised_date  = models.DateField(auto_now_add=True)

    # Currency — many suppliers price in USD
    currency     = models.CharField(max_length=3, default='USD')

    # FX at point of PO creation
    fx_rate      = models.DecimalField(max_digits=10, decimal_places=6, null=True, blank=True)
    fx_rate_date = models.DateField(null=True, blank=True)

    total        = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    total_gbp    = models.DecimalField(max_digits=12, decimal_places=2, default=0)

    expected_date = models.DateField(null=True, blank=True)
    notes        = models.TextField(blank=True)
    po_pdf       = models.FileField(upload_to='purchase_orders/', null=True, blank=True)

    created_at   = models.DateTimeField(auto_now_add=True)
    updated_at   = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f'PO-{self.reference} — {self.supplier.bp_name}'

    def recalculate_totals(self):
        self.total     = sum(line.line_total     for line in self.lines.all())
        self.total_gbp = sum(line.line_total_gbp for line in self.lines.all())
        self.save(update_fields=['total', 'total_gbp', 'updated_at'])

    def update_status(self):
        lines = self.lines.all()
        if not lines.exists():
            return
        if all(l.match_status == 'matched' for l in lines):
            self.status = 'complete'
        elif any(l.quantity_received > 0 for l in lines):
            self.status = 'partial'
        self.save(update_fields=['status', 'updated_at'])


class PurchaseOrderLine(models.Model):
    id             = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    purchase_order = models.ForeignKey(PurchaseOrder, on_delete=models.CASCADE, related_name='lines')

    # Optional — item may not exist in inventory yet at PO creation
    item           = models.ForeignKey(
                         'inventory.Item',
                         on_delete=models.PROTECT,
                         related_name='po_lines',
                         null=True, blank=True
                     )

    # Free-text description for when no inventory item exists yet
    description    = models.CharField(max_length=255, blank=True)

    # Supplier's own SKU — critical for invoice matching
    supplier_sku   = models.CharField(max_length=100, blank=True)

    quantity          = models.PositiveIntegerField(default=1)
    quantity_received = models.PositiveIntegerField(default=0)

    # Pricing in supplier currency
    unit_cost      = models.DecimalField(max_digits=10, decimal_places=2)
    currency       = models.CharField(max_length=3, default='USD')

    # FX conversion — locked at point of line creation
    fx_rate        = models.DecimalField(max_digits=10, decimal_places=6, null=True, blank=True)
    fx_rate_date   = models.DateField(null=True, blank=True)
    unit_cost_gbp  = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)

    notes          = models.TextField(blank=True)

    @property
    def line_total(self):
        return self.unit_cost * self.quantity

    @property
    def line_total_gbp(self):
        if self.unit_cost_gbp is not None:
            return self.unit_cost_gbp * self.quantity
        return 0

    @property
    def outstanding(self):
        return self.quantity - self.quantity_received

    @property
    def match_status(self):
        if self.quantity_received == 0:
            return 'not_received'
        if self.quantity_received < self.quantity:
            return 'short'
        if self.quantity_received == self.quantity:
            return 'matched'
        return 'over'

    def save(self, *args, **kwargs):
        # Auto-calculate GBP if rate provided
        if self.fx_rate and self.unit_cost:
            self.unit_cost_gbp = round(self.unit_cost / self.fx_rate, 2)
        super().save(*args, **kwargs)
        self.purchase_order.recalculate_totals()

    def __str__(self):
        name = self.item.name if self.item else self.description
        return f'{self.quantity}× {name}'


class GoodsReceipt(models.Model):
    id             = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    purchase_order = models.ForeignKey(PurchaseOrder, on_delete=models.PROTECT, related_name='goods_receipts')

    delivery_ref   = models.CharField(max_length=100, blank=True)  # supplier delivery note
    supplier_ref   = models.CharField(max_length=100, blank=True)  # their invoice/appro ref

    received_by    = models.ForeignKey(
                         settings.AUTH_USER_MODEL,
                         on_delete=models.SET_NULL,
                         null=True, blank=True,
                         related_name='goods_receipts'
                     )
    received_date  = models.DateField()
    notes          = models.TextField(blank=True)

    # AI extraction — populated by Claude Vision
    raw_image      = models.ImageField(upload_to='grn_images/', null=True, blank=True)
    extracted_data = models.JSONField(null=True, blank=True)

    created_at     = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-received_date', '-created_at']

    def __str__(self):
        return f'GRN-{self.pk} — {self.purchase_order.reference}'


class GoodsReceiptLine(models.Model):
    DISCREPANCY_CHOICES = [
        ('none',    'None'),
        ('short',   'Short delivery'),
        ('over',    'Over delivery'),
        ('damaged', 'Damaged'),
        ('wrong',   'Wrong item'),
    ]

    id                = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    goods_receipt     = models.ForeignKey(GoodsReceipt, on_delete=models.CASCADE, related_name='lines')
    po_line           = models.ForeignKey(PurchaseOrderLine, on_delete=models.PROTECT, related_name='receipt_lines')
    quantity_received = models.PositiveIntegerField(default=0)
    discrepancy       = models.CharField(max_length=20, choices=DISCREPANCY_CHOICES, default='none')
    discrepancy_note  = models.TextField(blank=True)

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        self._update_po_line_received()

    def _update_po_line_received(self):
        total = sum(rl.quantity_received for rl in self.po_line.receipt_lines.all())
        self.po_line.quantity_received = total
        self.po_line.save(update_fields=['quantity_received'])
        self.po_line.purchase_order.update_status()

    def __str__(self):
        name = self.po_line.item.name if self.po_line.item else self.po_line.description
        return f'{self.quantity_received}× {name}'

class SupplierQuote(models.Model):
    STATUS_CHOICES = [
        ('requested', 'Requested'),
        ('received',  'Received'),
        ('accepted',  'Accepted'),
        ('rejected',  'Rejected'),
        ('expired',   'Expired'),
    ]

    id          = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    so_line     = models.ForeignKey(
                      'sales.SalesOrderLine',
                      on_delete=models.CASCADE,
                      related_name='quotes'
                  )
    supplier    = models.ForeignKey(
                      'partners.BusinessPartner',
                      on_delete=models.PROTECT,
                      related_name='quotes'
                  )
    status      = models.CharField(max_length=20, choices=STATUS_CHOICES, default='requested')

    # Pricing — may be blank until supplier responds
    price        = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    currency     = models.CharField(max_length=3, default='USD')
    fx_rate      = models.DecimalField(max_digits=10, decimal_places=6, null=True, blank=True)
    fx_rate_date = models.DateField(null=True, blank=True)
    price_gbp    = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)

    supplier_sku = models.CharField(max_length=100, blank=True)
    valid_until  = models.DateField(null=True, blank=True)
    notes        = models.TextField(blank=True)

    created_at   = models.DateTimeField(auto_now_add=True)
    updated_at   = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        # One quote per supplier per SO line
        unique_together = [('so_line', 'supplier')]

    def save(self, *args, **kwargs):
        # Auto-calculate GBP equivalent
        if self.fx_rate and self.price:
            self.price_gbp = round(self.price / self.fx_rate, 2)
        elif self.currency == 'GBP' and self.price:
            self.price_gbp = self.price
        super().save(*args, **kwargs)

    def accept(self):
        """Accept this quote — reject all siblings, update SO line."""
        # Reject all other quotes for this SO line
        SupplierQuote.objects.filter(
            so_line=self.so_line
        ).exclude(pk=self.pk).update(status='rejected')

        self.status = 'accepted'
        self.save()

        # Update SO line with winning supplier and supplier SKU
        self.so_line.supplier = self.supplier
        self.so_line.supplier_sku = self.supplier_sku
        self.so_line.status = 'quoted'
        self.so_line.save(update_fields=['supplier', 'supplier_sku', 'status'])

    def __str__(self):
        return f'Quote {self.supplier.bp_name} → {self.so_line}'