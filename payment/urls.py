from django.urls import path
from . import views

urlpatterns = [
    # Payment flow below
    path('payment/plans', views.plansPage, name='plans'),
    path('payment/initiate/<id>', views.createOrder, name="payment"),
    path('payment/status', views.paymentStatus, name='payment_status'),
    path('payment/done', views.paymentSuccessPage, name="success"),
    path('payment/free', views.freePurchasePage, name="free-success"),
    path('payment/coupon', views.add_coupon, name="coupon"),
    path('payment/removeCoupon', views.remove_coupon, name="removeCoupon"),
]
