from django.urls import path
from . import views
from agora.views import Agora
from django.contrib.auth import views as auth_views

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
    path('request/astro', views.requestCallAstro, name="astro_request"),

    path('request/details', views.requestPage, name="request_details"),
    path('accept/mentor', views.acceptCall, name="accept_call"),

    # Mentor Dash
    path('mentorboard/', views.mentorDashboard, name="mentorboard"),
    path('mentorboard/viewDetails', views.mentorDetailsView, name="view_details_mentor"),
    path('mentorboard/prevDetails', views.mentorHistory, name="view_history_mentor"),

    # Jyolsyan Dash
    path('astroboard', views.astroDashboard,name="astroboard"),
    path('astroboard/viewDetails', views.astroDetailsView, name="view_details_astro"), 
    path('mentorboard/prevDetails', views.astroHistory, name="view_history_astro"),


    # Admin panel
    path('dashboard/admin',views.adminDashboard, name="admin_panel"),
    path('dashboard/admin/request/<int:id>',views.respondCallRequest, name="respond_call"),
    path('dashboard/admin/schedule', views.requestSchedule, name="send_schedule"),
    path('dashboard/admin/schedules/<int:id>',views.showSchedules, name="show_schedules"),
    path('dashboard/admin/schedule/drop/<int:id>',views.dropSchedule, name="drop_schedule"),
 
    # Conference call URLs
    path('dashboard/ready', views.callDetails, name="call_details"),
    path('dashboard/conference/',Agora.as_view(), name="conference"),
    path('dashboard/conference/end',views.endCall, name="end_call"),


    # Static pages
    path('privacy_policy', views.viewPrivacyPolicy, name="privacy"),
    path('terms_and_conditions', views.viewTerms, name="terms"),
    path('refund_policy', views.viewRefund, name="refund"),

    # email_verification
    path('activate/<uidb64>/<token>/', views.activate_account, name='activate'),

    # Password reset pages

    # path('reset_password', views.ResetPasswordRequestView.as_view(), name="reset_password"),

    path('password-reset/',
         auth_views.PasswordResetView.as_view(
             template_name='accounts/password_reset.html'
         ),
         name='password_reset'),
    path('password-reset/done/',
         auth_views.PasswordResetDoneView.as_view(
             template_name='accounts/password_reset_done.html'
         ),
         name='password_reset_done'),
    path('password-reset-confirm/<uidb64>/<token>/',
         auth_views.PasswordResetConfirmView.as_view(
             template_name='accounts/password_reset_confirm.html'
         ),
         name='password_reset_confirm'),
    path('password-reset-complete/',
         auth_views.PasswordResetCompleteView.as_view(
             template_name='accounts/password_reset_complete.html'
         ),
    name='password_reset_complete'),
    

]
