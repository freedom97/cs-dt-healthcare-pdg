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
"""
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

"""
sys.path.insert(1, '/python_fitbit_wapi/')
from .python_fitbit_wapi import gather_keys_oauth2 as Oauth2


# Create your views here.
auth2_client = fitbit.api.Fitbit
userpatient = User
urlCSV =""
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
    return R
    #template_name= 'index'

def authUser(request):    
    username = request.POST['username']
    password = request.POST['password']
    print(username)
    print(password)
    user = authenticate(request, username=username, password=password)
    print(user)
    if user is not None:
        login(request, user)
        print(user)
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
    print("this kind of works")
    logout(request)
    render(request,'login/login.html')
    return JsonResponse([],safe=False)

def registerUser(request):
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
        patientusr = patientUser(user = user, identificationCard=request.POST['iCrd'],    name=request.POST['name'],  lastName =request.POST['lstN'],  weight=request.POST['wght'],    height=request.POST['hght'],    age=request.POST['ageU'],    size_patient=request.POST['size'])        
        
    except Exception as ex1:
        datas.append(str(ex1))
        return JsonResponse(datas,safe=False)     
    
    user.save()
    patientusr.check()        
    myGroup = Group.objects.get(name='pacientes')
    myGroup.user_set.add(user)    
    request.user = user
    datas.append('none')
            
    return JsonResponse(datas,safe=False)

def Register(request):
    return render(request,'login/register.html')

def Patient(request):
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
                return render(request,'login/patient.html')    
    return HttpResponseRedirect('/login')

def Doctor(request):    
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
                auth2_client= fitbit.Fitbit(CLIENT_ID, CLIENT_SECRET, oauth2=True, access_token=ACCESS_TOKEN, refresh_token=REFRESH_TOKEN) 
                return render(request,'login/doctor.html')   
    return HttpResponseRedirect('/login')
def showPatient(request):
    idpatient = request.POST['idPatient']
    try:
        user = User.objects.get(id =idpatient) 
    except ValueError as verr:
        user = User.objects.get(username =idpatient)
    except Exception as exc:
        user = User.objects.get(username =idpatient)
    global userpatient
    userpatient = user
    print('el nombre del usuario es: '+request.user.username)    
    return JsonResponse([user.username],safe=False)



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
            roomie = fit_statsHrate['activities-heart']
            for i in roomie:
                DayHeart = []
                for j in range(len(i['value']['heartRateZones'])):
                    print(i['value']['heartRateZones'][j]['minutes'])
                    DayHeart.append(i['value']['heartRateZones'][j]['minutes'])
                datashet.append(DayHeart)
                datalabel.append(i['dateTime'])
            print(datashet)    
        elif types =="ST":                
            fit_statsnrStp = auth2_client.time_series(resource='activities/steps', base_date='today', end_date='1w')
            roomie = fit_statsnrStp['activities-steps']
            for i in roomie:
                if i['value'] != 0:  
                    datashet.append(i['value'])
                    datalabel.append(str(i['dateTime']))
            
    elif(labels == "month"):
        if   types== "HR":
            fit_statsHrate = auth2_client.time_series(resource='activities/heart', base_date='today', end_date='1w')
            roomie = fit_statsHrate['activities-heart']
            for i in roomie:
                DayHeart = []
                try:
                    for j in range(len(i['value']['heartRateZones'])):
                        DayHeart.append(i['value']['heartRateZones'][j]['minutes'])
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
    print(datas)
    return JsonResponse(datas,safe=False)


def getDataFitbitWeight(request):
    global userpatient
    print(userpatient.patient.weight)
    M2 = float(userpatient.patient.height)*float(userpatient.patient.height)
    W = float(userpatient.patient.weight)
    datas =['peso',userpatient.patient.weight,'altura',userpatient.patient.height,'indice de masa corporal:',(W/M2)]

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

    global urlCSV
    urlCSV = '/Users/croos/Onedrive/Escritorio/'+today+'profile.csv'
    profileFitUsr.to_csv(urlCSV, \
                columns=['time','timeHR','heart_Rate','step_Count','full Name','waterLvl','weight','height','age','gender'], \
                header=True, \
                sep=';', \
                index = False)
    return HttpResponseRedirect("hellow there")
    

"""       
    # ANOMALY DETECTION
def dataClean():
    data=pd.read_csv(urlCSV, sep=";")
    data=data.drop(['full Name', 'waterLvl', 'weight','height','age','gender'], axis=1)
    df=data
    df=df.drop(['time', 'timeHR'], axis=1)
    return df
def dataSetTrain():
    heart1=[]
    resultDF=dataClean()
    for i in range(math.floor(len(resultDF.heart_Rate)/2)):
        if (resultDF.heart_Rate[i]<=94):
            heart1.insert(len(heart1),[resultDF.heart_Rate[i],resultDF.step_Count[i]])
    a1=np.array(heart1)
    a_train = np.r_[a1+4, a1+2]
    a_train[0:3]
    return a_train
def dataSetTest():
    heart2=[]
    resultDF=dataClean()
    for i in range(math.floor(len(resultDF.heart_Rate)/2)):
        if (resultDF.heart_Rate[(math.floor(len(resultDF.heart_Rate)/2))+i]<=94):
            heart2.insert(len(heart2),[resultDF.heart_Rate[(math.floor(len(resultDF.heart_Rate)/2))+i],resultDF.step_Count[(math.floor(len(resultDF.heart_Rate)/2))+i]])
    a2 =np.array(heart2)
    a2_test = np.r_[a2 + 4, a2 + 2]
    a2_test[0:3]
    return a2_test
def dataSetOutliers():
    resultDF=dataClean()
    heart3=[]
       
    for i in range(len(resultDF.heart_Rate)):
        if resultDF.heart_Rate[i]>=99:
            heart3.insert(len(heart3),[resultDF.heart_Rate[i],resultDF.step_Count[i]])
    X_outliers=np.array(heart3)
    X_outliers2=np.r_[X_outliers + 4, X_outliers + 2]
    return X_outliers2

clf = OneClassSVM()
clf.fit(dataSetTrain())
def plot_oneclass_svm(svm):
    # Definimos una grilla de puntos sobre la cual vamos a determinar la frontera de detección de anomalías:
    xx, yy = np.meshgrid(np.linspace(-200, 200, 500), np.linspace(-200, 200, 500))

    # Obtenemos la distancia con la frontera de decisión para cada punto
    Z = svm.decision_function(np.c_[xx.ravel(), yy.ravel()])
    Z = Z.reshape(xx.shape)
    plt.title("Fronteras de detección de anomalías (en rojo)")
    
    # Ploteamos fronteras y pintamos regiones interna y externa a la frontera
    plt.contourf(xx, yy, Z, levels=[Z.min(), 0], colors="gray") # Región anómala
    a = plt.contour(xx, yy, Z, levels=[0], linewidths=4, colors='red') # Fronteras de decisión
    plt.contourf(xx, yy, Z, levels=[0, Z.max()], colors='palevioletred') # Región de tipicidad
    
    # Ploteamos los puntos de entrenamiento, test y anomalías
    s = 250
    b1 = plt.scatter(dataSetTrain() [:, 0],dataSetTrain()[:, 1], s=s, edgecolors='k', c="g") # Puntos de entrenamiento
    b2 = plt.scatter(dataSetTest()[:, 0],dataSetTest()[:, 1], s=s, edgecolors='k', c="y") # Puntos de Test
    c = plt.scatter(dataSetOutliers()[:, 0], dataSetOutliers()[:, 1], s=s, edgecolors='k', c="r") # Puntos excepcionales
    
    #Leyenda
    plt.axis('tight') # Solo el espacio necesario
    plt.xlim((-121, 121))
    plt.ylim((-121, 121))
    plt.legend([a.collections[0], b1, b2, c],
               ["Frontera de anomalías", "Training", "Test normales", "Test anómalos"],
               loc="upper left",
               prop=matplotlib.font_manager.FontProperties(size=11))
    plt.show()
    
    # Calculamos accuracy del training, test positivos y negativos
    y_pred_train = clf.predict(dataSetTrain())
    y_pred_test = clf.predict(dataSetTest())
    y_pred_outliers = clf.predict(dataSetOutliers())
    n_error_train = y_pred_train[y_pred_train == -1].size
    n_error_test = y_pred_test[y_pred_test == -1].size
    n_error_outliers = y_pred_outliers[y_pred_outliers == 1].size
    
    print("Accuracy del training set: "+str(1-n_error_train/len(dataSetTrain() )))
    print("Recall (normales) del test set: "+str(1-n_error_test/len(dataSetTest())))
    print("Especificidad (anomalías) del test set: "+str(1-n_error_outliers/len(dataSetOutliers())))
    print("Accuracy del test set entero: "+ str(1-(n_error_test+n_error_outliers)/(len(dataSetTest())+len(dataSetOutliers()))))
    

def accuracyDataTraining():
     # Calculamos accuracy del training, test positivos y negativos
    y_pred_train = clf.predict(dataSetTrain())
    y_pred_test = clf.predict(dataSetTest())
    y_pred_outliers = clf.predict(dataSetOutliers())
    n_error_train = y_pred_train[y_pred_train == -1].size
    n_error_test = y_pred_test[y_pred_test == -1].size
    n_error_outliers = y_pred_outliers[y_pred_outliers == 1].size
    accuracyTrainingSet= str(1-n_error_train/len(dataSetTrain() ))
   # print("Accuracy del training set: "+str(1-n_error_train/len(a_train ))),print("Recall (normales) del test set: "+str(1-n_error_test/len(a2_test))),print("Especificidad (anomalías) del test set: "+str(1-n_error_outliers/len(X_outliers2))),print("Accuracy del test set entero: "+ str(1-(n_error_test+n_error_outliers)/(len(a2_test)+len(X_outliers2))))
    return accuracyTrainingSet
def recallDataTestNormales():
    y_pred_train = clf.predict(dataSetTrain())
    y_pred_test = clf.predict(dataSetTest())
    y_pred_outliers = clf.predict(dataSetOutliers())
    n_error_train = y_pred_train[y_pred_train == -1].size
    n_error_test = y_pred_test[y_pred_test == -1].size
    n_error_outliers = y_pred_outliers[y_pred_outliers == 1].size
    recallNormalesTestSet=str(1-n_error_test/len(dataSetTest()))
    return recallDataTestNormales

def especificidadDataTestAnomalias():
    y_pred_train = clf.predict(dataSetTrain())
    y_pred_test = clf.predict(dataSetTest())
    y_pred_outliers = clf.predict(dataSetOutliers())
    n_error_train = y_pred_train[y_pred_train == -1].size
    n_error_test = y_pred_test[y_pred_test == -1].size
    n_error_outliers = y_pred_outliers[y_pred_outliers == 1].size
    especificidadAnomaliasTestSet=str(1-n_error_outliers/len(dataSetOutliers()))
    return especificidadAnomaliasTestSet

def accuracyGlobalDataTest():
    y_pred_train = clf.predict(dataSetTrain())
    y_pred_test = clf.predict(dataSetTest())
    y_pred_outliers = clf.predict(dataSetOutliers())
    n_error_train = y_pred_train[y_pred_train == -1].size
    n_error_test = y_pred_test[y_pred_test == -1].size
    n_error_outliers = y_pred_outliers[y_pred_outliers == 1].size
    accuracyTestGlobal=str(1-(n_error_test+n_error_outliers)/(len(dataSetTest())+len(dataSetOutliers())))
    return accuracyTestGlobal
def modelOneClassSVM():
    nu=random.uniform(0,1)
    gamma=random.uniform(0,5)
    accuracyTraining= accuracyDataTraining()
    recal= recallDataTestNormales()
    especificidad=especificidadDataTestAnomalias()
    accuracyGlobal= accuracyGlobalDataTest()
    clf = OneClassSVM(nu,gamma)
    if(accuracyTraining=>0.99 and recal=>0.99 and especificidad=>0.99 and accuracyGlobal=>0.99):
        clf.fit(dataSetTrain())
    return clf.fit(dataSetTrain())

plot_oneclass_svm(modelOneClassSVM())
"""