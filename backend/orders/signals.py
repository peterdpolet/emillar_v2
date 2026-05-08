from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Order


@receiver(post_save, sender=Order)
def on_order_confirmed(sender, instance, **kwargs):
    """Generate and store invoice PDF when order is confirmed."""
    if instance.status == 'confirmed' and not instance.invoice_pdf:
        from documents.tasks import generate_and_store_invoice
        generate_and_store_invoice.delay(instance.id)