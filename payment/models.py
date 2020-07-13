from django.db import models


# Create your models here.
from accounts.models import UserPurchases


class RazorPayTransactions(models.Model):
    purchase = models.ForeignKey(UserPurchases, on_delete=models.CASCADE, related_name='transaction_details')
    razorpay_order_id = models.CharField(max_length=255, blank=True)
    razorpay_payment_id = models.CharField(max_length=255, blank=True)
    razorpay_signature = models.CharField(max_length=255, blank=True)
    status = models.BooleanField(default=0)
    refund = models.BooleanField(default=0)
    refund_date = models.DateTimeField(blank=True, null=True)
    payment_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return 'Transaction id: {}'.format(self.id)

    @property
    def product_refunded(self):
        return self.refund

    @property
    def transaction_success(self):
        return self.status

