from django.db import models
from accounts.models import *


# Create your models here.
def product_gen():
    uid = uuid.uuid4()
    last_prod = Product.objects.all().order_by('id').last()
    if not last_prod:
        return 'PROD-' + uid.hex
    prod_id = 'PROD-' + str(uid.hex)
    return prod_id


class Product(models.Model):
    id = models.CharField(max_length=255, default=product_gen, primary_key=True, editable=False)
    name = models.CharField(max_length=255)
    description = models.CharField(max_length=255)
    amount = models.FloatField()
    active_discount = models.FloatField()
    call_required = models.BooleanField(default=0)
    is_package = models.BooleanField(default=0)
    prod_type = models.CharField(default="O", max_length=2)
    # O for other, M for mentoring, J for astrology
    active = models.BooleanField(default=1)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return 'Product name: {}'.format(self.name)


class ProductFeatures(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    feature = models.CharField(max_length=255)

    def __str__(self):
        return 'Product name: {}'.format(self.product.name)


class ProductPackages(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='package_product')
    package = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='product_package')

    def __str__(self):
        return 'Package name: {}'.format(self.package.name)


class Coupon(models.Model):
    code = models.CharField(max_length=255)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    discount_percent = models.DecimalField(max_digits=5, decimal_places=2)
    count = models.IntegerField(default=1)
    multiple_usage = models.BooleanField(default=0)
    active = models.BooleanField(default=1)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return 'Product name: {}'.format(self.product.name)

    @property
    def is_siteWide(self):
        if (self.product == ""):
            return True
        else:
            return False


class UserRedeemCoupon(models.Model):
    coupon = models.ForeignKey(Coupon, on_delete=models.CASCADE, related_name='coupon_details', null=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user_details', null=False)
    discount_percent = models.DecimalField(max_digits=5, decimal_places=2)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return 'User name: {}'.format(self.user.full_name)
