from sklearn.covariance import EllipticEnvelope
from preprocess import label_encoder, one_hot_encoder, transform_data_gaussian, normalize_data, standarize_data, mds_transform, pca_transform
from sklearn.metrics import accuracy_score, f1_score, precision_score, recall_score, mean_squared_error, roc_auc_score, roc_curve, confusion_matrix
import pandas as pd 
import numpy as np
import scipy.stats as stats
import matplotlib.mlab as mlab
import matplotlib.pyplot as plt
import seaborn as sns
from scipy import stats
import timeit
from datetime import timedelta, datetime
import gc

plot_path = "output/ellipticenvelope_ul/"
outlier_frac= 0.05 


def train_model(df,labels):
    start = timeit.default_timer()

    df = preprocess(df)

    corr_matrix = df.corr(method='pearson').abs()
    with pd.option_context('display.max_rows', None, 'display.max_columns', None,'display.max_colwidth', -1):
        with open(str(plot_path + 'score.txt'), 'a') as out:
            out.write('Feature Correlation:\n'+str(corr_matrix)+'\n')
 
    m = (corr_matrix.mask(np.eye(len(corr_matrix), dtype=bool)).abs() >= 0.90).any()
    raw = corr_matrix.loc[m, m]
    raw[raw < 0.90] = 0
    with pd.option_context('display.max_rows', None, 'display.max_columns', None,'display.max_colwidth', -1):
        with open(str(plot_path + 'score.txt'), 'a') as out:
            out.write('Highly correlated features:\n'+str(raw)+'\n')

    print('\nTraining of Elliptic Envelope (Unsupervised Learning) starting...')
    ell = EllipticEnvelope(contamination=outlier_frac)
    model = ell.fit(df)
    print('...Training of Elliptic Envelope (UL) finished.')

    evaluate(df,labels,model,outlier_frac)

    stop = timeit.default_timer()
    duration = stop - start
    with open(str(plot_path + 'score.txt'), 'a') as out:
        out.write('Model Parameters:'+str(model)+'\n')
        out.write('Duration:'+str(timedelta(seconds=duration)) + '\n')
    print('Elliptic Envelope (UL) Train and Evaluation duration: ',str(timedelta(seconds=duration)))
    return model

def preprocess(df):
    print('\nPreprocessing of dataframe:',df.shape,' starting...')
    #df = df.drop(['timestamp'], axis=1)    # EllipticEnvelope has better score without timestamp
    df = df.drop(['timestamp', 'ETH_ip', 'ARP_hln', 'ARP_pln', 'ARP_pro', \
        'IP_len', 'IP_opts', 'IP_sum', 'IP_v', 'IP_id', 'IP_off', 'TCP_opts', 'TCP_sum', 'UDP_sum', 'UDP_ulen',\
             'ICMP_sum', 'PAYLOAD_raw'], axis=1)

    df = df.fillna(0)
    ## LE is needed for Gaussian transformation, does not matter if only categoric or not, returns same final result
    df = label_encoder(df,True)    # Bad Results overall
    #df = label_encoder(df,False)   # Better but still bad for EE
    #df = one_hot_encoder(df,True)  # Not usefull for EE
    df = transform_data_gaussian(df)   # Needed for EE
    #df = mds_transform(df)
    df = pca_transform(df)
    
    print('MDS transform result:')
    print(df.shape)
    print(df.head(5))
    
    ## Not needed normalization or standarization, because PowerTransformer(in transform_data_gaussian function) already normalizes the data
    #df = normalize_data(df)    
    #df = standarize_data(df)

    print('EllipticEnvelope plot saved: ',str(plot_path+'ee_hist.png'))
    print('Preprocessing of dataframe:',df.shape,' finished.')
    return df

def pairgrid_heatmap(x, y, **kws):
    cmap = sns.light_palette(kws.pop("color"), as_cmap=True) #, reverse=True
    plt.hist2d(x, y, cmap=cmap, cmin=1, **kws) #cmap='hot'

# Not working well
def contour_scatter(x, y, decision, **kws):
    x1s = np.linspace(np.min(x)-5, np.max(y)+5, 110)
    x2s = np.linspace(np.min(x)-5, np.max(y)+5, 110)
    x1grid, x2grid = np.meshgrid(x1s, x2s) 

    print('x1grid shape:',x1grid.shape)
    Xgrid = np.c_[x1grid.ravel(), x2grid.ravel()]
    densgrid = decision.reshape(x1grid.shape)

    fig, ax = plt.subplots()
    threshold = stats.scoreatpercentile(decision, 100*outlier_frac)
    ax.contourf(x1grid, x2grid, densgrid, cmap=plt.get_cmap('Blues'), levels=np.linspace(decision.min(), threshold, 7))

def evaluate(df,labels,model,outlier_frac):
    print('\nEvaluation/Prediction of Elliptic Envelope (UL) starting...')

    ## Binary prediction of normal vs. outlier
    pred = model.predict(df)
    outlier_map = np.where(pred==-1)
    n_outliers = sum(pred == -1)  # Outlier points are predicted as -1
    print('Number of outliers: ', n_outliers)
    n_benign = sum(pred == 1)  # Benign points are predicted as 1
    print('Number of benign packets: ', n_benign)

    ## Continuous output of the decision_function
    decision = model.decision_function(df)
    print('Min:',decision.min(), ' Max:', decision.max(), ' Len:',len(decision)) #continuous value that reflects the fitted density at the input point(s)

    threshold = stats.scoreatpercentile(decision, 100*outlier_frac)
    print('Threshold:',threshold)

    ## Calculate Mahalanobis
    #mahalanobis = model.score_samples(df)  # Compute the negative Mahalanobis distances.
    mahalanobis = model.mahalanobis(df)     # Computes the squared Mahalanobis distances of given observations.
    print('Min:',mahalanobis.min(), ' Max:', mahalanobis.max(), ' Len:',len(mahalanobis))

    dateTimeObj = datetime.now()
    timestamp = dateTimeObj.strftime("%d-%b-%Y %H:%M:%S")
    result_text = str(timestamp)+" - Elliptic Envelope UL - "+\
        "\nMahalanobis result:\n"+', '.join(str(e) for e in mahalanobis)+\
        "\nMahalanobis Min:"+str(mahalanobis.min())+'; Mahalanobis Max:'+str(mahalanobis.max())+";"+\
        "\nDecision Function:\n"+ ', '.join(str(e) for e in decision) +\
        "\nDecision Function Min:"+str(decision.min())+'; Decision Function Max:'+str(decision.max())+"; Threshold: "+str(threshold)+";"+\
        "\nNumber of outliers: "+str(n_outliers)+\
        "\nNumber of benign: "+str(n_benign)
    with open(str(plot_path + 'score.txt'), 'a') as out:
         out.write(result_text + '\n')

    tn, fp, fn, tp = confusion_matrix(labels, pred).ravel() #,labels=[-1,1]
    accuracy = accuracy_score(labels, pred)
    fscore = f1_score(labels, pred)#,average='weighted')
    precision = precision_score(labels, pred)#,average='weighted')
    if (float(tn)+float(fp))!=0:
        specificity = float(tn)/(float(tn)+float(fp))
        fpr = float(fp)/(float(tn)+float(fp))
    else:
        specificity = float('nan')
        fpr = float('nan')
    recall = recall_score(labels, pred)#,average='weighted')    #also known as True Positive Rate
    auc=float('nan')
    if n_outliers>0:
        auc = roc_auc_score(labels, pred)

    dateTimeObj = datetime.now()
    timestamp = dateTimeObj.strftime("%d-%b-%Y %H:%M:%S")
    result_text = "[TN:"+str(tn)+"; FP:"+str(fp)+"; FN:"+str(fn)+"; TP:"+str(tp)+";]\n"+ \
        "[Accuracy:"+str(accuracy)+"; F-score:"+str(fscore)+"; Precision:"+str(precision)+"; Recall/ True Positive Rate:"+str(recall)+";"+\
        "Specificity:"+str(specificity)+"; False Positive Rate:"+str(fpr)+";"+\
        "AUC ROC score:"+str(auc)+";"+"] \n" +\
        "Model Parameteres: "+str(model) +"\n"+\
        "Pre-processing performed: "+ "Label Encoding - all; Gaussian;"
    print(result_text)
    with open(str(plot_path + 'score.txt'), 'a') as out:
        out.write(result_text + '\n')
        
    print('Generating plots...')

    ## ROC Plot
    fpr_roc, tpr_roc, threshold = roc_curve(labels, pred)    
    plt.plot(fpr_roc, tpr_roc, color='orange', label = 'AUC = %0.2f' % auc)
    plt.plot([0, 1], [0, 1], color='darkblue', linestyle='--')
    plt.xlabel('False Positive Rate')
    plt.ylabel('True Positive Rate (Recall)')
    plt.title('Receiver Operating Characteristic (ROC) Curve')
    plt.legend()
    plt.savefig(plot_path+'ee_roc.png',bbox_inches='tight')
    print('EllipticEnvelope plot saved: ',str(plot_path+'ee_roc.png'))
    plt.clf()


    ## Individual Scatter plot 

    ##Column in the middle of the list: IP_sum
    x_columns = df.columns
    for x_column in x_columns:
        for y_column in df.columns:
            ## Scatter
            plt.figure(1)   
            xlist = np.linspace(df[x_column].min(), df[x_column].max(), 10) 
            ylist = np.linspace(df[y_column].min(), df[y_column].max(), 10)
            X, Y = np.meshgrid(xlist, ylist)
            z = np.sqrt(X**2 + Y**2)
            plt.contour(X, Y, z)
            plt.scatter(df[x_column].where(pred==1), df[y_column].where(pred==1))
            plt.scatter(df[x_column].where(pred==-1),df[y_column].where(pred==-1), color='r', edgecolors="red",s=80,label="predicted outliers")
            plt.savefig(plot_path+'ee_scatter_'+x_column+'_'+y_column+'.png',bbox_inches='tight')
            print('EllipticEnvelope plot saved: ',str(plot_path+'ee_scatter_'+x_column+'_'+y_column+'.png'))
            plt.clf()
            gc.collect()
        ## Distribution benign and anomalies
        try:
            plt.figure(2)   
            sns.distplot(df[x_column],  color='b')
            sns.distplot(df[x_column].where(pred==-1), color='r')
            plt.savefig(plot_path+'ee_dist_'+x_column+'.png',bbox_inches='tight')
            print('EllipticEnvelope plot saved: ',str(plot_path+'ee_dist_'+x_column+'_'+y_column+'.png'))
            plt.clf()
            gc.collect()
        except Exception as e:
            print('Elliptic Envelope - Error plotting distribution of column:',x_column)
            print(e)
    
    x_columns = df.columns
    for x_column in x_columns:
        for y_column in df.columns:
            ## Scatter
            plt.figure(1)   
            xlist = np.linspace(df[x_column].min(), df[x_column].max(), 10) 
            ylist = np.linspace(df[y_column].min(), df[y_column].max(), 10)
            X, Y = np.meshgrid(xlist, ylist)
            z = np.sqrt(X**2 + Y**2)
            plt.contour(X, Y, z)
            plt.scatter(df[x_column].where(labels==1), df[y_column].where(labels==1))
            plt.scatter(df[x_column].where(labels==-1),df[y_column].where(labels==-1), color='r', edgecolors="red",s=80,label="predicted outliers")
            plt.savefig(plot_path+'ee_real_scatter_'+x_column+'_'+y_column+'.png',bbox_inches='tight')
            print('EllipticEnvelope plot saved: ',str(plot_path+'ee_real_scatter_'+x_column+'_'+y_column+'.png'))
            plt.clf()
            gc.collect()
        ## Distribution benign and anomalies
        try:
            plt.figure(2)   
            sns.distplot(df[x_column],  color='b')
            sns.distplot(df[x_column].where(labels==-1), color='r')
            plt.savefig(plot_path+'ee_real_dist_'+x_column+'.png',bbox_inches='tight')
            print('EllipticEnvelope plot saved: ',str(plot_path+'ee_real_dist_'+x_column+'_'+y_column+'.png'))
            plt.clf()
            gc.collect()
        except Exception as e:
            print('Elliptic Envelope - Error plotting distribution of column:',x_column)
            print(e)

    print('Finished generating plots.')
    print('Evaluation/Prediction of Elliptic Envelope (UL) ended...')
