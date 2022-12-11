CREATE TABLE "User" ( id SERIAL UNIQUE PRIMARY KEY NOT NULL, username VARCHAR(40) 
			UNIQUE NOT NULL, email VARCHAR(40) UNIQUE NOT NULL, password bytea
		); GRANT ALL PRIVILEGES ON TABLE "User" TO "pi"; GRANT ALL ON SEQUENCE "User_id_seq" TO pi;
		
		CREATE TABLE "Device" ( id SERIAL UNIQUE PRIMARY KEY NOT NULL, devicename VARCHAR(200) UNIQUE NOT NULL, mac VARCHAR(40) UNIQUE NOT NULL, description VARCHAR(400), nAlerts INTEGER NOT NULL 
                        DEFAULT 0
                ); GRANT ALL PRIVILEGES ON TABLE "Device" TO "pi"; GRANT ALL ON SEQUENCE "Device_id_seq" TO pi;
		
		CREATE TYPE PluginStatus as enum('Free','ReadingPCAP','DataPreProcessing','PluginEvaluation');
		CREATE TYPE PluginCategory as enum('Supervised','Unsupervised'); CREATE TYPE PeriodType as enum('Instances','Second','Minute','Hour','Day','Week','Month'); CREATE TABLE "Plugin" ( pluginid SERIAL 
			UNIQUE PRIMARY KEY NOT NULL, pluginname VARCHAR(60) UNIQUE NOT NULL, filepath VARCHAR(300) UNIQUE NOT NULL, category PluginCategory, active BOOLEAN NOT NULL, retrain BOOLEAN NOT NULL, forcetrain BOOLEAN NOT NULL, creationdate 
			TIMESTAMP, lasttrained TIMESTAMP, trainingperiodduration INTEGER DEFAULT 7, trainingperiodtype PeriodType, testsize DECIMAL DEFAULT 0.3, anomalysize DECIMAL DEFAULT 0.3, status PluginStatus, error BOOLEAN NOT NULL
		); GRANT ALL PRIVILEGES ON TABLE "Plugin" TO "pi"; GRANT ALL ON SEQUENCE "Plugin_pluginid_seq" TO pi; CREATE TABLE "DatasetFields" ( datasetid SERIAL UNIQUE PRIMARY KEY NOT NULL, pluginid 
			INTEGER UNIQUE NOT NULL, timestamp BOOLEAN NOT NULL, ETHER_DST BOOLEAN NOT NULL, ETHER_src BOOLEAN NOT NULL, ETHER_ip BOOLEAN NOT NULL, ETHER_type BOOLEAN NOT NULL, ARP_hln BOOLEAN NOT NULL, ARP_hrd BOOLEAN NOT NULL, ARP_op BOOLEAN NOT NULL, ARP_pln BOOLEAN NOT NULL, ARP_pro BOOLEAN NOT NULL, ARP_sha BOOLEAN NOT NULL, ARP_spa BOOLEAN NOT NULL, ARP_tha BOOLEAN NOT NULL, ARP_tpa BOOLEAN NOT NULL, IP_df BOOLEAN 
			NOT NULL, IP_src BOOLEAN NOT NULL, IP_dst BOOLEAN NOT NULL, IP_hl BOOLEAN NOT NULL, IP_id BOOLEAN NOT NULL, IP_len BOOLEAN NOT NULL, IP_mf BOOLEAN NOT NULL, IP_off BOOLEAN NOT 
			NULL, IP_offset BOOLEAN NOT NULL, IP_opts BOOLEAN NOT NULL, IP_p BOOLEAN NOT NULL, IP_rf BOOLEAN NOT NULL, IP_sum BOOLEAN NOT NULL, IP_tos BOOLEAN NOT NULL, IP_ttl BOOLEAN NOT 
			NULL, IP_v BOOLEAN NOT NULL, ICMP_type BOOLEAN NOT NULL, ICMP_code BOOLEAN NOT NULL, ICMP_sum BOOLEAN NOT NULL, TCP_ack BOOLEAN NOT NULL, TCP_dport BOOLEAN NOT NULL, TCP_sport BOOLEAN NOT NULL, TCP_flags BOOLEAN NOT NULL, TCP_off BOOLEAN NOT NULL, TCP_opts 
			BOOLEAN NOT NULL, TCP_seq BOOLEAN NOT NULL, TCP_sum BOOLEAN NOT NULL, TCP_urp BOOLEAN NOT NULL, TCP_win BOOLEAN NOT NULL, UDP_dport BOOLEAN NOT NULL, UDP_sport BOOLEAN NOT NULL, 
			UDP_sum BOOLEAN NOT NULL, UDP_ulen BOOLEAN NOT NULL, PAYLOAD_len BOOLEAN NOT NULL, PAYLOAD_raw BOOLEAN NOT NULL, PAYLOAD_hex BOOLEAN NOT NULL
		); GRANT ALL PRIVILEGES ON TABLE "DatasetFields" TO "pi"; GRANT ALL ON SEQUENCE "DatasetFields_datasetid_seq" TO pi; CREATE TABLE "DataPreProcessing" ( preprocessingid SERIAL UNIQUE 
			PRIMARY KEY NOT NULL, pluginid INTEGER UNIQUE NOT NULL, cleaning BOOLEAN NOT NULL, integration BOOLEAN NOT NULL, selectionperiodduration INTEGER DEFAULT 1, selectionperiodtype PeriodType, labelencodertransformation BOOLEAN NOT NULL, onehotencodertransformation BOOLEAN NOT NULL, gaussiantransformation BOOLEAN NOT NULL, normalization BOOLEAN NOT NULL, standarization BOOLEAN NOT NULL, pca2d BOOLEAN NOT NULL
		); GRANT ALL PRIVILEGES ON TABLE "DataPreProcessing" TO "pi"; GRANT ALL ON SEQUENCE "DataPreProcessing_preprocessingid_seq" TO pi; CREATE TABLE "EvaluationMethods" ( methodid SERIAL 
                        UNIQUE PRIMARY KEY NOT NULL, pluginid INTEGER UNIQUE NOT NULL,
			accuracy BOOLEAN NOT NULL, precision BOOLEAN NOT NULL, recall BOOLEAN NOT NULL, f_score BOOLEAN NOT NULL, specificity BOOLEAN NOT NULL, false_positive_rate BOOLEAN NOT NULL, mahalanobis BOOLEAN NOT NULL, mse BOOLEAN NOT NULL, roc BOOLEAN NOT NULL 
                );
        GRANT ALL PRIVILEGES ON TABLE "EvaluationMethods" TO "pi"; GRANT ALL ON SEQUENCE "EvaluationMethods_methodid_seq" TO pi; CREATE TYPE DataType as enum('Training','Test'); CREATE TABLE "EvaluationResults" ( resultid SERIAL UNIQUE PRIMARY KEY NOT 
                        NULL, pluginid INTEGER NOT NULL, datatype DataType, accuracy FLOAT, precision FLOAT, recall FLOAT, f_score FLOAT, specificity FLOAT, false_positive_rate FLOAT, mahalanobis_min FLOAT, mahalanobis_max FLOAT, mse FLOAT, roc VARCHAR(200), duration FLOAT
			 ); GRANT ALL PRIVILEGES ON TABLE "EvaluationResults" TO "pi";
        GRANT ALL ON SEQUENCE "EvaluationResults_resultid_seq" TO pi;
