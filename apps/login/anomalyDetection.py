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
#warnings.filterwarnings(action=‘ignore’,category=DeprecationWarning)
#warnings.filterwarnings(action=‘ignore’,category=FutureWarning)

def dataClean():
    data=pd.read_csv("20191117profile.csv", sep=";")
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
    
    # Calculamos accuracy del training, test positivos y negativos
    y_pred_train = clf.predict(a_train)
    y_pred_test = clf.predict(a2_test)
    y_pred_outliers = clf.predict(X_outliers2)
    n_error_train = y_pred_train[y_pred_train == -1].size
    n_error_test = y_pred_test[y_pred_test == -1].size
    n_error_outliers = y_pred_outliers[y_pred_outliers == 1].size
    
    print("Accuracy del training set: "+str(1-n_error_train/len(a_train )))
    print("Recall (normales) del test set: "+str(1-n_error_test/len(a2_test)))
    print("Especificidad (anomalías) del test set: "+str(1-n_error_outliers/len(X_outliers2)))
    print("Accuracy del test set entero: "+ str(1-(n_error_test+n_error_outliers)/(len(a2_test)+len(X_outliers2))))



def accuracyDataTraining():
     # Calculamos accuracy del training, test positivos y negativos
    y_pred_train = clf.predict(a_train)
    y_pred_test = clf.predict(a2_test)
    y_pred_outliers = clf.predict(X_outliers2)
    n_error_train = y_pred_train[y_pred_train == -1].size
    n_error_test = y_pred_test[y_pred_test == -1].size
    n_error_outliers = y_pred_outliers[y_pred_outliers == 1].size
    accuracyTrainingSet= str(1-n_error_train/len(a_train ))
   # print("Accuracy del training set: "+str(1-n_error_train/len(a_train ))),print("Recall (normales) del test set: "+str(1-n_error_test/len(a2_test))),print("Especificidad (anomalías) del test set: "+str(1-n_error_outliers/len(X_outliers2))),print("Accuracy del test set entero: "+ str(1-(n_error_test+n_error_outliers)/(len(a2_test)+len(X_outliers2))))
    return accuracyTrainingSet
def recallDataTestNormales():
    y_pred_train = clf.predict(a_train)
    y_pred_test = clf.predict(a2_test)
    y_pred_outliers = clf.predict(X_outliers2)
    n_error_train = y_pred_train[y_pred_train == -1].size
    n_error_test = y_pred_test[y_pred_test == -1].size
    n_error_outliers = y_pred_outliers[y_pred_outliers == 1].size
    recallNormalesTestSet=str(1-n_error_test/len(a2_test))
    return recallDataTestNormales

def especificidadDataTestAnomalias():
    y_pred_train = clf.predict(a_train)
    y_pred_test = clf.predict(a2_test)
    y_pred_outliers = clf.predict(X_outliers2)
    n_error_train = y_pred_train[y_pred_train == -1].size
    n_error_test = y_pred_test[y_pred_test == -1].size
    n_error_outliers = y_pred_outliers[y_pred_outliers == 1].size
    especificidadAnomaliasTestSet=str(1-n_error_outliers/len(X_outliers2))
    return especificidadAnomaliasTestSet

def accuracyGlobalDataTest():
    y_pred_train = clf.predict(a_train)
    y_pred_test = clf.predict(a2_test)
    y_pred_outliers = clf.predict(X_outliers2)
    n_error_train = y_pred_train[y_pred_train == -1].size
    n_error_test = y_pred_test[y_pred_test == -1].size
    n_error_outliers = y_pred_outliers[y_pred_outliers == 1].size
    accuracyTestGlobal=str(1-(n_error_test+n_error_outliers)/(len(a2_test)+len(X_outliers2)))
    return accuracyTestGlobal
   
def modelOneClassSVM():
    nu=random.uniform(0,1)
    gamma=random.uniform(0,5)
   clf = OneClassSVM(nu,gamma)
   return clf.fit(dataSetTrain())

plot_oneclass_svm(modelOneClassSVM())