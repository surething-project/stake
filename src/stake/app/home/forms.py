from flask_wtf import FlaskForm
from wtforms import TextField, IntegerField, TextAreaField, SelectField, BooleanField, DecimalField 
from wtforms.validators import InputRequired, DataRequired, IPAddress 
from flask_wtf.file import FileField, FileRequired

class DeviceForm(FlaskForm):
    add_name    = TextField('Name'        , id='add_name'    , validators=[DataRequired()])
    add_mac = TextField('IP' , id='add_mac'      , validators=[DataRequired(),IPAddress(ipv4=True)])
    add_description = TextAreaField('Description' , id='add_description'      , validators=[DataRequired()],render_kw={"rows": 2, "cols": 11, "maxlength": 200})
    remove_name    = SelectField('Name'        , id='remove_name'    , validators=[DataRequired()],choices=[('name', 'Name')])

class PlugInForm(FlaskForm):
    #### Add
    ### Plugin 
    add_pluginname = TextField('Name'        , id='add_pluginname'    , validators=[DataRequired()])
    add_category = SelectField('Category', id='add_category'    , validators=[DataRequired()], \
        choices=[('category', 'Category'),('Supervised', 'Supervised'),('Unsupervised','Unsupervised')])
    add_activate = BooleanField('Active Anomaly Detection'        , id='add_activate'    )
    add_retrain = BooleanField('Automatic Re-train Plug-in'        , id='add_retrain'    )
    #creationdate 
    #lasttrained
    add_trainingperiodtype = SelectField('Training Period Type', id='add_trainingperiodtype'    , validators=[DataRequired()], \
        choices=[('trainingperiodtype', 'Training Period Type'),('Second','Second'),('Minute', 'Minute'),('Hour','Hour'), ('Day','Day'),\
            ('Week','Week'),('Month','Month')])
    add_trainingperiodduration = TextField('Training Periodicity', id='add_trainingperiodduration'    , validators=[DataRequired()])
    ## Dataset
    add_testsize = DecimalField('Test Size (0.00-1.00)', id='add_testsize', rounding=None,places=3)
    add_anomalysize = DecimalField('Anomaly Size (0.00-1.00)', id='add_anomalysize', rounding=None,places=3)
    ## Filepath
    add_file = FileField('Plug-in Model File (.sav)',id='add_file', validators=[FileRequired()])
    
    ### DatasetFields: other table
    add_timestamp = BooleanField('Timestamp'        , id='add_timestamp'    )
    ## Ethernet Fields
    add_ETHER_dst = BooleanField('Destination MAC Address'        , id='add_ETHER_dst'   )
    add_ETHER_src = BooleanField('Source MAC Address'        , id='add_ETHER_src'   )
    add_ETHER_ip = BooleanField('Ethernet Packet Information'        , id='add_ETHER_ip'   )
    add_ETHER_type = BooleanField('Ethernet Packet Type'        , id='add_ETHER_type'   )
    ## ARP Fields
    add_ARP_hln = BooleanField('ARP Header Length'        , id='add_ARP_hln'   )
    add_ARP_hrd = BooleanField('ARP Hardware Type'        , id='add_ARP_hrd'   )
    add_ARP_op = BooleanField('ARP Operation Code'        , id='add_ARP_op'   )
    add_ARP_pln = BooleanField('ARP Address Protocol Length'        , id='add_ARP_pln'   )
    add_ARP_pro = BooleanField('ARP Address Protocol Type'        , id='add_ARP_pro'   )
    add_ARP_sha = BooleanField('ARP Sender Hardware Address'        , id='add_ARP_sha'   )
    add_ARP_spa = BooleanField('ARP Sender Protocol Address'        , id='add_ARP_spa'   )
    add_ARP_tha = BooleanField('ARP Target Hardware Address'        , id='add_ARP_tha'   )
    add_ARP_tpa = BooleanField('ARP Target Protocol Address'        , id='add_ARP_tpa'   )
    ## IP fields
    add_IP_df = BooleanField('IP \"Don\'t Fragment\" Flag'        , id='add_IP_df'   )
    add_IP_src = BooleanField('Source IP'        , id='add_IP_src'    )
    add_IP_dst = BooleanField('Destination IP'        , id='add_IP_dst'   )
    add_IP_hl = BooleanField('IP Header Length'        , id='add_IP_hl'    )
    add_IP_id = BooleanField('IP Packet ID'        , id='add_IP_id'   )
    add_IP_len = BooleanField('IP Packet Length'        , id='add_IP_len'    )
    add_IP_mf = BooleanField('IP \"More Fragment\" Flag'        , id='add_IP_mf'    )
    add_IP_off = BooleanField('IP Offset Value'        , id='add_IP_off'    )
    add_IP_offset = BooleanField('IP \"Offset\" Flag'        , id='add_IP_offset'   )
    add_IP_opts = BooleanField('IP Options'        , id='add_IP_opts'   )
    add_IP_p = BooleanField('IP Encapsulated Protocol'        , id='add_IP_p'    )
    add_IP_rf = BooleanField('IP Reserved Flag'        , id='add_IP_rf'   )
    add_IP_sum = BooleanField('IP Checksum'        , id='add_IP_sum'   )
    add_IP_tos = BooleanField('IP Type of Service'        , id='add_IP_tos'   )
    add_IP_ttl = BooleanField('IP \"Time to Live\" Flag'        , id='add_IP_ttl'  )
    add_IP_v = BooleanField('IP Version'        , id='add_IP_v'    )
    ## ICMP fields
    add_ICMP_type = BooleanField('ICMP type'        , id='add_ICMP_type'   )
    add_ICMP_code = BooleanField('ICMP code (sub-type)'        , id='add_ICMP_code'   )
    add_ICMP_sum = BooleanField('ICMP Checksum'        , id='add_ICMP_sum'   )
    ## TCP fields
    add_TCP_ack = BooleanField('TCP \"Ack\" Flag'        , id='add_TCP_ack'   )
    add_TCP_dport = BooleanField('TCP Destination Port'        , id='add_TCP_dport'    )
    add_TCP_sport = BooleanField('TCP Source Port'        , id='add_TCP_sport'  )
    add_TCP_flags = BooleanField('TCP Flags'        , id='add_TCP_flags'   )
    add_TCP_off = BooleanField('TCP \"Offset\" Flag '        , id='add_TCP_off'   )
    add_TCP_opts = BooleanField('TCP Options'        , id='add_TCP_opts'    )
    add_TCP_seq = BooleanField('TCP Sequence Number'        , id='add_TCP_seq'    )
    add_TCP_sum = BooleanField('TCP Checksum'        , id='add_TCP_sum'    )
    add_TCP_urp = BooleanField('TCP \"Urgent Pointer\" Flag'        , id='add_TCP_urp'   )
    add_TCP_win = BooleanField('TCP Window Size'        , id='add_TCP_win'    )
    ## UDP fields
    add_UDP_dport = BooleanField('UDP Destination Port'        , id='add_UDP_dport'    )
    add_UDP_sport = BooleanField('UDP Source Port'        , id='add_UDP_sport'   )
    add_UDP_sum = BooleanField('UDP Checksum'        , id='add_UDP_sum'    )
    add_UDP_ulen = BooleanField('UDP Packet Length'        , id='add_UDP_ulen'   )
    ## Payload fields
    add_PAYLOAD_len = BooleanField('Payload Length'        , id='add_PAYLOAD_len'   )
    add_PAYLOAD_raw = BooleanField('Payload Raw'        , id='add_PAYLOAD_raw'   )
    add_PAYLOAD_hex = BooleanField('Payload Hex'        , id='add_PAYLOAD_hex'    )

    ### DataPreProcessing: other table
    ## DataPreProcessing
    # Feature Extraction
    add_cleaning = BooleanField('Data Cleaning [Recommended only for Supervised Learning Plug-ins]'        , id='add_cleaning'    )
    add_integration = BooleanField('Data Integration [Mandatory]'        , id='add_integration'    )
    # Feature Selection
    
    add_selectionperiodduration = TextField('Data Training Size', id='add_selectionperiodduration', validators=[DataRequired()])
    add_selectionperiodtype = SelectField('Data Training Size Type', id='add_selectionperiodtype'    , validators=[DataRequired()], \
        choices=[('selectionperiodtype', 'Training Period Type'),('Instances','Instances'),('Second','Second'),('Minute', 'Minute'),('Hour','Hour'), ('Day','Day'),\
            ('Week','Week'),('Month','Month')])
    # add_transformation = SelectField('Type of transformation', id='add_transformation'    , validators=[DataRequired()], \
    #   choices=[('notransformation', 'No Transformation'),('labelencoder','Label Encoder'),('onehotencoder', 'One Hot Encoder'), \
    #        ('gaussian','Gaussian')])
    add_transformation = SelectField('Type of transformation', id='add_transformation'    , validators=[DataRequired()], \
        choices=[('notransformation', 'No Transformation'),('labelencoder','Label Encoder'),('gaussian','Gaussian')])
    add_secondary_transformation = SelectField('Type of secondary transformation', id='add_secondary_transformation'    , validators=[DataRequired()], \
        choices=[('notransformation', 'No Transformation'),('normalization','Normalization'),('standarization', 'Standarization'), \
                 ('pca2d','PCA - 2 Dimensional')])
    
    ### EvaluationMethods: other table
    ## Basic Evaluation Methods
    add_accuracy = BooleanField('Accuracy'        , id='add_accuracy'   )
    add_precision = BooleanField('Precision'        , id='add_precision'    )
    add_recall = BooleanField('Recall (True Positive Rate)'        , id='add_recall'    )
    add_f_score = BooleanField('F-Score'        , id='add_f_score'    )
    add_specificity = BooleanField('Specificity'        , id='add_specificity'    )
    add_false_positive_rate = BooleanField('False Positive Rate'        , id='add_false_positive_rate'    )
    ## Advanced Evaluation Methods
    add_mahalanobis = BooleanField('Mahalanobis'        , id='add_mahalanobis'    )
    add_mse = BooleanField('Mean Squared Error'        , id='add_mse'   )
    ## Plot Evaluation Methods
    add_roc = BooleanField('Receiver Operating Characteristic(ROC)'        , id='add_roc'    )

    #### Edit/Remove ___________________________________________________________________________________________________________________________
    ### Plugin
    edit_pluginname = SelectField('Plug-in Name'        , id='edit_pluginname'    , validators=[DataRequired()],choices=[('name', 'Plug-in Name')])
    edit_category = SelectField('Category', id='edit_category'    , validators=[DataRequired()], \
        choices=[('category', 'Category'),('Supervised', 'Supervised'),('Unsupervised','Unsupervised')])
    edit_activate = BooleanField('Active Anomaly Detection'        , id='edit_activate'    )
    edit_retrain = BooleanField('Automatic Re-train Plug-in'        , id='edit_retrain'    )
    #creationdate 
    #lasttrained
    edit_trainingperiodtype = SelectField('Training Period Type', id='edit_trainingperiodtype'    , validators=[DataRequired()], \
        choices=[('trainingperiodtype', 'Training Period Type'),('Second','Second'),('Minute', 'Minute'),('Hour','Hour'), ('Day','Day'),\
            ('Week','Week'),('Month','Month')])
    edit_trainingperiodduration = TextField('Training Periodicity', id='edit_trainingperiodduration'    , validators=[DataRequired()])
    ## Dataset
    edit_testsize = TextField('Test Size (0.00-1.00)', id='edit_testsize')
    edit_anomalysize = TextField('Anomaly Size (0.00-1.00)', id='edit_anomalysize')
    ## Filepath
    edit_file = FileField('Plug-in Model File (.sav)',id='edit_file', validators=[FileRequired()])
    
    ### DatasetFields: other table
    edit_timestamp = BooleanField('Timestamp'        , id='edit_timestamp'    )
    ## Ethernet Fields
    edit_ETHER_dst = BooleanField('Destination MAC Address'        , id='edit_ETHER_dst'   )
    edit_ETHER_src = BooleanField('Source MAC Address'        , id='edit_ETHER_src'   )
    edit_ETHER_ip = BooleanField('Ethernet Packet Information'        , id='edit_ETHER_ip'   )
    edit_ETHER_type = BooleanField('Ethernet Packet Type'        , id='edit_ETHER_type'   )
    ## ARP Fields
    edit_ARP_hln = BooleanField('ARP Header Length'        , id='edit_ARP_hln'   )
    edit_ARP_hrd = BooleanField('ARP Hardware Type'        , id='edit_ARP_hrd'   )
    edit_ARP_op = BooleanField('ARP Operation Code'        , id='edit_ARP_op'   )
    edit_ARP_pln = BooleanField('ARP Address Protocol Length'        , id='edit_ARP_pln'   )
    edit_ARP_pro = BooleanField('ARP Address Protocol Type'        , id='edit_ARP_pro'   )
    edit_ARP_sha = BooleanField('ARP Sender Hardware Address'        , id='edit_ARP_sha'   )
    edit_ARP_spa = BooleanField('ARP Sender Protocol Address'        , id='edit_ARP_spa'   )
    edit_ARP_tha = BooleanField('ARP Target Hardware Address'        , id='edit_ARP_tha'   )
    edit_ARP_tpa = BooleanField('ARP Target Protocol Address'        , id='edit_ARP_tpa'   )
    ## IP fields
    edit_IP_df = BooleanField('IP \"Don\'t Fragment\" Flag'        , id='edit_IP_df'   )
    edit_IP_src = BooleanField('Source IP'        , id='edit_IP_src'    )
    edit_IP_dst = BooleanField('Destination IP'        , id='edit_IP_dst'   )
    edit_IP_hl = BooleanField('IP Header Length'        , id='edit_IP_hl'    )
    edit_IP_id = BooleanField('IP Packet ID'        , id='edit_IP_id'   )
    edit_IP_len = BooleanField('IP Packet Length'        , id='edit_IP_len'    )
    edit_IP_mf = BooleanField('IP \"More Fragment\" Flag'        , id='edit_IP_mf'    )
    edit_IP_off = BooleanField('IP Offset Value'        , id='edit_IP_off'    )
    edit_IP_offset = BooleanField('IP \"Offset\" Flag'        , id='edit_IP_offset'   )
    edit_IP_opts = BooleanField('IP Options'        , id='edit_IP_opts'   )
    edit_IP_p = BooleanField('IP Encapsulated Protocol'        , id='edit_IP_p'    )
    edit_IP_rf = BooleanField('IP Reserved Flag'        , id='edit_IP_rf'   )
    edit_IP_sum = BooleanField('IP Checksum'        , id='edit_IP_sum'   )
    edit_IP_tos = BooleanField('IP Type of Service'        , id='edit_IP_tos'   )
    edit_IP_ttl = BooleanField('IP \"Time to Live\" Flag'        , id='edit_IP_ttl'  )
    edit_IP_v = BooleanField('IP Version'        , id='edit_IP_v'    )
    ## ICMP fields
    edit_ICMP_type = BooleanField('ICMP type'        , id='edit_ICMP_type'   )
    edit_ICMP_code = BooleanField('ICMP code (sub-type)'        , id='edit_ICMP_code'   )
    edit_ICMP_sum = BooleanField('ICMP Checksum'        , id='edit_ICMP_sum'   )
    ## TCP fields
    edit_TCP_ack = BooleanField('TCP \"Ack\" Flag'        , id='edit_TCP_ack'   )
    edit_TCP_dport = BooleanField('TCP Destination Port'        , id='edit_TCP_dport'    )
    edit_TCP_sport = BooleanField('TCP Source Port'        , id='edit_TCP_sport'  )
    edit_TCP_flags = BooleanField('TCP Flags'        , id='edit_TCP_flags'   )
    edit_TCP_off = BooleanField('TCP \"Offset\" Flag '        , id='edit_TCP_off'   )
    edit_TCP_opts = BooleanField('TCP Options'        , id='edit_TCP_opts'    )
    edit_TCP_seq = BooleanField('TCP Sequence Number'        , id='edit_TCP_seq'    )
    edit_TCP_sum = BooleanField('TCP Checksum'        , id='edit_TCP_sum'    )
    edit_TCP_urp = BooleanField('TCP \"Urgent Pointer\" Flag'        , id='edit_TCP_urp'   )
    edit_TCP_win = BooleanField('TCP Window Size'        , id='edit_TCP_win'    )
    ## UDP fields
    edit_UDP_dport = BooleanField('UDP Destination Port'        , id='edit_UDP_dport'    )
    edit_UDP_sport = BooleanField('UDP Source Port'        , id='edit_UDP_sport'   )
    edit_UDP_sum = BooleanField('UDP Checksum'        , id='edit_UDP_sum'    )
    edit_UDP_ulen = BooleanField('UDP Packet Length'        , id='edit_UDP_ulen'   )
    ## Payload fields
    edit_PAYLOAD_len = BooleanField('Payload Length'        , id='edit_PAYLOAD_len'   )
    edit_PAYLOAD_raw = BooleanField('Payload Raw'        , id='edit_PAYLOAD_raw'   )
    edit_PAYLOAD_hex = BooleanField('Payload Hex'        , id='edit_PAYLOAD_hex'    )

    ### DataPreProcessing: other table
    ## DataPreProcessing
    # Feature Extraction
    edit_cleaning = BooleanField('Data Cleaning [Recommended only for Supervised Learning Plug-ins]'        , id='edit_cleaning'    )
    edit_integration = BooleanField('Data Integration [Mandatory]'        , id='edit_integration'    )
    # Feature Selection
    edit_selectionperiodduration = TextField('Data Training Size', id='edit_selectionperiodduration', validators=[DataRequired()])
    edit_selectionperiodtype = SelectField('Data Training Size Type', id='edit_selectionperiodtype'    , validators=[DataRequired()], \
        choices=[('trainingperiodtype', 'Data Training Size Type'),('Instances','Instances'),('Second','Second'),('Minute', 'Minute'),('Hour','Hour'), ('Day','Day'),\
            ('Week','Week'),('Month','Month')])
    # edit_transformation = SelectField('Type of transformation', id='edit_transformation'    , validators=[DataRequired()], \
    #   choices=[('notransformation', 'No Transformation'),('labelencoder','Label Encoder'),('onehotencoder', 'One Hot Encoder'), \
    #       ('gaussian','Gaussian')])
    edit_transformation = SelectField('Type of transformation', id='edit_transformation'    , validators=[DataRequired()], \
       choices=[('notransformation', 'No Transformation'),('labelencoder','Label Encoder'),('gaussian','Gaussian')])
    edit_secondary_transformation = SelectField('Type of secondary transformation', id='edit_secondary_transformation'    , validators=[DataRequired()], \
        choices=[('notransformation', 'No Transformation'),('normalization','Normalization'),('standarization', 'Standarization'),\
                 ('pca2d','PCA - 2 Dimensional')])
    
    ### EvaluationMethods: other table
    ## Basic Evaluation Methods
    edit_accuracy = BooleanField('Accuracy'        , id='edit_accuracy'   )
    edit_precision = BooleanField('Precision'        , id='edit_precision'    )
    edit_recall = BooleanField('Recall (True Positive Rate)'        , id='edit_recall'    )
    edit_f_score = BooleanField('F-Score'        , id='edit_f_score'    )
    edit_specificity = BooleanField('Specificity'        , id='edit_specificity'    )
    edit_false_positive_rate = BooleanField('False Positive Rate'        , id='edit_false_positive_rate'    )
    ## Advanced Evaluation Methods
    edit_mahalanobis = BooleanField('Mahalanobis'        , id='edit_mahalanobis'    )
    edit_mse = BooleanField('Mean Squared Error'        , id='edit_mse'   )
    ## Plot Evaluation Methods
    edit_roc = BooleanField('Receiver Operating Characteristic(ROC)'        , id='edit_roc'    )