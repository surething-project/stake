from sklearn.preprocessing import LabelEncoder, PowerTransformer, MinMaxScaler, StandardScaler #OneHotEncoder
from sklearn.manifold import MDS
from sklearn.decomposition import PCA
from imblearn.datasets import make_imbalance
from imblearn.over_sampling import SMOTE
from imblearn.under_sampling import RandomUnderSampler
import numpy as np
import pandas as pd

def label_encoder(df,only_categoric):
    le = LabelEncoder()
    for col_name in df.columns:    #all columns iterated: (categoric/all columns option)
        try: 
            if only_categoric:
                if df[col_name].dtype == 'object':
                    df[col_name] = le.fit_transform(df[col_name].astype(str))   #only categoric columns are encoded
            else:   
                df[col_name] = le.fit_transform(df[col_name].astype(str))   #all columns are encoded
        except:
            try:
                print('Dropped column:',col_name)
                df.drop(col_name, axis=1, inplace=True)
            except:
                print('ERRO LABEL ENCODER')
                continue
    df = df.reset_index(drop=True)
    return df

def label_encoder_specific_columns(df,encode_columns,only_categoric):
    #encode_columns = ['ETH_dst','ETH_ip', 'ETH_src', \
    #     'IP_dst', 'IP_p', 'IP_src','PAYLOAD_len','PAYLOAD_raw','PAYLOAD_hex']
    le = LabelEncoder()
    for col_name in encode_columns: #only specific columns are encoded
        try:         
            if only_categoric:
                if df[col_name].dtype == 'object':
                    df[col_name] = le.fit_transform(df[col_name].astype(str))   #only categoric columns are encoded
            else:   
                df[col_name] = le.fit_transform(df[col_name].astype(str))   #all columns are encoded
        except:
            try:
                print('Dropped column:',col_name)
                df.drop(col_name, axis=1, inplace=True)
            except:
                print('ERRO LABEL ENCODER')
                continue
    df = df.reset_index(drop=True)
    return df

def one_hot_encoder(df,only_categoric):
    # Some columns need to be Label Encoded, specially payload or byte related features
    label_encoded_columns = ['ETH_ip','PAYLOAD_len','PAYLOAD_raw','PAYLOAD_hex']    
    df = label_encoder_specific_columns(df,label_encoded_columns,False) 

    #One Hot Encoding categoric data 
    cat_columns = list()
    for col_name in df.columns: #only specific columns are encoded
        if df[col_name].dtype == 'object':
            cat_columns.append(str(col_name))
    df = pd.get_dummies(df,columns=cat_columns)
    df = df.reset_index(drop=True)
    return df

def clean_data(df):
    df.dropna(axis=0, thresh=11, inplace=True) #how='all'
    print('Finished Cleaning dataframe ',df.shape,'.')
    return df

def clean_data_labels(df,labels):
    print('Starting Cleaning dataframe: ',df.shape,' and labels:',len(labels),'.')       

    df['labels'] = labels
    df_clean = df.dropna(axis=0,thresh=12)  
    labels = df_clean['labels'].to_numpy()
    df_clean.drop(columns='labels',inplace=True)

    print('Finished Cleaning dataframe: ',df_clean.shape,' and labels:',len(labels),'.')
    return df_clean,labels

def transform_data_gaussian(df):
    pt = PowerTransformer(method='yeo-johnson', standardize=True) #method='yeo-johnson', standardize=True
    columns = df.columns
    df = pt.fit_transform(df)   
    df = pd.DataFrame(df,columns=columns)
    return df

def normalize_data(df):
    x = df.values 
    columns = df.columns
    min_max_scaler = MinMaxScaler()
    x_scaled = min_max_scaler.fit_transform(x)
    df = pd.DataFrame(x_scaled,columns=columns)
    return df

def standarize_data(df):
    x = df.values 
    columns = df.columns
    standarizer = StandardScaler()
    x_scaled = standarizer.fit_transform(x)
    df = pd.DataFrame(x_scaled,columns=columns)
    return df

def oversample_data(df,target,anomaly_percentage):
    sm = SMOTE(sampling_strategy=anomaly_percentage)
    X_res, y_res = sm.fit_resample(df, target)
    return X_res, y_res

def undersample_data(df,target,anomaly_percentage):
    rus = RandomUnderSampler(sampling_strategy=anomaly_percentage)
    X_res, y_res = rus.fit_resample(df, target)
    return X_res, y_res

def balance_data(df,target,class_0,class_1):
    X_res, y_res = make_imbalance(df, target, sampling_strategy={0: class_0, 1: class_1}, random_state=42)
    return X_res, y_res

def mds_transform(df):
    mds = MDS(2,random_state=0)
    df = mds.fit_transform(df)
    return df

def pca_transform(df):
    pca = PCA(n_components=2)
    principalComponents = pca.fit_transform(df)
    df = pd.DataFrame(data = principalComponents,columns = ['component_1', 'component_2'])
    return df