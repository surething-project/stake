from sklearn.ensemble import RandomForestClassifier #, RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, f1_score, precision_score, recall_score, mean_squared_error, roc_auc_score, roc_curve #, make_scorer
from sklearn.metrics import confusion_matrix #, classification_report
from sklearn.model_selection import GridSearchCV
from preprocess import label_encoder, clean_data_labels, normalize_data, one_hot_encoder
import pandas as pd 
import numpy as np
import scipy.stats as stats
import matplotlib.pyplot as plt
import seaborn as sns
from math import isnan
from sklearn import tree
from os import system
import timeit
from datetime import timedelta, datetime
import gc
from matplotlib.legend_handler import HandlerLine2D

plot_path = "output/randomforest_sl/"

def train_model(df,labels):
    start = timeit.default_timer()
    df,labels = preprocess(df,labels)

    corr_matrix = df.corr(method='pearson').abs()
    with pd.option_context('display.max_rows', None, 'display.max_columns', None,'display.max_colwidth', -1):
        with open(str(plot_path + 'score.txt'), 'a') as out:
            out.write('Feature Correlation:\n'+str(corr_matrix)+'\n')
 
    m = (corr_matrix.mask(np.eye(len(corr_matrix), dtype=bool)).abs() >= 0.90).any()
    raw = corr_matrix.loc[m, m]
    raw[raw < 0.90] = 0
    with pd.option_context('display.max_rows', None, 'display.max_columns', None,'display.max_colwidth', -1):
        print('Highly correlated features:\n',raw)
        with open(str(plot_path + 'score.txt'), 'a') as out:
            out.write('Highly correlated features:\n'+str(raw)+'\n')

    evaluate_model(df,labels)

    ## GridSearch 1 -> Tests: 1-8
    # param_grid = { 
    # 'n_estimators': [100,500,1000],   
    # 'criterion': ["gini"],
    # 'max_features': [8,17,33],
    # 'max_depth': [5,10,15],       
    # 'bootstrap': [False],
    # 'min_samples_split': [2,5],
    # 'min_samples_leaf': [2,5]
    # }

    ## GridSearch 2 -> Tests: 9-15
    # param_grid = { 
    # 'n_estimators': [100,500,1000],   
    # 'criterion': ["gini"],
    # 'max_features': [4,8,17],
    # 'max_depth': [5,10,15],       
    # 'bootstrap': [False],
    # 'min_samples_split': [2,5],
    # 'min_samples_leaf': [2,5]
    # }

    ## GridSearch 3 -> Tests: 29
    # param_grid = { 
    # 'n_estimators': [100,1000,10000],   #each 10000 takes 22 min to train
    # 'criterion': ["gini"],
    # 'max_features': [1,4,17,33],
    # 'max_depth': [5,50,100],       
    # 'bootstrap': [False],
    # 'min_samples_split': [5,50,100],
    # 'min_samples_leaf': [5,50,100]
    # }

    ## GridSearch 4 -> Tests: 38
    # param_grid = { 
    # 'n_estimators': [1000],   
    # 'criterion': ["gini"],
    # 'max_features': [8,17,33],
    # 'max_depth': [5,50,100],       
    # 'bootstrap': [False],
    # 'min_samples_split': [50,100,150],
    # 'min_samples_leaf': [50,100,150]
    # }

    ## GridSearch 5 -> Tests: 39, 40
    # param_grid = { 
    # 'n_estimators': [1000],   
    # 'criterion': ["gini"],
    # 'max_features': [17,33],
    # 'max_depth': [1,2,3,5],       
    # 'bootstrap': [False],
    # 'min_samples_split': [100],
    # 'min_samples_leaf': [100]
    # }

    ## GridSearch 6 -> Tests: 39, 41
    # param_grid = { 
    # 'n_estimators': [1,10,50,1000],   
    # 'criterion': ["gini"],
    # 'max_features': [4,8,17,33],
    # 'max_depth': [2,50],       
    # 'bootstrap': [False],
    # 'min_samples_split': [100],
    # 'min_samples_leaf': [100]
    # }

    ## GridSearch 7 -> Tests: 42-51
    # param_grid = { 
    # 'n_estimators': [15,20,25],   
    # 'criterion': ["gini"],
    # 'max_features': [10],
    # 'max_depth': [2,3,4,5],       
    # 'bootstrap': [False],
    # 'min_samples_split': [20],
    # 'min_samples_leaf': [10,20,30]
    # }

    ## GridSearch 8 -> Best Grid
    param_grid = { 
    'n_estimators': [20],   
    'criterion': ["gini"],
    'max_features': [10],
    'max_depth': [2],       
    'bootstrap': [False],
    'min_samples_split': [20],
    'min_samples_leaf': [10]
    }
    
    ## GridSearch 9 -> Constrained Grid
    #param_grid = { 
    #'n_estimators': [3],   
    #'criterion': ["gini"],
    #'max_features': [2],
    #'max_depth': [1],       
    #'bootstrap': [False],
    #'min_samples_split': [80],
    #'min_samples_leaf': [60]
    #}

    print('\nTraining of Random Forest (Supervised Learning) starting...')
    X_train, X_test, y_train, y_test = train_test_split(df, labels, test_size = 0.33, random_state = 42)
    rf = RandomForestClassifier(random_state = 42) 
    #model = rf.fit(X_train, y_train)
    grid_rf = GridSearchCV(estimator=rf, param_grid=param_grid, cv=5, verbose=10) #verbose to print progress 
    grid_model = grid_rf.fit(X_train, y_train)
    print('...Training of Random Forest (SL) finished.')
    
    model = grid_model.best_estimator_
    print('Best Random Forest (Supervised Learning) parameteres',model)
    
    ## Extract feature importances
    fi = pd.DataFrame({'feature': list(X_train.columns),'importance': model.feature_importances_}).\
        sort_values('importance', ascending = False)

    with pd.option_context('display.max_rows', None, 'display.max_columns', None,'display.max_colwidth', -1):
        print('\nFeature Importance:\n',fi)
        with open(str(plot_path + 'score.txt'), 'a') as out:
            out.write('\nFeature Importance:\n'+str(fi)+'\n')
    
    evaluate(X_train,y_train,X_test,y_test,model)

    ## Print Random Forest
    stop = timeit.default_timer()
    duration = stop - start
    with open(str(plot_path + 'score.txt'), 'a') as out:
        out.write('Duration:'+str(timedelta(seconds=duration)) + '\n')
    print('Random Forest (SL) Train and Evaluation duration: ',str(timedelta(seconds=duration)))
    return model

def preprocess(df,labels):
    print('\nPreprocessing of dataframe:',df.shape,' starting...')
    #df = df.drop(['timestamp'], axis=1)
    df = df.drop(['timestamp', 'ETH_ip', 'ARP_hln', 'ARP_pln', 'ARP_pro', \
        'IP_len', 'IP_opts', 'IP_sum', 'IP_v', 'IP_id', 'IP_off', 'TCP_opts', 'TCP_sum', 'UDP_sum', 'UDP_ulen',\
             'ICMP_sum', 'PAYLOAD_raw'], axis=1)

    #df,labels = clean_data_labels(df,labels)
    df = df.fillna(0)
    df = label_encoder(df,False)
    #df = one_hot_encoder(df,True)
    #df = normalize_data(df)

    print('Preprocessing of dataframe:',df.shape,' finished.')
    return df,labels

def pairgrid_heatmap(x, y, **kws):
    cmap = sns.light_palette(kws.pop("color"), as_cmap=True)
    plt.hist2d(x, y, cmap=cmap, cmin=1, **kws) #cmap='hot'

def evaluate(df,labels,X_test,y_test,model):
    print('\nEvaluation/Prediction of Random Forest (SL) starting...')

    pred = model.predict(X_test)
    print('Prediction Training:',pred)
    n_outliers = sum(pred == -1)  # Outlier points are predicted as -1
    print('Number of outliers: ', n_outliers)

    ## General Evaluation Methods
    #cm = confusion_matrix(y_test, pred,labels=[0,1])
    cm = confusion_matrix(y_test, pred)
    print('Confusion Matrix: \n',cm)
    tn, fp, fn, tp = confusion_matrix(y_test, pred).ravel()
    accuracy = accuracy_score(y_test, pred)
    fscore = f1_score(y_test, pred)#,average='weighted')
    precision = precision_score(y_test, pred)#,average='weighted')
    if (float(tn)+float(fp))!=0:
        specificity = float(tn)/(float(tn)+float(fp))
        fpr = float(fp)/(float(tn)+float(fp))
    else:
        specificity = float('nan')
        fpr = float('nan')
    recall = recall_score(y_test, pred)#,average='weighted')    #also known as True Positive Rate
    auc=float('nan')
    if n_outliers>0:
        auc = roc_auc_score(y_test, pred)
    ## Specific Evaluation Methods
    mse = mean_squared_error(y_test, pred)
    if isnan(mse):
        mse=0

    full_pred = model.predict(df)
    full_n_outliers = sum(full_pred == -1)
    full_cm = confusion_matrix(labels, full_pred)
    print('Confusion Matrix: \n',full_cm)
    full_tn, full_fp, full_fn, full_tp = confusion_matrix(labels, full_pred).ravel()
    full_accuracy = accuracy_score(labels, full_pred)
    full_fscore = f1_score(labels, full_pred)#,average='weighted')
    full_precision = precision_score(labels, full_pred)#,average='weighted')
    if (float(full_tn)+float(full_fp))!=0:
        full_specificity = float(full_tn)/(float(full_tn)+float(full_fp))
        full_fpr = float(full_fp)/(float(full_tn)+float(full_fp))
    else:
        full_specificity = float('nan')
        full_fpr = float('nan')
    full_recall = recall_score(labels, full_pred)#,average='weighted')    #also known as True Positive Rate
    full_auc=float('nan')
    if full_n_outliers>0:
        full_auc = roc_auc_score(labels, full_pred)
    ## Specific Evaluation Methods
    full_mse = mean_squared_error(labels, full_pred)
    if isnan(full_mse):
        full_mse=0
    
    print('Generating plots...')

    ## ROC Plot
    fpr_roc, tpr_roc, threshold = roc_curve(y_test, pred)    
    plt.figure(3)
    plt.plot(fpr_roc, tpr_roc, color='orange', label = 'AUC = %0.2f' % auc)
    plt.plot([0, 1], [0, 1], color='darkblue', linestyle='--')
    plt.xlabel('False Positive Rate')
    plt.ylabel('True Positive Rate (Recall)')
    plt.title('Receiver Operating Characteristic (ROC) Curve')
    plt.legend()
    plt.savefig(plot_path+'rf_roc_norm.png',bbox_inches='tight')
    print('RandomForest plot saved: ',str(plot_path+'rf_roc.png'))
    plt.clf()

    dateTimeObj = datetime.now()
    timestamp = dateTimeObj.strftime("%d-%b-%Y %H:%M:%S")
    result_text = str(timestamp)+" - Random Forest SL -\nTest data:\n"+\
        "[TN:"+str(tn)+"; FP:"+str(fp)+"; FN:"+str(fn)+"; TP:"+str(tp)+";]\n"+ \
        "[Accuracy:"+str(accuracy)+"; F-score:"+str(fscore)+"; Precision:"+str(precision)+"; Recall/ True Positive Rate:"+str(recall)+";"+\
        "Specificity:"+str(specificity)+"; False Positive Rate:"+str(fpr)+"; Mean Squared Error:"+str(mse)+";"+\
        "AUC ROC score:"+str(auc)+";"+"] \n" +\
        "Training data:\n[TN:"+str(full_tn)+"; FP:"+str(full_fp)+"; FN:"+str(full_fn)+"; TP:"+str(full_tp)+";]\n"+ \
        "[Accuracy:"+str(full_accuracy)+"; F-score:"+str(full_fscore)+"; Precision:"+str(full_precision)+"; Recall/ True Positive Rate:"+str(full_recall)+";"+\
        "Specificity:"+str(full_specificity)+"; False Positive Rate:"+str(full_fpr)+"; Mean Squared Error:"+str(full_mse)+";"+\
        "AUC ROC score:"+str(full_auc)+";"+"] \n" +\
        "Model Parameteres: "+str(model) +"\n"+\
        "Pre-processing performed: "+ "Label Encoding - all;"
    print(result_text)
    with open(str(plot_path + 'score.txt'), 'a') as out:
        out.write(result_text + '\n')

    print('Evaluation/Prediction of Random Forest (SL) ended...')

def evaluate_model(df,labels):
    X_train, X_test, y_train, y_test = train_test_split(df, labels, test_size = 0.33, random_state = 42)

    print('Evaluating \'n_estimators\' hyper-parameter')
    n_estimators = [1, 2, 4, 8, 16,24, 32,46,50, 64, 100,150, 200]
    train_results = []
    test_results = []
    for estimator in n_estimators:
        rf = RandomForestClassifier(n_estimators=estimator, n_jobs=-1,bootstrap=False)
        rf.fit(X_train, y_train)
        train_pred = rf.predict(X_train)
        roc_auc = roc_auc_score(y_train, train_pred)
        train_results.append(roc_auc)
        y_pred = rf.predict(X_test)
        roc_auc = roc_auc_score(y_test, y_pred)
        test_results.append(roc_auc)
    plt.figure(7)
    line1, = plt.plot(n_estimators, train_results, 'b', label="Train AUC")
    line2, = plt.plot(n_estimators, test_results, 'r', label="Test AUC")
    plt.legend(handler_map={line1: HandlerLine2D(numpoints=2)})
    plt.ylabel('AUC score')
    plt.xlabel('N estimators hyper-parameter')
    plt.savefig(plot_path+'rf_n_estimators.png',bbox_inches='tight')
    print('RandomForest plot saved: ',str(plot_path+'rf_n_estimators.png'))
    plt.clf()

    print('Evaluating \'max_depths\' hyper-parameter')
    max_depths = np.linspace(1, 32, 32, endpoint=True)
    train_results = []
    test_results = []
    for max_depth in max_depths:
        rf = RandomForestClassifier(max_depth=max_depth, n_jobs=-1,bootstrap=False)
        rf.fit(X_train, y_train)
        train_pred = rf.predict(X_train)
        roc_auc = roc_auc_score(y_train, train_pred)
        train_results.append(roc_auc)
        y_pred = rf.predict(X_test)
        roc_auc = roc_auc_score(y_test, y_pred)
        test_results.append(roc_auc)
    plt.figure(7)
    line1, = plt.plot(max_depths, train_results, 'b', label="Train AUC")
    line2, = plt.plot(max_depths, test_results, 'r', label="Test AUC")
    plt.legend(handler_map={line1: HandlerLine2D(numpoints=2)})
    plt.ylabel('AUC score')
    plt.xlabel('Maximum depth hyper-parameter')
    plt.savefig(plot_path+'rf_max_depths.png',bbox_inches='tight')
    print('RandomForest plot saved: ',str(plot_path+'rf_max_depths.png'))
    plt.clf()

    print('Evaluating \'min_samples_splits\' hyper-parameter')
    min_samples_splits = [2, 5, 10,15,20,25,30,35,40,45,50,60,70,80,90,100]
    train_results = []
    test_results = []
    for min_samples_split in min_samples_splits:
        rf = RandomForestClassifier(min_samples_split=min_samples_split,bootstrap=False)
        rf.fit(X_train, y_train)
        train_pred = rf.predict(X_train)
        roc_auc = roc_auc_score(y_train, train_pred)
        train_results.append(roc_auc)
        y_pred = rf.predict(X_test)
        roc_auc = roc_auc_score(y_test, y_pred)
        test_results.append(roc_auc)
    plt.figure(7)
    line1, = plt.plot(min_samples_splits, train_results,'b', label="Train AUC")
    line2, = plt.plot(min_samples_splits, test_results,  'r', label="Test AUC")
    plt.legend(handler_map={line1: HandlerLine2D(numpoints=2)})
    plt.ylabel('AUC score')
    plt.xlabel('Mininum samples split hyper-parameter')
    plt.savefig(plot_path+'rf_min_samples_splits.png',bbox_inches='tight')
    print('RandomForest plot saved: ',str(plot_path+'rf_min_samples_splits.png'))
    plt.clf()

    print('Evaluating \'min_samples_leafs\' hyper-parameter')
    min_samples_leafs = [2, 5, 10,15,20,25,30,35,40,45,50,60,70,80,90,100]
    train_results = []
    test_results = []
    for min_samples_leaf in min_samples_leafs:
        rf = RandomForestClassifier(min_samples_leaf=min_samples_leaf,bootstrap=False)
        rf.fit(X_train, y_train)
        train_pred = rf.predict(X_train)
        roc_auc = roc_auc_score(y_train, train_pred)
        train_results.append(roc_auc)
        y_pred = rf.predict(X_test)
        roc_auc = roc_auc_score(y_test, y_pred)
        test_results.append(roc_auc)
    plt.figure(7)
    line1, = plt.plot(min_samples_leafs, train_results, 'b', label="Train AUC")
    line2, = plt.plot(min_samples_leafs, test_results, 'r', label="Test AUC")
    plt.legend(handler_map={line1: HandlerLine2D(numpoints=2)})
    plt.ylabel('AUC score')
    plt.xlabel('Minimum samples leaf hyper-parameter')
    plt.savefig(plot_path+'rf_min_samples_leaf.png',bbox_inches='tight')
    print('RandomForest plot saved: ',str(plot_path+'rf_min_samples_leaf.png'))
    plt.clf()

    print('Evaluating \'max_features\' hyper-parameter')
    max_features = list(range(1,X_train.shape[1]))
    train_results = []
    test_results = []
    for max_feature in max_features:
        rf = RandomForestClassifier(max_features=max_feature,bootstrap=False)
        rf.fit(X_train, y_train)
        train_pred = rf.predict(X_train)
        roc_auc = roc_auc_score(y_train, train_pred)
        train_results.append(roc_auc)
        y_pred = rf.predict(X_test)
        roc_auc = roc_auc_score(y_test, y_pred)
        test_results.append(roc_auc)
    plt.figure(7)
    line1, = plt.plot(max_features, train_results, 'b', label="Train AUC")
    line2, = plt.plot(max_features, test_results, 'r', label="Test AUC")
    plt.legend(handler_map={line1: HandlerLine2D(numpoints=2)})
    plt.ylabel('AUC score')
    plt.xlabel('Maximum features hyper-parameter')
    plt.savefig(plot_path+'rf_max_features.png',bbox_inches='tight')
    print('RandomForest plot saved: ',str(plot_path+'rf_max_features.png'))
    plt.clf()
