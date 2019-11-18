"""webPageDigitalTwin URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.2/topics/http/urls/
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
from django.urls import path,include
from django.contrib.auth.decorators import login_required

from django.contrib.auth.views import LoginView,logout_then_login
from apps.login.views import LoginHome
from apps.login.views import Profile
from apps.login.views import Register
from apps.login.views import Patient
from apps.login.views import Doctor
from apps.login.views import initategatherin
from apps.login.views import getDataFitbitCharts
from apps.login.views import getDataFitbitFoods
from apps.login.views import getDataFitbitWeight



urlpatterns = [
    path('admin/', admin.site.urls),
     #  path('login/', include(('apps.login.urls','login'))),
    path('',LoginView.as_view(template_name='login/login.html'), name='login'),
    path('index/',Profile, name='Profile'),
    path('register/', Register, name='Register'),
    path('patient/', Patient, name='Patient'),
    path('doctor/', Doctor, name='Doctor'),
    
    # functions from the Doctor.html    
    path('doctor/generate-report/', initategatherin),
    path('doctor/get-data-fitbit/', getDataFitbitCharts),
    path('doctor/get-data-fitbit-food/', getDataFitbitFoods),
    path('doctor/get-data-fitbit-weight/', getDataFitbitWeight),

]