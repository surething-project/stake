# STAKEPrototype
STAKE project code - Kevin B. Corrales - advisor Miguel L Pardal

## STAKE System Demo
The STAKE system is available via HTTP protocol. \
The Web interface allows users to access various functionalities and information from the Machine Learning plug-ins and network.
### Entry page:
The **Entry page** of the system allows the user is able to sign in or log in. \
The information needed to sign in are: Username, E-mail and Password. \
![Sign-in page](images/entry/register.png) \
The information needed to give to log in are: Username and Password. \
![Log-in in page](images/entry/login.png)

### Dashboard page:
After the user is authenticated, the user is redirected to the **Dashboard page**. \
This page displays a summary of information available from the following pages: **Captured Traffic page**, **System Information page**, **Device Management page**, **Alerts page** and **Plug-ins Results page**. \
![Dashboard page - upper part](images/dashboard/dashboard1.png) 
![Dashboard page - middle part](images/dashboard/dashboard2.png)
![Dashboard page - lower part](images/dashboard/dashboard3.png)

### Profile Settings page:
The  **Profile Settings page** is available through the Web interface header. \
This page enables the user to edit his profile information. \
![Profile Settings page](images/profile/profile_settings.png)

### Device Management page:
The **Device Management page** allows the user to manage the network devices. \
The auditing of alerts raised by an anomaly detection is important, since it enables the ability to investigate the anomaly. \
Thus, devices can be identified in this page by matching a name with the device MAC address. \
Additionally, the user is able to add a short description about the identified device. \
![Device Management page](images/device/devices2.png)

### Plug-in Configuration page:
The most compounded page is the **Plug-in Configuration page**. \
This page allows the user to add, edit and remove plug-ins. \
By adding or editing a plug-in the user can configure specific plug-ins information such as:
- Plug-in file path (".sav" extension is mandatory);
- Plug-in name;
- Identify the Plug-in category (Supervised/Unsupervised);
- Enable/Disable Plug-in anomaly detection;
- Enable/Disable automatic Plug-in re-training;
- Configure the re-training periodicity;
- Select the anomaly percentage of the training data;
- Select the train/test split percentage for the training data(only for Supervised Learning plug-ins);
- Select the Data Pre-processing steps in the training data. This includes feature selection methods selection, training data size selection and data transformation methods selection;
- Select the Dataset features used in the training data;
- Select the evaluation metrics used for Plug-in training evaluation;

Add Plug-in configuration tab:\
![Plug-in Configuration page - add Plug-in tab - upper part](images/plugin_config/plugins_config1_1.png) 
![Plug-in Configuration page - add Plug-in tab - middle upper part](images/plugin_config/plugins_config1_2.png) 
![Plug-in Configuration page - add Plug-in tab - middle lower part](images/plugin_config/plugins_config1_3.png) 
![Plug-in Configuration page - add Plug-in tab - lower part](images/plugin_config/plugins_config1_4.png) 

Edit Plug-in configuration tab:\
![Plug-in Configuration page - edit Plug-in tab - upper part](images/plugin_config/plugins_config2_1.png) 
![Plug-in Configuration page - edit Plug-in tab - middle upper part](images/plugin_config/plugins_config2_2.png) 
![Plug-in Configuration page - edit Plug-in tab - middle lower part](images/plugin_config/plugins_config2_3.png) 
![Plug-in Configuration page - add Plug-in tab - lower part](images/plugin_config/plugins_config2_4.png) 

### Plug-in Results page:
The plug-ins training results from the evaluation metrics selected for each plug-in from the previous page (**Plug-in Configuration page**) is then shown in the **Plug-in Results page**. \
In this page, the user is able to confirm if the training was a success or if there is a need for adjusment in the plug-in configuration. \
Random Forest results example: \
![Plug-in Results page - Random Forest Plug-in tab](images/plugin_results/plugins_results1.png) 
Elliptic Envelope results example: \
![Plug-in Results page - Elliptic Envelope Plug-in tab](images/plugin_results/plugins_results2.png) 

### Alerts page:
All the anomaly alerts from the system can be reviewed in the **Alerts page**. \
In addition, the system also provides information about the plug-in training status and system errors.
![Alerts page - upper part](images/alerts/alerts1.png) 
![Alerts page - lower part](images/alerts/alerts2.png) 
The information can be filtered in the search:
![Alerts page - search filter](images/alerts/alerts3.png) 

### Captured Traffic page:
The **Captured Traffic page** shows information and statistics about the last `N` captured packets(configured in the .ini file from the system) by the system. \
![Traffic page - upper part](images/traffic/traffic1.png) 
![Traffic page - middle part](images/traffic/traffic3.png) 
![Traffic page - lower part](images/traffic/traffic4.png)

### System Information page:
Being aware of the system status is also important. \
Therefore, the **System Information page** allows the user to verify the usage of different hardware components of the system. \
![System Information page](images/system/system_info.png)

## Tools Demo
Creating effective plug-ins is a critical part for the system anomaly detection to work efficiently. \
But, to create plug-ins, we need data. \
Thus, a dataset creation tool was also developed. \
The tools are located at the `src/tools` folder.
### Create Dataset:
The path of the dataset and the adapter which will be sniffed are hardcoded. \
The dataset is saved as '.pcap' format.
To execute the tool, we simply run:
```
python3 database_creator.py
```
### Create Plug-ins:
The developed plug-ins were based on **Elliptic Envelope** and **Random Forest** models. \
The tool used to create the plug-ins executes 4 main steps: 
1. Read the '.pcap' file containing the captured packets and parse it into a dataframe.
2. Train the selected plug-in models.
3. Save the training results and plots.
4. Save each of the trained models into '.sav' files.

To execute this tool, we can run:
```
python3 plugin_creator.py
```
All configurations need to be hardcoded.

### Test Plug-ins:
Additionally, if it is desired to test the plug-ins after being saved, we can use the following plug-in testing tool:
```
python3 plugin_tester.py
```
Just like the previous tools, all settings also need to be hardcoded.
