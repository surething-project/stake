import pickle, gc, re
import _pickle as cPickle
from scapy.all import wrpcap
from datetime import datetime
from os import listdir, makedirs
from os.path import basename, exists

from app.home.models import Plugin, DataPreProcessing, DatasetFields, EvaluationMethods, EvaluationResults
from app import db, remove_uploaded_file
from app.emitter import send_alert, get_devices_names
from app.log import writeLog
from app.pcap_reader import pcap2dataframe, pcap2dataframe_timestamp
from app.preprocess import label_encoder, label_encoder_specific_columns, one_hot_encoder, gaussian, normalize_data, standarize_data, data_clean, data_filter_fields, pca_transform

import numpy as np
import pandas as pd
from math import isnan
from sklearn.metrics import accuracy_score, f1_score, precision_score, recall_score, mean_squared_error, roc_auc_score, roc_curve, confusion_matrix
import matplotlib.pyplot as plt
from sklearn.model_selection import train_test_split
import timeit
from datetime import datetime,timedelta

APP_STATIC_PATH = "app/base/static/"
PCA_STATIC_PATH = '/pca'     #folder name from plug-in path of pca transformation model of the plug-in

def trainModel(pcap_file_path,anomaly_file_path,plugins_path,plot_path,model,app):
    try:
        start = timeit.default_timer()
        plugins_model_path = plugins_path+model

        ## Selecting the percentage of benign and anomaly samples
        anomaly_percentage = 0.3
        benign_percentage = 1 - anomaly_percentage
        with app.app_context():
            plugin = Plugin.query.filter_by(filepath=plugins_model_path).first()
            if plugin:
                description = 'Starting '+plugin.pluginname +' Dataset Pre-processing ...'
                print('\n'+description)
                short_description = plugin.pluginname +' Pre-Processing starting...'
                writeLog('Plugins','info','Pre-Processing Starting',short_description,description)
                send_alert('info',description)
            
                anomaly_percentage = plugin.anomalysize
                benign_percentage = 1 - anomaly_percentage
        dataframe = data_preprocess(pcap_file_path,plugins_model_path,app,benign_percentage)
        benign_ammount = dataframe.shape[0]
        labels = np.ones(benign_ammount)

        dataframe_anomalies = data_preprocess(anomaly_file_path,plugins_model_path,app,anomaly_percentage)
        anomaly_ammount = dataframe_anomalies.shape[0]
        labels = np.append(labels,np.negative(np.ones(anomaly_ammount)))
        dataframe = dataframe.append(dataframe_anomalies)
        
        ## PCA transformation (requires full dataframe for correct execution)
        with app.app_context():
            plugin = Plugin.query.filter_by(filepath=plugins_model_path).first()
            if plugin:
                preprocessing = DataPreProcessing.query.filter_by(pluginid=plugin.pluginid).first()
                if preprocessing.pca2d:
                    if not exists((plugins_path+PCA_STATIC_PATH)):
                        makedirs((plugins_path+PCA_STATIC_PATH))
                    pca_path=plugins_path+PCA_STATIC_PATH+'/pca_'+str(plugin.pluginid)
                    dataframe = pca_transform(dataframe,pca_path,2,True)
        #class_benign = round(int(dataframe.shape[0]) *benign_percentage)
        #class_anomaly = round(int(dataframe.shape[0]) *anomaly_percentage)
        #dataframe,labels = make_imbalance(dataframe, labels, sampling_strategy={1: class_benign, -1: class_anomaly}, random_state=42)

        X_train = dataframe
        X_test = None
        y_train = labels
        y_test = None
        
        dataframe = dataframe.fillna(0)
        labels = np.nan_to_num(labels)

        with app.app_context():
                description = 'Finished '+plugin.pluginname +' Dataset Pre-processing .'
                print(description+'\n')
                short_description = plugin.pluginname +' Pre-Processing Finished.'
                writeLog('Plugins','success','Pre-Processing Finished',short_description,description)
                send_alert('success',description)
        loaded_model = pickle.load(open((plugins_model_path), 'rb'))
        with app.app_context():
            plugin = Plugin.query.filter_by(filepath=plugins_model_path).first()
            ## Model training in case of Supervised Learning
            if plugin.testsize > 0 and plugin.testsize<=1 and str(plugin.category.value).lower()=='supervised':        
                X_train, X_test, y_train, y_test = train_test_split(dataframe, labels, test_size = plugin.testsize, random_state = 42)
                trained_model = loaded_model.fit(X_train,y_train)
            ## Model training in case of Unsupervised Learning
            else:
                trained_model = loaded_model.fit(dataframe)
        ## Evaluate the model
        if not exists((APP_STATIC_PATH+plot_path)):
            makedirs((APP_STATIC_PATH+plot_path))
        plot_model_path= plot_path+model
        evaluate_model(trained_model,X_train, X_test, y_train, y_test,plot_model_path,plugins_model_path,app)
        
        ## Save model status after training and evaluating
        pickle.dump(trained_model, open(plugins_model_path, 'wb'))
        with app.app_context():
            stop = timeit.default_timer()
            duration = stop - start
            
            plugin = Plugin.query.filter_by(filepath=plugins_model_path).first()
            plugin.status = "Free"
            plugin.error = False
            result = EvaluationResults.query.filter_by(pluginid=plugin.pluginid,datatype="Training").first()
            result.duration = duration
            if str(plugin.category.value).lower()=='supervised':
                result_test = EvaluationResults.query.filter_by(pluginid=plugin.pluginid,datatype="Test").first()
                result_test.duration = duration
            db.session.commit()
            
            description = 'Finished training '+plugin.pluginname+' plug-in| Duration:'+str(timedelta(seconds=duration))+''
            print(description+'\n')
            short_description = 'Plug-in: '+plugin.pluginname+' trained.'
            writeLog('Plugins','success','Training Finished',short_description,description)
            send_alert('success',description)
        gc.collect()
    except:
        with app.app_context():
            plugin = Plugin.query.filter_by(filepath=plugins_model_path).first()
            plugin.status = "Free"
            plugin.error = True
            db.session.commit()
            description = 'Error while Training plug-in: '+plugin.pluginname
            print(description+'\n')
            short_description = 'Error Training - '+plugin.pluginname
            writeLog('Plugins','error','Error Training!',short_description,description)
            send_alert('error',description)
        raise

def predictModel(plugins_path,model_path,temp_dataframe,original_new_packets,scapy_packets,benign_pcap,malign_pcap,app):
    plugins_model_path = plugins_path+model_path
    try:
        new_packets = data_predict_preprocess(original_new_packets.copy(),plugins_model_path,plugins_path,app)
        print('\n','Starting predicting '+basename(plugins_model_path)+' model...')
        loaded_model=None
        ## Some python versions do not support pickle
        try:
            loaded_model = pickle.load(open(plugins_model_path, 'rb'))
        except:
            loaded_model = cPickle.load(open(plugins_model_path,'rb'))
        prediction= loaded_model.predict(new_packets)
        p = 0
        ## Predict in case there are more than 0 packets
        if len(scapy_packets)>0:
            for packet in scapy_packets:
                if p<len(prediction):
                    ## If the packet is benign
                    if prediction[p]== 1:
                        wrpcap(benign_pcap, packet, append=True)
                    ## If the packet is anomalous
                    else:
                        wrpcap(malign_pcap, packet, append=True) 
                p=+1
        pred = pd.DataFrame(data=prediction,columns=['anomaly'])

        result = pd.concat([original_new_packets, pred], axis=1)
        result['src_device_name'] = "Unknown"
        result['dst_device_name'] = "Unknown"
        devices_list = get_devices_names(app)
        
        ## Identify devices in case they were configured by the administrator
        if 'ETH_src' in result.columns:
            for device in devices_list:
                result['src_device_name'] = np.where((result.ETH_src == device),devices_list[device],result.src_device_name)
        if 'ETH_dst' in result.columns:
            for device in devices_list:    
                result['dst_device_name'] = np.where((result.ETH_dst == device),devices_list[device],result.dst_device_name)
                
        ## Remove duplicated anomalies
        result = result.loc[result['anomaly'] == -1]
        if 'ETH_src' in result.columns and 'ETH_dst' in result.columns:
            result.drop_duplicates(subset =['ETH_src','ETH_dst'], keep = "last", inplace = True)

        ## Send alerts and write in the log about the anomalies
        with app.app_context():
            plugin = Plugin.query.filter_by(filepath=plugins_model_path).first()
            context = 'Devices'
            for index, anomaly in result.iterrows():
                if anomaly['src_device_name'] == 'Unknown' and anomaly['src_device_name'] == 'Unknown':
                    context='Traffic'
                description = 'Anomaly detected with '+plugin.pluginname+' plug-in'
                if 'ETH_src' in result.columns:
                    description = description+ '| Source Device:'+anomaly['src_device_name']+ ' \
                        (MAC: '+anomaly['ETH_src']+')'
                else:
                    description = description+ '| Source Device: Unknown'
                if 'ETH_dst' in result.columns:
                    description = description+ '| Destination Device: '+anomaly['dst_device_name']+' (MAC: '+anomaly['ETH_dst']+')'
                else:
                    description = description+ '| Destination Device: Unknown'
                description = description + '| Packet Timestamp:'+ str(datetime.fromtimestamp(anomaly['timestamp']).strftime("%H:%M:%S.%f"))
                print(description+'\n')
                short_description = 'Anomaly detected with '+plugin.pluginname
                writeLog(context,'anomaly','Anomaly Detected!',short_description,description)
                send_alert('anomaly',description)
        print('Finished predicting ',basename(plugins_model_path),' model.\n')
        gc.collect()
    except:
        with app.app_context():
            plugin = Plugin.query.filter_by(filepath=plugins_model_path).first()
            plugin.status = "Free"
            plugin.error = True
            db.session.commit()
            description = 'Error while Predicting anomalies with plug-in: '+plugin.pluginname+'| Possible solution: Re-train plug-in'
            print(description+'\n')
            short_description = 'Error Predicting - '+plugin.pluginname
            writeLog('Plugins','error','Error Predicting!',short_description,description)
            send_alert('error',description)
        raise

def data_preprocess(pcap_file_path,plugins_model_path,app,instances_percentage):
    plugin = None
    preprocessing = None
    datasetfields = None
    with app.app_context():
        plugin = Plugin.query.filter_by(filepath=plugins_model_path).first()
        if plugin:
            preprocessing = DataPreProcessing.query.filter_by(pluginid=plugin.pluginid).first()
            datasetfields = DatasetFields.query.filter_by(pluginid=plugin.pluginid).first()
    if preprocessing:
        print('Starting dataframe Selection...')
        if preprocessing.selectionperiodduration and preprocessing.selectionperiodtype:
            if preprocessing.selectionperiodtype.value.lower() == "instances":
                total_instances = preprocessing.selectionperiodduration*instances_percentage
                dataframe = pcap2dataframe(pcap_file_path,total_instances)
            else:
                dataframe = pcap2dataframe_timestamp(pcap_file_path,preprocessing.selectionperiodduration,preprocessing.selectionperiodtype.value)
        else:
            if preprocessing.selectionperiodduration<=0:
                dataframe = pcap2dataframe_timestamp(pcap_file_path,None,None)
        print('Finished dataframe Selection ',dataframe.shape,'.')
        with app.app_context():
            plugin = Plugin.query.filter_by(filepath=plugins_model_path).first()
            plugin.status = "DataPreProcessing"
            db.session.commit()
        #if preprocessing.cleaning:
        #    dataframe = data_clean(dataframe)
        if datasetfields:
            dataframe = data_filter_fields(datasetfields,dataframe)
        if preprocessing.labelencodertransformation:
            dataframe = label_encoder(dataframe)
        elif preprocessing.onehotencodertransformation:
            dataframe = dataframe.fillna(0)
            #dataframe = label_encoder(dataframe)
            dataframe = one_hot_encoder(dataframe)
        elif preprocessing.gaussiantransformation:
            dataframe = dataframe.fillna(0)
            dataframe = label_encoder(dataframe)
            dataframe = gaussian(dataframe)
        if preprocessing.normalization:
            dataframe = normalize_data(dataframe)
        elif preprocessing.standarization:
            dataframe = standarize_data(dataframe)
        #elif preprocessing.pca2d:
        #    dataframe = pca_transform(dataframe,2)
        return dataframe

def data_predict_preprocess(dataframe,plugins_model_path,plugins_path,app):
    plugin = None
    preprocessing = None
    datasetfields = None
    with app.app_context():
        plugin = Plugin.query.filter_by(filepath=plugins_model_path).first()
        if plugin:
            preprocessing = DataPreProcessing.query.filter_by(pluginid=plugin.pluginid).first()
            datasetfields = DatasetFields.query.filter_by(pluginid=plugin.pluginid).first()
    if datasetfields:
        dataframe = data_filter_fields(datasetfields,dataframe)
    if preprocessing.labelencodertransformation:
        dataframe = label_encoder(dataframe)
    elif preprocessing.onehotencodertransformation:
        dataframe = dataframe.fillna(0)
        #dataframe = label_encoder(dataframe)
        dataframe = one_hot_encoder(dataframe)
    elif preprocessing.gaussiantransformation:
        dataframe = dataframe.fillna(0)
        dataframe = label_encoder(dataframe)
        dataframe = gaussian(dataframe)
    if preprocessing.normalization:
        dataframe = normalize_data(dataframe)
    elif preprocessing.standarization:
        dataframe = standarize_data(dataframe)
    elif preprocessing.pca2d:
        if not exists((plugins_path+'/pca')):
            makedirs((plugins_path+'/pca'))
        pca_path = plugins_path+PCA_STATIC_PATH+'/pca_'+str(plugin.pluginid)
        dataframe = pca_transform(dataframe,pca_path,2,False)
    return dataframe

def evaluate_model(trained_model,X_train,X_test,y_train,y_test,plot_model_path,plugins_model_path,app):
    with app.app_context():
        plugin = Plugin.query.filter_by(filepath=plugins_model_path).first()
        if plugin:
            plugin.status = "PluginEvaluation"
            db.session.commit()
            description = 'Starting Evaluating '+plugin.pluginname +' Plug-in...'
            print('\n'+description)
            short_description = plugin.pluginname+ ' Evaluation starting...'
            writeLog('Plugins','info','Evaluation Starting',short_description,description)
            send_alert('info',description)
            
            methods = EvaluationMethods.query.filter_by(pluginid=plugin.pluginid).first()
            if not(X_train is None and y_train is None):
                result = EvaluationResults.query.filter_by(pluginid=plugin.pluginid,datatype="Training").first()
                if result:
                    result.datatype="Training"
                    result.evaluationdate = datetime.now()
                    ## Supervised Evaluation Methods
                    pred = trained_model.predict(X_train)
                    tn, fp, fn, tp = confusion_matrix(y_train, pred,labels=[-1,1]).ravel()
                    #tn, fp, fn, tp = confusion_matrix(y_train, pred).ravel()
                    if methods.accuracy:
                        result.accuracy = accuracy_score(y_train,pred)
                    else:
                        result.accuracy= None
                    if methods.precision:
                        result.precision = precision_score(y_train, pred)
                    else:
                        result.precision= None
                    if methods.recall:
                        result.recall= recall_score(y_train, pred)
                    else:
                        result.recall= None
                    if methods.f_score:
                        result.f_score =  f1_score(y_train, pred)
                    else:
                        result.f_score= None
                    if methods.specificity:
                        if (float(tn)+float(fp))!=0 and float(tn)!=0:
                            result.specificity = float(tn)/(float(tn)+float(fp))
                        else:
                            result.specificity = float('nan')
                    else:
                        result.specificity= None
                    if methods.false_positive_rate:
                        if (float(tn)+float(fp))!=0 and float(fp)!=0:
                            result.false_positive_rate = float(fp)/(float(tn)+float(fp))
                        else:
                            result.false_positive_rate = float('nan')
                    else:
                        result.false_positive_rate= None
                    if methods.mse:
                        mse = mean_squared_error(y_train, pred)
                        if isnan(mse):
                            result.mse=0
                        else:
                            result.mse=mse
                    else:
                        result.mse= None
                    ## Plots
                    if methods.roc:
                        if result.roc:
                            remove_uploaded_file(result.roc)
                        auc=1.00
                        if sum(pred == -1) != len(pred) and sum(pred==1)!=len(pred):
                            auc = roc_auc_score(y_train, pred)
                        fpr_roc, tpr_roc, threshold = roc_curve(y_train, pred)
                        plt.figure()
                        plt.plot(fpr_roc, tpr_roc, color='orange', label = 'AUC = %0.2f' % auc)
                        plt.plot([0, 1], [0, 1], color='darkblue', linestyle='--')
                        plt.xlabel('False Positive Rate')
                        plt.ylabel('True Positive Rate (Recall)')
                        plt.title('Receiver Operating Characteristic (ROC) Curve')
                        plt.legend()
                        result.roc = APP_STATIC_PATH+plot_model_path+'.png'
                        plt.savefig(result.roc)
                        print('File ',result.roc, ' saved.')
                        plt.clf()
                    ## Unsupervised Evaluation Methods
                    if methods.mahalanobis:
                        try:
                            mahalanobis = trained_model.mahalanobis(X_train)
                            #result.mahalanobis=', '.join(map(str, str(mahalanobis)))
                            result.mahalanobis_min = mahalanobis.min()
                            result.mahalanobis_max = mahalanobis.max()
                        except:

                            #result.mahalanobis= None
                            result.mahalanobis_min = None
                            result.mahalanobis_max = None
                    else:
                        #result.mahalanobis= None
                        result.mahalanobis_min = None
                        result.mahalanobis_max = None
                else:
                    result = EvaluationResults()
                    result.datatype="Training"
                    result.pluginid = plugin.pluginid
                    result.evaluationdate = datetime.now()
                    ## Supervised Evaluation Methods
                    pred = trained_model.predict(X_train)
                    tn, fp, fn, tp = confusion_matrix(y_train, pred).ravel()
                    if methods.accuracy:
                        result.accuracy = accuracy_score(y_train,pred)
                    else:
                        result.accuracy= None
                    if methods.precision:
                        result.precision = precision_score(y_train, pred)
                    else:
                        result.precision= None
                    if methods.recall:
                        result.recall= recall_score(y_train, pred)
                    else:
                        result.recall= None
                    if methods.f_score:
                        result.f_score =  f1_score(y_train, pred)
                    else:
                        result.f_score= None
                    if methods.specificity:
                        if (float(tn)+float(fp))!=0 and float(tn)!=0:
                            result.specificity = float(tn)/(float(tn)+float(fp))
                        else:
                            result.specificity = float('nan')
                    else:
                        result.specificity= None
                    if methods.false_positive_rate:
                        if (float(tn)+float(fp))!=0 and float(fp)!=0:
                            result.false_positive_rate = float(fp)/(float(tn)+float(fp))
                        else:
                            result.false_positive_rate = float('nan')
                    else:
                        result.false_positive_rate= None
                    if methods.mse:
                        mse = mean_squared_error(y_train, pred)
                        if isnan(mse):
                            result.mse=0
                        else:
                            result.mse=mse
                    else:
                        result.mse= None
                    ## Plots
                    if methods.roc:
                        auc=1.00
                        if sum(pred == -1) != len(pred) and sum(pred==1)!=len(pred):
                            auc = roc_auc_score(y_train, pred)
                        fpr_roc, tpr_roc, threshold = roc_curve(y_train, pred)
                        plt.figure()
                        plt.plot(fpr_roc, tpr_roc, color='orange', label = 'AUC = %0.2f' % auc)
                        plt.plot([0, 1], [0, 1], color='darkblue', linestyle='--')
                        plt.xlabel('False Positive Rate')
                        plt.ylabel('True Positive Rate (Recall)')
                        plt.title('Receiver Operating Characteristic (ROC) Curve')
                        plt.legend()
                        result.roc = APP_STATIC_PATH+plot_model_path+'.png'
                        plt.savefig(result.roc)
                        print('File ',result.roc, ' saved.')
                        plt.clf()
                    ## Unsupervised Evaluation Methods
                    if methods.mahalanobis:
                        try:
                            mahalanobis = trained_model.mahalanobis(X_train)
                            #result.mahalanobis=', '.join(map(str, str(mahalanobis)))
                            result.mahalanobis_min = mahalanobis.min()
                            result.mahalanobis_max = mahalanobis.max()
                        except:
                            #result.mahalanobis= None
                            result.mahalanobis_min = None
                            result.mahalanobis_max = None
                    else:
                        #result.mahalanobis= None
                        result.mahalanobis_min = None
                        result.mahalanobis_max = None
                    db.session.add(result)
            if not(X_test is None and y_test is None):
                result = EvaluationResults.query.filter_by(pluginid=plugin.pluginid,datatype="Test").first()
                if result:
                    result.datatype="Test"
                    result.evaluationdate = datetime.now()
                    ## Supervised Evaluation Methods
                    pred = trained_model.predict(X_test)
                    tn, fp, fn, tp = confusion_matrix(y_test, pred,labels=[-1,1]).ravel()
                    #tn, fp, fn, tp = confusion_matrix(y_test, pred).ravel()
                    if methods.accuracy:
                        result.accuracy = accuracy_score(y_test,pred)
                    else:
                        result.accuracy= None
                    if methods.precision:
                        result.precision = precision_score(y_test, pred)
                    else:
                        result.precision= None
                    if methods.recall:
                        result.recall= recall_score(y_test, pred)
                    else:
                        result.recall= None
                    if methods.f_score:
                        result.f_score =  f1_score(y_test, pred)
                    else:
                        result.f_score= None
                    if methods.specificity:
                        if (float(tn)+float(fp))!=0 and float(tn)!=0:
                            result.specificity = float(tn)/(float(tn)+float(fp))
                        else:
                            result.specificity = float('nan')
                    else:
                        result.specificity= None
                    if methods.false_positive_rate:
                        if (float(tn)+float(fp))!=0 and float(fp)!=0:
                            result.false_positive_rate = float(fp)/(float(tn)+float(fp))
                        else:
                            result.false_positive_rate = float('nan')
                    else:
                        result.false_positive_rate= None
                    if methods.mse:
                        mse = mean_squared_error(y_test, pred)
                        if isnan(mse):
                            result.mse=0
                        else:
                            result.mse=mse
                    else:
                        result.mse= None
                    ## Plots
                    if methods.roc:
                        if result.roc:
                            remove_uploaded_file(result.roc)
                        auc=1.00
                        if sum(pred == -1) != len(pred) and sum(pred==1)!=len(pred):
                            auc = roc_auc_score(y_test, pred)
                        fpr_roc, tpr_roc, threshold = roc_curve(y_test, pred)
                        plt.figure()
                        plt.plot(fpr_roc, tpr_roc, color='orange', label = 'AUC = %0.2f' % auc)
                        plt.plot([0, 1], [0, 1], color='darkblue', linestyle='--')
                        plt.xlabel('False Positive Rate')
                        plt.ylabel('True Positive Rate (Recall)')
                        plt.title('Receiver Operating Characteristic (ROC) Curve')
                        plt.legend()
                        result.roc = APP_STATIC_PATH+plot_model_path+'.png'
                        plt.savefig(result.roc)
                        print('File ',result.roc, ' saved.')
                        plt.clf()
                    ## Unsupervised Evaluation Methods
                    if methods.mahalanobis:
                        try:
                            mahalanobis = trained_model.mahalanobis(X_test)
                            #result.mahalanobis=', '.join(map(str, str(mahalanobis)))
                            result.mahalanobis_min = mahalanobis.min()
                            result.mahalanobis_max = mahalanobis.max()
                        except:

                            #result.mahalanobis= None
                            result.mahalanobis_min = None
                            result.mahalanobis_max = None
                    else:
                        #result.mahalanobis= None
                        result.mahalanobis_min = None
                        result.mahalanobis_max = None
                else:
                    result = EvaluationResults()
                    result.datatype="Test"
                    result.pluginid = plugin.pluginid
                    result.evaluationdate = datetime.now()
                    ## Supervised Evaluation Methods
                    pred = trained_model.predict(X_test)
                    tn, fp, fn, tp = confusion_matrix(y_test, pred).ravel()
                    if methods.accuracy:
                        result.accuracy = accuracy_score(y_test,pred)
                    else:
                        result.accuracy= None
                    if methods.precision:
                        result.precision = precision_score(y_test, pred)
                    else:
                        result.precision= None
                    if methods.recall:
                        result.recall= recall_score(y_test, pred)
                    else:
                        result.recall= None
                    if methods.f_score:
                        result.f_score =  f1_score(y_test, pred)
                    else:
                        result.f_score= None
                    if methods.specificity:
                        if (float(tn)+float(fp))!=0 and float(tn)!=0:
                            result.specificity = float(tn)/(float(tn)+float(fp))
                        else:
                            result.specificity = float('nan')
                    else:
                        result.specificity= None
                    if methods.false_positive_rate:
                        if (float(tn)+float(fp))!=0 and float(fp)!=0:
                            result.false_positive_rate = float(fp)/(float(tn)+float(fp))
                        else:
                            result.false_positive_rate = float('nan')
                    else:
                        result.false_positive_rate= None
                    if methods.mse:
                        mse = mean_squared_error(y_test, pred)
                        if isnan(mse):
                            result.mse=0
                        else:
                            result.mse=mse
                    else:
                        result.mse= None
                    ## Plots
                    if methods.roc:
                        auc=1.00
                        if sum(pred == -1) != len(pred) and sum(pred==1)!=len(pred):
                            auc = roc_auc_score(y_test, pred)
                        fpr_roc, tpr_roc, threshold = roc_curve(y_test, pred)
                        plt.figure()
                        plt.plot(fpr_roc, tpr_roc, color='orange', label = 'AUC = %0.2f' % auc)
                        plt.plot([0, 1], [0, 1], color='darkblue', linestyle='--')
                        plt.xlabel('False Positive Rate')
                        plt.ylabel('True Positive Rate (Recall)')
                        plt.title('Receiver Operating Characteristic (ROC) Curve')
                        plt.legend()
                        result.roc = APP_STATIC_PATH+plot_model_path+'.png'
                        plt.savefig(result.roc)
                        print('File ',result.roc, ' saved.')
                        plt.clf()
                    ## Unsupervised Evaluation Methods
                    if methods.mahalanobis:
                        try:
                            mahalanobis = trained_model.mahalanobis(X_test)
                            #result.mahalanobis=', '.join(map(str, str(mahalanobis)))
                            result.mahalanobis_min = mahalanobis.min()
                            result.mahalanobis_max = mahalanobis.max()
                        except:
                            #result.mahalanobis= None
                            result.mahalanobis_min = None
                            result.mahalanobis_max = None
                    else:
                        #result.mahalanobis= None
                        result.mahalanobis_min = None
                        result.mahalanobis_max = None
                    db.session.add(result)   
            db.session.commit()
            description = 'Finished '+plugin.pluginname +' Plug-in Evaluation.'
            print(description+'\n')
            short_description = plugin.pluginname +' Plug-in Evaluation Finished.'
            writeLog('Plugins','success','Plugin Evaluation Finished',short_description,description)
            send_alert('success',description)