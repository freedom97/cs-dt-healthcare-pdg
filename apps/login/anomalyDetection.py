

def dataClean():
    data=pd.read_csv("20191117profile.csv", sep=";")
    data=data.drop(['full Name', 'waterLvl', 'weight','height','age','gender'], axis=1)
    df=data
    df=df.drop(['time', 'timeHR'], axis=1)
    return df
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
    s = 120
    b1 = plt.scatter(a_train [:, 0], a_train [:, 1], s=s, edgecolors='k', c="g") # Puntos de entrenamiento
    b2 = plt.scatter(a2_test[:, 0], a2_test[:, 1], s=s, edgecolors='k', c="y") # Puntos de Test
    c = plt.scatter(X_outliers2[:, 0], X_outliers2[:, 1], s=s, edgecolors='k', c="r") # Puntos excepcionales
    
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
def modelOneClassSVM():
    clf = OneClassSVM(nu=0.0001,gamma=0.00001)
    return clf.fit(a_train)

plot_oneclass_svm(modelOneClassSVM())

def accuracyGeneral():
     # Calculamos accuracy del training, test positivos y negativos
    y_pred_train = clf.predict(a_train)
    y_pred_test = clf.predict(a2_test)
    y_pred_outliers = clf.predict(X_outliers2)
    n_error_train = y_pred_train[y_pred_train == -1].size
    n_error_test = y_pred_test[y_pred_test == -1].size
    n_error_outliers = y_pred_outliers[y_pred_outliers == 1].size
    accuracyTrainingSet= str(1-n_error_train/len(a_train ))
    recallNormalesTestSet=str(1-n_error_test/len(a2_test))
    especificidadAnomaliasTestSet=str(1-n_error_outliers/len(X_outliers2))
    accuracyTestGlobal=str(1-(n_error_test+n_error_outliers)/(len(a2_test)+len(X_outliers2)))
   # print("Accuracy del training set: "+str(1-n_error_train/len(a_train ))),print("Recall (normales) del test set: "+str(1-n_error_test/len(a2_test))),print("Especificidad (anomalías) del test set: "+str(1-n_error_outliers/len(X_outliers2))),print("Accuracy del test set entero: "+ str(1-(n_error_test+n_error_outliers)/(len(a2_test)+len(X_outliers2))))
    return accuracyTrainingSet,recallNormalesTestSet,especificidadAnomaliasTestSet,accuracyTestGlobal

def dataSetTrain():
    heart1=[]
    resultDF=dataClean()
    for i in range(len(resultDF.heart_Rate)):
        if resultDF.heart_Rate[i]!=0 and resultDF.heart_Rate[i]<=100:
            heart1.insert(len(heart1),[resultDF.heart_Rate[i],resultDF.step_Count[i+1]])
    a1=np.array(heart1)
    a_train = np.r_[a1+4, a1+2]
    a_train[0:3]
    return a_train
def dataSetTest():
    heart2=[]
    resultDF=dataClean()
    for i in range(math.floor(len(resultDF.heart_Rate)/2)):
        if resultDF.heart_Rate[i]!=0 and resultDF.heart_Rate[i]<=100:
            heart2.insert(len(heart2),resultDF.heart_Rate[(math.floor(len(heart1)/2))+(i+1)-1])
    a2 =np.array(heart2)
    a2_test = np.r_[a2 + 4, a2 + 2]
    a2_test[0:3]
    return a2_test
def dataSetOutliers():
    resultDF=dataClean()
    heart3=[]
       
    for i in range(len(resultDF.heart_Rate)):
        if resultDF.heart_Rate[i]!=0 and resultDF.heart_Rate[i]>=101:
            heart3.insert(len(heart3),[resultDF.heart_Rate[i],resultDF.step_Count[i+1]])
    X_outliers=np.array(heart3)
    X_outliers2=np.r_[X_outliers + 4, X_outliers + 2]
    return X_outliers2