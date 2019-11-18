from django.urls import path
from . import views
urlpatterns = [
     path('',views.LoginHome,name='login'),
     path('index/',views.Profile,name='index'),
     path('login/',views.Register,name='register'),
     path('login/',views.Patient,name='patient'),
     path('login/',views.Doctor,name='doctor'),
     #  path('login/', include(('apps.login.urls','login'))),

    # functions from the Doctor.html
     path('doctor/generate-report/', views.initategatherin),
     path('doctor/get-data-fitbit/', views.getDataFitbitCharts),
     path('doctor/get-data-fitbit-food/', views.getDataFitbitFoods),
     path('doctor/get-data-fitbit-weight/', views.getDataFitbitWeight),
]