from django.shortcuts import render,redirect
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.views.decorators.cache import never_cache
from django.views.decorators.csrf import csrf_protect
from django.views.generic.edit import FormView
from django.views.generic import TemplateView
from django.contrib.auth import login
from django.http import HttpResponseRedirect
from .forms import FormularioLogin
import fitbit
import pandas as pd 
from fontawesome.fields import IconField
import datetime
import sys
import threading
sys.path.insert(1, '/python_fitbit_wapi/')
from .python_fitbit_wapi import gather_keys_oauth2 as Oauth2




# Create your views here.
class LoginHome(FormView):
    template_name = 'login'
    form_class = FormularioLogin
    success_url = reverse_lazy('index')

    @method_decorator(csrf_protect)
    @method_decorator(never_cache)
    def dispatch(self,request,*args,**kwargs):
        if request.user.is_authenticated:
            return HttpResponseRedirect(self.get_success_url())
        else:
            return super(LoginHome,self).dispatch(request,*args,**kwargs)

    def form_valid(self,form):
        login(self.request,form.get_user())
        return super(LoginHome,self).form_valid(form)

def Profile(request):
    R = render(request,'login/index.html') 
    try:
        threadData = threading.Thread(target=initategatherin, args = ())
        threadData.start()
    except :
        print( 'error: unable to start')
        
    return R
    #template_name= 'index'

def Register(request):
    return render(request,'login/register.html')

def Patient(request):
    return render(request,'login/patient.html')
def Doctor(request):
    return render(request,'login/doctor.html')    

def initategatherin():
    CLIENT_ID = '22B57B'
    CLIENT_SECRET = 'a22948cb93e1a4d745d0c4a9d29ce698'
    
    print('AHUEVOOOOO')
    server = Oauth2.OAuth2Server(CLIENT_ID, CLIENT_SECRET)
    
    print('AHUEVOOOOOx2')
    server.browser_authorize()
    print('AHUEVOOOOOx3')
    ACCESS_TOKEN = str(server.fitbit.client.session.token['access_token'])
    REFRESH_TOKEN = str(server.fitbit.client.session.token['refresh_token'])

    auth2_client = fitbit.Fitbit(CLIENT_ID, CLIENT_SECRET, oauth2=True, access_token=ACCESS_TOKEN, refresh_token=REFRESH_TOKEN)

    yesterday  = str((datetime.datetime.now() - datetime.timedelta(days=2)).strftime("%Y%m%d"))
    yesterday2 = str((datetime.datetime.now() - datetime.timedelta(days=1)).strftime("%Y-%m-%d"))
    today = str(datetime.datetime.now().strftime("%Y%m%d"))

    time_listHR =[]
    val_listHR  =[]
    time_listSTP=[]
    val_listSTP =[]
    val_listName=[]
    val_listWeig=[]
    val_listHeig=[]
    val_listWatr=[]
    val_listGndr=[]
    valu_listAge=[]

    fit_statsHR = auth2_client.intraday_time_series('activities/heart', base_date='today', detail_level='1min',start_time='00:00',end_time='23:59')
    fit_statsSteps = auth2_client.intraday_time_series('activities/steps', base_date='today', detail_level='1min',start_time='00:00',end_time='23:59')
    fit_statsWater = auth2_client.water_goal()
    fit_statsUsr = auth2_client.user_profile_get()
    for i in fit_statsSteps['activities-steps-intraday']['dataset']:
        val_listSTP.append(i['value'])
        time_listSTP.append(i['time'])
        val_listHR.append('0')
        time_listHR.append('0')
        val_listName.append(str(fit_statsUsr['user']['fullName']))
        val_listWeig.append(str(fit_statsUsr['user']['weight']  ))
        val_listHeig.append(str(fit_statsUsr['user']['height']  ))
        val_listWatr.append(str(fit_statsWater['goal']['goal']  ))
        val_listGndr.append(str(fit_statsUsr['user']['gender']  ))
        valu_listAge.append(str(fit_statsUsr['user']['age']     ))
    cont =0    
    for i in fit_statsHR['activities-heart-intraday']['dataset']:
        time_listHR.pop(len(time_listHR)-1)
        time_listHR.insert(cont, i['time'])
        val_listHR.pop(len(val_listHR)-1)
        val_listHR.insert(cont, i['value'])
        cont+=1
    print(len(val_listSTP))
    print(len(time_listSTP))
    print(len(val_listHR))
    print(len(time_listHR))

    data = {'timeHR':time_listHR,'heart_Rate':val_listHR,'time':time_listSTP,'step_Count':val_listSTP,'full Name':val_listName,'weight':val_listWeig,'height':val_listHeig,'age':valu_listAge,'gender':val_listGndr,'waterLvl':val_listWatr}
        
    profileFitUsr = pd.DataFrame(data)


    profileFitUsr.to_csv('/Users/croos/Onedrive/Escritorio/'+ \
                today+'profile.csv', \
                columns=['time','timeHR','heart_Rate','step_Count','full Name','waterLvl','weight','height','age','gender'], \
                header=True, \
                sep=';', \
                index = False)

