# -*- encoding: utf-8 -*-
"""
License: MIT
Copyright (c) 2019 - present AppSeed.us
"""
from   os import environ, path
import configparser

class Config_file():
    def __init__(self, file='config.ini'):
        self.config = configparser.ConfigParser()
        self.config.read(file)        

    def getWebValue(self,key):
        return self.config['Web'][key]

    def getCookieValue(self,key):
        return self.config['Cookie'][key]
    
    def getPostgreSQLValue(self,key):
        return self.config['PostgreSQL'][key]

    def getSTAKEValue(self,key):
        return self.config['STAKE'][key]
    
    def getLogValue(self,key):
        return self.config['Log'][key]

    def getSTAKEConfig(self):
        stake = self.STAKE(self.config)
        return stake

    def getLogConfig(self):
        log = self.Log(self.config)
        return log
    
    class STAKE():
        def __init__(self,config):
            section = 'STAKE'
            self.networkAdapter = config[section]['NetworkAdapter']
            self.pcapPath = config[section]['PcapPath']
            self.anomalyPcapPath = config[section]['AnomalyPcapPath']
            self.pluginsPath = config[section]['PluginsPath']
            self.plotPath = config[section]['PlotsPath']
            self.refreshRatio = int(config[section]['RefreshRatio'])
            self.maxPackets = int(config[section]['MaxPackets'])

    class Log():
        def __init__(self,config):
            section = 'Log'
            self.path = config[section]['LOG_PATH']
            self.maxrows = int(config[section]['LOG_MAX_ROWS'])

class Config(object):
    config = Config_file()
    basedir    = path.abspath(path.dirname(__file__))
    SECRET_KEY = config.getWebValue('SecretKey')

    # This will create a file in <app> FOLDER
    localDB = config.getWebValue('LocalDB')
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + path.join(basedir, localDB)

    # For 'in memory' database, please use:
    # SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    SQLALCHEMY_TRACK_MODIFICATIONS = config.getWebValue('SQLALCHEMY_TRACK_MODIFICATIONS')

    # THEME SUPPORT
    #  if set then url_for('static', filename='', theme='')
    #  will add the theme name to the static URL:
    #    /static/<DEFAULT_THEME>/filename
    # DEFAULT_THEME = "themes/dark"
    DEFAULT_THEME = config.getWebValue('DEFAULT_THEME')

class ProductionConfig(Config):
    config = Config_file()
    DEBUG = False
    # Security
    SESSION_COOKIE_HTTPONLY = config.getCookieValue('SESSION_COOKIE_HTTPONLY')
    REMEMBER_COOKIE_HTTPONLY = config.getCookieValue('REMEMBER_COOKIE_HTTPONLY')
    REMEMBER_COOKIE_DURATION = config.getCookieValue('REMEMBER_COOKIE_DURATION')
    # PostgreSQL database
    SQLALCHEMY_DATABASE_URI = 'postgresql://{}:{}@{}:{}/{}'.format(
        environ.get('APPSEED_DATABASE_USER', config.getPostgreSQLValue('APPSEED_DATABASE_USER')),
        environ.get('APPSEED_DATABASE_PASSWORD', config.getPostgreSQLValue('APPSEED_DATABASE_PASSWORD')),
        environ.get('APPSEED_DATABASE_HOST', config.getPostgreSQLValue('APPSEED_DATABASE_HOST')),
        environ.get('APPSEED_DATABASE_PORT', config.getPostgreSQLValue('APPSEED_DATABASE_PORT')),
        environ.get('APPSEED_DATABASE_NAME', config.getPostgreSQLValue('APPSEED_DATABASE_NAME'))
    )

class DebugConfig(Config):
    DEBUG = True

config_dict = {
    'Production': ProductionConfig,
    'Debug': DebugConfig
}