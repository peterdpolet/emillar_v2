# orders/models.py
from django.db import models
from django.conf import settings


class Order(models.Model):

    STATUS_CHOICES = [
        ('draft',     'Draft'),
        ('confirmed', 'Confirmed'),
        ('shipped',   'Shipped'),
        ('delivered', 'Delivered'),
        ('cancelled', 'Cancelled'),
    ]

    customer     = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name='orders'
    )
    status       = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    notes        = models.TextField(blank=True)
    currency     = models.CharField(max_length=3, default='GBP')

    # Financials — stored as computed on save
    subtotal     = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    vat_amount   = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    total        = models.DecimalField(max_digits=12, decimal_places=2, default=0)

    # PDF storage — pre-generated for slow networks
    invoice_pdf  = models.FileField(upload_to='invoices/', null=True, blank=True)

    # Dates
    due_date     = models.DateField(null=True, blank=True)
    created_at   = models.DateTimeField(auto_now_add=True)
    updated_at   = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Order #{self.id} — {self.customer}"

    def recalculate_totals(self):
        """Called after lines are saved/deleted."""
        lines         = self.lines.all()
        self.subtotal = sum(l.line_total for l in lines)
        self.vat_amount = self.subtotal * 0  # adjust if VAT applies
        self.total    = self.subtotal + self.vat_amount
        self.save(update_fields=['subtotal', 'vat_amount', 'total'])


class OrderLine(models.Model):
    order      = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='lines')
    item       = models.ForeignKey('purchasing.Item', on_delete=models.PROTECT)
    quantity   = models.PositiveIntegerField(default=1)
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)

    @property
    def line_total(self):
        return self.quantity * self.unit_price

    def __str__(self):
        return f"{self.quantity} × {self.item.sku}"


class OrderStatusLog(models.Model):
    order      = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='status_logs')
    from_status = models.CharField(max_length=20, blank=True)
    to_status  = models.CharField(max_length=20)
    note       = models.TextField(blank=True)
    changed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True, blank=True
    )
    changed_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['changed_at']