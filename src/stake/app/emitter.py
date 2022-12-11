from app.home.models import Device
from app import socketio
from app.log import readLastLogs
import gc
import pandas as pd 
import numpy as np

def get_devices_names(app):
    with app.app_context():
        devices = Device.query.all()
        devices_list = {}
        for device in devices:
            devices_list[device.mac] = device.devicename
        return devices_list

def send_table(dataframe,app):
    ## Filter features for WebApp
    dataframe = dataframe.filter(['ETH_src','ETH_dst','IP_dst','IP_src','timestamp','IP_p',\
        'TCP_dport','TCP_sport','UDP_dport','UDP_sport'])
    dataframe['timestamp'] = pd.to_datetime(dataframe['timestamp'], unit='s').dt.round('1s').astype(str)
    dataframe['src_device_name'] = "Unknown"
    dataframe['dst_device_name'] = "Unknown"
    devices_list = get_devices_names(app)
    for device in devices_list:
        dataframe['src_device_name'] = np.where((dataframe.ETH_src == device),devices_list[device],dataframe.src_device_name)
        dataframe['dst_device_name'] = np.where((dataframe.ETH_dst == device),devices_list[device],dataframe.dst_device_name)
    dataframe= dataframe.fillna("")
    dataframe_dict = dataframe.to_dict(orient='records')
    socketio.emit('table',dataframe_dict)
    gc.collect()

def send_pie_charts(dataframe):
    ## Filter features for WebApp
    dataframe_src = dataframe['IP_src'].value_counts()
    dataframe_src= dataframe_src.to_json()
    socketio.emit('src_ip_pie_chart',dataframe_src)

    dataframe_dst = dataframe['IP_dst'].value_counts()
    dataframe_dst= dataframe_dst.to_json()
    socketio.emit('dst_ip_pie_chart',dataframe_dst)

    dataframe_src = dataframe['ETH_src'].value_counts()
    dataframe_src= dataframe_src.to_json()
    socketio.emit('src_mac_pie_chart',dataframe_src)

    dataframe_dst = dataframe['ETH_dst'].value_counts()
    dataframe_dst= dataframe_dst.to_json()
    socketio.emit('dst_mac_pie_chart',dataframe_dst)
    gc.collect()

def send_donut_charts(dataframe):
    ## Filter features for WebApp
    dataframe = dataframe['IP_p'].value_counts()
    dataframe= dataframe.to_json()
    socketio.emit('donut_chart',dataframe)
    gc.collect()

def send_bar_charts(dataframe):
    ## Filter features for WebApp
    dataframe_src = dataframe.filter(['TCP_sport','UDP_sport'])
    dataframe_src = pd.value_counts(dataframe_src.values.flatten())
    dataframe_src= dataframe_src.to_json()
    socketio.emit('src_bar_chart',dataframe_src)

    dataframe_dst = dataframe.filter(['TCP_dport','UDP_dport'])
    dataframe_dst = pd.value_counts(dataframe_dst.values.flatten())
    dataframe_dst= dataframe_dst.to_json()
    socketio.emit('dst_bar_chart',dataframe_dst)
    gc.collect()

def send_alert(alert_type,msg):
    df = readLastLogs()[:1]
    jsonResp = (df.to_json(orient='records'))
    socketio.emit(alert_type,[msg,jsonResp])