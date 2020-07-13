from django.urls import path
from . import views

urlpatterns = [
    # Payment flow below
    path('payment/plans', views.plansPage, name='plans'),
    path('payment/initiate', views.createOrder, name="payment"),
    path('payment/status', views.paymentStatus, name='payment_status'),
    path('payment/done', views.paymentSuccessPage, name="success"),
]
