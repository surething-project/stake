from scapy.all import sniff, wrpcap
from app import db
import pandas as pd 
import numpy as np

import re#,gc
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
from os import listdir, stat, makedirs
from os.path import exists
from threading import Thread

from app.home.models import Plugin
from app.plugin import trainModel, predictModel
from app.log import writeLog
from app.emitter import send_alert, send_bar_charts, send_donut_charts, send_pie_charts, send_table
from app.pcap_reader import pcap2dataframe,packets2dataframe

def trainPlugins(pcap_file_path,anomaly_file_path,plugins_path,plot_path,app,first_run):
    print('Starting Training plug-ins...')
    if not exists(plugins_path):
        makedirs(plugins_path)
    for model in listdir(plugins_path):
        if re.search(".+sav$", model):
            plugins_model_path = plugins_path+model
            with app.app_context():
                plugin = Plugin.query.filter_by(filepath=plugins_model_path).first()
            if plugin:
                nextevaluationdate = plugin.lasttrained
                if plugin.trainingperiodtype.value=="Second":
                    nextevaluationdate+=+ timedelta(seconds=plugin.trainingperiodduration)
                elif plugin.trainingperiodtype.value=="Minute":
                    nextevaluationdate+=+ timedelta(minutes=plugin.trainingperiodduration)
                elif plugin.trainingperiodtype.value=="Hour":
                    nextevaluationdate+=+ timedelta(hours=plugin.trainingperiodduration)
                elif plugin.trainingperiodtype.value=="Day":
                    nextevaluationdate+=+ timedelta(days=plugin.trainingperiodduration)
                elif plugin.trainingperiodtype.value=="Week":
                    nextevaluationdate+=+ timedelta(weeks=plugin.trainingperiodduration)
                elif plugin.trainingperiodtype.value=="Month":
                    #nextevaluationdate+=+ relativedelta(months=+plugin.trainingperiodduration)
                    nextevaluationdate+= relativedelta(months=+plugin.trainingperiodduration)
                now = datetime.now()

                print('PluginID:',plugin.pluginid ,'| STATUS:',plugin.status.value ,'| NOW:',now,'| NextEvaluationDate:',nextevaluationdate, \
                    '| DateDiff:',nextevaluationdate<=now,'| FIRST_RUN:',first_run, '| ForceTrain:',plugin.forcetrain, \
                        '| Error:',plugin.error,'\n')
                
                if (plugin.retrain and nextevaluationdate<=now and plugin.status.value == "Free") or (first_run and plugin.retrain) or \
                     (plugin.forcetrain and plugin.status.value == "Free"):
                    description = 'Starting training '+plugin.pluginname+' plugin...'
                    print('\n'+description)
                    short_description = 'Plugin: '+plugin.pluginname+' training...'
                    writeLog('Plugins','info','Training Started',short_description,description)
                    send_alert('info',description)
                    
                    with app.app_context():
                        plugin = Plugin.query.filter_by(filepath=plugins_model_path).first()
                        if plugin.forcetrain:
                            plugin.forcetrain = False
                        plugin.lasttrained=now
                        plugin.status = "ReadingPCAP"
                        db.session.commit()
                    Thread(target = trainModel, daemon=True,args=(pcap_file_path,anomaly_file_path,plugins_path,plot_path,model,app,)).start()

def predictPlugins(plugins_path,dataframe,new_packets,packets,pcapPath,anomalyPcapPath,app):
    print('Starting Predicting plug-ins...')
    active_plugins=0
    if new_packets.shape[0]>0:
        for model in listdir(plugins_path):
            if re.search(".+sav$", model):
               plugins_model_path = plugins_path+model
               with app.app_context():
                   plugin = Plugin.query.filter_by(filepath=plugins_model_path).first()
               if plugin:
                   if plugin.active and not plugin.error:
                       active_plugins=1
                       Thread(target = predictModel, daemon=True,args=(plugins_path,model,dataframe,new_packets,packets,pcapPath,anomalyPcapPath,app,)).start()
        if active_plugins==0:
            wrpcap(pcapPath, packets, append=True)
    print('\nFinished Predicting plug-ins.\n')

def sniff_packets(stake,app):
    for model in listdir(stake.pluginsPath):
        if re.search(".+sav$", model):
            plugins_model_path = stake.pluginsPath+model
            with app.app_context():
                plugin = Plugin.query.filter_by(filepath=plugins_model_path).first()
                plugin.status = "Free"
                db.session.commit()
    description="STAKE System Initiated."
    short_description = 'STAKE System Initiated'
    writeLog('System','info','System Initiated',short_description,description)   
    send_alert('info',description)

    if not exists(stake.pcapPath) or stat(stake.pcapPath).st_size == 0:
        dataframe = pd.DataFrame()
        packets = sniff(iface=stake.networkAdapter,count=stake.refreshRatio)
        wrpcap(stake.pcapPath, packets, append=True)
        
    dataframe = pcap2dataframe(stake.pcapPath,stake.maxPackets)
    dataframe_anomalies = pcap2dataframe(stake.anomalyPcapPath,stake.maxPackets)
    dataframe = dataframe.append(dataframe_anomalies)
    dataframe= dataframe.sort_values(by=['timestamp'])
    dataframe = dataframe.tail(stake.maxPackets)    
    trainPlugins(stake.pcapPath,stake.anomalyPcapPath,stake.pluginsPath,stake.plotPath,app,True)
    while(True):
        packets = sniff(iface=stake.networkAdapter,count=stake.refreshRatio)

        new_packets = pd.DataFrame()
        new_packets = packets2dataframe(packets,stake.pcapPath)   
        dataframe = dataframe[:-stake.refreshRatio]
        dataframe = new_packets.append(dataframe)

        print('Starting Sending near real time data...')
        send_table(dataframe,app)
        send_pie_charts(dataframe)
        send_donut_charts(dataframe)
        send_bar_charts(dataframe)
        print('Finished Sending near real time data.')

        predictPlugins(stake.pluginsPath,dataframe,new_packets,packets,stake.pcapPath,stake.anomalyPcapPath,app)
        trainPlugins(stake.pcapPath,stake.anomalyPcapPath,stake.pluginsPath,stake.plotPath,app,False)