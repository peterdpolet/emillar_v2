from django.db import models

class PurchaseOrder(models.Model):
    STATUS_CHOICES = [
        ('draft',      'Draft'),
        ('sent',       'Sent to Supplier'),
        ('partial',    'Partially Received'),
        ('complete',   'Complete'),
        ('cancelled',  'Cancelled'),
    ]
    supplier       = models.ForeignKey(Supplier, on_delete=models.PROTECT,
                       related_name='purchase_orders')
    reference      = models.CharField(max_length=100, blank=True,
                       help_text='Your internal PO reference number')
    supplier_ref   = models.CharField(max_length=100, blank=True,
                       help_text='Supplier order reference if provided')
    status         = models.CharField(max_length=20,
                       choices=STATUS_CHOICES, default='draft')
    expected_date  = models.DateField(null=True, blank=True)
    notes          = models.TextField(blank=True)
    raised_by      = models.ForeignKey(settings.AUTH_USER_MODEL,
                       on_delete=models.SET_NULL, null=True,
                       related_name='purchase_orders_raised')
    created_at     = models.DateTimeField(auto_now_add=True)
    updated_at     = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    @property
    def total(self):
        return sum(line.line_total for line in self.lines.all())

    @property
    def total_expected(self):
        return sum(line.quantity for line in self.lines.all())

    @property
    def total_received(self):
        return sum(
            line.quantity_received for line in self.lines.all()
        )

    def _update_status(self):
        """Recalculate PO status from its lines after a goods receipt."""
        lines = self.lines.all()
        if not lines.exists():
            return
        if all(l.match_status == 'matched' for l in lines):
            self.status = 'complete'
        elif any(l.quantity_received > 0 for l in lines):
            self.status = 'partial'
        self.save(update_fields=['status', 'updated_at'])

    PurchaseOrder._update_status = _update_status

    def __str__(self):
        return f'PO-{self.pk:04d} — {self.supplier.name}'


class PurchaseOrderLine(models.Model):
    purchase_order    = models.ForeignKey(PurchaseOrder,
                          on_delete=models.CASCADE, related_name='lines')
    item              = models.ForeignKey(Item, on_delete=models.PROTECT,
                          related_name='po_lines')
    quantity          = models.PositiveIntegerField(default=1)
    unit_cost         = models.DecimalField(max_digits=10, decimal_places=2)
    quantity_received = models.PositiveIntegerField(default=0,
                          help_text='Updated by goods receipts')

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

    def __str__(self):
        return f'{self.quantity}x {self.item.name}'


class GoodsReceipt(models.Model):
    purchase_order  = models.ForeignKey(PurchaseOrder,
                        on_delete=models.PROTECT,
                        related_name='goods_receipts')
    delivery_ref    = models.CharField(max_length=100, blank=True,
                        help_text='Supplier delivery note number')
    received_by     = models.ForeignKey(settings.AUTH_USER_MODEL,
                        on_delete=models.SET_NULL, null=True,
                        related_name='goods_receipts')
    received_date   = models.DateField()
    notes           = models.TextField(blank=True)
    created_at      = models.DateTimeField(auto_now_add=True)

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
    goods_receipt      = models.ForeignKey(GoodsReceipt,
                           on_delete=models.CASCADE,
                           related_name='lines')
    po_line            = models.ForeignKey(PurchaseOrderLine,
                           on_delete=models.PROTECT,
                           related_name='receipt_lines')
    quantity_received  = models.PositiveIntegerField(default=0)
    discrepancy        = models.CharField(max_length=20,
                           choices=DISCREPANCY_CHOICES, default='none')
    discrepancy_note   = models.TextField(blank=True)

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        # Update the PO line running total when a receipt line is saved
        self._update_po_line_received()

    def _update_po_line_received(self):
        total = sum(
            rl.quantity_received
            for rl in self.po_line.receipt_lines.all()
        )
        self.po_line.quantity_received = total
        self.po_line.save(update_fields=['quantity_received'])
        # Update PO status based on all lines
        self.po_line.purchase_order._update_status()

    def __str__(self):
        return f'{self.quantity_received}x {self.po_line.item.name}'
