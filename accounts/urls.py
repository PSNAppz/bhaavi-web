from django.urls import path
from . import views
from agora.views import Agora

urlpatterns = [
    # Basic page URLs
    path('', views.homePage,name="home"),
    path('dashboard/profile', views.profilePage, name="profile"),
    path('dashboard/profile/save', views.saveProfile, name="profile_save"),
    path('dashboard', views.userDashboard,name="dashboard"),
    path('login', views.loginPage, name="login"),
    path('mentor/register', views.mentorRegisterPage, name="mentor_register"),
    path('jyolsyan/register', views.jyolsyanRegisterPage, name="jyolsyan_register"),
    path('user/register', views.userRegisterPage, name="register"),
    path('logout', views.logoutUser, name="logout"),  

    # Payment flow below
    path('payment/plans', views.plansPage, name='plans'),
    path('payment/initiate', views.createOrder , name="payment"), 
    path('payment/status', views.paymentStatus, name = 'payment_status'),
    path('payment/done', views.paymentSuccessPage , name="success"), 

    path('request/mentor', views.requestCall, name="mentor_request"),
    path('accept/mentor', views.acceptCall, name="accept_call"),

    # Mentor Dash
    path('mentorboard/', views.mentorDashboard, name="mentorboard"),

    # Admin panel
    path('dashboard/admin',views.adminDashboard, name="admin_panel"),
    path('dashboard/admin/request/<int:id>',views.respondCallRequest, name="respond_call"),
    path('dashboard/admin/schedule', views.requestSchedule, name="send_schedule"),
    path('dashboard/admin/schedules/<int:id>',views.showSchedules, name="show_schedules"),
    path('dashboard/admin/schedule/drop/<int:id>',views.dropSchedule, name="drop_schedule"),
 
    # Conference call URLs
    path('dashboard/ready', views.callDetails, name="call_details"),
    path('dashboard/conference/',Agora.as_view(), name="conference"),

    # Static pages
    path('privacy_policy', views.viewPrivacyPolicy, name="privacy"),
    path('terms_and_conditions', views.viewTerms, name="terms"),
    path('refund_policy', views.viewRefund, name="refund"),


]
