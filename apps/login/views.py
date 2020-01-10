from django.shortcuts import render,redirect
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.views.decorators.cache import never_cache
from django.views.decorators.csrf import csrf_protect
from django.views.generic.edit import FormView
from django.views.generic import TemplateView
from django.contrib.auth import login,logout,get_user_model,authenticate
from django.contrib.auth.models import Group,User
from apps.login.models import Patient as patientUser
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
from datetime import timedelta, date
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.font_manager
import math 
import pandas as pd #tratamiento de datos
import seaborn as sns
from sklearn.svm import OneClassSVM
import random
import warnings
warnings.filterwarnings('ignore')


sys.path.insert(1, '/python_fitbit_wapi/')
from .python_fitbit_wapi import gather_keys_oauth2 as Oauth2


# Create your views here.
auth2_client = fitbit.api.Fitbit
userpatient = User
urlCSV =""
fit_statsHR=[]
fit_statsSteps=[]
contadorHR=0
contadorAnomaliasHRreposo=0
contadorAnomaliasHRejercicio=0
contadorAnomaliasStesp=0
accuracyHRreposo=False
accuracyHRejercicio=False
accuracyActividadFisica=False
especificidadHRreposo=False
especificidadHRejercicio=False
especificidadActividadFisica=False

profileFitUsr=pd.DataFrame({}) 

class LoginHome(FormView):
    template_name = 'login'
    form_class = FormularioLogin
    success_url = reverse_lazy('index')
    print("INICIO INDEX")

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
    print("INICIO PROFILE")
    R = render(request,'login/index.html')         
    return R
    #template_name= 'index'

def authUser(request):  
    print("INICIO AUTENTICACION")  
    username = request.POST['username']
    password = request.POST['password']
    user = authenticate(request, username=username, password=password)
    if user is not None:
        login(request, user)
        datas =[]
        for g in Group.objects.filter(user = user):
            if g.name == 'pacientes':
                datas = ['patient']
            elif g.name == 'doctores':
                datas = ['doctor']
        return JsonResponse(datas,safe=False)
    else:
         return JsonResponse([],safe=False)

def logOutUser(request):
    print("INICIO CERRAR SESION")
    print("this kind of works")
    logout(request)
    render(request,'login/login.html')
    return JsonResponse([],safe=False)

def registerUser(request):
    print("INICIO REGISTRO")
    print( request.POST['user']+":"+request.POST['lstN']+":"+request.POST['name']+":"+request.POST['wght']+":"+request.POST['hght']+":"+request.POST['ageU']+":"+request.POST['size']+":"+request.POST['user']+":"+request.POST['pswr']+":"+ request.POST['mail'])
    datas = []
    user= None
    patientusr = None
    try:
        user = User.objects._create_user(username = request.POST['user'],password = request.POST['pswr'],email= request.POST['mail'])        
    except Exception as ex:
        datas.append(str(ex))
        return JsonResponse(datas,safe=False)
    try:
        patientusr = patientUser(user = user, identificationCard=request.POST['iCrd'],    name=request.POST['name'],  lastName =request.POST['lstN'],  weight=request.POST['wght'],    height=request.POST['hght'],    age=request.POST['ageU'], glucose =request.POST['gluc'],    size_patient=request.POST['size'])                
    except Exception as ex1:
        datas.append(str(ex1))
        return JsonResponse(datas,safe=False)     
    
    user.save()
    patientusr.save()
    myGroup = Group.objects.get(name='pacientes')
    myGroup.user_set.add(user)    
    request.user = user
    datas.append('none')
    return JsonResponse(datas,safe=False)

def Register(request):
    print("INICIO REGISTRO HTML")
    return render(request,'login/register.html')

def EditProfile(request):
    print("INICIO EDITAR PERFIL HTML")
    return render(request,'login/profile.html')

def Patient(request):
    print("INICIO PACIENTE!!")
    if request.user.is_authenticated:
        for g in Group.objects.filter(user = request.user):
            if g.name == 'pacientes':
                CLIENT_ID = '22B57B'
                CLIENT_SECRET = 'a22948cb93e1a4d745d0c4a9d29ce698'
                server = Oauth2.OAuth2Server(CLIENT_ID, CLIENT_SECRET)
                server.browser_authorize()  
                ACCESS_TOKEN = str(server.fitbit.client.session.token['access_token'])
                REFRESH_TOKEN = str(server.fitbit.client.session.token['refresh_token'])
                global auth2_client
                auth2_client= fitbit.Fitbit(CLIENT_ID, CLIENT_SECRET, oauth2=True, access_token=ACCESS_TOKEN, refresh_token=REFRESH_TOKEN)
                print(request.user.username)
                global userpatient
                userpatient = request.user
                print("COMIENZO")
                yesterday  = str((datetime.datetime.now() - datetime.timedelta(days=1)).strftime("%Y%m%d"))
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
                print("Inicializar variables")
                global fit_statsHR
                fit_statsHR = auth2_client.intraday_time_series('activities/heart', base_date="today", detail_level='1min',start_time='00:00',end_time='23:59')
                global fit_statsSteps
                fit_statsSteps = auth2_client.intraday_time_series('activities/steps', base_date="today", detail_level='1min',start_time='00:00',end_time='23:59')
                
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
               
                print("AQUI LLEENO EL DATAFRAME")
                global profileFitUsr
                profileFitUsr = pd.DataFrame(data)
                return render(request,'login/patient.html')    
    return HttpResponseRedirect('/login')

def InfoProfile(request):
    if request.user.is_authenticated:
        render(request,'login/doctor.html')
        global userpatient
        datas =[request.user.username
        ,userpatient.patient.identificationCard
        ,userpatient.patient.name
        ,userpatient.patient.lastName
        ,userpatient.patient.weight
        ,userpatient.patient.height
        ,userpatient.patient.size_patient
        ,request.user.email
        ,userpatient.patient.age
        ,userpatient.patient.glucose]
        return JsonResponse(datas, safe=False)
    return HttpResponseRedirect('/login')

def modifyProfile(request):
        usa = patientUser.objects.get(identificationCard = request.POST['iCrd'])
        usa.identificationCard = request.POST['iCrd']        
        usa.name = request.POST['name']
        usa.lastName = request.POST['lstN']
        usa.weight = int(request.POST['wght'])
        usa.height = request.POST['hght']
        usa.size_patient = request.POST['size']
        usa.age = int(request.POST['ageU'])
        usa.glucose = request.POST['gluc']
        usa.save()
        return JsonResponse(['none'],safe=False)

def Doctor(request): 
    print("INICIO DOCTOR")   
    if request.user.is_authenticated:
        for g in Group.objects.filter(user = request.user):
            if g.name == 'doctores':
                CLIENT_ID = '22B57B'
                CLIENT_SECRET = 'a22948cb93e1a4d745d0c4a9d29ce698'
                server = Oauth2.OAuth2Server(CLIENT_ID, CLIENT_SECRET)
                server.browser_authorize()
                ACCESS_TOKEN = str(server.fitbit.client.session.token['access_token'])
                REFRESH_TOKEN = str(server.fitbit.client.session.token['refresh_token'])
                global auth2_client
                global fit_statsHR
                global fit_statsSteps
                fit_statsHR = auth2_client.intraday_time_series('activities/heart', base_date='today', detail_level='1min',start_time='00:00',end_time='23:59')
                fit_statsSteps = auth2_client.intraday_time_series('activities/steps', base_date='today', detail_level='1min',start_time='00:00',end_time='23:59')
                
                auth2_client= fitbit.Fitbit(CLIENT_ID, CLIENT_SECRET, oauth2=True, access_token=ACCESS_TOKEN, refresh_token=REFRESH_TOKEN) 
                
                

                return render(request,'login/doctor.html')   
    return HttpResponseRedirect('/login')

def showPatient(request):
    print("INICIO IDENTIFICA TIPO USUARIO")
    idpatient = request.POST['idPatient']
    try:
        user = User.objects.get(id =idpatient) 
    except ValueError as verr:
        user = User.objects.get(username =idpatient)
    except Exception as exc:
        user = User.objects.get(username =idpatient)
    global userpatient
    userpatient = user  
    return JsonResponse([user.username],safe=False)

def getDataFitbitCharts(request):
    print("INICIO CANVAS")
    
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
            day = str((datetime.datetime.now() - datetime.timedelta(days=(0))).strftime("%Y-%m-%d"))
        roomie =[]
        if   types== "HR":
            fit_statsHrate =auth2_client.intraday_time_series('activities/heart', base_date=day, detail_level='15min',start_time='00:00',end_time='23:59')
            roomie = fit_statsHrate['activities-heart-intraday']
        elif types =="ST":
            fit_statsnrStp =auth2_client.intraday_time_series('activities/steps', base_date=day, detail_level='15min',start_time='00:00',end_time='23:59')
            roomie = fit_statsnrStp['activities-steps-intraday']

        for i in roomie['dataset']:
                datashet.append(i['value'])
                datalabel.append(str(i['time'])  )
        pass        
    elif(labels == "week"): 
        if   types== "HR":
            fit_statsHrate = auth2_client.time_series(resource='activities/heart', base_date='today', end_date='1w')
            roomie = fit_statsHrate['activities-heart']
            for i in roomie:
                DayHeart = []
                try:
                    for j in range(len(i['value']['heartRateZones'])):
                        DayHeart.append(i['value']['heartRateZones'][j]['minutes']/60)
                    datashet.append(DayHeart)
                    datalabel.append(i['dateTime'])
                except Exception as e:
                    print(e.__cause__)
        elif types =="ST":                
            fit_statsnrStp = auth2_client.time_series(resource='activities/steps', base_date='today', end_date='1w')
            roomie = fit_statsnrStp['activities-steps']
            for i in roomie:
                if i['value'] != 0:  
                    datashet.append(i['value'])
                    datalabel.append(str(i['dateTime']))
            
    elif(labels == "month"):
        if   types== "HR":
            fit_statsHrate = auth2_client.time_series(resource='activities/heart', base_date='today', end_date='1m')
            roomie = fit_statsHrate['activities-heart']
            print(roomie)
            for i in roomie:
                DayHeart = []
                try:
                    for j in range(len(i['value']['heartRateZones'])):
                        DayHeart.append((i['value']['heartRateZones'][j]['minutes'])/60)
                    datashet.append(DayHeart)
                    datalabel.append(i['dateTime'])
                except Exception as e:
                    print(e.__cause__)
        elif types =="ST":
            fit_statsnrStp = auth2_client.time_series(resource='activities/steps', base_date='today', end_date='1m')
            roomie = fit_statsnrStp['activities-steps']
            for i in roomie:
                if i['value'] != 0:  
                    datashet.append(i['value'])
                    datalabel.append(str(i['dateTime']))
    else:
        datashet = [650,820,230,330,550,123,440,550,650,100,100]
        datalabel    = ['A','a','q','w','e','r','t','y','u','i','o','p']
        pass 
    datas.append(datashet)
    datas.append(datalabel)
    
    return JsonResponse(datas,safe=False)

def getDataFitbitInfo(request):
    print("INICIO DATOS PESO")
    global userpatient
    M2 = float(userpatient.patient.height)*float(userpatient.patient.height)
    W = float(userpatient.patient.weight)
    global profileFitUsr
    if(not profileFitUsr.empty):
        print("no es vacio")
        datasA= getAnomaly(profileFitUsr)
    datas =['Peso:',userpatient.patient.weight,'Altura:',userpatient.patient.height,'Índice de masa corporal:',int(W/M2),"Cantidad de anomalías de frecuencia cardiaca:",datasA[0],"Cantidad de anomalías actividad física:",datasA[5],"Accuracy anomalías frecuencia cardiaca:",datasA[1],"Accuracy anomalías actividad física:",datasA[3],"Especificidad anomalías frecuencia cardiaca:",datasA[2],"Especificidad anomalías actividad física:",datasA[4],"Sexo:",datasA[6]]
    return JsonResponse(datas,safe=False)   

def getDataFitbitFoods(request):
    print("INICIO COMIDA")
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
        fit_statsFood = auth2_client._food_stats(qualifier='date/'+yesterday)
        days.append(fit_statsFood)
    elif(labels == "month"):
        for k in range(8):
            yesterday  = str((datetime.datetime.now() - datetime.timedelta(days=(k))).strftime("%Y-%m-%d"))
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
            foodi= [name,qty,"Fecha",date,"Calorías",cal,"Carbohidratos",car,"Grasa",fat,"Fibra",fib,"Proteina",pro,"Sodio",sod]
            datas.append(foodi)
    return JsonResponse(datas,safe=False) 

def initategatherin(request):
    print("INICIO DESCARGA CSV")
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
    global fit_statsHR
    fit_statsHR = auth2_client.intraday_time_series('activities/heart', base_date='today', detail_level='1min',start_time='00:00',end_time='23:59')
    global fit_statsSteps
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
    global profileFitUsr
    print("AQUI LLEGA")
    profileFitUsr = pd.DataFrame(data)
    


    global urlCSV
    urlCSV ='/Users/ASUS/ICESI/PDG/PDG2/cs-dt-healthcare-plataform/Platform/cs-dt-healthcare-pdg/'+today+'profile.csv' 
    # '/Users/croos/Onedrive/Escritorio/'+today+'profile.csv'
    profileFitUsr.to_csv(urlCSV, \
                columns=['time','timeHR','heart_Rate','step_Count','full Name','waterLvl','weight','height','age','gender'], \
                header=True, \
                sep=';', \
                index = False)
    return HttpResponseRedirect("hellow there")
    

       
    # ANOMALY DETECTION

def getAnomaly( DataFrame):
    print("INICIO ANOMALIAAAA")
    global profileFitUsr
    print("GET ANOMALY LLAMADO")
    resultDF=dataClean(profileFitUsr)
    # test=101
    dato1=""  
    dato2="" 
    dato3="" 
    dato4="" 
    dato5="" 
    dato6="" 
    dato7=""
  
    countAnomalyHR=0
    countAnomalySteps=0
    data=[]
    i=0
    print("antes del if")
    if(len(resultDF)<=500):
        print("adentro del if tamaño>2")
        dataSetTrainHRreposo()
        dataSetTrainHRejericio()
        dataSetTrainActividadFisica()
    elif(len(resultDF)>500):
        print("INICIO DATATEST")
        dataSetTrainHRreposo()
        dataSetTrainHRejericio()
        dataSetTrainActividadFisica()
        dataSetTestHRreposo()
        dataSetTestHRrejercicio()
        dataSetTestSteps()
        dataSetOutliersHR()
        dataSetOutliersSteps()

    getCLF()
    accuracyResultHR=accuracyGlobalDataTestHR()
    global accuracyHRreposo
    accuracyHRreposo=False
    global accuracyHRejercicio
    accuracyHRejercicio=False
    especificidadResultHR=especificidadDataTestAnomaliasHR()
    global especificidadHRreposo
    especificidadHRreposo=False
    global especificidadHRejercicio
    especificidadHRejercicio=False
    accuracyResultSteps=accuracyGlobalDataTestSteps()
    global accuracyActividadFisica
    accuracyActividadFisica=False
    
    especificidadResultSteps=especificidadDataTestAnomaliasSteps()
    global especificidadActividadFisica
    especificidadActividadFisica=False
    print("AccuracyResultHR")
    print(accuracyResultHR)
    print("especificidadResultHR")
    print(especificidadResultHR)
    print("AccuracyResultSteps")
    print(accuracyResultSteps)
    print("especificidadResultSteps")
    print(especificidadResultSteps)
    

    print("antes del if de getanomaly accuracy")
    # if(float(accuracyResultHR)!=0 and float(especificidadResultHR)!=0 and float(accuracyResultSteps)!=0 and float(especificidadResultSteps)!=0 ):
    print("adentro del if de getanomaly accuracy")
    global contadorAnomaliasHRejercicio
    global contadorAnomaliasHRreposo
    countAnomalyHR=contadorAnomaliasHRreposo+contadorAnomaliasHRejercicio
    countAnomalySteps=contadorAnomaliasStesp
    dato1=str(countAnomalyHR)
    dato2=str(accuracyResultHR)
    dato3=str(especificidadResultHR)
    dato4=str(accuracyResultSteps)
    dato5=str(especificidadResultSteps)
    dato6=str(countAnomalySteps)
    if(resultDF.gender[0]=="MALE"):
        dato7="Masculino"
    elif(reresultDF.gender[0]=="FEMALE"):
        dato7="Femenino"
        
    print("sale del if getanomaly accuracy ")
    data.append(dato1)
    data.append(dato2)
    data.append(dato3)
    data.append(dato4)
    data.append(dato5)
    data.append(dato6)
    data.append(dato7)
    
    print("esto es el data")
    print(data)
    return data  

def dataClean(DataFrame):
    print("INICIO DATACLEAN SOY EL PRIMERO")
    data=profileFitUsr
    print("DATACLEAN sin borrar")
    print(profileFitUsr)
    data=data.drop(['full Name', 'waterLvl', 'weight','height'], axis=1)
    print("dataclean luego de borrar")
    print(data)
    df=data
    print("creo df")
    df=df.drop(['timeHR'], axis=1)
    print("borrar columnas en el df")
    print(df)
    df=df[df.heart_Rate!=0]
    print("VERIFICAR DF RETURN")
    print(df)
    return df

def dataSetTrainHRreposo():
    print("INICIO DATATRAINHRenreposo")
    heart1=[]
    flag=False
    global profileFitUsr
    resultDF=dataClean(profileFitUsr)
    print("LLAMADO EN EL DATATRAIN")
    #PULSO CARDIACO EN REPOSO
    if(flag!=True):
        flag=True
        if(len(resultDF.heart_Rate)<=500):
            for i in range(len(resultDF.heart_Rate)):
                if (int(resultDF.heart_Rate[i])<=98 and int(resultDF.step_Count[i])==0):
                    heart1.insert(len(heart1),[int(resultDF.heart_Rate[i]),int(resultDF.age[i])])
    elif(resultDF.time=="00:00:00"):
        flag=False
        
    a1=np.array(heart1)
    a_train = np.r_[a1+2, a1+0]
    a_train[0:3]
    print("este es el dataTRAIN")
    return a_train
def dataSetTrainHRejericio():
    print("INICIO DATATRAINHRejercicio")
    global profileFitUsr
    resultDF=dataClean(profileFitUsr)
    print("LLAMADO EN EL DATATRAINHRejercicio")
    heart5=[]
    #PULSO CARDIACO EN ACTIVIDAD FISICA
    if(len(resultDF.heart_Rate)<=500):
        for i in range(len(resultDF.heart_Rate)):
            if (int(resultDF.heart_Rate[i])>=98 and int(resultDF.heart_Rate[i])<=195 and int(resultDF.step_Count[i])>=3429 and int(resultDF.age[i])<=25):
                heart5.insert(len(heart5),[int(resultDF.heart_Rate[i]),int(resultDF.age[i])])
            elif(int(resultDF.heart_Rate[i])>=93 and int(resultDF.heart_Rate[i])<=185 and int(resultDF.step_Count[i])>=3429 and int(resultDF.age[i])>=35):
                heart5.insert(len(heart5),[int(resultDF.heart_Rate[i]),int(resultDF.age[i])])
            elif(int(resultDF.heart_Rate[i])>=88 and int(resultDF.heart_Rate[i])<=175 and int(resultDF.step_Count[i])>=3429 and int(resultDF.age[i])>=45):
                heart5.insert(len(heart5),[resultDF.heart_Rate[i],resultDF.age[i]])
            elif(int(resultDF.heart_Rate[i])>=83 and int(resultDF.heart_Rate[i])<=165 and int(resultDF.step_Count[i])>=3429 and int(resultDF.age[i])>=55):
                heart5.insert(len(heart5),[int(resultDF.heart_Rate[i]),int(resultDF.age[i])])
            elif(int(resultDF.heart_Rate[i])>=78 and int(resultDF.heart_Rate[i])<=156 and int(resultDF.step_Count[i])>=3429 and int(resultDF.age[i])>=65):
                heart5.insert(len(heart5),[int(resultDF.heart_Rate[i]),int(resultDF.age[i])])  
    a5=np.array(heart5)
    a_trainHRactivadFisica = np.r_[a5+2, a5+0]
    a_trainHRactivadFisica[0:3]
    print("este es el dataTRAIN")
    return a_trainHRactivadFisica


#Metodo para convertir str en int
def getNumbers():
    numeros=[]
    global profileFitUsr
    resultDF=dataClean(profileFitUsr)
    for i in range(0,18):
        if(resultDF.time[i]=="00:01:00"):
            numeros.insert(len(numeros),i)
        elif(resultDF.time[i]=="00:02:00"):
            numeros.insert(len(numeros),i)
        elif(resultDF.time[i]=="00:03:00"):
            numeros.insert(len(numeros),i)
        elif(resultDF.time[i]=="00:04:00"):
            numeros.insert(len(numeros),i)
        elif(resultDF.time[i]=="00:05:00"):
            numeros.insert(len(numeros),i)
        elif(resultDF.time[i]=="00:06:00"):
            numeros.insert(len(numeros),i)
        elif(resultDF.time[i]=="00:07:00"):
            numeros.insert(len(numeros),i)
        elif(resultDF.time[i]=="00:08:00"):
            numeros.insert(len(numeros),i)
        elif(resultDF.time[i]=="00:09:00"):
            numeros.insert(len(numeros),i)
        elif(resultDF.time[i]=="00:10:00"):
            numeros.insert(len(numeros),i)
        elif(resultDF.time[i]=="00:11:00"):
            numeros.insert(len(numeros),i)
        elif(resultDF.time[i]=="00:12:00"):
            numeros.insert(len(numeros),i)
        elif(resultDF.time[i]=="00:13:00"):
            numeros.insert(len(numeros),i)
        elif(resultDF.time[i]=="00:14:00"):
            numeros.insert(len(numeros),i)
        elif(resultDF.time[i]=="00:15:00"):
            numeros.insert(len(numeros),i)
        elif(resultDF.time[i]=="00:16:00"):
            numeros.insert(len(numeros),i)
        elif(resultDF.time[i]=="00:17:00"):
            numeros.insert(len(numeros),i)
    return numeros


def dataSetTrainActividadFisica():
    #Train actividad fisica
     print("INICIO DATATRAIN")
     steps=[]
     numeros=getNumbers()
     global profileFitUsr
     resultDF=dataClean(profileFitUsr)
     flag=False
     if(flag!=True):
         flag=True
         if(len(resultDF.heart_Rate)<=500):
             for i in range(len(resultDF.step_Count)):
                 if (int(resultDF.age[i])<=35 and int(resultDF.step_Count[i])==3429):
                     if(resultDF.gender=="MALE" and resultDF.time[i]=="00:11:00"):
                         steps.insert(len(steps),[numeros[i],int(resultDF.age[i])])
                     elif (resultDF.gender=="FEMALE" and resultDF.time[i]=="00:13:00"):
                         steps.insert(len(steps),[numeros[i],int(resultDF.age[i])])
                 elif (int(resultDF.age[i])<=45 and int(resultDF.step_Count[i])==3429):
                     if(resultDF.gender=="MALE" and resultDF.time[i]=="00:12:00"):
                         steps.insert(len(steps),[numeros[i],int(resultDF.age[i])])
                     elif (resultDF.gender=="FEMALE" and resultDF.time[i]=="00:14:00"):
                         steps.insert(len(steps),[numeros[i],int(resultDF.age[i])])
                 elif (int(resultDF.age[i])<=55 and int(resultDF.step_Count[i])==3429):
                     if(resultDF.gender=="MALE" and resultDF.time[i]=="00:13:00"):
                         steps.insert(len(steps),[numeros[i],int(resultDF.age[i])])
                     elif (resultDF.gender=="FEMALE" and resultDF.time[i]=="00:16:00"):
                         steps.insert(len(steps),[numeros[i],int(resultDF.age[i])])
                 elif (int(resultDF.age[i])<=65 and int(resultDF.step_Count[i])==3429):
                     if(resultDF.gender=="MALE" and resultDF.time[i]=="00:14:00"):
                         steps.insert(len(steps),[numeros[i],int(resultDF.age[i])])
                     elif (resultDF.gender=="FEMALE" and resultDF.time[i]=="00:17:00"):
                         steps.insert(len(steps),[numeros[i],int(resultDF.age[i])])
         elif(len(resultDF.heart_Rate)==1):
             flag=False
     aSteps1=np.array(steps)
     a_trainSteps = np.r_[aSteps1+2, aSteps1+0]
     a_trainSteps[0:3]
     return a_trainSteps

def dataSetTestHRreposo():
    print("INICIO DATATEST metodo")
    print("crear h2")
    global profileFitUsr
    resultDF=dataClean(profileFitUsr)
    heart6=[]
    #TEST PULSO CARDIACO
    print("antes del if testHRreposo")
    if(len(resultDF.heart_Rate)>500):
        print("adentro del if testHRreposo")
        for i in range(len(resultDF.heart_Rate)-500):
            print("adentro del for testHRreposo")
            print("HR 500+i")
           
            if (int(resultDF.heart_Rate[500+i])<=98 and int(resultDF.step_Count[500+i])==0):
                print("adentro del 2do if testHRreposo")
                heart6.insert(len(heart6),[int(resultDF.heart_Rate[500+i]),int(resultDF.age[500+i])])
    a6=np.array(heart6)
    a6_testHRreposo = np.r_[a6+2, a6+0]
    a6_testHRreposo[0:3]
    print("este es el dataTest")
    print(a6_testHRreposo)
    return a6_testHRreposo
def dataSetTestHRrejercicio():
    print("INICIO DATATEST metodo")
    print("crear h2")
    global profileFitUsr
    resultDF=dataClean(profileFitUsr)
    heart7=[]

    #TEST PULSO CARDIACO EN ACTIVIDAD FISICA
    if(len(resultDF.heart_Rate)>500):
        for i in range(len(resultDF.heart_Rate)-500):
            if (int(resultDF.heart_Rate[500+i])>=98 and int(resultDF.heart_Rate[500+i])<=195 and int(resultDF.step_Count[500+i])>=3429 and int(resultDF.age[500+i])<=25):
                heart7.insert(len(heart7),[resultDF.heart_Rate[500+i],int(resultDF.age[500+i])])
            elif(int(resultDF.heart_Rate[500+i])>=93 and int(resultDF.heart_Rate[500+i])<=185 and int(resultDF.step_Count[500+i])>=3429 and int(resultDF.age[500+i])>=35):
                heart7.insert(len(heart7),[int(resultDF.heart_Rate[500+i]),int(resultDF.age[500+i])])
            elif(int(resultDF.heart_Rate[500+i])>=88 and int(resultDF.heart_Rate[500+i])<=175 and int(resultDF.step_Count[500+i])>=3429 and int(resultDF.age[500+i])>=45):
                heart7.insert(len(heart7),[int(resultDF.heart_Rate[500+i]),int(resultDF.age[500+i])])
            elif(int(resultDF.heart_Rate[500+i])>=83 and int(resultDF.heart_Rate[500+i])<=165 and int(resultDF.step_Count[500+i])>=3429 and int(resultDF.age[500+i])>=55):
                heart7.insert(len(heart7),[int(resultDF.heart_Rate[500+i]),int(resultDF.age[500+i])])
            elif(int(resultDF.heart_Rate[500+i])>=78 and int(resultDF.heart_Rate[500+i])<=156 and int(resultDF.step_Count[500+i])>=3429 and int(resultDF.age[500+i])>=65):
                heart7.insert(len(heart7),[int(resultDF.heart_Rate[500+i]),int(resultDF.age[500+i])])
    a7 =np.array(heart7)
    a7_test = np.r_[a7 + 2, a7 + 0]
    a7_test[0:3]
    return a7_test

def dataSetTestSteps():
    print("INICIO DATATEST metodo")
    print("crear h2")
    global profileFitUsr
    numeros=getNumbers()
    resultDF=dataClean(profileFitUsr)
    steps2=[]
    #TEST actividad fisica
    if(len(resultDF.heart_Rate)>500):
        for i in range(len(resultDF.step_Count)-500):
            if (int(resultDF.age[500+i])<=35 and int(resultDF.step_Count[500+i])==3429):
                if(resultDF.gender=="MALE" and resultDF.time[500+i]=="00:11:00"):
                    steps2.insert(len(steps2),[numeros[500+i],int(resultDF.age[500+i])])
                elif (resultDF.gender=="FEMALE" and resultDF.time[500+i]=="00:13:00"):
                    steps2.insert(len(steps2),[numeros[500+i],int(resultDF.age[500+i])])
            elif (int(resultDF.age[500+i])<=45 and int(resultDF.step_Count[500+i])==3429):
                if(resultDF.gender=="MALE" and resultDF.time[500+i]=="00:12:00"):
                    steps2.insert(len(steps2),[numeros[500+i],int(resultDF.age[500+i])])
                elif (resultDF.gender=="FEMALE" and resultDF.time[500+i]=="00:14:00"):
                    steps2.insert(len(steps2),[numeros[500+i],int(resultDF.age[500+i])])
            elif (int(resultDF.age[500+i])<=55 and int(resultDF.step_Count[500+i])==3429):
                if(resultDF.gender=="MALE" and resultDF.time[500+i]=="00:13:00"):
                    steps2.insert(len(steps2),[numeros[500+i],int(resultDF.age[500+i])])
                elif (resultDF.gender=="FEMALE" and resultDF.time[500+i]=="00:16:00"):
                    steps2.insert(len(steps2),[numeros[500+i],int(resultDF.age[500+i])])
            elif (int(resultDF.age[500+i])<=65 and int(resultDF.step_Count[500+i])==3429 ):
                if(resultDF.gender=="MALE" and resultDF.time[500+i]=="00:14:00"):
                    steps2.insert(len(steps2),[numeros[500+i],int(resultDF.age[500+i])])
                elif (resultDF.gender=="FEMALE" and resultDF.time[500+i]=="00:17:00"):
                    steps2.insert(len(steps2),[numeros[500+i],int(resultDF.age[500+i])])
                    
    aSteps2=np.array(steps2)
    a_testSteps = np.r_[aSteps2 + 2, aSteps2 + 0]
    a_testSteps[0:3]
    return a_testSteps
    
def dataSetOutliersHR():
    print("INICIO DATANOMALIAS")
    global profileFitUsr
    resultDF=dataClean(profileFitUsr)
    heart8=[]
    global contadorAnomaliasHRreposo
    contadorAnomaliasHRreposo=0
    global contadorAnomaliasHRejercicio
    contadorAnomaliasHRejercicio=0
    for i in range(len(resultDF.heart_Rate)):
            if (int(resultDF.heart_Rate[i])>=98 and int(resultDF.step_Count[i])==0):
                heart8.insert(len(heart8),[int(resultDF.heart_Rate[i]),int(resultDF.age[i])])
                contadorAnomaliasHRreposo+=1
            if (int(resultDF.heart_Rate[i])>=196 and int(resultDF.step_Count[i])>=3429 and int(resultDF.age[i])<=25):
                heart8.insert(len(heart8),[int(resultDF.heart_Rate[i]),int(resultDF.age[i])])
                contadorAnomaliasHRejercicio+=1
            elif(int(resultDF.heart_Rate[i])>=186 and int(resultDF.step_Count[i])>=3429 and int(resultDF.age[i])>=35):
                heart8.insert(len(heart8),[int(resultDF.heart_Rate[i]),int(resultDF.age[i])])
                contadorAnomaliasHRejercicio+=1
            elif(int(resultDF.heart_Rate[i])>=176 and int(resultDF.step_Count[i])>=3429 and int(resultDF.age[i])>=45):
                heart8.insert(len(heart8),[int(resultDF.heart_Rate[i]),int(resultDF.age[i])])
                contadorAnomaliasHRejercicio+=1
            elif(int(resultDF.heart_Rate[i])>=166 and int(resultDF.step_Count[i])>=3429 and int(resultDF.age[i])>=55):
                heart8.insert(len(heart8),[int(resultDF.heart_Rate[i]),int(resultDF.age[i])])
                contadorAnomaliasHRejercicio+=1
            elif(int(resultDF.heart_Rate[i])>=157 and int(resultDF.step_Count[i])>=3429 and int(resultDF.age[i])>=65):
                heart8.insert(len(heart8),[int(resultDF.heart_Rate[i]),int(resultDF.age[i])])
                contadorAnomaliasHRejercicio+=1
    X_outliers5=np.array(heart8)
    X_outliers6=np.r_[X_outliers5 + 2, X_outliers5 + 0]
    return X_outliers6
def dataSetOutliersSteps():
    print("INICIO DATANOMALIAS")
    numeros=getNumbers()
    global profileFitUsr
    resultDF=dataClean(profileFitUsr)
    steps3=[]
    contadorAnomaliasStesp=0
    #ANOMALIAS STEPS
    for i in range(len(resultDF.step_Count)):
        if (int(resultDF.age[i])<=35 and int(resultDF.step_Count[i])==3429):
            if(resultDF.gender=="MALE" and numeros[i]>11):
                steps3.insert(len(steps3),[numeros[i],int(resultDF.age[i])])
                contadorAnomaliasStesp+=1
        elif (int(resultDF.age[i])<=35 and int(resultDF.step_Count[i])==3429):
            if(resultDF.gender=="FEMALE" and numeros[i]>13):
                steps3.insert(len(steps3),[numeros[i],int(resultDF.age[i])])
                contadorAnomaliasStesp+=1
        elif (int(resultDF.age[i])<=45 and int(resultDF.step_Count[i])==3429): 
            if(resultDF.gender=="MALE" and numeros[i]==12):
                steps3.insert(len(steps3),[numeros[i],int(resultDF.age[i])])
                contadorAnomaliasStesp+=1
        elif (int(resultDF.age[i])<=45 and int(resultDF.step_Count[i])==3429):
            if(resultDF.gender=="FEMALE" and numeros[i]>14):
                steps3.insert(len(steps3),[numeros[i],int(resultDF.age[i])])
                contadorAnomaliasStesp+=1
        elif (int(resultDF.age[i])<=55 and int(resultDF.step_Count[i])==3429):
            if(resultDF.gender=="MALE" and numeros[i]>13):
                steps3.insert(len(steps3),[numeros[i],int(resultDF.age[i])])
                contadorAnomaliasStesp+=1
        elif (int(resultDF.age[i])<=55 and int(resultDF.step_Count[i])==3429):
            if(resultDF.gender=="FEMALE" and numeros[i]>16):
                steps3.insert(len(steps3),[numeros[i],int(resultDF.age[i])])
                contadorAnomaliasStesp+=1
        elif (int(resultDF.age[i])<=65 and int(resultDF.step_Count[i])==3429):
            if(resultDF.gender=="MALE" and numeros[i]>14):
                steps3.insert(len(steps3),[numeros[i],int(resultDF.age[i])])
                contadorAnomaliasStesp+=1
        elif (int(resultDF.age[i])<=65 and int(resultDF.step_Count[i])==3429):
            if(resultDF.gender=="FEMALE" and numeros[i]>17):
                steps3.insert(len(steps3),[numeros[i],int(resultDF.age[i])])
                contadorAnomaliasStesp+=1
    X_outliersSteps=np.array(steps3)
    X_outliersSteps=np.r_[X_outliersSteps + 2, X_outliersSteps + 0]
    return X_outliersSteps


def getCLF():
    print("INICIO CLF")
    clf = OneClassSVM()
    if(len(dataSetTrainHRreposo())!=0):
        clf.fit(dataSetTrainHRreposo())
    elif(len(dataSetTrainHRejericio())!=0):
        clf.fit(dataSetTrainHRejericio())
    elif(len(dataSetTrainActividadFisica())!=0):
        clf.fit(dataSetTrainActividadFisica())
    return clf
 

def especificidadDataTestAnomaliasHR():
    clf=getCLF()
    especificidadAnomaliasTestSet=0
    if(len(dataSetTrainHRreposo())!=0 and len(dataSetTestHRreposo())!=0 and len(dataSetOutliersHR())!=0):
        global especificidadHRreposo
        especificidadHRreposo=True
        y_pred_train = clf.predict(dataSetTrainHRreposo())
        y_pred_test = clf.predict(dataSetTestHRreposo())
        y_pred_outliers = clf.predict(dataSetOutliersHR())
        n_error_train = y_pred_train[y_pred_train == -1].size
        n_error_test = y_pred_test[y_pred_test == -1].size
        n_error_outliers = y_pred_outliers[y_pred_outliers == 1].size
        especificidadAnomaliasTestSet=str(1-n_error_outliers/len(dataSetOutliersHR()))
    elif(len(dataSetTrainHRejericio())!=0 and len(dataSetTestHRrejercicio())!=0 and len(dataSetOutliersHR())!=0):
        global especificidadHRejercicio
        especificidadHRejercicio=True
        y_pred_train = clf.predict(dataSetTestHRreposo())
        y_pred_test = clf.predict(dataSetTestHRrejercicio())
        y_pred_outliers = clf.predict(dataSetOutliersHR())
        n_error_train = y_pred_train[y_pred_train == -1].size
        n_error_test = y_pred_test[y_pred_test == -1].size
        n_error_outliers = y_pred_outliers[y_pred_outliers == 1].size
        especificidadAnomaliasTestSet=str(1-n_error_outliers/len(dataSetOutliersHR()))
    return especificidadAnomaliasTestSet
def especificidadDataTestAnomaliasSteps():
    especificidadAnomaliasTestSet=0
    clf=getCLF()
    if(len(dataSetTrainActividadFisica())!=0 and len(dataSetTestSteps())!=0 and len(dataSetOutliersSteps())!=0):
        global especificidadHRejercicio
        especificidadHRejercicio=True
        y_pred_train = clf.predict(dataSetTrainActividadFisica())
        y_pred_test = clf.predict(dataSetTestSteps())
        y_pred_outliers = clf.predict(dataSetOutliersSteps())
        n_error_train = y_pred_train[y_pred_train == -1].size
        n_error_test = y_pred_test[y_pred_test == -1].size
        n_error_outliers = y_pred_outliers[y_pred_outliers == 1].size
        especificidadAnomaliasTestSet=str(1-n_error_outliers/len(dataSetOutliersSteps()))
    return especificidadAnomaliasTestSet

def accuracyGlobalDataTestHR():
    print("INICIO ACCURACYGLOBAL")
    clf=getCLF()
    accuracyTestGlobal=0
    if(len(dataSetTrainHRreposo())!=0 and len(dataSetTestHRreposo())!=0 and len(dataSetOutliersHR())!=0):
        global accuracyHRreposo
        accuracyHRreposo=True
        y_pred_train = clf.predict(dataSetTrainHRreposo())
        y_pred_test = clf.predict(dataSetTestHRreposo())
        y_pred_outliers = clf.predict(dataSetOutliersHR())
        n_error_train = y_pred_train[y_pred_train == -1].size
        n_error_test = y_pred_test[y_pred_test == -1].size
        n_error_outliers = y_pred_outliers[y_pred_outliers == 1].size
        accuracyTestGlobal=str(1-(n_error_test+n_error_outliers)/(len(dataSetTestHRreposo())+len(dataSetOutliersHR())))
    elif(len(dataSetTrainHRejericio())!=0 and len(dataSetTestHRrejercicio())!=0 and len(dataSetOutliersHR())!=0):
        global accuracyHRejercicio
        accuracyHRejercicio=True
        y_pred_train = clf.predict(dataSetTrainHRejericio())
        y_pred_test = clf.predict(dataSetTestHRrejercicio())
        y_pred_outliers = clf.predict(dataSetOutliersHR())
        n_error_train = y_pred_train[y_pred_train == -1].size
        n_error_test = y_pred_test[y_pred_test == -1].size
        n_error_outliers = y_pred_outliers[y_pred_outliers == 1].size
        accuracyTestGlobal=str(1-(n_error_test+n_error_outliers)/(len(dataSetTestHRrejercicio())+len(dataSetOutliersHR())))
    elif(len(dataSetTrainActividadFisica())!=0 and len(dataSetTestSteps())!=0 and len(dataSetOutliersSteps())!=0):
        global accuracyActividadFisica
        accuracyActividadFisica=True
        y_pred_train = clf.predict(dataSetTrainActividadFisica())
        y_pred_test = clf.predict(dataSetTestSteps())
        y_pred_outliers = clf.predict(dataSetOutliersSteps())
        n_error_train = y_pred_train[y_pred_train == -1].size
        n_error_test = y_pred_test[y_pred_test == -1].size
        n_error_outliers = y_pred_outliers[y_pred_outliers == 1].size
        accuracyTestGlobal=str(1-(n_error_test+n_error_outliers)/(len(dataSetTestSteps())+len(dataSetOutliersSteps())))    
    return accuracyTestGlobal

def accuracyGlobalDataTestSteps():
    print("INICIO ACCURACYGLOBAL")
    accuracyTestGlobal=0
    clf=getCLF()
    if(len(dataSetTrainActividadFisica())!=0 and len(dataSetTestSteps())!=0 and len(dataSetOutliersSteps())!=0):
        global accuracyActividadFisica
        accuracyActividadFisica=True
        y_pred_train = clf.predict(dataSetTrainActividadFisica())
        y_pred_test = clf.predict(dataSetTestSteps())
        y_pred_outliers = clf.predict(dataSetOutliersSteps())
        n_error_train = y_pred_train[y_pred_train == -1].size
        n_error_test = y_pred_test[y_pred_test == -1].size
        n_error_outliers = y_pred_outliers[y_pred_outliers == 1].size
        accuracyTestGlobal=str(1-(n_error_test+n_error_outliers)/(len(dataSetTestSteps())+len(dataSetOutliersSteps())))    
    return accuracyTestGlobal

""" def modelOneClassSVM():
    print("INICIO MODELONC")
    clf=getCLF()
    nu=random.uniform(0,1)
    gamma=random.uniform(0,5)
    accuracyTraining= accuracyDataTraining()
    recal= recallDataTestNormales()
    especificidad=especificidadDataTestAnomalias()
    accuracyGlobal= accuracyGlobalDataTest()
    clf = OneClassSVM(nu,gamma)
    if(accuracyTraining>=0.99 and recal>=0.99 and especificidad>=0.99 and accuracyGlobal>=0.99):
        clf.fit(dataSetTrain())
    return clf.fit(dataSetTrain()) """
    # plot_oneclass_svm(modelOneClassSVM())  
 