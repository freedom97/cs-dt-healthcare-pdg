from django.urls import path
from . import views
urlpatterns = [
     path('',views.LoginHome,name='login'),
     path('index/',views.Profile,name='index'),
     path('login/',views.Register,name='register'),
     path('login/',views.Patient,name='patient'),
     path('login/',views.Doctor,name='doctor'),
    path('login/authenticate-user/', views.authUser),
    path('register/register-user/', views.registerUser),
     #  path('login/', include(('apps.login.urls','login'))),

    # functions from the Doctor.html
     path('doctor/generate-report/', views.initategatherin),
     path('doctor/get-data-fitbit/', views.getDataFitbitCharts),
     path('doctor/get-data-fitbit-food/', views.getDataFitbitFoods),
     path('doctor/get-data-fitbit-weight/', views.getDataFitbitWeight),
     path('doctor/log-out-user/', views.logOutUser),     
     path('doctor/show-patient/', views.showPatient),

     # functions from the patient.html
     path('patient/generate-report/', views.initategatherin),
     path('patient/get-data-fitbit/', views.getDataFitbitCharts),
     path('patient/get-data-fitbit-food/', views.getDataFitbitFoods),
     path('patient/get-data-fitbit-weight/', views.getDataFitbitWeight),
     path('patient/log-out-user/', views.logOutUser),
]