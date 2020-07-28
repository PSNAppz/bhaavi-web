"""bhaavi URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('support/', include('helpdesk.urls', namespace='support')),

    path('', include('accounts.urls')),
    path('', include('picset.urls')),


    # Payment flow below
    path('', include('payment.urls'))

]
handler400 = 'accounts.views.handler400'
handler403 = 'accounts.views.handler403'
handler404 = 'accounts.views.handler404'
handler500 = 'accounts.views.handler500'
