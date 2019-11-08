from django.urls import path
from . import views
urlpatterns = [
     path('',views.LoginHome,name='login'),
     path('index/',views.Profile,name='index'),
     path('login/',views.Register,name='register'),
     path('login/',views.Patient,name='patient'),
     path('login/',views.Doctor,name='doctor'),
     #  path('login/', include(('apps.login.urls','login'))),
]