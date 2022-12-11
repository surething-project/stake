import pandas as pd
import numpy as np
from datetime import datetime,timedelta
from pcap_reader import pcap2dataframe
import elliptic_envelope_ul
import random_forest_sl
import pickle
import timeit

## Benign data
#benign_pcap_path ="/media/sf_VM-SharedFolder/IoT_NIDS_Dataset/iot_intrusion_dataset/benign-dec.pcap"    #total size= 137396
#benign_max_packets = 300#137396   #1000  
#/home/pi/Documents/TrainingDataset/
benign_pcap_path ="/home/pi/Documents/TrainingDataset/stake-benign.pcap"
benign_max_packets = 41578 #200000 #1158539

## Anomaly data
append_anomaly_data = True
#anomaly_pcap_path = "/media/sf_VM-SharedFolder/IoT_NIDS_Dataset/iot_intrusion_dataset/mirai-hostbruteforce-1-dec.pcap" #total size= 135146
#anomaly_max_packets = 10#50000  #86
#anomaly_pcap_path_0 = "/media/sf_VM-SharedFolder/Database/stake-new-device.pcap" #123
anomaly_pcap_path_0 = "/home/pi/Documents/TrainingDataset/stake-new-device-filtered.pcap"
anomaly_max_packets_0 =  2 #2 #123 
#anomaly_pcap_path_1 = "/media/sf_VM-SharedFolder/Database/stake-port-scan.pcap" #1389
anomaly_pcap_path_1 = "/home/pi/Documents/TrainingDataset/stake-port-scan-filtered.pcap"
anomaly_max_packets_1 =  100 #335 #1389 
#anomaly_pcap_path_2 = "/media/sf_VM-SharedFolder/Database/stake-port-scan-stake.pcap" #152
anomaly_pcap_path_2 = "/home/pi/Documents/TrainingDataset/stake-port-scan-stake-filtered.pcap"
anomaly_max_packets_2 =  54 #54 #152 
#anomaly_pcap_path_3 = "/media/sf_VM-SharedFolder/Database/stake-port-scan-raspcam.pcap" #194
anomaly_pcap_path_3 = "/home/pi/Documents/TrainingDataset/stake-port-scan-raspcam-filtered.pcap"
anomaly_max_packets_3 =  60 #60 #194 
#anomaly_pcap_path_4 = "/media/sf_VM-SharedFolder/Database/stake-port-scan-laptop.pcap" #863
anomaly_pcap_path_4 = "/home/pi/Documents/TrainingDataset/stake-port-scan-laptop-filtered.pcap"
anomaly_max_packets_4 =  100 #220 #863 
#anomaly_pcap_path_5 = "/media/sf_VM-SharedFolder/Database/stake-flood-syn-stake.pcap" #60782
anomaly_pcap_path_5 = "/home/pi/Documents/TrainingDataset/stake-flood-syn-stake-filtered.pcap"
anomaly_max_packets_5 =  400 #59048 #60782
#anomaly_pcap_path_6 = "/media/sf_VM-SharedFolder/Database/stake-flood-syn-raspcam.pcap" #168
anomaly_pcap_path_6 = "/home/pi/Documents/TrainingDataset/stake-flood-syn-raspcam-filtered.pcap"
anomaly_max_packets_6 =  87 #87 #168 
#anomaly_pcap_path_7 = "/media/sf_VM-SharedFolder/Database/stake-flood-icmp-stake.pcap" #31102
anomaly_pcap_path_7 = "/home/pi/Documents/TrainingDataset/stake-flood-icmp-stake-filtered.pcap"
anomaly_max_packets_7 =  400 #30845 #31102
#anomaly_pcap_path_8 = "/media/sf_VM-SharedFolder/Database/stake-flood-icmp-raspcam.pcap" #1394
anomaly_pcap_path_8 = "/home/pi/Documents/TrainingDataset/stake-flood-icmp-raspcam-filtered.pcap"
anomaly_max_packets_8 =  400 #1226 #1394 
#anomaly_pcap_path_9 = "/media/sf_VM-SharedFolder/Database/stake-arp-spoof.pcap" #10143
anomaly_pcap_path_9 = "/home/pi/Documents/TrainingDataset/stake-arp-spoof-filtered.pcap"
anomaly_max_packets_9 =  400 #1897 #10143 
## Plot output folder
model_path = "output/models/"

if __name__ == '__main__':
    start = timeit.default_timer()

    df = pcap2dataframe(benign_pcap_path,benign_max_packets)
    #Supervised Learning algorithms need labels
    labels = np.ones(df.shape[0])       
    if append_anomaly_data:
        complete_anomaly_df = pcap2dataframe(anomaly_pcap_path_0,anomaly_max_packets_0)
        anomaly_df = pcap2dataframe(anomaly_pcap_path_1,anomaly_max_packets_1)
        complete_anomaly_df = complete_anomaly_df.append(anomaly_df)
        anomaly_df = pcap2dataframe(anomaly_pcap_path_2,anomaly_max_packets_2)
        complete_anomaly_df = complete_anomaly_df.append(anomaly_df)
        anomaly_df = pcap2dataframe(anomaly_pcap_path_3,anomaly_max_packets_3)
        complete_anomaly_df = complete_anomaly_df.append(anomaly_df)
        anomaly_df = pcap2dataframe(anomaly_pcap_path_4,anomaly_max_packets_4)
        complete_anomaly_df = complete_anomaly_df.append(anomaly_df)
        anomaly_df = pcap2dataframe(anomaly_pcap_path_5,anomaly_max_packets_5)
        complete_anomaly_df = complete_anomaly_df.append(anomaly_df)
        anomaly_df = pcap2dataframe(anomaly_pcap_path_6,anomaly_max_packets_6)
        complete_anomaly_df = complete_anomaly_df.append(anomaly_df)
        anomaly_df = pcap2dataframe(anomaly_pcap_path_7,anomaly_max_packets_7)
        complete_anomaly_df = complete_anomaly_df.append(anomaly_df)
        anomaly_df = pcap2dataframe(anomaly_pcap_path_8,anomaly_max_packets_8)
        complete_anomaly_df = complete_anomaly_df.append(anomaly_df)
        anomaly_df = pcap2dataframe(anomaly_pcap_path_9,anomaly_max_packets_9)
        complete_anomaly_df = complete_anomaly_df.append(anomaly_df)

        df = df.append(complete_anomaly_df)
        labels = np.append(labels,np.negative(np.ones(complete_anomaly_df.shape[0])))

    print('\n Complete Dataframe shape:',df.shape,"")
    print('\n Complete Labels shape:',len(labels),"")
    labelp1 = sum(labels == 1)
    print('labels==1 ->',labelp1)
    labeln1 = sum(labels == -1)
    print('labels==-1 ->',labeln1)

    stop = timeit.default_timer()
    duration = stop - start
    print('Dataset .pcap reading duration: ',str(timedelta(seconds=duration)))

    plugins = list()

    ## Elliptic Envelope(UL) model
    ee_result = elliptic_envelope_ul.train_model(df,labels)
    plugins.append(("EllipticEnvelopeUL",ee_result))

    ## Random Forest(SL) model
    rf_result = random_forest_sl.train_model(df,labels)
    plugins.append(("RandomForestSL",rf_result))

    dateTimeObj = datetime.now()
    timestamp = dateTimeObj.strftime("%d-%b-%Y_%H-%M-%S")
    print('')
    for (pluginname,result) in plugins:
        ## Use the below for model testing and the above for saving the model
        filename = model_path+pluginname+'_'+timestamp+'.sav'  #Saving
        # filename = model_path+pluginname+'.sav'                 #Testing

        pickle.dump(result, open(filename, 'wb'))
        print('Saved ',pluginname, ' plugin in the path:',filename)
