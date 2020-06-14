from django.urls import path
from . import views

urlpatterns = [
    path('', views.homePage,name="home"),
    path('user/profile', views.profilePage, name="profile"),
    path('dashboard', views.userDashboard,name="dashboard"),
    path('login', views.loginPage, name="login"),
    path('mentor/register', views.mentorRegisterPage, name="mentor_register"),
    path('jyolsyan/register', views.jyolsyanRegisterPage, name="jyolsyan_register"),
    path('user/register', views.userRegisterPage, name="register"),
    path('logout', views.logoutUser, name="logout"),  
    path('pricing', views.pricingDetails,name="pricing"),
    path('chat', views.chatpage, name='chat'),  
    # Payment flow below
    path('plans', views.plansPage, name='plans'),
    path('checkout', views.checkoutPage, name='checkout'), 
    path('payment_success', views.paymentSuccessPage, name="success_payment"), 

    path('request/mentor', )
    #path('request/jyothishan', )
]
