import pandas as pd
import numpy as np
from pcap_reader import pcap2dataframe
import pickle, re
from os import listdir
from preprocess import label_encoder, clean_data

## Benign data
benign_pcap_path ="/media/sf_VM-SharedFolder/IoT_NIDS_Dataset/iot_intrusion_dataset/benign-dec.pcap"
benign_max_packets = 25   
## Anomaly data
append_anomaly_data = True
anomaly_pcap_path = "/media/sf_VM-SharedFolder/IoT_NIDS_Dataset/iot_intrusion_dataset/mirai-hostbruteforce-2-dec.pcap"
anomaly_max_packets = 25   
## Plot output folder
model_path = "output/models/"

def preprocess(df):
    print('\nPreprocessing of dataframe:',df.shape,' starting...')

    df = clean_data(df)
    df = df.fillna(0)
    df = label_encoder(df,True)

    print('Preprocessing of dataframe:',df.shape,' finished.')
    return df

if __name__ == '__main__':
    test_data = pcap2dataframe(benign_pcap_path,benign_max_packets)    
    if append_anomaly_data:
        anomaly_df = pcap2dataframe(anomaly_pcap_path,anomaly_max_packets)
        test_data = test_data.append(anomaly_df)

    print('\n Complete Test Dataframe shape:',test_data.shape,"")

    test_data = preprocess(test_data)

    ## Specific model:
    model="RandomForestSL.sav"
    model_load_path = model_path+model
    loaded_model = pickle.load(open((model_load_path), 'rb'))
    result = loaded_model.predict(test_data)
    print('Prediction: \n',result)
    labelp1 = sum(result == 1)
    print('Result==1 ->',labelp1)
    labeln1 = sum(result == -1)
    print('Result==-1 ->',labeln1)

    ## All models
    #for model in listdir(model_path):
    #    if re.search(".+sav$", model):
    #        model_load_path = model_path+model
    #        loaded_model = torch.load(open((model_load_path), 'rb'))
    #        loaded_model.predict(test_data)
    #        print('Model:'+loaded_model+' Prediction: \n',result)
    #        labelp1 = sum(result == 1)
    #        print('Result==1 ->',labelp1)
    #        labeln1 = sum(result == -1)
    #        print('Result==-1 ->',labeln1)
