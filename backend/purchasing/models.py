# purchasing/models.py
from django.db import models
from django.conf import settings
from partners.models import Supplier


class Item(models.Model):
    """
    Stock item / product catalogue entry.
    Referenced by both OrderLine and PurchaseOrderLine.
    """
    STATUS_CHOICES = [
        ('active',   'Active'),
        ('inactive', 'Inactive'),
        ('archived', 'Archived'),
    ]

    sku                  = models.CharField(max_length=100, unique=True)
    name                 = models.CharField(max_length=255)
    description          = models.TextField(blank=True)
    status               = models.CharField(
                               max_length=20,
                               choices=STATUS_CHOICES,
                               default='active'
                           )

    # Precious stone specific
    certification_number = models.CharField(max_length=100, blank=True,
                               help_text='e.g. GIA certificate number')
    carat_weight         = models.DecimalField(
                               max_digits=8, decimal_places=3,
                               null=True, blank=True
                           )
    origin               = models.CharField(max_length=100, blank=True)

    # Pricing
    base_price           = models.DecimalField(
                               max_digits=12, decimal_places=2,
                               null=True, blank=True
                           )
    currency             = models.CharField(max_length=3, default='GBP')

    created_at           = models.DateTimeField(auto_now_add=True)
    updated_at           = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['sku']

    def __str__(self):
        return f'{self.sku} — {self.name}'


class PurchaseOrder(models.Model):
    STATUS_CHOICES = [
        ('draft',     'Draft'),
        ('sent',      'Sent to Supplier'),
        ('partial',   'Partially Received'),
        ('complete',  'Complete'),
        ('cancelled', 'Cancelled'),
    ]

    supplier      = models.ForeignKey(
                        Supplier,
                        on_delete=models.PROTECT,
                        related_name='purchase_orders'
                    )
    reference     = models.CharField(
                        max_length=100, blank=True,
                        help_text='Internal PO reference number'
                    )
    supplier_ref  = models.CharField(
                        max_length=100, blank=True,
                        help_text='Supplier order reference if provided'
                    )
    status        = models.CharField(
                        max_length=20,
                        choices=STATUS_CHOICES,
                        default='draft'
                    )
    raised_by     = models.ForeignKey(
                        settings.AUTH_USER_MODEL,
                        on_delete=models.SET_NULL,
                        null=True, blank=True,
                        related_name='purchase_orders_raised'
                    )
    currency      = models.CharField(max_length=3, default='GBP')

    # Stored totals — consistent with Order, avoids N+1 in PDF generation
    total         = models.DecimalField(
                        max_digits=12, decimal_places=2,
                        default=0
                    )

    # PDF storage — pre-generated for slow networks
    po_pdf        = models.FileField(
                        upload_to='purchase_orders/',
                        null=True, blank=True
                    )

    expected_date = models.DateField(null=True, blank=True)
    notes         = models.TextField(blank=True)
    created_at    = models.DateTimeField(auto_now_add=True)
    updated_at    = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f'PO-{self.pk:04d} — {self.supplier.name}'

    def recalculate_totals(self):
        """Mirrors Order.recalculate_totals — called after lines change."""
        self.total = sum(
            line.line_total for line in self.lines.all()
        )
        self.save(update_fields=['total', 'updated_at'])

    @property
    def total_expected(self):
        return sum(line.quantity for line in self.lines.all())

    @property
    def total_received(self):
        return sum(line.quantity_received for line in self.lines.all())

    def update_status(self):
        """Recalculate PO status from its lines after a goods receipt."""
        lines = self.lines.all()
        if not lines.exists():
            return
        if all(l.match_status == 'matched' for l in lines):
            self.status = 'complete'
        elif any(l.quantity_received > 0 for l in lines):
            self.status = 'partial'
        self.save(update_fields=['status', 'updated_at'])


class PurchaseOrderLine(models.Model):
    purchase_order    = models.ForeignKey(
                            PurchaseOrder,
                            on_delete=models.CASCADE,
                            related_name='lines'
                        )
    item              = models.ForeignKey(
                            Item,
                            on_delete=models.PROTECT,
                            related_name='po_lines'
                        )
    quantity          = models.PositiveIntegerField(default=1)
    unit_cost         = models.DecimalField(max_digits=10, decimal_places=2)
    supplier_sku      = models.CharField(
                            max_length=100, blank=True,
                            help_text='Supplier SKU for invoice matching'
                        )
    quantity_received = models.PositiveIntegerField(
                            default=0,
                            help_text='Running total updated by goods receipts'
                        )

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
        # Keep PO stored total in sync
        self.purchase_order.recalculate_totals()

    def __str__(self):
        return f'{self.quantity}× {self.item.name}'


class GoodsReceipt(models.Model):
    purchase_order = models.ForeignKey(
                         PurchaseOrder,
                         on_delete=models.PROTECT,
                         related_name='goods_receipts'
                     )
    delivery_ref   = models.CharField(
                         max_length=100, blank=True,
                         help_text='Supplier delivery note number'
                     )
    received_by    = models.ForeignKey(
                         settings.AUTH_USER_MODEL,
                         on_delete=models.SET_NULL,
                         null=True, blank=True,
                         related_name='goods_receipts'
                     )
    received_date  = models.DateField()
    notes          = models.TextField(blank=True)
    created_at     = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-received_date', '-created_at']

    def __str__(self):
        return f'GR-{self.pk:04d} — {self.purchase_order}'


class GoodsReceiptLine(models.Model):
    DISCREPANCY_CHOICES = [
        ('none',    'None'),
        ('short',   'Short delivery'),
        ('over',    'Over delivery'),
        ('damaged', 'Damaged'),
        ('wrong',   'Wrong item'),
    ]

    goods_receipt     = models.ForeignKey(
                            GoodsReceipt,
                            on_delete=models.CASCADE,
                            related_name='lines'
                        )
    po_line           = models.ForeignKey(
                            PurchaseOrderLine,
                            on_delete=models.PROTECT,
                            related_name='receipt_lines'
                        )
    quantity_received = models.PositiveIntegerField(default=0)
    discrepancy       = models.CharField(
                            max_length=20,
                            choices=DISCREPANCY_CHOICES,
                            default='none'
                        )
    discrepancy_note  = models.TextField(blank=True)

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        self._update_po_line_received()

    def _update_po_line_received(self):
        """Update running received total on the PO line, then cascade up."""
        total = sum(
            rl.quantity_received
            for rl in self.po_line.receipt_lines.all()
        )
        self.po_line.quantity_received = total
        self.po_line.save(update_fields=['quantity_received'])
        # Cascade — recalculate PO status
        self.po_line.purchase_order.update_status()

    def __str__(self):
        return f'{self.quantity_received}× {self.po_line.item.name}'