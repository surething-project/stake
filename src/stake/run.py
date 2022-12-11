# -*- encoding: utf-8 -*-
"""
License: Commercial
Copyright (c) 2019 - present AppSeed.us
"""
from flask_migrate import Migrate
from os import environ
from sys import exit
from config import config_dict
from app import create_app, db , get_upload_dir
from config import Config_file
from app.capturer import sniff_packets
from threading import Thread
import signal
import sys

config_file = Config_file()
stake = config_file.getSTAKEConfig()
log = config_file.getLogConfig()

environment =config_file.getWebValue('Environment')
get_config_mode = environ.get('APPSEED_CONFIG_MODE', environment)
try:
    config_mode = config_dict[get_config_mode.capitalize()]
except KeyError:
    exit('Error: Invalid APPSEED_CONFIG_MODE environment variable entry.')

app = create_app(config_mode,stake.networkAdapter,stake.pluginsPath,log) 
Migrate(app, db)

def run_thread(stake,app):
    sniff_packets(stake,app)

def signal_handler(signal, frame):
    print('\n>>STAKE PROGRAM TERMINATED\n')
    sys.exit(0)

if __name__ == "__main__":
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    Thread(target = run_thread, daemon=True,args=(stake,app,)).start()
    app.run(host=config_file.getWebValue('HostIP'))