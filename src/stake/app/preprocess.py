import numpy as np
import pandas as pd
from math import isnan
from sklearn.preprocessing import LabelEncoder, PowerTransformer, MinMaxScaler, StandardScaler
from sklearn.decomposition import PCA
import pickle

def label_encoder(dataframe):
    print('Starting Label Encoding Transforming dataframe ',dataframe.shape,'...')
    le = LabelEncoder()
    for col_name in dataframe.columns:
        try:  
            dataframe[col_name] = le.fit_transform(dataframe[col_name].astype(str))
        except:
            try:
                print('[Transforming Error] Dropped column:',col_name)
                dataframe.drop(col_name, axis=1, inplace=True)
            except:
                print('LABEL ENCODER ERROR')
                continue
    dataframe = dataframe.reset_index(drop=True)
    print('Finished Label Encoding Transforming dataframe ',dataframe.shape,'.')
    return dataframe

def label_encoder_specific_columns(dataframe,encode_columns):
    le = LabelEncoder()
    for col_name in encode_columns: #only specific columns are encoded
        try:         
            if col_name in dataframe.columns:
                dataframe[col_name] = le.fit_transform(dataframe[col_name].astype(str))   
        except:
            try:
                print('Dropped column:',col_name)
                dataframe.drop(col_name, axis=1, inplace=True)
            except:
                print('ERRO LABEL ENCODER')
                continue
    dataframe = dataframe.reset_index(drop=True)
    return dataframe

def one_hot_encoder(dataframe):
    print('Starting One Hot Encoding Transforming dataframe ',dataframe.shape,'...')
    label_encoded_columns = ['ETH_ip','PAYLOAD_len','PAYLOAD_raw','PAYLOAD_hex']    
    dataframe = label_encoder_specific_columns(dataframe,label_encoded_columns) 

    #One Hot Encoding categoric data 
    cat_columns = list()
    for col_name in dataframe.columns: #only specific columns are encoded
        if dataframe[col_name].dtype == 'object':
            cat_columns.append(str(col_name))
    dataframe = pd.get_dummies(dataframe,columns=cat_columns)
    dataframe = dataframe.fillna(0)
    dataframe = dataframe.reset_index(drop=True)

    print('Finished One Hot Encoding Transforming dataframe ',dataframe.shape,'.')
    return dataframe

def gaussian(dataframe):
    print('Starting Gaussian Transforming dataframe ',dataframe.shape,'...')
    pt = PowerTransformer(method='yeo-johnson', standardize=True) #method='yeo-johnson', standardize=True
    dataframe = pt.fit_transform(dataframe)   
    dataframe = pd.DataFrame(dataframe)
    print('Finished Gaussian Transforming dataframe ',dataframe.shape,'.')
    return dataframe

def normalize_data(df):
    print('Starting Normalizing dataframe ',df.shape,'...')
    x = df.values 
    columns = df.columns
    min_max_scaler = MinMaxScaler()
    x_scaled = min_max_scaler.fit_transform(x)
    df = pd.DataFrame(x_scaled,columns=columns)
    print('Finished Normalizing dataframe ',df.shape,'.')
    return df

def standarize_data(df):
    print('Starting Standarazing dataframe ',df.shape,'...')
    x = df.values 
    columns = df.columns
    standarizer = StandardScaler()
    x_scaled = standarizer.fit_transform(x)
    df = pd.DataFrame(x_scaled,columns=columns)
    print('Finished Normalizing dataframe ',df.shape,'.')
    return df

# def oversample_data(df,target,anomaly_percentage):
#     sm = SMOTE(sampling_strategy=anomaly_percentage)
#     X_res, y_res = sm.fit_resample(df, target)
#     return X_res, y_res

# def undersample_data(df,target,anomaly_percentage):
#     rus = RandomUnderSampler(sampling_strategy=anomaly_percentage)
#     X_res, y_res = rus.fit_resample(df, target)
#     return X_res, y_res

def data_clean(dataframe):
    print('Starting Cleaning dataframe ',dataframe.shape,'...')
    
    ## Version 1 of Cleaning (exception in case the columns are not selected, thus, removed):
    # ignore_subset = ['TCP_ack', 'TCP_dport', 'TCP_flags', 'TCP_off', 'TCP_opts', \
    #                 'TCP_seq', 'TCP_sport', 'TCP_sum', 'TCP_urp', 'TCP_win', \
    #                 'UDP_dport', 'UDP_sport', 'UDP_sum', 'UDP_ulen']
    # df = dataframe.isna().all()
    # df[ignore_subset] = False
    # dataframe = dataframe.loc[:, ~df]
    # verify_subset = dataframe.columns.difference(ignore_subset)
    #dataframe.dropna(axis=0, thresh=20, subset=verify_subset, inplace=True) #how='all'

    ## Version 2, Working but not recommended to be used
    dataframe.dropna(axis=0, thresh=11, inplace=True) #how='all'
    print('Finished Cleaning dataframe ',dataframe.shape,'.')
    return dataframe

def pca_transform(df,pca_path,components,fit):
    print('Starting PCA '+str(components)+' Dimension Transforming dataframe ',df.shape,'...')
    principalComponents=None
    if fit:
        pca = PCA(n_components=components)
        principalComponents = pca.fit_transform(df)
        pickle.dump(pca, open(pca_path, 'wb'))
    else:
        pca = pickle.load(open((pca_path), 'rb'))
        principalComponents = pca.transform(df)
    suffix_component = 'component_'
    components_list= [suffix_component + str((sub+1)) for sub in range(components)]
    df = pd.DataFrame(data = principalComponents,columns = components_list)
    print('Finished PCA '+str(components)+' Dimension Transforming dataframe ',df.shape,'.')
    return df

def data_filter_fields(datasetfields,dataframe):
    print('Starting Filtering Fields dataframe ',dataframe.shape,'...')
    fields_filter = []
    # Extra Fields
    if datasetfields.timestamp:
        fields_filter.append('timestamp')
    # Ethernet Fields
    if datasetfields.ether_dst:
        fields_filter.append('ETH_dst')
    if datasetfields.ether_src:
        fields_filter.append('ETH_src')
    if datasetfields.ether_ip:
        fields_filter.append('ETH_ip')
    if datasetfields.ether_type:
        fields_filter.append('ETH_type')
    # ARP Fields
    if datasetfields.arp_hln:
        fields_filter.append('ARP_hln')
    if datasetfields.arp_hrd:
        fields_filter.append('ARP_hrd')
    if datasetfields.arp_op:
        fields_filter.append('ARP_op')
    if datasetfields.arp_pln:
        fields_filter.append('ARP_pln')
    if datasetfields.arp_pro:
        fields_filter.append('ARP_pro')
    if datasetfields.arp_sha:
        fields_filter.append('ARP_sha')
    if datasetfields.arp_spa:
        fields_filter.append('ARP_spa')
    if datasetfields.arp_tha:
        fields_filter.append('ARP_tha')
    if datasetfields.arp_tpa:
        fields_filter.append('ARP_tpa')
    # IP Fields
    if datasetfields.ip_df:
        fields_filter.append('IP_df')
    if datasetfields.ip_src:
        fields_filter.append('IP_src')
    if datasetfields.ip_dst:
        fields_filter.append('IP_dst')
    if datasetfields.ip_hl:
        fields_filter.append('IP_hl')
    if datasetfields.ip_id:
        fields_filter.append('IP_id')
    if datasetfields.ip_len:
        fields_filter.append('IP_len')
    if datasetfields.ip_mf:
        fields_filter.append('IP_mf')
    if datasetfields.ip_off:
        fields_filter.append('IP_off')
    if datasetfields.ip_offset:
        fields_filter.append('IP_offset')
    if datasetfields.ip_opts:
        fields_filter.append('IP_opts')
    if datasetfields.ip_p:
        fields_filter.append('IP_p')
    if datasetfields.ip_rf:
        fields_filter.append('IP_rf')
    if datasetfields.ip_sum:
        fields_filter.append('IP_sum')
    if datasetfields.ip_tos:
        fields_filter.append('IP_tos')
    if datasetfields.ip_ttl:
        fields_filter.append('IP_ttl')
    if datasetfields.ip_v:
        fields_filter.append('IP_v')
    # ICMP Fields
    if datasetfields.icmp_type:
        fields_filter.append('ICMP_type')
    if datasetfields.icmp_code:
        fields_filter.append('ICMP_code')
    if datasetfields.icmp_sum:
        fields_filter.append('ICMP_sum')
    # TCP Fields
    if datasetfields.tcp_ack:
        fields_filter.append('TCP_ack')
    if datasetfields.tcp_dport:
        fields_filter.append('TCP_dport')
    if datasetfields.tcp_sport:
        fields_filter.append('TCP_sport')
    if datasetfields.tcp_flags:
        fields_filter.append('TCP_flags')
    if datasetfields.tcp_off:
        fields_filter.append('TCP_off')
    if datasetfields.tcp_opts:
        fields_filter.append('TCP_opts')
    if datasetfields.tcp_seq:
        fields_filter.append('TCP_seq')
    if datasetfields.tcp_sum:
        fields_filter.append('TCP_sum')
    if datasetfields.tcp_urp:
        fields_filter.append('TCP_urp')
    if datasetfields.tcp_win:
        fields_filter.append('TCP_win')
    # UDP Fields
    if datasetfields.udp_dport:
        fields_filter.append('UDP_dport')
    if datasetfields.udp_sport:
        fields_filter.append('UDP_sport')
    if datasetfields.udp_sum:
        fields_filter.append('UDP_sum')
    if datasetfields.udp_ulen:
        fields_filter.append('UDP_ulen')
    # Payload Fields
    if datasetfields.payload_len:
        fields_filter.append('PAYLOAD_len')
    if datasetfields.payload_raw:
        fields_filter.append('PAYLOAD_raw')
    if datasetfields.payload_hex:
        fields_filter.append('PAYLOAD_hex')
    
    dataframe = dataframe.filter(fields_filter)
    print('Finished Filtering Fields dataframe ',dataframe.shape,'.')
    return dataframe