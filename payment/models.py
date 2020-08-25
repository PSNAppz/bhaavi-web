import decimal
import uuid

from django.db import models

# Create your models here.
from accounts.models import User
from product.models import Product, Coupon


def invoice_gen():
    uid = uuid.uuid4()
    last_invoice = UserPurchases.objects.all().order_by('id').last()
    if not last_invoice:
        return 'BHVI-' + uid.hex
    new_invoice_no = 'BHVI-' + str(uid.hex)
    return new_invoice_no


class UserPurchases(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user_products')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    status = models.BooleanField(default=0)
    payment_progress = models.BooleanField(default=1)
    consumed = models.BooleanField(default=0)
    in_use = models.BooleanField(default=0)
    coupon = models.ForeignKey(Coupon, on_delete=models.CASCADE, null=True, blank=True)
    invoice = models.CharField(max_length=255, default=invoice_gen)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return 'Receipt id: {}'.format(self.invoice)

    def get_total(self):
        total = self.product.amount - self.product.active_discount
        if self.coupon:
            coupon_discount = decimal.Decimal(total/100) * self.coupon.discount_percent
            total = decimal.Decimal(total) - coupon_discount
            return total
        return total

    def get_product_discount(self):
        discount_price =self.product.amount - self.product.active_discount
        if self.coupon:
            discount = decimal.Decimal(discount_price / 100) * self.coupon.discount_percent
            discount_price = decimal.Decimal(discount_price) - decimal.Decimal(discount)
            return discount_price
        return discount_price


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
