from django.shortcuts import render,redirect
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.views.decorators.cache import never_cache
from django.views.decorators.csrf import csrf_protect
from django.views.generic.edit import FormView
from django.views.generic import TemplateView
from django.contrib.auth import login
from django.http import HttpResponseRedirect
import requests as requis
from .forms import FormularioLogin
import fitbit
import django.http.response
import pandas as pd 
from django.http import JsonResponse
from fontawesome.fields import IconField
import datetime
import sys
import threading
sys.path.insert(1, '/python_fitbit_wapi/')
from .python_fitbit_wapi import gather_keys_oauth2 as Oauth2


# Create your views here.
auth2_client = fitbit.api.Fitbit
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
    CLIENT_ID = '22B57B'
    CLIENT_SECRET = 'a22948cb93e1a4d745d0c4a9d29ce698'
    server = Oauth2.OAuth2Server(CLIENT_ID, CLIENT_SECRET)
    server.browser_authorize()
    ACCESS_TOKEN = str(server.fitbit.client.session.token['access_token'])
    REFRESH_TOKEN = str(server.fitbit.client.session.token['refresh_token'])
    global auth2_client
    auth2_client= fitbit.Fitbit(CLIENT_ID, CLIENT_SECRET, oauth2=True, access_token=ACCESS_TOKEN, refresh_token=REFRESH_TOKEN)
    return render(request,'login/doctor.html')


def getDataFitbitCharts(request):
    
    types = request.POST['dataType']
    labels= request.POST['dataTime']
    spectrum =[]
    datas=[]
    datashet =[]
    datalabel=[]
    if(labels == "day" or labels =="yesterday"):
        day= ""
        if labels =="yesterday":
            day = str((datetime.datetime.now() - datetime.timedelta(days=(1))).strftime("%Y-%m-%d"))
        else:
            day  = 'today'
        roomie =[]
        if   types== "HR":
            fit_statsHrate =auth2_client.intraday_time_series('activities/heart', base_date=day, detail_level='15min',start_time='00:00',end_time='23:59')
            roomie = fit_statsHrate['activities-heart-intraday']
        elif types =="ST":
            fit_statsnrStp =auth2_client.intraday_time_series('activities/steps', base_date=day, detail_level='15min',start_time='00:00',end_time='23:59')
            roomie = fit_statsnrStp['activities-steps-intraday']

        for i in roomie['dataset']:
            if i['value'] != 0:  
                datashet.append(i['value'])
                datalabel.append(str(i['time'])  )
        pass        
    elif(labels == "week"): 
        if   types== "HR":
            fit_statsHrate = auth2_client.time_series(resource='activities/heart', base_date='today', end_date='1w')
            spectrum.append(fit_statsHrate)
        elif types =="ST":                
            fit_statsHrate = auth2_client.time_series(resource='activities/steps', base_date='today', end_date='1w')
            spectrum.append(fit_statsHrate)

    elif(labels == "month"):
        if   types== "HR":
            fit_statsHrate = auth2_client.time_series(resource='activities/heart', base_date='today', end_date='1m')
        elif types =="ST":
            fit_statsHrate = auth2_client.time_series(resource='activities/steps', base_date='today', end_date='1m')
    else:
        datashet = [650,820,230,330,550,123,440,550,650,100,100]
        datalabel    = ['A','a','q','w','e','r','t','y','u','i','o','p']
        pass 
    datas.append(datashet)
    datas.append(datalabel)
    return JsonResponse(datas,safe=False)


def getDataFitbitWeight(request):
    global auth2_client
    fit_statsWeight = auth2_client._get_body(type_="weight",base_date="2019-10-19")
    print(fit_statsWeight)
    datas=['sumit']
    return JsonResponse(datas,safe=False)   

def getDataFitbitFoods(request):
    types = request.POST['dataType']
    labels= request.POST['dataTime']
    global auth2_client
    datas=[]
    days=[]
    if(labels == "day"):
        fit_statsFood = auth2_client._food_stats(qualifier='date/today')
        days.append(fit_statsFood)
    elif(labels == "week"): 
        yesterday  = str((datetime.datetime.now() - datetime.timedelta(days=1)).strftime("%Y-%m-%d"))
        print(yesterday)
        fit_statsFood = auth2_client._food_stats(qualifier='date/'+yesterday)
        days.append(fit_statsFood)
    elif(labels == "month"):
        for k in range(8):
            yesterday  = str((datetime.datetime.now() - datetime.timedelta(days=(k))).strftime("%Y-%m-%d"))
            print(yesterday)
            fit_statsFood = auth2_client._food_stats(qualifier='date/'+yesterday)
            days.append(fit_statsFood)
    for j in days:
        for i in j['foods']:
            name = i['loggedFood']['name']+ ""
            date = str(i['logDate'])
            qty  = str(i['loggedFood']['amount']) + " " + i['loggedFood']['unit']['name']
            cal  = i['nutritionalValues']['calories']
            car  = i['nutritionalValues']['carbs']
            fat  = i['nutritionalValues']['fat']
            fib  = i['nutritionalValues']['fiber']
            pro  = i['nutritionalValues']['protein']
            sod  = i['nutritionalValues']['sodium']
            foodi= [name,qty,"fecha",date,"calorias",cal,"carbohidratos",car,"grasa",fat,"fibra",fib,"proteina",pro,"sodio",sod]
            datas.append(foodi)
    return JsonResponse(datas,safe=False) 


def initategatherin(request):
    global auth2_client
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
    data = {'timeHR':time_listHR,'heart_Rate':val_listHR,'time':time_listSTP,'step_Count':val_listSTP,'full Name':val_listName,'weight':val_listWeig,'height':val_listHeig,'age':valu_listAge,'gender':val_listGndr,'waterLvl':val_listWatr}       
    profileFitUsr = pd.DataFrame(data)
    profileFitUsr.to_csv('/Users/croos/Onedrive/Escritorio/'+ \
                today+'profile.csv', \
                columns=['time','timeHR','heart_Rate','step_Count','full Name','waterLvl','weight','height','age','gender'], \
                header=True, \
                sep=';', \
                index = False)
    return HttpResponseRedirect("hellow there")

