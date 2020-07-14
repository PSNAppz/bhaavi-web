from django.contrib import admin

# Register your models here.
from payment.models import UserPurchases, RazorPayTransactions

admin.site.register(UserPurchases)
admin.site.register(RazorPayTransactions)
