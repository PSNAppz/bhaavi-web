from django.contrib import admin
from product.models import *

# Register your models here.
admin.site.register(Product)
admin.site.register(ProductFeatures)
admin.site.register(ProductPackages)
admin.site.register(Coupon)
admin.site.register(UserRedeemCoupon)

