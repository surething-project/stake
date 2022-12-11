# -*- encoding: utf-8 -*-
"""
License: MIT
Copyright (c) 2019 - present AppSeed.us
"""
from app.home import blueprint
from flask import render_template, redirect, url_for
from flask_login import login_required, current_user
from jinja2 import TemplateNotFound
from . import system_info
from flask import Markup,jsonify,request
from app.home.forms import DeviceForm,PlugInForm
from app.home.models import Device, Plugin, DatasetFields, DataPreProcessing, EvaluationMethods, EvaluationResults
from app import db, get_upload_dir, remove_uploaded_file, get_network_adapter
from os import path
import re, json
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
from werkzeug.utils import secure_filename
from app.log import readLog, readLastLogs

@blueprint.route('/index')
@login_required
def index():
    if current_user.is_authenticated:
        df = readLog()
        df = df.filter(['TIMESTAMP','ALERT_TYPE','TITLE','SHORT_DESCRIPTION'])[50:]
        table = json.loads(df.to_json(orient='index')).items()
        devicesTable = get_devices_short_table()
        plugins_data = get_plugins_short_data()
        plugin_tab = get_plugins_tab()
        return render_template('index.html', cpu_usage=system_info.get_cpu_usage(),\
            mem_total= system_info.get_mem_total(),mem_used=system_info.get_mem_used(), mem_usage=system_info.get_mem_usage(), \
            swap_total= system_info.get_swap_total(),swap_used=system_info.get_swap_used(), swap_usage=system_info.get_swap_usage(), \
            disk_total= system_info.get_disk_total(),disk_used=system_info.get_disk_used(), disk_usage=system_info.get_disk_usage(), \
            bytes_sent=system_info.get_bytes_sent(),bytes_recv=system_info.get_bytes_recv(), \
                bytes_percentage=system_info.get_bytes_percentage(),interfaces=system_info.get_interfaces(get_network_adapter()), \
                interfaces_progress=Markup(system_info.get_interfaces_progress(get_network_adapter())),table=table,columns=df.columns,devices_table=devicesTable, \
                plugins=plugins_data,pluginsTab=plugin_tab)
    return redirect(url_for('base_blueprint.login'))

@blueprint.route('/raspberry')
@login_required
def raspberry():
    if not current_user.is_authenticated:
        return redirect(url_for('base_blueprint.login'))
    return render_template('/raspberry.html',\
        os_info=system_info.get_os_info(),cpu_info=system_info.get_cpu_info(), \
        mem_info=system_info.get_mem_info(),network_info=system_info.get_network_info(get_network_adapter()), \
        cpu_usage=system_info.get_cpu_usage(),\
        mem_total= system_info.get_mem_total(),mem_used=system_info.get_mem_used(), mem_usage=system_info.get_mem_usage(), \
        swap_total= system_info.get_swap_total(),swap_used=system_info.get_swap_used(), swap_usage=system_info.get_swap_usage(), \
        disk_total= system_info.get_disk_total(),disk_used=system_info.get_disk_used(), disk_usage=system_info.get_disk_usage(), \
        bytes_sent=system_info.get_bytes_sent(),bytes_recv=system_info.get_bytes_recv(), \
            bytes_percentage=system_info.get_bytes_percentage(),interfaces=system_info.get_interfaces(get_network_adapter()), \
            interfaces_progress=Markup(system_info.get_interfaces_progress(get_network_adapter())))

@blueprint.route('/traffic')
@login_required
def traffic():
    if current_user.is_authenticated:
        return render_template('traffic.html')
    return redirect(url_for('base_blueprint.login'))

@blueprint.route('/devices', methods=['GET', 'POST'])
@login_required
def devices():
    device_form = DeviceForm(request.form)
    if current_user.is_authenticated:
        if 'submit_add_device' in request.form:
            name = request.form['add_name']
            mac = request.form['add_mac']
            description = request.form['add_description']
            deviceNameList,devicesTable = get_devices()
            device_form.remove_name.choices = deviceNameList
            if name and mac and description and is_valid_mac(mac):
                add_device_name = Device.query.filter_by(devicename=name).first()
                add_device_mac = Device.query.filter_by(mac=mac).first()
                if not add_device_name and not add_device_mac:
                    device = Device(**request.form)
                    device.devicename = name
                    device.mac = mac
                    device.description = description
                    device.nalerts = 0
                    db.session.add(device)
                    db.session.commit()
                    deviceNameList,devicesTable = get_devices()
                    device_form.remove_name.choices = deviceNameList
                    return render_template('devices.html',msg_add='Device Added',form=device_form,devices_table=devicesTable,color='lime')
                else:
                    return render_template('devices.html',msg_add='Device Already Exists',form=device_form,devices_table=devicesTable,color='red')
            else:
                return render_template('devices.html',msg_add='Invalid Device',form=device_form,devices_table=devicesTable,color='red')
        elif 'submit_remove_device' in request.form:
            name = request.form['remove_name']
            remove_device = Device.query.filter_by(devicename=name).first()
            if name and remove_device:
                db.session.delete(remove_device)
                db.session.commit()
                deviceNameList,devicesTable = get_devices()
                device_form.remove_name.choices = deviceNameList
                return render_template('devices.html',msg_remove='Device Removed',form=device_form,devices_table=devicesTable,color='orange')
            else:
                deviceNameList,devicesTable = get_devices()
                device_form.remove_name.choices = deviceNameList
                return render_template('devices.html',msg_remove='Invalid Device',form=device_form,devices_table=devicesTable,color='red')
        deviceNameList,devicesTable = get_devices()
        device_form.remove_name.choices = deviceNameList
        return render_template('devices.html',form=device_form,devices_table=devicesTable)
    return redirect(url_for('base_blueprint.login'))

def is_valid_mac(mac):
    m = re.match("^[a-fA-F0-9:]{17}|[a-fA-F0-9]{12}$", mac)
    return bool(m) and all(map(lambda n: 0 <= int(n) <= 255, m.groups()))

def get_devices():
    devices = Device.query.all()
    deviceNameList = [('name','Name')]
    devicesTable=""
    for device in devices:
        devicesTable = devicesTable +"<tr><td>"+device.devicename+"</td><td>"+device.mac+"</td> \
            <td>"+device.description+"</td><td>"+str(device.nalerts)+"</td></tr>"
        deviceNameList.append( (device.devicename,device.devicename))
    return deviceNameList,devicesTable

def get_devices_short_table():
    devices = Device.query.order_by(Device.id).limit(5).all()
    devicesTable=""
    for device in devices:
        devicesTable = devicesTable +"<tr><td>"+device.devicename+"</td><td>"+device.mac+"</td></tr>"
    return devicesTable

@blueprint.route('/configure-plugins', methods=['GET', 'POST'])
@login_required
def configure_plugins():
    plugin_form = PlugInForm(request.form)
    if current_user.is_authenticated:
        plugin_form.add_integration.checked = True
        plugin_form.add_integration.disabled = True
        if 'submit_add_plugin' in request.form or 'submit_add_plugin_train' in request.form:
            ## Plug-in Information
            plugin = Plugin()
            pluginNameList = get_plugins()
            plugin_form.edit_pluginname.choices = pluginNameList
            plugin.active = bool(request.form.get('add_activate'))
            plugin.retrain = bool(request.form.get('add_retrain'))
            if 'submit_add_plugin' in request.form:
                plugin.forcetrain = False
                final_msg = "Plug-in Added"
            elif 'submit_add_plugin_train' in request.form:
                plugin.forcetrain = True
                final_msg = "Plug-in Added and set for Training"
            plugin.status= "Free"
            plugin.error = False

            add_category = request.form['add_category']
            if not add_category or add_category=='category':
                return render_template('configure-plugins.html',form=plugin_form,msg_add="[Plug-in Information] Please select a valid plug-in category",color="red",add_tab=True)
            plugin.category = add_category

            add_testsize = request.form['add_testsize']
            if add_category=='Supervised':
                if not add_testsize or not is_valid_float(add_testsize):
                    return render_template('configure-plugins.html',form=plugin_form,msg_add="[Plug-in Information] Please select a valid test size value",color="red",add_tab=True)
                add_testsize = float(add_testsize)
                if add_testsize<=0 or add_testsize>=1:
                    return render_template('configure-plugins.html',form=plugin_form,msg_add="[Plug-in Information] Test size must be between 1.0 and 0.0",color="red",add_tab=True)
                plugin.testsize = add_testsize
            else:
                plugin.testsize = 0
            
            add_anomalysize = request.form['add_anomalysize']
            if not add_anomalysize or not is_valid_float(add_anomalysize):
                return render_template('configure-plugins.html',form=plugin_form,msg_add="[Plug-in Information] Please select a valid anomaly size value",color="red",add_tab=True)
            add_anomalysize = float(add_anomalysize)
            if add_anomalysize<=0 or add_anomalysize>=1:
                return render_template('configure-plugins.html',form=plugin_form,msg_add="[Plug-in Information] Anomaly size must be between 1.0 and 0.0",color="red",add_tab=True)
            plugin.anomalysize = add_anomalysize

            add_trainingperiodtype = request.form['add_trainingperiodtype']
            if not add_trainingperiodtype or add_trainingperiodtype=='trainingperiodtype':
                return render_template('configure-plugins.html',form=plugin_form,msg_add="[Plug-in Information] Please select a valid period type",color="red",add_tab=True)
            plugin.trainingperiodtype = add_trainingperiodtype

            add_trainingperiodduration = request.form['add_trainingperiodduration']
            if not add_trainingperiodduration or not is_valid_integer(add_trainingperiodduration) :
                return render_template('configure-plugins.html',form=plugin_form,msg_add="[Plug-in Information] Please select a valid training periodicity value",color="red",add_tab=True)
            add_trainingperiodduration = int(add_trainingperiodduration)
            if add_trainingperiodduration<=0:
                return render_template('configure-plugins.html',form=plugin_form,msg_add="[Plug-in Information] Training periodicity must be more than 0",color="red",add_tab=True)
            plugin.trainingperiodduration = add_trainingperiodduration

            add_pluginname = request.form['add_pluginname']
            exist_pluginname = Plugin.query.filter_by(pluginname=add_pluginname).first()
            dateTimeObj = datetime.now()
            timestamp = dateTimeObj.strftime("_%d-%b-%Y_%H-%M-%S")
            file_path = get_upload_dir()+secure_filename(add_pluginname) + timestamp + ".sav"
            exist_pluginpath = Plugin.query.filter_by(filepath=file_path).first()
            if exist_pluginname or exist_pluginpath:
                return render_template('configure-plugins.html',form=plugin_form,msg_add="[Plug-in Information] Plug-in already exists",color="red",add_tab=True)
            add_file = request.files['add_file'] if request.files.get('add_file') else None
            if not add_file or not add_file.filename.lower().endswith('.sav'): 
                return render_template('configure-plugins.html',form=plugin_form,msg_add="[Plug-in Information] Invalid plug-in file",color="red",add_tab=True)
            plugin.pluginname = add_pluginname
            plugin.filepath = file_path
            plugin.creationdate = dateTimeObj
            plugin.lasttrained = dateTimeObj

            db.session.add(plugin)
            db.session.commit()
            pluginid = Plugin.query.filter_by(pluginname=add_pluginname).first().pluginid

            ## Data Pre-processing Steps
            datapreprocessing = DataPreProcessing()
            datapreprocessing.pluginid = pluginid

            ## These settings are currently static because data integration is always required and cleaning data needs specific configuration which is not yet available
            #datapreprocessing.cleaning = bool(request.form.get('add_cleaning'))
            datapreprocessing.cleaning = False
            #datapreprocessing.integration = bool(request.form.get('add_integration'))
            datapreprocessing.integration = True
            #datapreprocessing.transformation = bool(request.form.get('add_transformation'))

            add_selectionperiodtype = request.form['add_selectionperiodtype']
            if not add_selectionperiodtype or add_selectionperiodtype=='selectionperiodtype':
                return render_template('configure-plugins.html',form=plugin_form,msg_add="[Data Pre-Processing Information] Please select a valid Data selection period type",color="red",add_tab=True)
            datapreprocessing.selectionperiodtype = add_selectionperiodtype

            add_selectionperiodduration = request.form['add_selectionperiodduration']
            if not add_selectionperiodduration or not is_valid_integer(add_selectionperiodduration) :
                return render_template('configure-plugins.html',form=plugin_form,msg_add="[Data Pre-Processing Information] Please select a valid Data selection periodicity value",color="red",add_tab=True)
            add_selectionperiodduration = int(add_selectionperiodduration)
            if add_selectionperiodduration<0:
                return render_template('configure-plugins.html',form=plugin_form,msg_add="[Data Pre-Processing Information] Data selection periodicity must be more than 0",color="red",add_tab=True)
            datapreprocessing.selectionperiodduration = add_selectionperiodduration

            add_transformation = request.form['add_transformation']
            if not add_transformation:
                return render_template('configure-plugins.html',form=plugin_form,msg_add="[Data Pre-Processing Information] Please select a valid Data transformation",color="red",add_tab=True)
            datapreprocessing.labelencodertransformation = False
            datapreprocessing.onehotencodertransformation = False
            datapreprocessing.gaussiantransformation = False
            if str(add_transformation).lower() == "labelencoder":
                datapreprocessing.labelencodertransformation = True
            elif str(add_transformation).lower() == "onehotencoder":
                datapreprocessing.onehotencodertransformation = True
            elif str(add_transformation).lower() == "gaussian":
                datapreprocessing.gaussiantransformation = True

            add_secondary_transformation = request.form['add_secondary_transformation']
            if not add_secondary_transformation:
                return render_template('configure-plugins.html',form=plugin_form,msg_add="[Data Pre-Processing Information] Please select a valid Secondary Data transformation",color="red",add_tab=True)
            datapreprocessing.normalization = False
            datapreprocessing.standarization = False
            datapreprocessing.pca2d = False
            if str(add_secondary_transformation).lower() == "normalization":
                datapreprocessing.normalization = True
            elif str(add_secondary_transformation).lower() == "standarization":
                datapreprocessing.standarization = True
            elif str(add_secondary_transformation).lower() == "pca2d":
                datapreprocessing.pca2d = True

            ## Dataset Fields
            datasetfields = DatasetFields()
            datasetfields.pluginid = pluginid

            if not ( bool(request.form.get('add_ETHER_dst')) or bool(request.form.get('add_ETHER_src')) or bool(request.form.get('add_ETHER_ip')) or \
                bool(request.form.get('add_ETHER_type')) or bool(request.form.get('add_ARP_hln')) or bool(request.form.get('add_ARP_hrd')) or\
                bool(request.form.get('add_ARP_op')) or bool(request.form.get('add_ARP_pln')) or bool(request.form.get('add_ARP_pro')) or\
                bool(request.form.get('add_ARP_sha')) or bool(request.form.get('add_ARP_spa')) or bool(request.form.get('add_ARP_tha')) or\
                bool(request.form.get('add_ARP_tpa')) or bool(request.form.get('add_IP_df')) or bool(request.form.get('add_IP_src')) or \
                bool(request.form.get('add_IP_dst')) or bool(request.form.get('add_IP_hl')) or bool(request.form.get('add_IP_id')) or \
                bool(request.form.get('add_IP_len')) or bool(request.form.get('add_IP_mf')) or bool(request.form.get('add_IP_off')) or \
                bool(request.form.get('add_IP_offset')) or bool(request.form.get('add_IP_opts')) or bool(request.form.get('add_IP_p')) or \
                bool(request.form.get('add_IP_rf')) or bool(request.form.get('add_IP_sum')) or bool(request.form.get('add_IP_tos')) or \
                bool(request.form.get('add_IP_ttl')) or bool(request.form.get('add_IP_v')) or bool(request.form.get('add_ICMP_type')) or\
                bool(request.form.get('add_ICMP_code')) or bool(request.form.get('add_ICMP_sum')) or bool(request.form.get('add_TCP_ack')) or \
                bool(request.form.get('add_TCP_dport')) or bool(request.form.get('add_TCP_sport')) or bool(request.form.get('add_TCP_flags')) or \
                bool(request.form.get('add_TCP_off')) or bool(request.form.get('add_TCP_opts')) or bool(request.form.get('add_TCP_seq')) or \
                bool(request.form.get('add_TCP_sum')) or bool(request.form.get('add_TCP_urp')) or bool(request.form.get('add_TCP_win')) or \
                bool(request.form.get('add_UDP_dport')) or bool(request.form.get('add_UDP_sport')) or bool(request.form.get('add_UDP_sum')) or \
                bool(request.form.get('add_UDP_ulen')) or bool(request.form.get('add_PAYLOAD_len')) or bool(request.form.get('add_PAYLOAD_raw')) or \
                bool(request.form.get('add_PAYLOAD_hex')) or bool(request.form.get('add_timestamp')) ):
                db.session.delete(plugin)
                db.session.commit()
                return render_template('configure-plugins.html',form=plugin_form,msg_add="[Dataset Fields] No fields were selected",color="red",add_tab=True)
            # Ethernet
            datasetfields.ether_dst = bool(request.form.get('add_ETHER_dst'))
            datasetfields.ether_src = bool(request.form.get('add_ETHER_src'))
            datasetfields.ether_ip = bool(request.form.get('add_ETHER_ip'))
            datasetfields.ether_type = bool(request.form.get('add_ETHER_type'))
            # ARP
            datasetfields.arp_hln = bool(request.form.get('add_ARP_hln'))
            datasetfields.arp_hrd = bool(request.form.get('add_ARP_hrd'))
            datasetfields.arp_op = bool(request.form.get('add_ARP_op'))
            datasetfields.arp_pln = bool(request.form.get('add_ARP_pln'))
            datasetfields.arp_pro = bool(request.form.get('add_ARP_pro'))
            datasetfields.arp_sha = bool(request.form.get('add_ARP_sha'))
            datasetfields.arp_spa = bool(request.form.get('add_ARP_spa'))
            datasetfields.arp_tha = bool(request.form.get('add_ARP_tha'))
            datasetfields.arp_tpa = bool(request.form.get('add_ARP_tpa'))
            #IP 
            datasetfields.ip_df = bool(request.form.get('add_IP_df'))
            datasetfields.ip_src = bool(request.form.get('add_IP_src'))
            datasetfields.ip_dst = bool(request.form.get('add_IP_dst'))
            datasetfields.ip_hl = bool(request.form.get('add_IP_hl'))
            datasetfields.ip_id = bool(request.form.get('add_IP_id'))
            datasetfields.ip_len = bool(request.form.get('add_IP_len'))
            datasetfields.ip_mf = bool(request.form.get('add_IP_mf'))
            datasetfields.ip_off = bool(request.form.get('add_IP_off'))
            datasetfields.ip_offset = bool(request.form.get('add_IP_offset'))
            datasetfields.ip_opts = bool(request.form.get('add_IP_opts'))
            datasetfields.ip_p = bool(request.form.get('add_IP_p'))
            datasetfields.ip_rf = bool(request.form.get('add_IP_rf'))
            datasetfields.ip_sum = bool(request.form.get('add_IP_sum'))
            datasetfields.ip_tos = bool(request.form.get('add_IP_tos'))
            datasetfields.ip_ttl = bool(request.form.get('add_IP_ttl'))
            datasetfields.ip_v = bool(request.form.get('add_IP_v'))
            #ICMP
            datasetfields.icmp_type = bool(request.form.get('add_ICMP_type'))
            datasetfields.icmp_code = bool(request.form.get('add_ICMP_code'))
            datasetfields.icmp_sum = bool(request.form.get('add_ICMP_sum'))
            #TCP
            datasetfields.tcp_ack = bool(request.form.get('add_TCP_ack'))
            datasetfields.tcp_dport = bool(request.form.get('add_TCP_dport'))
            datasetfields.tcp_sport = bool(request.form.get('add_TCP_sport'))
            datasetfields.tcp_flags = bool(request.form.get('add_TCP_flags'))
            datasetfields.tcp_off = bool(request.form.get('add_TCP_off'))
            datasetfields.tcp_opts = bool(request.form.get('add_TCP_opts'))
            datasetfields.tcp_seq = bool(request.form.get('add_TCP_seq'))
            datasetfields.tcp_sum = bool(request.form.get('add_TCP_sum'))
            datasetfields.tcp_urp = bool(request.form.get('add_TCP_urp'))
            datasetfields.tcp_win = bool(request.form.get('add_TCP_win'))
            #UDP
            datasetfields.udp_dport = bool(request.form.get('add_UDP_dport'))
            datasetfields.udp_sport = bool(request.form.get('add_UDP_sport'))
            datasetfields.udp_sum = bool(request.form.get('add_UDP_sum'))
            datasetfields.udp_ulen = bool(request.form.get('add_UDP_ulen'))
            #Payload
            datasetfields.payload_len = bool(request.form.get('add_PAYLOAD_len'))
            datasetfields.payload_raw = bool(request.form.get('add_PAYLOAD_raw'))
            datasetfields.payload_hex = bool(request.form.get('add_PAYLOAD_hex'))
            #Extra
            datasetfields.timestamp = bool(request.form.get('add_timestamp'))
            
            ## Evaluation Methods
            evaluationmethods = EvaluationMethods()
            evaluationmethods.pluginid = pluginid

            if not ( bool(request.form.get('add_accuracy')) or bool(request.form.get('add_precision')) or bool(request.form.get('add_recall')) or \
                bool(request.form.get('add_f_score')) or bool(request.form.get('add_mahalanobis')) or bool(request.form.get('add_mse')) or \
                bool(request.form.get('add_specificity')) or bool(request.form.get('add_false_positive_rate')) or \
                bool(request.form.get('add_roc')) ):
                db.session.delete(plugin)
                db.session.commit()
                return render_template('configure-plugins.html',form=plugin_form,msg_add="[Evaluation Methods] No evaluation methods were selected",color="red",add_tab=True)
            evaluationmethods.mahalanobis = bool(request.form.get('add_mahalanobis'))
            evaluationmethods.accuracy = bool(request.form.get('add_accuracy'))
            evaluationmethods.precision = bool(request.form.get('add_precision'))
            evaluationmethods.recall = bool(request.form.get('add_recall'))
            evaluationmethods.f_score = bool(request.form.get('add_f_score'))
            evaluationmethods.specificity = bool(request.form.get('add_specificity'))
            evaluationmethods.false_positive_rate = bool(request.form.get('add_false_positive_rate'))
            evaluationmethods.roc = bool(request.form.get('add_roc'))
            evaluationmethods.mse = bool(request.form.get('add_mse'))

            db.session.add(datapreprocessing)
            db.session.add(datasetfields)
            db.session.add(evaluationmethods)

            pluginNameList = get_plugins()
            plugin_form.edit_pluginname.choices = pluginNameList

            db.session.commit()
            add_file.save(file_path)
            return render_template('configure-plugins.html',form=plugin_form,msg_add=final_msg,color="lime",add_tab=True)
        elif 'submit_edit_plugin'in request.form or 'submit_edit_plugin_train' in request.form:  
            edit_pluginname = request.form['edit_pluginname']   
            if not edit_pluginname or edit_pluginname=='plugin name':
                return render_template('configure-plugins.html',form=plugin_form,msg_edit="[Plug-in Information] Please select a valid plug-in",color="red",add_tab=False)
            
            plugin = Plugin.query.filter_by(pluginname=str(edit_pluginname)).first()

            pluginNameList = get_plugins()
            plugin_form.edit_pluginname.choices = pluginNameList

            ## Plugin Information
            plugin.active = bool(request.form.get('edit_activate'))
            plugin.retrain = bool(request.form.get('edit_retrain'))
            if 'submit_edit_plugin' in request.form:
                plugin.forcetrain = False
                final_msg = "Plug-in Updated"
            elif 'submit_edit_plugin_train' in request.form:
                plugin.forcetrain = True
                final_msg = "Plug-in Updated and set for Training"

            edit_category = request.form['edit_category']
            if not edit_category or edit_category=='category':
                return render_template('configure-plugins.html',form=plugin_form,msg_edit="[Plug-in Information] Please select a valid plug-in category",color="red",add_tab=False)
            plugin.category = edit_category

            edit_testsize = request.form['edit_testsize']
            if edit_category=='Supervised':
                if not edit_testsize or not is_valid_float(edit_testsize) :
                    return render_template('configure-plugins.html',form=plugin_form,msg_edit="[Plug-in Information] Please select a valid test size value",color="red",add_tab=False)
                edit_testsize = float(edit_testsize)
                if edit_testsize<=0 or edit_testsize>=1:
                    return render_template('configure-plugins.html',form=plugin_form,msg_edit="[Plug-in Information] Test size must be between 1.0 and 0.0",color="red",add_tab=False)
                plugin.testsize = edit_testsize
            else:
                plugin.testsize = 0
            
            edit_anomalysize = request.form['edit_anomalysize']
            if not edit_anomalysize or not is_valid_float(edit_anomalysize) :
                return render_template('configure-plugins.html',form=plugin_form,msg_edit="[Plug-in Information] Please select a valid anomaly size value",color="red",add_tab=False)
            edit_anomalysize = float(edit_anomalysize)
            if edit_anomalysize<=0 or edit_anomalysize>=1:
                return render_template('configure-plugins.html',form=plugin_form,msg_edit="[Plug-in Information] Anomaly size must be between 1.0 and 0.0",color="red",add_tab=False)
            plugin.anomalysize = edit_anomalysize

            edit_trainingperiodtype = request.form['edit_trainingperiodtype']
            if not edit_trainingperiodtype or edit_trainingperiodtype=='trainingperiodtype':
                return render_template('configure-plugins.html',form=plugin_form,msg_edit="[Plug-in Information] Please select a valid period type",color="red",add_tab=False)
            plugin.trainingperiodtype = edit_trainingperiodtype

            edit_trainingperiodduration = request.form['edit_trainingperiodduration']
            if not edit_trainingperiodduration or not is_valid_integer(edit_trainingperiodduration) :
                return render_template('configure-plugins.html',form=plugin_form,msg_edit="[Plug-in Information] Please select a valid training periodicity value",color="red",add_tab=False)
            edit_trainingperiodduration = int(edit_trainingperiodduration)
            if edit_trainingperiodduration<=0:
                return render_template('configure-plugins.html',form=plugin_form,msg_edit="[Plug-in Information] Training periodicity must be more than 0",color="red",add_tab=False)
            plugin.trainingperiodduration = edit_trainingperiodduration

            ## Data Pre-processing Steps
            datapreprocessing = DataPreProcessing.query.filter_by(pluginid=plugin.pluginid).first()

            ## These settings are currently static because data integration is always required and cleaning data needs specific configuration which is not yet available
            #datapreprocessing.cleaning = bool(request.form.get('edit_cleaning'))
            datapreprocessing.cleaning = False
            #datapreprocessing.integration = bool(request.form.get('edit_integration'))
            datapreprocessing.integration = True
            #datapreprocessing.transformation = bool(request.form.get('edit_transformation'))

            edit_selectionperiodtype = request.form['edit_selectionperiodtype']
            if not edit_selectionperiodtype or edit_selectionperiodtype=='selectionperiodtype':
                return render_template('configure-plugins.html',form=plugin_form,msg_edit="[Data Pre-Processing Information] Please select a valid Data selection period type",color="red",add_tab=False)
            datapreprocessing.selectionperiodtype = edit_selectionperiodtype

            edit_selectionperiodduration = request.form['edit_selectionperiodduration']
            if not edit_selectionperiodduration or not is_valid_integer(edit_selectionperiodduration) :
                return render_template('configure-plugins.html',form=plugin_form,msg_edit="[Data Pre-Processing Information] Please select a valid Data selection periodicity value",color="red",add_tab=False)
            edit_selectionperiodduration = int(edit_selectionperiodduration)
            if edit_selectionperiodduration<0:
                return render_template('configure-plugins.html',form=plugin_form,msg_edit="[Data Pre-Processing Information] Data selection periodicity must be more than 0",color="red",add_tab=False)
            datapreprocessing.selectionperiodduration = edit_selectionperiodduration

            edit_transformation = request.form['edit_transformation']
            if not edit_transformation:
                return render_template('configure-plugins.html',form=plugin_form,msg_add="[Data Pre-Processing Information] Please select a valid Data transformation",color="red",add_tab=False)
            datapreprocessing.labelencodertransformation = False
            datapreprocessing.onehotencodertransformation = False
            datapreprocessing.gaussiantransformation = False
            if str(edit_transformation).lower() == "labelencoder":
                datapreprocessing.labelencodertransformation = True
            elif str(edit_transformation).lower() == "onehotencoder":
                datapreprocessing.onehotencodertransformation = True
            elif str(edit_transformation).lower() == "gaussian":
                datapreprocessing.gaussiantransformation = True

            edit_secondary_transformation = request.form['edit_secondary_transformation']
            if not edit_secondary_transformation:
                return render_template('configure-plugins.html',form=plugin_form,msg_add="[Data Pre-Processing Information] Please select a valid Secondary Data transformation",color="red",add_tab=False)
            datapreprocessing.normalization = False
            datapreprocessing.standarization = False
            datapreprocessing.pca2d = False
            if str(edit_secondary_transformation).lower() == "normalization":
                datapreprocessing.normalization = True
            elif str(edit_secondary_transformation).lower() == "standarization":
                datapreprocessing.standarization = True
            elif str(edit_secondary_transformation).lower() == "pca2d":
                datapreprocessing.pca2d = True

            ## Dataset Fields
            datasetfields = DatasetFields.query.filter_by(pluginid=plugin.pluginid).first()
            if not ( bool(request.form.get('edit_ETHER_dst')) or bool(request.form.get('edit_ETHER_src')) or bool(request.form.get('edit_ETHER_ip')) or \
                bool(request.form.get('edit_ETHER_type')) or bool(request.form.get('edit_ARP_hln')) or bool(request.form.get('edit_ARP_hrd')) or\
                bool(request.form.get('edit_ARP_op')) or bool(request.form.get('edit_ARP_pln')) or bool(request.form.get('edit_ARP_pro')) or\
                bool(request.form.get('edit_ARP_sha')) or bool(request.form.get('edit_ARP_spa')) or bool(request.form.get('edit_ARP_tha')) or\
                bool(request.form.get('edit_ARP_tpa')) or bool(request.form.get('edit_IP_df')) or bool(request.form.get('edit_IP_src')) or \
                bool(request.form.get('edit_IP_dst')) or bool(request.form.get('edit_IP_hl')) or bool(request.form.get('edit_IP_id')) or \
                bool(request.form.get('edit_IP_len')) or bool(request.form.get('edit_IP_mf')) or bool(request.form.get('edit_IP_off')) or \
                bool(request.form.get('edit_IP_offset')) or bool(request.form.get('edit_IP_opts')) or bool(request.form.get('edit_IP_p')) or \
                bool(request.form.get('edit_IP_rf')) or bool(request.form.get('edit_IP_sum')) or bool(request.form.get('edit_IP_tos')) or \
                bool(request.form.get('edit_IP_ttl')) or bool(request.form.get('edit_IP_v')) or bool(request.form.get('edit_ICMP_type')) or\
                bool(request.form.get('edit_ICMP_code')) or bool(request.form.get('edit_ICMP_sum')) or bool(request.form.get('edit_TCP_ack')) or \
                bool(request.form.get('edit_TCP_dport')) or bool(request.form.get('edit_TCP_sport')) or bool(request.form.get('edit_TCP_flags')) or \
                bool(request.form.get('edit_TCP_off')) or bool(request.form.get('edit_TCP_opts')) or bool(request.form.get('edit_TCP_seq')) or \
                bool(request.form.get('edit_TCP_sum')) or bool(request.form.get('edit_TCP_urp')) or bool(request.form.get('edit_TCP_win')) or \
                bool(request.form.get('edit_UDP_dport')) or bool(request.form.get('edit_UDP_sport')) or bool(request.form.get('edit_UDP_sum')) or \
                bool(request.form.get('edit_UDP_ulen')) or bool(request.form.get('edit_PAYLOAD_len')) or bool(request.form.get('edit_PAYLOAD_raw')) or \
                bool(request.form.get('edit_PAYLOAD_hex')) or bool(request.form.get('edit_timestamp')) ):
                return render_template('configure-plugins.html',form=plugin_form,msg_edit="[Dataset Fields] No fields were selected",color="red",add_tab=False)
            # Ethernet
            datasetfields.ether_dst = bool(request.form.get('edit_ETHER_dst'))
            datasetfields.ether_src = bool(request.form.get('edit_ETHER_src'))
            datasetfields.ether_ip = bool(request.form.get('edit_ETHER_ip'))
            datasetfields.ether_type = bool(request.form.get('edit_ETHER_type'))
            # ARP
            datasetfields.arp_hln = bool(request.form.get('edit_ARP_hln'))
            datasetfields.arp_hrd = bool(request.form.get('edit_ARP_hrd'))
            datasetfields.arp_op = bool(request.form.get('edit_ARP_op'))
            datasetfields.arp_pln = bool(request.form.get('edit_ARP_pln'))
            datasetfields.arp_pro = bool(request.form.get('edit_ARP_pro'))
            datasetfields.arp_sha = bool(request.form.get('edit_ARP_sha'))
            datasetfields.arp_spa = bool(request.form.get('edit_ARP_spa'))
            datasetfields.arp_tha = bool(request.form.get('edit_ARP_tha'))
            datasetfields.arp_tpa = bool(request.form.get('edit_ARP_tpa'))
            #IP 
            datasetfields.ip_df = bool(request.form.get('edit_IP_df'))
            datasetfields.ip_src = bool(request.form.get('edit_IP_src'))
            datasetfields.ip_dst = bool(request.form.get('edit_IP_dst'))
            datasetfields.ip_hl = bool(request.form.get('edit_IP_hl'))
            datasetfields.ip_id = bool(request.form.get('edit_IP_id'))
            datasetfields.ip_len = bool(request.form.get('edit_IP_len'))
            datasetfields.ip_mf = bool(request.form.get('edit_IP_mf'))
            datasetfields.ip_off = bool(request.form.get('edit_IP_off'))
            datasetfields.ip_offset = bool(request.form.get('edit_IP_offset'))
            datasetfields.ip_opts = bool(request.form.get('edit_IP_opts'))
            datasetfields.ip_p = bool(request.form.get('edit_IP_p'))
            datasetfields.ip_rf = bool(request.form.get('edit_IP_rf'))
            datasetfields.ip_sum = bool(request.form.get('edit_IP_sum'))
            datasetfields.ip_tos = bool(request.form.get('edit_IP_tos'))
            datasetfields.ip_ttl = bool(request.form.get('edit_IP_ttl'))
            datasetfields.ip_v = bool(request.form.get('edit_IP_v'))
            #ICMP
            datasetfields.icmp_type = bool(request.form.get('edit_ICMP_type'))
            datasetfields.icmp_code = bool(request.form.get('edit_ICMP_code'))
            datasetfields.icmp_sum = bool(request.form.get('edit_ICMP_sum'))
            #TCP
            datasetfields.tcp_ack = bool(request.form.get('edit_TCP_ack'))
            datasetfields.tcp_dport = bool(request.form.get('edit_TCP_dport'))
            datasetfields.tcp_sport = bool(request.form.get('edit_TCP_sport'))
            datasetfields.tcp_flags = bool(request.form.get('edit_TCP_flags'))
            datasetfields.tcp_off = bool(request.form.get('edit_TCP_off'))
            datasetfields.tcp_opts = bool(request.form.get('edit_TCP_opts'))
            datasetfields.tcp_seq = bool(request.form.get('edit_TCP_seq'))
            datasetfields.tcp_sum = bool(request.form.get('edit_TCP_sum'))
            datasetfields.tcp_urp = bool(request.form.get('edit_TCP_urp'))
            datasetfields.tcp_win = bool(request.form.get('edit_TCP_win'))
            #UDP
            datasetfields.udp_dport = bool(request.form.get('edit_UDP_dport'))
            datasetfields.udp_sport = bool(request.form.get('edit_UDP_sport'))
            datasetfields.udp_sum = bool(request.form.get('edit_UDP_sum'))
            datasetfields.udp_ulen = bool(request.form.get('edit_UDP_ulen'))
            #Payload
            datasetfields.payload_len = bool(request.form.get('edit_PAYLOAD_len'))
            datasetfields.payload_raw = bool(request.form.get('edit_PAYLOAD_raw'))
            datasetfields.payload_hex = bool(request.form.get('edit_PAYLOAD_hex'))
            #Extra
            datasetfields.timestamp = bool(request.form.get('edit_timestamp'))

            ## Evaluation Methods
            evaluationmethods = EvaluationMethods.query.filter_by(pluginid=plugin.pluginid).first()
            if not ( bool(request.form.get('edit_accuracy')) or bool(request.form.get('edit_precision')) or bool(request.form.get('edit_recall')) or \
                bool(request.form.get('edit_f_score')) or bool(request.form.get('edit_mahalanobis')) or bool(request.form.get('edit_mse')) or \
                bool(request.form.get('edit_specificity')) or bool(request.form.get('edit_false_positive_rate')) or \
                bool(request.form.get('edit_roc')) ):
                db.session.delete(plugin)
                db.session.commit()
                return render_template('configure-plugins.html',form=plugin_form,msg_edit="[Evaluation Methods] No evaluation methods were selected",color="red",edit_tab=False)
            evaluationmethods.mahalanobis = bool(request.form.get('edit_mahalanobis'))
            evaluationmethods.accuracy = bool(request.form.get('edit_accuracy'))
            evaluationmethods.precision = bool(request.form.get('edit_precision'))
            evaluationmethods.recall = bool(request.form.get('edit_recall'))
            evaluationmethods.f_score = bool(request.form.get('edit_f_score'))
            evaluationmethods.specificity = bool(request.form.get('edit_specificity'))
            evaluationmethods.false_positive_rate = bool(request.form.get('edit_false_positive_rate'))
            evaluationmethods.roc = bool(request.form.get('edit_roc'))
            evaluationmethods.mse = bool(request.form.get('edit_mse'))

            pluginNameList = get_plugins()
            plugin_form.edit_pluginname.choices = pluginNameList

            db.session.commit()
            return render_template('configure-plugins.html',form=plugin_form,msg_edit=final_msg,color="yellow",add_tab=False)
        elif 'submit_remove_plugin'in request.form:
            edit_pluginname = request.form['edit_pluginname']   
            if not edit_pluginname or edit_pluginname=='plugin name':
                return render_template('configure-plugins.html',form=plugin_form,msg_edit="[Plug-in Information] Please select a valid plug-in",color="red",add_tab=False)   
            
            plugin = Plugin.query.filter_by(pluginname=str(edit_pluginname)).first()
            datapreprocessing = DataPreProcessing.query.filter_by(pluginid=plugin.pluginid).first()
            datasetfields = DatasetFields.query.filter_by(pluginid=plugin.pluginid).first()
            evaluationmethods = EvaluationMethods.query.filter_by(pluginid=plugin.pluginid).first()
            evaluationresults = EvaluationResults.query.filter_by(pluginid=plugin.pluginid).first()

            remove_uploaded_file(plugin.filepath)
            if evaluationresults:
                remove_uploaded_file(evaluationresults.roc)
                db.session.delete(evaluationresults)
            db.session.delete(plugin)
            db.session.delete(datapreprocessing)
            db.session.delete(datasetfields)
            db.session.delete(evaluationmethods)
            db.session.commit()

            pluginNameList = get_plugins()
            plugin_form.edit_pluginname.choices = pluginNameList            
            return render_template('configure-plugins.html',form=plugin_form,msg_edit="Plug-in Deleted",color="orange",add_tab=False)
        elif 'plugin_selected'in request.form:
            edit_pluginname = request.form['edit_pluginname']
            pluginNameList = get_plugins()
            plugin_form.edit_pluginname.choices = pluginNameList
            
            ##Plugin
            plugin = Plugin.query.filter_by(pluginname=str(edit_pluginname)).first()
            plugin_form.edit_pluginname.value=plugin.pluginname
            plugin_form.edit_category.data=plugin.category.value
            plugin_form.edit_trainingperiodduration.data= str(plugin.trainingperiodduration)
            plugin_form.edit_trainingperiodtype.data=plugin.trainingperiodtype.value
            plugin_form.edit_testsize.data=str(plugin.testsize)
            plugin_form.edit_anomalysize.data=str(plugin.anomalysize)
            plugin_form.edit_activate.checked = bool(plugin.active)
            plugin_form.edit_retrain.checked = bool(plugin.retrain)
            ##Data Pre-Processing
            datapreprocessing = DataPreProcessing.query.filter_by(pluginid=plugin.pluginid).first()
            plugin_form.edit_integration.checked = bool(datapreprocessing.integration)
            if bool(datapreprocessing.labelencodertransformation):
                plugin_form.edit_transformation.data = "labelencoder"
            elif bool(datapreprocessing.onehotencodertransformation):
                plugin_form.edit_transformation.data = "onehotencoder"
            elif bool(datapreprocessing.gaussiantransformation):
                plugin_form.edit_transformation.data = "gaussian"
            plugin_form.edit_secondary_transformation.data = "notransformation"
            if bool(datapreprocessing.normalization):
                plugin_form.edit_secondary_transformation.data = "normalization"
            elif bool(datapreprocessing.standarization):
                plugin_form.edit_secondary_transformation.data = "standarization"
            elif bool(datapreprocessing.pca2d):
                plugin_form.edit_secondary_transformation.data = "pca2d"
            plugin_form.edit_selectionperiodduration.data=str(datapreprocessing.selectionperiodduration)
            plugin_form.edit_selectionperiodtype.data=datapreprocessing.selectionperiodtype.value
            ##Dataset Fields
            datasetfields = DatasetFields.query.filter_by(pluginid=plugin.pluginid).first()
            #Extra
            plugin_form.edit_timestamp.checked = bool(datasetfields.timestamp)
            #Ethernet
            plugin_form.edit_ETHER_dst.checked = bool(datasetfields.ether_dst)
            plugin_form.edit_ETHER_src.checked = bool(datasetfields.ether_src)
            plugin_form.edit_ETHER_ip.checked = bool(datasetfields.ether_ip)
            plugin_form.edit_ETHER_type.data = bool(datasetfields.ether_type)
            #ARP
            plugin_form.edit_ARP_hln.checked = bool(datasetfields.arp_hln)
            plugin_form.edit_ARP_hrd.checked = bool(datasetfields.arp_hrd)
            plugin_form.edit_ARP_op.checked = bool(datasetfields.arp_op)
            plugin_form.edit_ARP_pln.checked = bool(datasetfields.arp_pln)
            plugin_form.edit_ARP_pro.checked = bool(datasetfields.arp_pro)
            plugin_form.edit_ARP_sha.checked = bool(datasetfields.arp_sha)
            plugin_form.edit_ARP_spa.checked = bool(datasetfields.arp_spa)
            plugin_form.edit_ARP_tha.checked = bool(datasetfields.arp_tha)
            plugin_form.edit_ARP_tpa.checked = bool(datasetfields.arp_tpa)
            #IP
            plugin_form.edit_IP_df.checked = bool(datasetfields.ip_df)
            plugin_form.edit_IP_src.checked = bool(datasetfields.ip_src)
            plugin_form.edit_IP_dst.checked = bool(datasetfields.ip_dst)
            plugin_form.edit_IP_hl.checked = bool(datasetfields.ip_hl)
            plugin_form.edit_IP_id.checked = bool(datasetfields.ip_id)
            plugin_form.edit_IP_len.checked = bool(datasetfields.ip_len)
            plugin_form.edit_IP_mf.checked = bool(datasetfields.ip_mf)
            plugin_form.edit_IP_off.checked = bool(datasetfields.ip_off)
            plugin_form.edit_IP_offset.checked = bool(datasetfields.ip_offset)
            plugin_form.edit_IP_opts.checked = bool(datasetfields.ip_opts)
            plugin_form.edit_IP_p.checked = bool(datasetfields.ip_p)
            plugin_form.edit_IP_rf.checked = bool(datasetfields.ip_rf)
            plugin_form.edit_IP_sum.checked = bool(datasetfields.ip_sum)
            plugin_form.edit_IP_tos.checked = bool(datasetfields.ip_tos)
            plugin_form.edit_IP_ttl.checked = bool(datasetfields.ip_ttl)
            plugin_form.edit_IP_v.checked = bool(datasetfields.ip_v)
            #ICMP
            plugin_form.edit_ICMP_type.checked = bool(datasetfields.icmp_type)
            plugin_form.edit_ICMP_code.checked = bool(datasetfields.icmp_code)
            plugin_form.edit_ICMP_sum.checked = bool(datasetfields.icmp_sum)
            #TCP
            plugin_form.edit_TCP_ack.checked = bool(datasetfields.tcp_ack)
            plugin_form.edit_TCP_dport.checked = bool(datasetfields.tcp_dport)
            plugin_form.edit_TCP_sport.checked = bool(datasetfields.tcp_sport)
            plugin_form.edit_TCP_flags.checked = bool(datasetfields.tcp_flags)
            plugin_form.edit_TCP_off.checked = bool(datasetfields.tcp_off)
            plugin_form.edit_TCP_opts.checked = bool(datasetfields.tcp_opts)
            plugin_form.edit_TCP_seq.checked = bool(datasetfields.tcp_seq)
            plugin_form.edit_TCP_sum.checked = bool(datasetfields.tcp_sum)
            plugin_form.edit_TCP_urp.checked = bool(datasetfields.tcp_urp)
            plugin_form.edit_TCP_win.checked = bool(datasetfields.tcp_win)
            #UDP
            plugin_form.edit_UDP_dport.checked = bool(datasetfields.udp_dport)
            plugin_form.edit_UDP_sport.checked = bool(datasetfields.udp_sport)
            plugin_form.edit_UDP_sum.checked = bool(datasetfields.udp_sum)
            plugin_form.edit_UDP_ulen.checked = bool(datasetfields.udp_ulen)
            #Payload
            plugin_form.edit_PAYLOAD_len.checked = bool(datasetfields.payload_len)
            plugin_form.edit_PAYLOAD_raw.checked = bool(datasetfields.payload_raw)
            plugin_form.edit_PAYLOAD_hex.checked = bool(datasetfields.payload_hex)
            ##Evaluation Methods
            evaluationmethods = EvaluationMethods.query.filter_by(pluginid=plugin.pluginid).first()
            plugin_form.edit_accuracy.checked = bool(evaluationmethods.accuracy)
            plugin_form.edit_precision.checked = bool(evaluationmethods.precision)
            plugin_form.edit_recall.checked = bool(evaluationmethods.recall)
            plugin_form.edit_f_score.checked = bool(evaluationmethods.f_score)
            plugin_form.edit_specificity.checked = bool(evaluationmethods.specificity)
            plugin_form.edit_false_positive_rate.checked = bool(evaluationmethods.false_positive_rate)
            plugin_form.edit_mahalanobis.checked = bool(evaluationmethods.mahalanobis)
            plugin_form.edit_mse.checked = bool(evaluationmethods.mse)
            plugin_form.edit_roc.checked = bool(evaluationmethods.roc)

            return render_template('configure-plugins.html',form=plugin_form,add_tab=False)
        pluginNameList = get_plugins()
        plugin_form.edit_pluginname.choices = pluginNameList
        return render_template('configure-plugins.html',form=plugin_form,add_tab=True)
    return redirect(url_for('base_blueprint.login'))

def get_plugins():
    plugins = Plugin.query.all()
    pluginNameList = [('plugin name','Plug-in Name')]
    for plugin in plugins:
        pluginNameList.append( (plugin.pluginname,plugin.pluginname))
    return pluginNameList

def is_valid_float(float_value):
    return re.match(r"^[+-]?([0-9]*[.])?[0-9]+$", float_value)

def is_valid_integer(integer_value):
    return re.match(r"^[-+]?[0-9]+$", integer_value) 

@blueprint.route('/plugins',methods=['GET'])
@login_required
def plugins():
    if current_user.is_authenticated:
      plugins_data = get_plugins_data()
      plugin_tab = get_plugins_tab()
      return render_template('plugins.html',plugins=plugins_data,pluginsTab=plugin_tab)
    return redirect(url_for('base_blueprint.login'))

@blueprint.route("/plugins/pluginsprogress",methods=['GET'])
def pluginsprogress():
    plugins = Plugin.query.with_entities(Plugin.pluginname, Plugin.status,Plugin.active,Plugin.retrain,Plugin.error).all()
    json_query = {}
    record = 0
    for plugin in plugins:
        json_query[record] = {'pluginname':plugin[0],'status': plugin[1].value,'active':plugin[2],'retrain':plugin[3],'error':plugin[4]}
        record+=1
    return jsonify(json_query)
    
def get_plugins_tab():
    plugins = Plugin.query.all()
    pluginTab=""
    if plugins:
        for plugin in plugins:
            evaluation = EvaluationResults.query.filter_by(pluginid=plugin.pluginid).first()
            if evaluation:
                pluginTab+= "<li class=\"\"><a href=\"#"+plugin.pluginname.lower().replace(' ','_')+"\" data-toggle=\"tab\">"+plugin.pluginname+"</a></li>"
    else:
        pluginTab+= "<li class=\"\"><a href=\"#noplugin\" data-toggle=\"tab\">No Plug-in trained</a></li>"
    return pluginTab

def get_plugins_data():
    results = EvaluationResults.query.filter_by(datatype="Training").order_by(EvaluationResults.pluginid).all()
    resultsList=""
    active_tab = True
    if results:
        for result in results:
            plugin = Plugin.query.filter_by(pluginid=result.pluginid).first()
            if plugin:
                pluginname = plugin.pluginname
                trainingperiodtype = plugin.trainingperiodtype.value
                trainingperiodduration = plugin.trainingperiodduration
                active = plugin.active
                error = plugin.error
                retrain = plugin.retrain
                status = plugin.status.value
                duration = result.duration
                if active_tab:
                    resultsList= resultsList+"<div class=\"tab-pane active\" id=\""+pluginname.lower().replace(' ','_')+"\">"
                    active_tab=False
                else:
                    resultsList= resultsList+"<div class=\"tab-pane\" id=\""+pluginname.lower().replace(' ','_')+"\">"

                resultsList= resultsList+"<div id=\'plugin_update_"+str(pluginname)+"\'>"
                resultsList= resultsList+"<ul><li><h3><header><span class=\"fw-semi-bold\">Plug-in: \'"+str(pluginname)+"\' </span>"
                if error:
                    resultsList= resultsList+ "<small>&emsp;<i class=\"fa fa-circle text-warning\"></i>&nbsp;<span class=\"fw-semi-bold\"> Anomaly Detection in Stand-by </span></small>"
                else:
                    if active:
                        resultsList= resultsList+ "<small>&emsp;<i class=\"fa fa-circle text-success\"></i>&nbsp;<span class=\"fw-semi-bold\">Active Anomaly Detection</span></small>"
                    else:
                        resultsList= resultsList+ "<small>&emsp;<i class=\"fa fa-circle text-danger\"></i>&nbsp;<span class=\"fw-semi-bold\">Inactive Anomaly Detection</span></small>"
                if retrain:
                    resultsList= resultsList+ "<small>&emsp;<i class=\"fa fa-circle text-success\"></i>&nbsp;<span class=\"fw-semi-bold\">Automatic Re-training</span></small>"
                else:
                    resultsList= resultsList+ "<small>&emsp;<i class=\"fa fa-circle text-danger\"></i>&nbsp;<span class=\"fw-semi-bold\">No Automatic Re-training</span></small>"
                resultsList= resultsList+"</header></h3></li></ul>"
                
                resultsList= resultsList+"<ul><h4><li>"
                if status == "Free":
                    if error:
                        resultsList= resultsList+"<span class=\"fw-semi-bold\">Status:</span> Error | <span class=\"fw-semi-bold\">Possible solution:</span> Re-train plugin</h4></li> "
                        resultsList= resultsList+ "<div class=\"progress progress-md mt-xs mb-0\">"
                        resultsList= resultsList+ "<div class=\"progress-bar progress-bar-striped progress-bar-danger\"\
                                                style=\"width: 100%\"></div>"
                        resultsList= resultsList+"</div></div>"
                    else:
                        resultsList= resultsList+"<span class=\"fw-semi-bold\">Status:</span> Free | <span class=\"fw-semi-bold\">Trainining Completed:</span> 100%</h4></li>"
                        resultsList= resultsList+ "<div class=\"progress progress-md mt-xs mb-0\">"
                        resultsList= resultsList+ "<div class=\"progress-bar progress-bar-striped progress-bar-success\"\
                                                style=\"width: 100%\"></div>"
                        resultsList= resultsList+"</div></div>"
                elif status == "ReadingPCAP":
                    resultsList= resultsList+"<span class=\"fw-semi-bold\">Status:</span> Reading .pcap file | <span class=\"fw-semi-bold\">Currently Trainining:</span> 10%</h4></li>"
                    resultsList= resultsList+ "<div class=\"progress progress-md mt-xs mb-0\">"
                    resultsList= resultsList+ "<div class=\"progress-bar progress-bar-striped progress-bar-warning\"\
                                             style=\"width: 10%\"></div>"
                    resultsList= resultsList+"</div></div>"
                elif status == "DataPreProcessing":
                    resultsList= resultsList+"<span class=\"fw-semi-bold\">Status:</span> Pre-processing data | <span class=\"fw-semi-bold\">Currently Trainining:</span> 80%</h4></li>"
                    resultsList= resultsList+ "<div class=\"progress progress-md mt-xs mb-0\">"
                    resultsList= resultsList+ "<div class=\"progress-bar progress-bar-striped progress-bar-info\"\
                                             style=\"width: 80%\"></div>"
                    resultsList= resultsList+"</div></div>"
                elif status == "PluginEvaluation":
                    resultsList= resultsList+"<span class=\"fw-semi-bold\">Status:</span> Evaluating Plug-in | <span class=\"fw-semi-bold\">Currently Trainining:</span> 90%</h4></li>"
                    resultsList= resultsList+ "<div class=\"progress progress-md mt-xs mb-0\">"
                    resultsList= resultsList+ "<div class=\"progress-bar progress-bar-striped progress-bar-gray-light\"\
                                             style=\"width: 90%\"></div>"
                    resultsList= resultsList+"</div></div>"
                else:
                    resultsList= resultsList+"<span class=\"fw-semi-bold\">Unknown Status</span></h4></li>"
                    resultsList= resultsList+ "<div class=\"progress progress-md mt-xs mb-0\">"
                    resultsList= resultsList+ "<div class=\"progress-bar progress-bar-striped progress-bar-danger\"\
                                             style=\"width: 0%\"></div>"
                    resultsList= resultsList+"</div></div>"
                resultsList= resultsList+"</ul>"
                                
                resultsList = resultsList + "<ul><li><h4><span class=\"fw-semi-bold\">Last Training:&nbsp;  </span> "+plugin.lasttrained.strftime("%d-%b-%Y %H:%M:%S")+"</h4></li>"
                nexttrainingdate = plugin.lasttrained
                if trainingperiodtype=="Second":
                    nexttrainingdate+=+ timedelta(seconds=trainingperiodduration)
                elif trainingperiodtype=="Minute":
                    nexttrainingdate+=+ timedelta(minutes=trainingperiodduration)
                elif trainingperiodtype=="Hour":
                    nexttrainingdate+=+ timedelta(hours=trainingperiodduration)
                elif trainingperiodtype=="Day":
                    nexttrainingdate+=+ timedelta(days=trainingperiodduration)
                elif trainingperiodtype=="Week":
                    nexttrainingdate+=+ timedelta(weeks=trainingperiodduration)
                elif trainingperiodtype=="Month":
                    nexttrainingdate+= relativedelta(months=+trainingperiodduration)
                
                resultsList = resultsList + "<ul><li><h4><span class=\"fw-semi-bold\">Last Training Duration:&nbsp;  </span> "+str(timedelta(seconds=duration))+"</h4></li>"
                resultsList = resultsList + "<li><h4><span class=\"fw-semi-bold\">Next Training:</span> "+nexttrainingdate.strftime("%d-%b-%Y %H:%M:%S")+"&nbsp; \
                    <small>(Plug-in trained each "+str(trainingperiodduration)+" "+ trainingperiodtype.lower()+"s)</small></h4></li></ul>"
                
                resultsList= resultsList+"<div class=\"row\">"
                resultsList= resultsList+"<div class=\'col-md-6\'>"
                resultsList= resultsList+"<h3><header> Plug-in Training Data Evaluations Results: </header></h3>"
                resultsList= resultsList+"<div class=\"widget-body\"><div class=\"widget-padding-md border rounded\" style=\"height:392px;\" ><ul> "
                
                if result.accuracy or result.precision or result.recall or result.f_score:
                    resultsList = resultsList +"<li><h4><span class=\"fw-semi-bold\">Basic Evaluation Methods:</span></h4></li>"
                    if result.accuracy:
                        resultsList = resultsList +"<li style='list-style-type: circle;list-style-position: inside;'> \
                            <span class=\"fw-semi-bold\">Accuracy:</span> "+'{:.2%}'.format(result.accuracy)+"</li>"
                    if result.precision:
                        resultsList = resultsList +"<li style='list-style-type: circle;list-style-position: inside;'> \
                            <span class=\"fw-semi-bold\">Precision:</span> "+'{:.2%}'.format(result.precision)+"</li>"
                    if result.recall:
                        resultsList = resultsList +"<li style='list-style-type: circle;list-style-position: inside;'> \
                            <span class=\"fw-semi-bold\">Recall (True Positive Rate):</span> "+'{:.2%}'.format(result.recall)+"</li>"
                    if result.f_score:
                        resultsList = resultsList +"<li style='list-style-type: circle;list-style-position: inside;'> \
                            <span class=\"fw-semi-bold\">F-Score:</span> "+'{:.2%}'.format(result.f_score)+"</li>"
                    if result.specificity:
                        resultsList = resultsList +"<li style='list-style-type: circle;list-style-position: inside;'> \
                            <span class=\"fw-semi-bold\">Specificity:</span> "+'{:.2%}'.format(result.specificity)+"</li>"
                    if result.false_positive_rate:
                        resultsList = resultsList +"<li style='list-style-type: circle;list-style-position: inside;'> \
                            <span class=\"fw-semi-bold\">False Positive Rate:</span> "+'{:.2%}'.format(result.false_positive_rate)+"</li>"
                            
                if result.mahalanobis_min or result.mahalanobis_max or result.mse:
                    resultsList = resultsList + "<br><li><h4><span class=\"fw-semi-bold\">Advanced Evaluation Methods:</span></h4></li>"
                    if result.mahalanobis_min or result.mahalanobis_max:
                        resultsList = resultsList + "<li style='list-style-type: circle;list-style-position: inside;'> \
                            <span class=\"fw-semi-bold\">Mahalanobis mininum</span> "+str(result.mahalanobis_min)+"</li>"
                        resultsList = resultsList + "<li style='list-style-type: circle;list-style-position: inside;'> \
                            <span class=\"fw-semi-bold\">Mahalanobis maximum</span> "+str(result.mahalanobis_max)+"</li>"
                    if result.mse:
                        resultsList = resultsList + "<li style='list-style-type: circle;list-style-position: inside;'> \
                            <span class=\"fw-semi-bold\">Mean Squared Error(MSE):</span> "+'{:.2%}'.format(result.mse)+"</li>"
                resultsList = resultsList +"</ul>"
                resultsList= resultsList+"</div></div>"
                resultsList= resultsList+"</div>"
                
                if result.roc and path.exists(result.roc):
                    index = result.roc.find('static')
                    plot = result.roc[index:]
                    resultsList= resultsList+"<div class=\'col-md-6\'>"
                    resultsList= resultsList+"<h3><header> Plug-in Training Data ROC Plot </header></h3>"
                    resultsList= resultsList+"<div class=\"widget-body\"><div class=\"widget-padding-md border rounded\"  align=\"center\">"
                    resultsList = resultsList +"<img src=\""+plot+"\" alt=\"ROC Plot "+pluginname+"\" height=\"350\" width=\"400\">"
                    resultsList= resultsList+"</div></div>"
                    resultsList= resultsList+"</div>"
                    
                if str(plugin.category.value).lower()=='supervised':
                    result = EvaluationResults.query.filter_by(pluginid=plugin.pluginid,datatype="Test").first()
                    
                    resultsList= resultsList+"<div class=\'col-md-6\'>"
                    resultsList= resultsList+"<h3><header> Plug-in Test Data Evaluations Results: </header></h3>"
                    resultsList= resultsList+"<div class=\"widget-body\"><div class=\"widget-padding-md border rounded\" style=\"height:392px;\" ><ul> "

                    if result.accuracy or result.precision or result.recall or result.f_score:
                        resultsList = resultsList +"<li><h4><span class=\"fw-semi-bold\">Basic Evaluation Methods:</span></h4></li>"
                        if result.accuracy:
                            resultsList = resultsList +"<li style='list-style-type: circle;list-style-position: inside;'> \
                                <span class=\"fw-semi-bold\">Accuracy:</span> "+'{:.2%}'.format(result.accuracy)+"</li>"
                        if result.precision:
                            resultsList = resultsList +"<li style='list-style-type: circle;list-style-position: inside;'> \
                                <span class=\"fw-semi-bold\">Precision:</span> "+'{:.2%}'.format(result.precision)+"</li>"
                        if result.recall:
                            resultsList = resultsList +"<li style='list-style-type: circle;list-style-position: inside;'> \
                                <span class=\"fw-semi-bold\">Recall (True Positive Rate):</span> "+'{:.2%}'.format(result.recall)+"</li>"
                        if result.f_score:
                            resultsList = resultsList +"<li style='list-style-type: circle;list-style-position: inside;'> \
                                <span class=\"fw-semi-bold\">F-Score:</span> "+'{:.2%}'.format(result.f_score)+"</li>"
                        if result.specificity:
                            resultsList = resultsList +"<li style='list-style-type: circle;list-style-position: inside;'> \
                                <span class=\"fw-semi-bold\">Specificity:</span> "+'{:.2%}'.format(result.specificity)+"</li>"
                        if result.false_positive_rate:
                            resultsList = resultsList +"<li style='list-style-type: circle;list-style-position: inside;'> \
                                <span class=\"fw-semi-bold\">False Positive Rate:</span> "+'{:.2%}'.format(result.false_positive_rate)+"</li>"
                                
                    if result.mahalanobis_min or result.mahalanobis_max or result.mse:
                        resultsList = resultsList + "<br><li><h4><span class=\"fw-semi-bold\">Advanced Evaluation Methods:</span></h4></li>"
                        if result.mahalanobis_min or result.mahalanobis_max:
                            resultsList = resultsList + "<li style='list-style-type: circle;list-style-position: inside;'> \
                                <span class=\"fw-semi-bold\">Mahalanobis mininum</span> "+str(result.mahalanobis_min)+"</li>"
                            resultsList = resultsList + "<li style='list-style-type: circle;list-style-position: inside;'> \
                                <span class=\"fw-semi-bold\">Mahalanobis maximum</span> "+str(result.mahalanobis_max)+"</li>"
                        if result.mse:
                            resultsList = resultsList + "<li style='list-style-type: circle;list-style-position: inside;'> \
                                <span class=\"fw-semi-bold\">Mean Squared Error(MSE):</span> "+'{:.2%}'.format(result.mse)+"</li>"
                    resultsList = resultsList +"</ul>"
                    resultsList= resultsList+"</div></div>"
                    resultsList= resultsList+"</div>"
                    
                    if result.roc and path.exists(result.roc):
                        index = result.roc.find('static')
                        plot = result.roc[index:]
                        resultsList= resultsList+"<div class=\'col-md-6\'>"
                        resultsList= resultsList+"<h3><header> Plug-in Test Data ROC Plot </header></h3>"
                        resultsList= resultsList+"<div class=\"widget-body\"><div class=\"widget-padding-md border rounded\"  align=\"center\">"
                        resultsList = resultsList +"<img src=\""+plot+"\" alt=\"ROC Plot "+pluginname+"\" height=\"350\" width=\"400\">"
                        resultsList= resultsList+"</div></div>"
                        resultsList= resultsList+"</div>"
                resultsList= resultsList+"</div>"
                resultsList= resultsList+"</div>"
                    
    else:
        resultsList= resultsList+"<div class=\"tab-pane active\" id=\"noplugin\">"
    return resultsList

def get_plugins_short_data():
    results = EvaluationResults.query.order_by(EvaluationResults.pluginid).all()
    resultsList=""
    for result in results:
        plugin = Plugin.query.filter_by(pluginid=result.pluginid).first()
        if plugin:
            pluginname = plugin.pluginname
            trainingperiodtype = plugin.trainingperiodtype.value
            trainingperiodduration = plugin.trainingperiodduration
            active = plugin.active
            retrain = plugin.retrain
            error = plugin.error
            status = plugin.status.value

            resultsList= resultsList+"<div class=\"widget-padding-md border rounded\">"
            resultsList= resultsList+"<div id=\'plugin_update_"+str(pluginname)+"\'>"
            resultsList= resultsList+"<ul><li><h3><header><span class=\"fw-semi-bold\">Plug-in: \'"+str(pluginname)+"\' </span>"
            if error:
                resultsList= resultsList+ "<small>&emsp;<i class=\"fa fa-circle text-warning\"></i>&nbsp;<span class=\"fw-semi-bold\"> Anomaly Detection in Stand-by </span></small>"
            else:
                if active:
                    resultsList= resultsList+ "<small>&emsp;<i class=\"fa fa-circle text-success\"></i>&nbsp;<span class=\"fw-semi-bold\">Active Anomaly Detection</span></small>"
                else:
                    resultsList= resultsList+ "<small>&emsp;<i class=\"fa fa-circle text-danger\"></i>&nbsp;<span class=\"fw-semi-bold\">Inactive Anomaly Detection</span></small>"
            if retrain:
                resultsList= resultsList+ "<small>&emsp;<i class=\"fa fa-circle text-success\"></i>&nbsp;<span class=\"fw-semi-bold\">Automatic Re-training</span></small>"
            else:
                resultsList= resultsList+ "<small>&emsp;<i class=\"fa fa-circle text-danger\"></i>&nbsp;<span class=\"fw-semi-bold\">No Automatic Re-training</span></small>"
            resultsList= resultsList+"</header></h3></li></ul>"
            
            resultsList= resultsList+"<ul><h4><li>"
            if status == "Free":
                if error:
                    resultsList= resultsList+"<span class=\"fw-semi-bold\">Status:</span> Error | <span class=\"fw-semi-bold\">Possible solution:</span> Re-train plugin</h4></li> "
                    resultsList= resultsList+ "<div class=\"progress progress-md mt-xs mb-0\">"
                    resultsList= resultsList+ "<div class=\"progress-bar progress-bar-striped progress-bar-danger\"\
                                            style=\"width: 100%\"></div>"
                    resultsList= resultsList+"</div>"
                else:
                    resultsList= resultsList+"<span class=\"fw-semi-bold\">Status:</span> Free | <span class=\"fw-semi-bold\">Trainining Completed:</span> 100%</h4></li>"
                    resultsList= resultsList+ "<div class=\"progress progress-md mt-xs mb-0\">"
                    resultsList= resultsList+ "<div class=\"progress-bar progress-bar-striped progress-bar-success\"\
                                            style=\"width: 100%\"></div>"
                    resultsList= resultsList+"</div>"
            elif status == "ReadingPCAP":
                resultsList= resultsList+"<span class=\"fw-semi-bold\">Status:</span> Reading .pcap file | <span class=\"fw-semi-bold\">Currently Trainining:</span> 10%</h4></li>"
                resultsList= resultsList+ "<div class=\"progress progress-md mt-xs mb-0\">"
                resultsList= resultsList+ "<div class=\"progress-bar progress-bar-striped progress-bar-warning\"\
                                            style=\"width: 10%\"></div>"
                resultsList= resultsList+"</div>"
            elif status == "DataPreProcessing":
                resultsList= resultsList+"<span class=\"fw-semi-bold\">Status:</span> Pre-processing data | <span class=\"fw-semi-bold\">Currently Trainining:</span> 80%</h4></li>"
                resultsList= resultsList+ "<div class=\"progress progress-md mt-xs mb-0\">"
                resultsList= resultsList+ "<div class=\"progress-bar progress-bar-striped progress-bar-info\"\
                                            style=\"width: 80%\"></div>"
                resultsList= resultsList+"</div>"
            elif status == "PluginEvaluation":
                resultsList= resultsList+"<span class=\"fw-semi-bold\">Status:</span> Evaluating Plug-in | <span class=\"fw-semi-bold\">Currently Trainining:</span> 90%</h4></li>"
                resultsList= resultsList+ "<div class=\"progress progress-md mt-xs mb-0\">"
                resultsList= resultsList+ "<div class=\"progress-bar progress-bar-striped progress-bar-gray-light\"\
                                            style=\"width: 90%\"></div>"
                resultsList= resultsList+"</div>"
            else:
                resultsList= resultsList+"<span class=\"fw-semi-bold\">Unknown Status</span></h4></li>"
            resultsList= resultsList+"</ul>"
            resultsList= resultsList+"</div>"

            resultsList = resultsList + "<ul><li><h4><span class=\"fw-semi-bold\">Last Training:&nbsp;  </span> "+plugin.lasttrained.strftime("%d-%b-%Y %H:%M:%S")+""
            nexttrainingdate = plugin.lasttrained
            if trainingperiodtype=="Second":
                nexttrainingdate+=+ timedelta(seconds=trainingperiodduration)
            elif trainingperiodtype=="Minute":
                nexttrainingdate+=+ timedelta(minutes=trainingperiodduration)
            elif trainingperiodtype=="Hour":
                nexttrainingdate+=+ timedelta(hours=trainingperiodduration)
            elif trainingperiodtype=="Day":
                nexttrainingdate+=+ timedelta(days=trainingperiodduration)
            elif trainingperiodtype=="Week":
                nexttrainingdate+=+ timedelta(weeks=trainingperiodduration)
            elif trainingperiodtype=="Month":
                nexttrainingdate+= relativedelta(months=+trainingperiodduration)
            resultsList = resultsList + "&nbsp;->&nbsp;<span class=\"fw-semi-bold\">Next Training:</span> "+nexttrainingdate.strftime("%d-%b-%Y %H:%M:%S")+"&nbsp; \
                </li><li><small>(Plug-in trained each "+str(trainingperiodduration)+" "+ trainingperiodtype.lower()+"s)</small></h4></li></ul></div>"
    return resultsList

@blueprint.route('/alerts')
@login_required
def alerts():
    if current_user.is_authenticated:
        df = readLog()
        table = json.loads(df.to_json(orient='index')).items()
        return render_template('alerts.html',table=table,columns=df.columns)
    return redirect(url_for('base_blueprint.login'))

@blueprint.route("/alerts/lastalerts",methods=['GET'])
def lastalerts():
    df = readLastLogs()
    df = df.filter(['ALERT_TYPE','TITLE','SHORT_DESCRIPTION'])
    jsonResp = jsonify((df.to_json(orient='records')))
    return jsonResp

@blueprint.route('/<template>')
@login_required
def route_template(template):
    if not current_user.is_authenticated:
        return redirect(url_for('base_blueprint.login'))
    try:
        return render_template(template + '.html')
    except TemplateNotFound:
        return render_template('page-404.html'), 404
    except:
        return render_template('page-500.html'), 500