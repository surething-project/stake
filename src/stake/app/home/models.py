from sqlalchemy import Column, Integer,Float,String,Boolean,DateTime,Enum
from app import db
import enum

class PluginStatus(enum.Enum):
    Free = "Free"
    ReadingPCAP = "ReadingPCAP"
    DataPreProcessing = "DataPreProcessing"
    PluginEvaluation = "PluginEvaluation"

class PluginCategory(enum.Enum):
    Supervised = "Supervised"
    Unsupervised = "Unsupervised"

class PeriodType(enum.Enum):
    Instances = "Instances"
    Second = "Second"
    Minute = "Minute"
    Hour = "Hour"
    Day = "Day"
    Week = "Week"
    Month = "Month"

class DataType(enum.Enum):
    Test = "Test"
    Training = "Training"

class Plugin(db.Model):
    __tablename__ = 'Plugin'
    __table_args__ = {'extend_existing': True}
    ## Main fields
    pluginid = Column(Integer, primary_key=True)
    pluginname = Column(String, unique=True)
    filepath = Column(String, unique=True)
    category = Column(Enum(PluginCategory)) #Supervised/Unsupervised
    active = Column(Boolean)
    retrain = Column(Boolean)
    forcetrain = Column(Boolean)
    ## Dates
    creationdate = Column(DateTime)
    lasttrained = Column(DateTime)
    trainingperiodduration = Column(Integer)
    trainingperiodtype = Column(Enum(PeriodType)) #Second/Minute/Hour/Day/Week/Month
    ## Dataset
    testsize = Column(Float)
    anomalysize = Column(Float)
    ## DatasetFields: other table
    ## DataPreProcessing: other table
    ## EvaluationMethods: other table
    status = Column(Enum(PluginStatus))
    error = Column(Boolean)
    def __init__(self, **kwargs):
        for property, value in kwargs.items():
            # depending on whether value is an iterable or not, we must
            # unpack it's value (when **kwargs is request.form, some values
            # will be a 1-element list)
            if hasattr(value, '__iter__') and not isinstance(value, str):
                # the ,= unpack of a singleton fails PEP8 (travis flake8 test)
                value = value[0]
            setattr(self, property, value)
    def __repr__(self):
        return str(self.pluginname)

class DatasetFields(db.Model):
    __tablename__ = 'DatasetFields'
    __table_args__ = {'extend_existing': True}
    ## Main fields
    datasetid = Column(Integer, primary_key=True)
    pluginid = Column(Integer)
    ##Packet
    # Extra
    timestamp = Column(Boolean)
    # Ethernet fields
    ether_dst = Column(Boolean)
    ether_src = Column(Boolean)
    ether_ip = Column(Boolean)
    ether_type = Column(Boolean)
    # ARP fields
    arp_hln = Column(Boolean)
    arp_hrd = Column(Boolean)
    arp_op = Column(Boolean)
    arp_pln = Column(Boolean)
    arp_pro = Column(Boolean)
    arp_sha = Column(Boolean)
    arp_spa = Column(Boolean)
    arp_tha = Column(Boolean)
    arp_tpa = Column(Boolean)
    # IP fields
    ip_df = Column(Boolean)
    ip_src = Column(Boolean)
    ip_dst = Column(Boolean)
    ip_hl = Column(Boolean)
    ip_id = Column(Boolean)
    ip_len = Column(Boolean)
    ip_mf = Column(Boolean)
    ip_off = Column(Boolean)
    ip_offset = Column(Boolean)
    ip_opts = Column(Boolean)
    ip_p = Column(Boolean)
    ip_rf = Column(Boolean)
    ip_sum = Column(Boolean)
    ip_tos = Column(Boolean)
    ip_ttl = Column(Boolean)
    ip_v = Column(Boolean)
    ## ICMP fields
    icmp_type = Column(Boolean)
    icmp_code = Column(Boolean)
    icmp_sum = Column(Boolean)
    # TCP fields
    tcp_ack = Column(Boolean)
    tcp_dport = Column(Boolean)
    tcp_sport = Column(Boolean)
    tcp_flags = Column(Boolean)
    tcp_off = Column(Boolean)
    tcp_opts = Column(Boolean)
    tcp_seq = Column(Boolean)
    tcp_sum = Column(Boolean)
    tcp_urp = Column(Boolean)
    tcp_win = Column(Boolean)
    # UDP fields
    udp_dport = Column(Boolean)
    udp_sport = Column(Boolean)
    udp_sum = Column(Boolean)
    udp_ulen = Column(Boolean)
    # Payload fields
    payload_len = Column(Boolean)
    payload_raw = Column(Boolean)
    payload_hex = Column(Boolean)
    def __init__(self, **kwargs):
        for property, value in kwargs.items():
            # depending on whether value is an iterable or not, we must
            # unpack it's value (when **kwargs is request.form, some values
            # will be a 1-element list)
            if hasattr(value, '__iter__') and not isinstance(value, str):
                # the ,= unpack of a singleton fails PEP8 (travis flake8 test)
                value = value[0]
            setattr(self, property, value)
    def __repr__(self):
        return str(self.pluginid)

class DataPreProcessing(db.Model):
    __tablename__ = 'DataPreProcessing'
    __table_args__ = {'extend_existing': True}
    ## Main fields
    preprocessingid = Column(Integer, primary_key=True)
    pluginid = Column(Integer)
    ## DataPreProcessing
        # Feature Extraction
    cleaning = Column(Boolean)
    integration = Column(Boolean)
         # Feature Selection
            # Data Selection
    selectionperiodduration = Column(Integer)
    selectionperiodtype = Column(Enum(PeriodType)) #Second/Minute/Hour/Day/Week/Month
            # Data Transformation
    labelencodertransformation = Column(Boolean)
    onehotencodertransformation = Column(Boolean)
    gaussiantransformation = Column(Boolean)
            # Secondary Data Transformation
    normalization = Column(Boolean)
    standarization = Column(Boolean)
    pca2d = Column(Boolean)
    def __init__(self, **kwargs):
        for property, value in kwargs.items():
            # depending on whether value is an iterable or not, we must
            # unpack it's value (when **kwargs is request.form, some values
            # will be a 1-element list)
            if hasattr(value, '__iter__') and not isinstance(value, str):
                # the ,= unpack of a singleton fails PEP8 (travis flake8 test)
                value = value[0]
            setattr(self, property, value)
    def __repr__(self):
        return str(self.pluginid)

class EvaluationMethods(db.Model):
    __tablename__ = 'EvaluationMethods'
    __table_args__ = {'extend_existing': True}
    ## Main fields
    methodid = Column(Integer, primary_key=True)
    pluginid = Column(Integer)
    ## Basic Evaluation Methods
    accuracy = Column(Boolean)
    precision = Column(Boolean)
    recall = Column(Boolean) #tpr
    f_score = Column(Boolean)
    specificity = Column(Boolean)
    false_positive_rate = Column(Boolean)
    ## Advanced Evaluation Methods
    mahalanobis = Column(Boolean)
    mse = Column(Boolean) # mean squared error
    ## Plot Evaluation Methods
    roc = Column(Boolean)
    def __init__(self, **kwargs):
        for property, value in kwargs.items():
            # depending on whether value is an iterable or not, we must
            # unpack it's value (when **kwargs is request.form, some values
            # will be a 1-element list)
            if hasattr(value, '__iter__') and not isinstance(value, str):
                # the ,= unpack of a singleton fails PEP8 (travis flake8 test)
                value = value[0]
            setattr(self, property, value)
    def __repr__(self):
        return str(self.pluginid)
    
class EvaluationResults(db.Model):
    __tablename__ = 'EvaluationResults'
    __table_args__ = {'extend_existing': True}
    ## Main fields
    resultid = Column(Integer, primary_key=True)
    pluginid = Column(Integer)
    datatype = Column(Enum(DataType))
    ## Basic Evaluation Methods
    accuracy = Column(Float)
    precision = Column(Float)
    recall = Column(Float)
    f_score = Column(Float)
    specificity = Column(Float)
    false_positive_rate = Column(Float)
    ## Advanced Evaluation Methods
    mahalanobis_min = Column(Float)
    mahalanobis_max = Column(Float)
    mse = Column(Float) # mean squared error
    ## Plot Evaluation Methods
    roc = Column(String)
    ## Extra Information
    duration = Column(Float)
    def __init__(self, **kwargs):
        for property, value in kwargs.items():
            # depending on whether value is an iterable or not, we must
            # unpack it's value (when **kwargs is request.form, some values
            # will be a 1-element list)
            if hasattr(value, '__iter__') and not isinstance(value, str):
                # the ,= unpack of a singleton fails PEP8 (travis flake8 test)
                value = value[0]
            setattr(self, property, value)
    def __repr__(self):
        return str(self.pluginid)

class Device(db.Model):
    __tablename__ = 'Device'
    __table_args__ = {'extend_existing': True}
    id = Column(Integer, primary_key=True)
    devicename = Column(String, unique=True)
    mac = Column(String, unique=True)
    description = Column(String)
    nalerts = Column(Integer)
    def __init__(self, **kwargs):
        for property, value in kwargs.items():
            # depending on whether value is an iterable or not, we must
            # unpack it's value (when **kwargs is request.form, some values
            # will be a 1-element list)
            if hasattr(value, '__iter__') and not isinstance(value, str):
                # the ,= unpack of a singleton fails PEP8 (travis flake8 test)
                value = value[0]
            setattr(self, property, value)
    def __repr__(self):
        return str(self.devicename)