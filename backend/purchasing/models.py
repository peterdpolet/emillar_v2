# purchasing/models.py
import uuid
from django.db import models
from django.conf import settings
from partners.models import Supplier




class PurchaseOrder(models.Model):
    STATUS_CHOICES = [
        ('draft',     'Draft'),
        ('sent',      'Sent to Supplier'),
        ('partial',   'Partially Received'),
        ('complete',  'Complete'),
        ('cancelled', 'Cancelled'),
    ]

    id            = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    # Link to BusinessPartner rather than Supplier
    supplier      = models.ForeignKey(
                        'partners.BusinessPartner',
                        on_delete=models.PROTECT,
                        related_name='purchase_orders'
                    )
    reference     = models.CharField(max_length=100, blank=True)  # your PO ref
    supplier_ref  = models.CharField(max_length=100, blank=True)  # their ref
    status        = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    raised_by     = models.ForeignKey(
                        settings.AUTH_USER_MODEL,
                        on_delete=models.SET_NULL,
                        null=True, blank=True,
                        related_name='purchase_orders_raised'
                    )
    currency      = models.CharField(max_length=3, default='GBP')
    total         = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    po_pdf        = models.FileField(upload_to='purchase_orders/', null=True, blank=True)
    expected_date = models.DateField(null=True, blank=True)
    notes         = models.TextField(blank=True)
    created_at    = models.DateTimeField(auto_now_add=True)
    updated_at    = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f'PO-{self.reference} — {self.supplier.bp_name}'

    def recalculate_totals(self):
        self.total = sum(line.line_total for line in self.lines.all())
        self.save(update_fields=['total', 'updated_at'])

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
    item           = models.ForeignKey('inventory.Item', on_delete=models.PROTECT, related_name='po_lines')
    
    # Supplier's own reference for this item — critical for invoice matching
    supplier_sku   = models.CharField(max_length=100, blank=True)
    
    quantity          = models.PositiveIntegerField(default=1)
    unit_cost         = models.DecimalField(max_digits=10, decimal_places=2)
    quantity_received = models.PositiveIntegerField(default=0)

    @property
    def line_total(self):
        return self.unit_cost * self.quantity

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
        super().save(*args, **kwargs)
        self.purchase_order.recalculate_totals()

    def __str__(self):
        return f'{self.quantity}× {self.item.name}'


class GoodsReceipt(models.Model):
    id             = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    purchase_order = models.ForeignKey(PurchaseOrder, on_delete=models.PROTECT, related_name='goods_receipts')
    
    # Supplier's delivery note reference — key for matching
    delivery_ref   = models.CharField(max_length=100, blank=True)
    supplier_ref   = models.CharField(max_length=100, blank=True)  # their invoice/approval ref
    
    received_by    = models.ForeignKey(
                         settings.AUTH_USER_MODEL,
                         on_delete=models.SET_NULL,
                         null=True, blank=True,
                         related_name='goods_receipts'
                     )
    received_date  = models.DateField()
    notes          = models.TextField(blank=True)
    
    # AI extraction fields — populated by Claude Vision
    raw_image      = models.ImageField(upload_to='grn_images/', null=True, blank=True)
    extracted_data = models.JSONField(null=True, blank=True)  # raw Claude Vision output
    
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
        return f'{self.quantity_received}× {self.po_line.item.name}'