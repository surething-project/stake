from os import makedirs
from os.path import exists, split
import pandas as pd
from datetime import datetime
from app import get_log_path, get_log_max_rows

def writeLog(context,alert_type,title,short_description,description):
    timestamp=datetime.now()
    try:
        message = """{timestamp};{context};{alert_type};{title};{short_description};{description}""".\
            format(timestamp=timestamp,context=context,alert_type=alert_type,title=title,\
                short_description=short_description,description=description)
        path,filename = split(get_log_path())
        if not exists(path):
            makedirs(path)
        if not exists(get_log_path()):
            with open(get_log_path(), 'w'): pass
        f = open(get_log_path(), 'a')
        f.write(message+'\n')
    except Exception as e:
        print(e)

def readLog():
    df = pd.DataFrame()
    if exists(get_log_path()):
    	df = pd.read_csv(get_log_path(), sep=';', names=['TIMESTAMP','CONTEXT','ALERT_TYPE','TITLE','SHORT_DESCRIPTION', \
        	'DESCRIPTION'], engine='python')  #,nrows=get_log_max_rows())
    	df = df.sort_values(by=['TIMESTAMP'], ascending=False)
    	return df[:get_log_max_rows()]
    return df

def readLastLogs():
    df = pd.DataFrame()
    if exists(get_log_path()):
    	df = pd.read_csv(get_log_path(), sep=';', names=['TIMESTAMP','CONTEXT','ALERT_TYPE','TITLE','SHORT_DESCRIPTION', \
        	'DESCRIPTION'], engine='python')  #,nrows=5)
    	df = df.sort_values(by=['TIMESTAMP'], ascending=False)
    	return df[:5]
    return df