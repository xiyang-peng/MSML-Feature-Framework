
#%feature extraction demo from PD
import matplotlib.pyplot as plt
import pandas as pd
from statsmodels.graphics.tsaplots import *
import seaborn as sns
import numpy as np
import sequence_fea_util
import scipy.stats as stats
from sklearn.preprocessing import StandardScaler
from scipy.signal import find_peaks
import sys
import os
sys.path.append("/Volumes/T7 Shield/TBME_code3.0/")
from utils import long_short_term_feature
from utils import tremor_utils
from utils import pd_utils
#%
# get feature
url= "/Volumes/T7 Shield/norm_named_raw_data/PD/"
path = "/Volumes/T7 Shield/TBME_code3.0/"
severity_data = pd.read_csv(path + 'Information_Sheet.csv')
severity_data = severity_data[["PatientID","Affected_Side","Severity_Level"]]
severity_data = severity_data.drop(0)
severity_data = severity_data.astype(int)
print(severity_data)
#%
Feature = pd.DataFrame()
for pd_num in range(1,101,1):
    # accdata = StandardScaler().fit_transform(accdata)
    for activity_num in range(1,15,1):
        #select severity side data  
        affected_Side = severity_data.loc[severity_data['PatientID'] == pd_num, 'Affected_Side']
        print(affected_Side.values[0]) 
        print(affected_Side) 
        # print("所有患者ID的唯一值：", severity_data['PatientID'].unique())
        # affected_Side = severity_data[severity_data['PatientID'] == pd_num]['Affected_Side'].values[0]
        print("pd_num:{},activity_num:{}".format(pd_num, activity_num))
        if(affected_Side.values[0]==1):
            filefullpath=url+"person{}/{}_session{}_wristr.csv".format(pd_num,pd_num,activity_num)
        else:
            filefullpath=url+"person{}/{}_session{}_wristr.csv".format(pd_num,pd_num,activity_num)
        if not os.path.exists(filefullpath):
            continue
        data = pd.read_csv(filefullpath,header=0)
        data = data.drop(0)
        
        new_column_labels = {"Accel_WR_X_CAL": "wr_acc_x", "Accel_WR_Y_CAL": "wr_acc_y", "Accel_WR_Z_CAL": "wr_acc_z", "Gyro_X_CAL": "gyro_x", "Gyro_Y_CAL": "gyro_y", "Gyro_Z_CAL": "gyro_z"}
        data = data.rename(columns=new_column_labels)
        
        for col in ["wr_acc_x","wr_acc_y","wr_acc_z"]:                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                      
            data[col] = data[col].astype('float64')
        for col in ["gyro_x","gyro_y","gyro_z"]:     
            data[col] = data[col].astype('float64')
        data["acca"]=np.sqrt(data["wr_acc_x"]*data["wr_acc_x"]+data["wr_acc_y"]*data["wr_acc_y"]+data["wr_acc_z"]*data["wr_acc_z"])
        data["gyroa"]=np.sqrt(data["gyro_x"]*data["gyro_x"]+data["gyro_y"]*data["gyro_y"]+data["gyro_z"]*data["gyro_z"])
        
        # data["wr_acc_x","wr_acc_y","wr_acc_z","acca"] = data["wr_acc_x","wr_acc_y","wr_acc_z","acca"].apply(lambda x : (x-np.mean(x))/(np.std(x)))
        # data["gyro_x","gyro_y","gyro_z","gyroa"] = data["gyro_x","gyro_y","gyro_z","gyroa"].apply(lambda x : (x-np.mean(x))/(np.std(x)))
        
        accdata=data[["wr_acc_x","wr_acc_y","wr_acc_z","acca"]]
        gyrodata=data[["gyro_x","gyro_y","gyro_z","gyroa"]]
        
        accdata = accdata.values
        gyrodata = gyrodata.values
        #输入需要为numpy数组
        accdata = StandardScaler().fit_transform(accdata)
        gyrodata = StandardScaler().fit_transform(gyrodata)
        databand_acc = accdata.copy()
        databand_gyro = gyrodata.copy()
        for k in range(0,4): 
            databand_acc[:,k] = pd_utils.butter_bandpass_filter(accdata[:,k],0.3, 17, 200, order = 3)
            databand_gyro[:,k] = pd_utils.butter_bandpass_filter(gyrodata[:,k],0.3, 17, 200, order = 3)
        
        # databand_gyro[:,2] = pd_utils.butter_bandpass_filter(accdata[:,2],0.3, 3, 200, order = 3)
        databand_gyro[:,2] = pd_utils.butter_bandpass_filter(gyrodata[:,2],0.3, 3, 200, order = 3)
        databand_acc = pd.DataFrame(databand_acc)
        databand_gyro = pd.DataFrame(databand_gyro)
        databand = pd.concat([databand_acc,databand_gyro],axis = 1)
        
        accdatax = databand.iloc[:,0]
        accdatay = databand.iloc[:,1]
        accdataz = databand.iloc[:,2]
        acca = databand.iloc[:,3]
        gyrodatax = databand.iloc[:,4]
        gyrodatay = databand.iloc[:,5]
        gyrodataz = databand.iloc[:,6]
        gyroa = databand.iloc[:,7]
        
        windowsize=300
        # overlappingrate = 1  #0 overlap
        overlappingrate = 2  #50% overlap
        fs = 200
        
        acc_feature = long_short_term_feature.longShortTermFeature(accdatax, accdatay, accdataz, acca, windowsize, overlappingrate, fs)
        # acc_feature = acc_feature.iloc[:, :-2]
        gyro_feature = long_short_term_feature.longShortTermFeature(gyrodatax, gyrodatay, gyrodataz, gyroa, windowsize, overlappingrate, fs)
        feature = pd.concat([acc_feature,gyro_feature],axis=1)
        feature.columns = fea_column
        
        feature["PatientID"]=pd_num
        feature["activity_label"]=activity_num
        if((pd_num==1)&(activity_num==1)):
            Feature  = feature
        else:
            Feature = pd.concat([Feature,feature],axis=0)

# Feature.to_csv("/Volumes/T7 Shield/augment/m12activity_long_short_636feature_right_side.csv")
Feature.to_csv(path + "14activity_long_short_636feature_right_side.csv")

#%%label feature for PD
import pandas as pd
path = "/Volumes/T7 Shield/TBME_code3.0/"
# Feature = pd.read_csv("/Volumes/T7 Shield/augment/m12activity_long_short_636feature_right_side.csv")
Feature = pd.read_csv(path + "14activity_long_short_636feature_right_side.csv", header=0)
# Feature.rename(columns={'pd_label': 'PatientID'}, inplace=True)

# 将修改后的 DataFrame 重新写入 CSV 文件
# df.to_csv(file_path, index=False)  # 这里的 index=False 表示不写入索引列
label_data = pd.read_csv(path + "Information_Sheet.csv")
label_table = label_data[["PatientID","Severity_Level"]]
label_table = label_table.drop(0)
label_table = label_table.astype(int)
# pd_label = label_data["pd_label"]
# severity_level = label_data["severity_level"]
feature_label = pd.merge(Feature,label_table,on = 'PatientID')
feature_label.to_csv(path + "pd_14activity_feature_label_right_level.csv", index=False)

#%%

sample_feature3 = ['acc_peaks_normal', 'acc_fea_sampley', 'acc_fea_samplex', 'acc_fea_infory', 'acc_fea_inforx', 'acc_peaks_abnormal', 'acc_meandif', 'acc_vardif', 'gyro_peaks_normal', 'gyro_fea_sampley', 'gyro_fea_samplex', 'gyro_fea_infory', 'gyro_fea_inforx', 'gyro_peaks_abnormal', 'gyro_meandif', 'gyro_vardif', 'acc_fea_autoy', 'acc_fea_auto_num', 'acc_t_xyCor', 'acc_t_xzCor', 'acc_t_xaCor', 'acc_t_yzCor', 'acc_t_yaCor', 'acc_t_zaCor', 'acc_f_peakXY1', 'acc_f_peakXY2', 'acc_f_peakXY3', 'acc_f_peakXY4', 'acc_f_peakXY5', 'acc_p_peakXY1', 'acc_p_peakXY2', 'acc_p_peakXY3', 'acc_p_peakXY4', 'acc_p_peakXY5', 'acc_a_peakXY1', 'acc_a_peakXY2', 'acc_a_peakXY3', 'acc_a_peakXY4', 'acc_a_peakXY5', 'acc_f_DF', 'acc_p_energyXYZ', 'acc_p_concent', 'gyro_fea_autoy', 'gyro_fea_auto_num', 'gyro_t_xyCor', 'gyro_t_xzCor', 'gyro_t_xaCor', 'gyro_t_yzCor', 'gyro_t_yaCor', 'gyro_t_zaCor', 'gyro_f_peakXY1', 'gyro_f_peakXY2', 'gyro_f_peakXY3', 'gyro_f_peakXY4', 'gyro_f_peakXY5', 'gyro_p_peakXY1', 'gyro_p_peakXY2', 'gyro_p_peakXY3', 'gyro_p_peakXY4', 'gyro_p_peakXY5', 'gyro_a_peakXY1', 'gyro_a_peakXY2', 'gyro_a_peakXY3', 'gyro_a_peakXY4', 'gyro_a_peakXY5', 'gyro_f_DF', 'gyro_p_energyXYZ', 'gyro_p_concent']
seg_feature = ['acc_t_amp_x', 'acc_t_mean_x', 'acc_t_max_x', 'acc_t_std_x', 'acc_t_var_x', 'acc_t_entr_x', 'acc_t_lgEnergy_x', 'acc_t_sma_x', 'acc_t_interq_x', 'acc_t_skew_x', 'acc_t_kurt_x', 'acc_t_rms_x', 'acc_t_difX_x', 'acc_t_cftor_x', 'acc_f_amp_x', 'acc_f_mean_x', 'acc_f_max_x', 'acc_f_std_x', 'acc_f_var_x', 'acc_f_entr_x', 'acc_f_lgEnergy_x', 'acc_f_sma_x', 'acc_f_interq_x', 'acc_f_skew_x', 'acc_f_kurt_x', 'acc_f_mainX_x', 'acc_f_mainY_x', 'acc_f_subX_x', 'acc_f_subY_x', 'acc_f_difX_x', 'acc_f_rms_x', 'acc_f_difY_x', 'acc_f_cftor_x', 'acc_p_amp_x', 'acc_p_mean_x', 'acc_p_max_x', 'acc_p_std_x', 'acc_p_var_x', 'acc_p_entr_x', 'acc_p_lgEnergy_x', 'acc_p_sma_x', 'acc_p_interq_x', 'acc_p_skew_x', 'acc_p_kurt_x', 'acc_p_rms_x', 'acc_p_mainX_x', 'acc_p_mainY_x', 'acc_p_subX_x', 'acc_p_subY_x', 'acc_p_difX_x', 'acc_p_difY_x', 'acc_p_cftor_x', 'acc_a_amp_x', 'acc_a_mean_x', 'acc_a_max_x', 'acc_a_std_x', 'acc_a_var_x', 'acc_a_entr_x', 'acc_a_lgEnergy_x', 'acc_a_sma_x', 'acc_a_interq_x', 'acc_a_skew_x', 'acc_a_kurt_x', 'acc_a_rms_x', 'acc_a_mainX_x', 'acc_a_mainY_x', 'acc_a_subX_x', 'acc_a_subY_x', 'acc_a_difX_x', 'acc_a_difY_x', 'acc_a_cftor_x', 'acc_t_amp_y', 'acc_t_mean_y', 'acc_t_max_y', 'acc_t_std_y', 'acc_t_var_y', 'acc_t_entr_y', 'acc_t_lgEnergy_y', 'acc_t_sma_y', 'acc_t_interq_y', 'acc_t_skew_y', 'acc_t_kurt_y', 'acc_t_rms_y', 'acc_t_difX_y', 'acc_t_cftor_y', 'acc_f_amp_y', 'acc_f_mean_y', 'acc_f_max_y', 'acc_f_std_y', 'acc_f_var_y', 'acc_f_entr_y', 'acc_f_lgEnergy_y', 'acc_f_sma_y', 'acc_f_interq_y', 'acc_f_skew_y', 'acc_f_kurt_y', 'acc_f_mainX_y', 'acc_f_mainY_y', 'acc_f_subX_y', 'acc_f_subY_y', 'acc_f_difX_y', 'acc_f_rms_y', 'acc_f_difY_y', 'acc_f_cftor_y', 'acc_p_amp_y', 'acc_p_mean_y', 'acc_p_max_y', 'acc_p_std_y', 'acc_p_var_y', 'acc_p_entr_y', 'acc_p_lgEnergy_y', 'acc_p_sma_y', 'acc_p_interq_y', 'acc_p_skew_y', 'acc_p_kurt_y', 'acc_p_rms_y', 'acc_p_mainX_y', 'acc_p_mainY_y', 'acc_p_subX_y', 'acc_p_subY_y', 'acc_p_difX_y', 'acc_p_difY_y', 'acc_p_cftor_y', 'acc_a_amp_y', 'acc_a_mean_y', 'acc_a_max_y', 'acc_a_std_y', 'acc_a_var_y', 'acc_a_entr_y', 'acc_a_lgEnergy_y', 'acc_a_sma_y', 'acc_a_interq_y', 'acc_a_skew_y', 'acc_a_kurt_y', 'acc_a_rms_y', 'acc_a_mainX_y', 'acc_a_mainY_y', 'acc_a_subX_y', 'acc_a_subY_y', 'acc_a_difX_y', 'acc_a_difY_y', 'acc_a_cftor_y', 'acc_t_amp_z', 'acc_t_mean_z', 'acc_t_max_z', 'acc_t_std_z', 'acc_t_var_z', 'acc_t_entr_z', 'acc_t_lgEnergy_z', 'acc_t_sma_z', 'acc_t_interq_z', 'acc_t_skew_z', 'acc_t_kurt_z', 'acc_t_rms_z', 'acc_t_difX_z', 'acc_t_cftor_z', 'acc_f_amp_z', 'acc_f_mean_z', 'acc_f_max_z', 'acc_f_std_z', 'acc_f_var_z', 'acc_f_entr_z', 'acc_f_lgEnergy_z', 'acc_f_sma_z', 'acc_f_interq_z', 'acc_f_skew_z', 'acc_f_kurt_z', 'acc_f_mainX_z', 'acc_f_mainY_z', 'acc_f_subX_z', 'acc_f_subY_z', 'acc_f_difX_z', 'acc_f_rms_z', 'acc_f_difY_z', 'acc_f_cftor_z', 'acc_p_amp_z', 'acc_p_mean_z', 'acc_p_max_z', 'acc_p_std_z', 'acc_p_var_z', 'acc_p_entr_z', 'acc_p_lgEnergy_z', 'acc_p_sma_z', 'acc_p_interq_z', 'acc_p_skew_z', 'acc_p_kurt_z', 'acc_p_rms_z', 'acc_p_mainX_z', 'acc_p_mainY_z', 'acc_p_subX_z', 'acc_p_subY_z', 'acc_p_difX_z', 'acc_p_difY_z', 'acc_p_cftor_z', 'acc_a_amp_z', 'acc_a_mean_z', 'acc_a_max_z', 'acc_a_std_z', 'acc_a_var_z', 'acc_a_entr_z', 'acc_a_lgEnergy_z', 'acc_a_sma_z', 'acc_a_interq_z', 'acc_a_skew_z', 'acc_a_kurt_z', 'acc_a_rms_z', 'acc_a_mainX_z', 'acc_a_mainY_z', 'acc_a_subX_z', 'acc_a_subY_z', 'acc_a_difX_z', 'acc_a_difY_z', 'acc_a_cftor_z', 'acc_t_amp_a', 'acc_t_mean_a', 'acc_t_max_a', 'acc_t_std_a', 'acc_t_var_a', 'acc_t_entr_a', 'acc_t_lgEnergy_a', 'acc_t_sma_a', 'acc_t_interq_a', 'acc_t_skew_a', 'acc_t_kurt_a', 'acc_t_rms_a', 'acc_t_difX_a', 'acc_t_cftor_a', 'acc_f_amp_a', 'acc_f_mean_a', 'acc_f_max_a', 'acc_f_std_a', 'acc_f_var_a', 'acc_f_entr_a', 'acc_f_lgEnergy_a', 'acc_f_sma_a', 'acc_f_interq_a', 'acc_f_skew_a', 'acc_f_kurt_a', 'acc_f_mainX_a', 'acc_f_mainY_a', 'acc_f_subX_a', 'acc_f_subY_a', 'acc_f_difX_a', 'acc_f_rms_a', 'acc_f_difY_a', 'acc_f_cftor_a', 'acc_p_amp_a', 'acc_p_mean_a', 'acc_p_max_a', 'acc_p_std_a', 'acc_p_var_a', 'acc_p_entr_a', 'acc_p_lgEnergy_a', 'acc_p_sma_a', 'acc_p_interq_a', 'acc_p_skew_a', 'acc_p_kurt_a', 'acc_p_rms_a', 'acc_p_mainX_a', 'acc_p_mainY_a', 'acc_p_subX_a', 'acc_p_subY_a', 'acc_p_difX_a', 'acc_p_difY_a', 'acc_p_cftor_a', 'acc_a_amp_a', 'acc_a_mean_a', 'acc_a_max_a', 'acc_a_std_a', 'acc_a_var_a', 'acc_a_entr_a', 'acc_a_lgEnergy_a', 'acc_a_sma_a', 'acc_a_interq_a', 'acc_a_skew_a', 'acc_a_kurt_a', 'acc_a_rms_a', 'acc_a_mainX_a', 'acc_a_mainY_a', 'acc_a_subX_a', 'acc_a_subY_a', 'acc_a_difX_a', 'acc_a_difY_a', 'acc_a_cftor_a', 'gyro_t_amp_x', 'gyro_t_mean_x', 'gyro_t_max_x', 'gyro_t_std_x', 'gyro_t_var_x', 'gyro_t_entr_x', 'gyro_t_lgEnergy_x', 'gyro_t_sma_x', 'gyro_t_interq_x', 'gyro_t_skew_x', 'gyro_t_kurt_x', 'gyro_t_rms_x', 'gyro_t_difX_x', 'gyro_t_cftor_x', 'gyro_f_amp_x', 'gyro_f_mean_x', 'gyro_f_max_x', 'gyro_f_std_x', 'gyro_f_var_x', 'gyro_f_entr_x', 'gyro_f_lgEnergy_x', 'gyro_f_sma_x', 'gyro_f_interq_x', 'gyro_f_skew_x', 'gyro_f_kurt_x', 'gyro_f_mainX_x', 'gyro_f_mainY_x', 'gyro_f_subX_x', 'gyro_f_subY_x', 'gyro_f_difX_x', 'gyro_f_rms_x', 'gyro_f_difY_x', 'gyro_f_cftor_x', 'gyro_p_amp_x', 'gyro_p_mean_x', 'gyro_p_max_x', 'gyro_p_std_x', 'gyro_p_var_x', 'gyro_p_entr_x', 'gyro_p_lgEnergy_x', 'gyro_p_sma_x', 'gyro_p_interq_x', 'gyro_p_skew_x', 'gyro_p_kurt_x', 'gyro_p_rms_x', 'gyro_p_mainX_x', 'gyro_p_mainY_x', 'gyro_p_subX_x', 'gyro_p_subY_x', 'gyro_p_difX_x', 'gyro_p_difY_x', 'gyro_p_cftor_x', 'gyro_a_amp_x', 'gyro_a_mean_x', 'gyro_a_max_x', 'gyro_a_std_x', 'gyro_a_var_x', 'gyro_a_entr_x', 'gyro_a_lgEnergy_x', 'gyro_a_sma_x', 'gyro_a_interq_x', 'gyro_a_skew_x', 'gyro_a_kurt_x', 'gyro_a_rms_x', 'gyro_a_mainX_x', 'gyro_a_mainY_x', 'gyro_a_subX_x', 'gyro_a_subY_x', 'gyro_a_difX_x', 'gyro_a_difY_x', 'gyro_a_cftor_x', 'gyro_t_amp_y', 'gyro_t_mean_y', 'gyro_t_max_y', 'gyro_t_std_y', 'gyro_t_var_y', 'gyro_t_entr_y', 'gyro_t_lgEnergy_y', 'gyro_t_sma_y', 'gyro_t_interq_y', 'gyro_t_skew_y', 'gyro_t_kurt_y', 'gyro_t_rms_y', 'gyro_t_difX_y', 'gyro_t_cftor_y', 'gyro_f_amp_y', 'gyro_f_mean_y', 'gyro_f_max_y', 'gyro_f_std_y', 'gyro_f_var_y', 'gyro_f_entr_y', 'gyro_f_lgEnergy_y', 'gyro_f_sma_y', 'gyro_f_interq_y', 'gyro_f_skew_y', 'gyro_f_kurt_y', 'gyro_f_mainX_y', 'gyro_f_mainY_y', 'gyro_f_subX_y', 'gyro_f_subY_y', 'gyro_f_difX_y', 'gyro_f_rms_y', 'gyro_f_difY_y', 'gyro_f_cftor_y', 'gyro_p_amp_y', 'gyro_p_mean_y', 'gyro_p_max_y', 'gyro_p_std_y', 'gyro_p_var_y', 'gyro_p_entr_y', 'gyro_p_lgEnergy_y', 'gyro_p_sma_y', 'gyro_p_interq_y', 'gyro_p_skew_y', 'gyro_p_kurt_y', 'gyro_p_rms_y', 'gyro_p_mainX_y', 'gyro_p_mainY_y', 'gyro_p_subX_y', 'gyro_p_subY_y', 'gyro_p_difX_y', 'gyro_p_difY_y', 'gyro_p_cftor_y', 'gyro_a_amp_y', 'gyro_a_mean_y', 'gyro_a_max_y', 'gyro_a_std_y', 'gyro_a_var_y', 'gyro_a_entr_y', 'gyro_a_lgEnergy_y', 'gyro_a_sma_y', 'gyro_a_interq_y', 'gyro_a_skew_y', 'gyro_a_kurt_y', 'gyro_a_rms_y', 'gyro_a_mainX_y', 'gyro_a_mainY_y', 'gyro_a_subX_y', 'gyro_a_subY_y', 'gyro_a_difX_y', 'gyro_a_difY_y', 'gyro_a_cftor_y', 'gyro_t_amp_z', 'gyro_t_mean_z', 'gyro_t_max_z', 'gyro_t_std_z', 'gyro_t_var_z', 'gyro_t_entr_z', 'gyro_t_lgEnergy_z', 'gyro_t_sma_z', 'gyro_t_interq_z', 'gyro_t_skew_z', 'gyro_t_kurt_z', 'gyro_t_rms_z', 'gyro_t_difX_z', 'gyro_t_cftor_z', 'gyro_f_amp_z', 'gyro_f_mean_z', 'gyro_f_max_z', 'gyro_f_std_z', 'gyro_f_var_z', 'gyro_f_entr_z', 'gyro_f_lgEnergy_z', 'gyro_f_sma_z', 'gyro_f_interq_z', 'gyro_f_skew_z', 'gyro_f_kurt_z', 'gyro_f_mainX_z', 'gyro_f_mainY_z', 'gyro_f_subX_z', 'gyro_f_subY_z', 'gyro_f_difX_z', 'gyro_f_rms_z', 'gyro_f_difY_z', 'gyro_f_cftor_z', 'gyro_p_amp_z', 'gyro_p_mean_z', 'gyro_p_max_z', 'gyro_p_std_z', 'gyro_p_var_z', 'gyro_p_entr_z', 'gyro_p_lgEnergy_z', 'gyro_p_sma_z', 'gyro_p_interq_z', 'gyro_p_skew_z', 'gyro_p_kurt_z', 'gyro_p_rms_z', 'gyro_p_mainX_z', 'gyro_p_mainY_z', 'gyro_p_subX_z', 'gyro_p_subY_z', 'gyro_p_difX_z', 'gyro_p_difY_z', 'gyro_p_cftor_z', 'gyro_a_amp_z', 'gyro_a_mean_z', 'gyro_a_max_z', 'gyro_a_std_z', 'gyro_a_var_z', 'gyro_a_entr_z', 'gyro_a_lgEnergy_z', 'gyro_a_sma_z', 'gyro_a_interq_z', 'gyro_a_skew_z', 'gyro_a_kurt_z', 'gyro_a_rms_z', 'gyro_a_mainX_z', 'gyro_a_mainY_z', 'gyro_a_subX_z', 'gyro_a_subY_z', 'gyro_a_difX_z', 'gyro_a_difY_z', 'gyro_a_cftor_z', 'gyro_t_amp_a', 'gyro_t_mean_a', 'gyro_t_max_a', 'gyro_t_std_a', 'gyro_t_var_a', 'gyro_t_entr_a', 'gyro_t_lgEnergy_a', 'gyro_t_sma_a', 'gyro_t_interq_a', 'gyro_t_skew_a', 'gyro_t_kurt_a', 'gyro_t_rms_a', 'gyro_t_difX_a', 'gyro_t_cftor_a', 'gyro_f_amp_a', 'gyro_f_mean_a', 'gyro_f_max_a', 'gyro_f_std_a', 'gyro_f_var_a', 'gyro_f_entr_a', 'gyro_f_lgEnergy_a', 'gyro_f_sma_a', 'gyro_f_interq_a', 'gyro_f_skew_a', 'gyro_f_kurt_a', 'gyro_f_mainX_a', 'gyro_f_mainY_a', 'gyro_f_subX_a', 'gyro_f_subY_a', 'gyro_f_difX_a', 'gyro_f_rms_a', 'gyro_f_difY_a', 'gyro_f_cftor_a', 'gyro_p_amp_a', 'gyro_p_mean_a', 'gyro_p_max_a', 'gyro_p_std_a', 'gyro_p_var_a', 'gyro_p_entr_a', 'gyro_p_lgEnergy_a', 'gyro_p_sma_a', 'gyro_p_interq_a', 'gyro_p_skew_a', 'gyro_p_kurt_a', 'gyro_p_rms_a', 'gyro_p_mainX_a', 'gyro_p_mainY_a', 'gyro_p_subX_a', 'gyro_p_subY_a', 'gyro_p_difX_a', 'gyro_p_difY_a', 'gyro_p_cftor_a', 'gyro_a_amp_a', 'gyro_a_mean_a', 'gyro_a_max_a', 'gyro_a_std_a', 'gyro_a_var_a', 'gyro_a_entr_a', 'gyro_a_lgEnergy_a', 'gyro_a_sma_a', 'gyro_a_interq_a', 'gyro_a_skew_a', 'gyro_a_kurt_a', 'gyro_a_rms_a', 'gyro_a_mainX_a', 'gyro_a_mainY_a', 'gyro_a_subX_a', 'gyro_a_subY_a', 'gyro_a_difX_a', 'gyro_a_difY_a', 'gyro_a_cftor_a']
time_feature2 = ['acc_peaks_normal', 'acc_fea_sampley', 'acc_fea_samplex', 'acc_fea_infory', 'acc_fea_inforx', 'acc_peaks_abnormal', 'acc_meandif', 'acc_vardif', 'gyro_peaks_normal', 'gyro_fea_sampley', 'gyro_fea_samplex', 'gyro_fea_infory', 'gyro_fea_inforx', 'gyro_peaks_abnormal', 'gyro_meandif', 'gyro_vardif', 'acc_t_xyCor', 'acc_t_xzCor', 'acc_t_xaCor', 'acc_t_yzCor', 'acc_t_yaCor', 'acc_t_zaCor', 'acc_t_amp_x', 'acc_t_mean_x', 'acc_t_max_x', 'acc_t_std_x', 'acc_t_var_x', 'acc_t_entr_x', 'acc_t_lgEnergy_x', 'acc_t_sma_x', 'acc_t_interq_x', 'acc_t_skew_x', 'acc_t_kurt_x', 'acc_t_rms_x', 'acc_t_difX_x', 'acc_t_cftor_x', 'acc_t_amp_y', 'acc_t_mean_y', 'acc_t_max_y', 'acc_t_std_y', 'acc_t_var_y', 'acc_t_entr_y', 'acc_t_lgEnergy_y', 'acc_t_sma_y', 'acc_t_interq_y', 'acc_t_skew_y', 'acc_t_kurt_y', 'acc_t_rms_y', 'acc_t_difX_y', 'acc_t_cftor_y', 'acc_t_amp_z', 'acc_t_mean_z', 'acc_t_max_z', 'acc_t_std_z', 'acc_t_var_z', 'acc_t_entr_z', 'acc_t_lgEnergy_z', 'acc_t_sma_z', 'acc_t_interq_z', 'acc_t_skew_z', 'acc_t_kurt_z', 'acc_t_rms_z', 'acc_t_difX_z', 'acc_t_cftor_z', 'acc_t_amp_a', 'acc_t_mean_a', 'acc_t_max_a', 'acc_t_std_a', 'acc_t_var_a', 'acc_t_entr_a', 'acc_t_lgEnergy_a', 'acc_t_sma_a', 'acc_t_interq_a', 'acc_t_skew_a', 'acc_t_kurt_a', 'acc_t_rms_a', 'acc_t_difX_a', 'acc_t_cftor_a', 'gyro_t_xyCor', 'gyro_t_xzCor', 'gyro_t_xaCor', 'gyro_t_yzCor', 'gyro_t_yaCor', 'gyro_t_zaCor', 'gyro_t_amp_x', 'gyro_t_mean_x', 'gyro_t_max_x', 'gyro_t_std_x', 'gyro_t_var_x', 'gyro_t_entr_x', 'gyro_t_lgEnergy_x', 'gyro_t_sma_x', 'gyro_t_interq_x', 'gyro_t_skew_x', 'gyro_t_kurt_x', 'gyro_t_rms_x', 'gyro_t_difX_x', 'gyro_t_cftor_x', 'gyro_t_amp_y', 'gyro_t_mean_y', 'gyro_t_max_y', 'gyro_t_std_y', 'gyro_t_var_y', 'gyro_t_entr_y', 'gyro_t_lgEnergy_y', 'gyro_t_sma_y', 'gyro_t_interq_y', 'gyro_t_skew_y', 'gyro_t_kurt_y', 'gyro_t_rms_y', 'gyro_t_difX_y', 'gyro_t_cftor_y', 'gyro_t_amp_z', 'gyro_t_mean_z', 'gyro_t_max_z', 'gyro_t_std_z', 'gyro_t_var_z', 'gyro_t_entr_z', 'gyro_t_lgEnergy_z', 'gyro_t_sma_z', 'gyro_t_interq_z', 'gyro_t_skew_z', 'gyro_t_kurt_z', 'gyro_t_rms_z', 'gyro_t_difX_z', 'gyro_t_cftor_z', 'gyro_t_amp_a', 'gyro_t_mean_a', 'gyro_t_max_a', 'gyro_t_std_a', 'gyro_t_var_a', 'gyro_t_entr_a', 'gyro_t_lgEnergy_a', 'gyro_t_sma_a', 'gyro_t_interq_a', 'gyro_t_skew_a', 'gyro_t_kurt_a', 'gyro_t_rms_a', 'gyro_t_difX_a', 'gyro_t_cftor_a']
frequency_feature = ['acc_f_peakXY1', 'acc_f_peakXY2', 'acc_f_peakXY3', 'acc_f_peakXY4', 'acc_f_peakXY5', 'acc_f_DF', 'acc_f_amp_x', 'acc_f_mean_x', 'acc_f_max_x', 'acc_f_std_x', 'acc_f_var_x', 'acc_f_entr_x', 'acc_f_lgEnergy_x', 'acc_f_sma_x', 'acc_f_interq_x', 'acc_f_skew_x', 'acc_f_kurt_x', 'acc_f_mainX_x', 'acc_f_mainY_x', 'acc_f_subX_x', 'acc_f_subY_x', 'acc_f_difX_x', 'acc_f_rms_x', 'acc_f_difY_x', 'acc_f_cftor_x', 'acc_f_amp_y', 'acc_f_mean_y', 'acc_f_max_y', 'acc_f_std_y', 'acc_f_var_y', 'acc_f_entr_y', 'acc_f_lgEnergy_y', 'acc_f_sma_y', 'acc_f_interq_y', 'acc_f_skew_y', 'acc_f_kurt_y', 'acc_f_mainX_y', 'acc_f_mainY_y', 'acc_f_subX_y', 'acc_f_subY_y', 'acc_f_difX_y', 'acc_f_rms_y', 'acc_f_difY_y', 'acc_f_cftor_y', 'acc_f_amp_z', 'acc_f_mean_z', 'acc_f_max_z', 'acc_f_std_z', 'acc_f_var_z', 'acc_f_entr_z', 'acc_f_lgEnergy_z', 'acc_f_sma_z', 'acc_f_interq_z', 'acc_f_skew_z', 'acc_f_kurt_z', 'acc_f_mainX_z', 'acc_f_mainY_z', 'acc_f_subX_z', 'acc_f_subY_z', 'acc_f_difX_z', 'acc_f_rms_z', 'acc_f_difY_z', 'acc_f_cftor_z', 'acc_f_amp_a', 'acc_f_mean_a', 'acc_f_max_a', 'acc_f_std_a', 'acc_f_var_a', 'acc_f_entr_a', 'acc_f_lgEnergy_a', 'acc_f_sma_a', 'acc_f_interq_a', 'acc_f_skew_a', 'acc_f_kurt_a', 'acc_f_mainX_a', 'acc_f_mainY_a', 'acc_f_subX_a', 'acc_f_subY_a', 'acc_f_difX_a', 'acc_f_rms_a', 'acc_f_difY_a', 'acc_f_cftor_a', 'gyro_f_peakXY1', 'gyro_f_peakXY2', 'gyro_f_peakXY3', 'gyro_f_peakXY4', 'gyro_f_peakXY5', 'gyro_f_DF', 'gyro_f_amp_x', 'gyro_f_mean_x', 'gyro_f_max_x', 'gyro_f_std_x', 'gyro_f_var_x', 'gyro_f_entr_x', 'gyro_f_lgEnergy_x', 'gyro_f_sma_x', 'gyro_f_interq_x', 'gyro_f_skew_x', 'gyro_f_kurt_x', 'gyro_f_mainX_x', 'gyro_f_mainY_x', 'gyro_f_subX_x', 'gyro_f_subY_x', 'gyro_f_difX_x', 'gyro_f_rms_x', 'gyro_f_difY_x', 'gyro_f_cftor_x', 'gyro_f_amp_y', 'gyro_f_mean_y', 'gyro_f_max_y', 'gyro_f_std_y', 'gyro_f_var_y', 'gyro_f_entr_y', 'gyro_f_lgEnergy_y', 'gyro_f_sma_y', 'gyro_f_interq_y', 'gyro_f_skew_y', 'gyro_f_kurt_y', 'gyro_f_mainX_y', 'gyro_f_mainY_y', 'gyro_f_subX_y', 'gyro_f_subY_y', 'gyro_f_difX_y', 'gyro_f_rms_y', 'gyro_f_difY_y', 'gyro_f_cftor_y', 'gyro_f_amp_z', 'gyro_f_mean_z', 'gyro_f_max_z', 'gyro_f_std_z', 'gyro_f_var_z', 'gyro_f_entr_z', 'gyro_f_lgEnergy_z', 'gyro_f_sma_z', 'gyro_f_interq_z', 'gyro_f_skew_z', 'gyro_f_kurt_z', 'gyro_f_mainX_z', 'gyro_f_mainY_z', 'gyro_f_subX_z', 'gyro_f_subY_z', 'gyro_f_difX_z', 'gyro_f_rms_z', 'gyro_f_difY_z', 'gyro_f_cftor_z', 'gyro_f_amp_a', 'gyro_f_mean_a', 'gyro_f_max_a', 'gyro_f_std_a', 'gyro_f_var_a', 'gyro_f_entr_a', 'gyro_f_lgEnergy_a', 'gyro_f_sma_a', 'gyro_f_interq_a', 'gyro_f_skew_a', 'gyro_f_kurt_a', 'gyro_f_mainX_a', 'gyro_f_mainY_a', 'gyro_f_subX_a', 'gyro_f_subY_a', 'gyro_f_difX_a', 'gyro_f_rms_a', 'gyro_f_difY_a', 'gyro_f_cftor_a']
autocorr_feature = ['acc_fea_autoy', 'acc_fea_auto_num', 'acc_a_peakXY1', 'acc_a_peakXY2', 'acc_a_peakXY3', 'acc_a_peakXY4', 'acc_a_peakXY5', 'acc_a_amp_x', 'acc_a_mean_x', 'acc_a_max_x', 'acc_a_std_x', 'acc_a_var_x', 'acc_a_entr_x', 'acc_a_lgEnergy_x', 'acc_a_sma_x', 'acc_a_interq_x', 'acc_a_skew_x', 'acc_a_kurt_x', 'acc_a_rms_x', 'acc_a_mainX_x', 'acc_a_mainY_x', 'acc_a_subX_x', 'acc_a_subY_x', 'acc_a_difX_x', 'acc_a_difY_x', 'acc_a_cftor_x', 'acc_a_amp_y', 'acc_a_mean_y', 'acc_a_max_y', 'acc_a_std_y', 'acc_a_var_y', 'acc_a_entr_y', 'acc_a_lgEnergy_y', 'acc_a_sma_y', 'acc_a_interq_y', 'acc_a_skew_y', 'acc_a_kurt_y', 'acc_a_rms_y', 'acc_a_mainX_y', 'acc_a_mainY_y', 'acc_a_subX_y', 'acc_a_subY_y', 'acc_a_difX_y', 'acc_a_difY_y', 'acc_a_cftor_y', 'acc_a_amp_z', 'acc_a_mean_z', 'acc_a_max_z', 'acc_a_std_z', 'acc_a_var_z', 'acc_a_entr_z', 'acc_a_lgEnergy_z', 'acc_a_sma_z', 'acc_a_interq_z', 'acc_a_skew_z', 'acc_a_kurt_z', 'acc_a_rms_z', 'acc_a_mainX_z', 'acc_a_mainY_z', 'acc_a_subX_z', 'acc_a_subY_z', 'acc_a_difX_z', 'acc_a_difY_z', 'acc_a_cftor_z', 'acc_a_amp_a', 'acc_a_mean_a', 'acc_a_max_a', 'acc_a_std_a', 'acc_a_var_a', 'acc_a_entr_a', 'acc_a_lgEnergy_a', 'acc_a_sma_a', 'acc_a_interq_a', 'acc_a_skew_a', 'acc_a_kurt_a', 'acc_a_rms_a', 'acc_a_mainX_a', 'acc_a_mainY_a', 'acc_a_subX_a', 'acc_a_subY_a', 'acc_a_difX_a', 'acc_a_difY_a', 'acc_a_cftor_a', 'gyro_fea_autoy', 'gyro_fea_auto_num', 'gyro_a_peakXY1', 'gyro_a_peakXY2', 'gyro_a_peakXY3', 'gyro_a_peakXY4', 'gyro_a_peakXY5', 'gyro_a_amp_x', 'gyro_a_mean_x', 'gyro_a_max_x', 'gyro_a_std_x', 'gyro_a_var_x', 'gyro_a_entr_x', 'gyro_a_lgEnergy_x', 'gyro_a_sma_x', 'gyro_a_interq_x', 'gyro_a_skew_x', 'gyro_a_kurt_x', 'gyro_a_rms_x', 'gyro_a_mainX_x', 'gyro_a_mainY_x', 'gyro_a_subX_x', 'gyro_a_subY_x', 'gyro_a_difX_x', 'gyro_a_difY_x', 'gyro_a_cftor_x', 'gyro_a_amp_y', 'gyro_a_mean_y', 'gyro_a_max_y', 'gyro_a_std_y', 'gyro_a_var_y', 'gyro_a_entr_y', 'gyro_a_lgEnergy_y', 'gyro_a_sma_y', 'gyro_a_interq_y', 'gyro_a_skew_y', 'gyro_a_kurt_y', 'gyro_a_rms_y', 'gyro_a_mainX_y', 'gyro_a_mainY_y', 'gyro_a_subX_y', 'gyro_a_subY_y', 'gyro_a_difX_y', 'gyro_a_difY_y', 'gyro_a_cftor_y', 'gyro_a_amp_z', 'gyro_a_mean_z', 'gyro_a_max_z', 'gyro_a_std_z', 'gyro_a_var_z', 'gyro_a_entr_z', 'gyro_a_lgEnergy_z', 'gyro_a_sma_z', 'gyro_a_interq_z', 'gyro_a_skew_z', 'gyro_a_kurt_z', 'gyro_a_rms_z', 'gyro_a_mainX_z', 'gyro_a_mainY_z', 'gyro_a_subX_z', 'gyro_a_subY_z', 'gyro_a_difX_z', 'gyro_a_difY_z', 'gyro_a_cftor_z', 'gyro_a_amp_a', 'gyro_a_mean_a', 'gyro_a_max_a', 'gyro_a_std_a', 'gyro_a_var_a', 'gyro_a_entr_a', 'gyro_a_lgEnergy_a', 'gyro_a_sma_a', 'gyro_a_interq_a', 'gyro_a_skew_a', 'gyro_a_kurt_a', 'gyro_a_rms_a', 'gyro_a_mainX_a', 'gyro_a_mainY_a', 'gyro_a_subX_a', 'gyro_a_subY_a', 'gyro_a_difX_a', 'gyro_a_difY_a', 'gyro_a_cftor_a']
spec_feature = ['acc_p_peakXY1', 'acc_p_peakXY2', 'acc_p_peakXY3', 'acc_p_peakXY4', 'acc_p_peakXY5', 'acc_p_energyXYZ', 'acc_p_concent', 'acc_p_amp_x', 'acc_p_mean_x', 'acc_p_max_x', 'acc_p_std_x', 'acc_p_var_x', 'acc_p_entr_x', 'acc_p_lgEnergy_x', 'acc_p_sma_x', 'acc_p_interq_x', 'acc_p_skew_x', 'acc_p_kurt_x', 'acc_p_rms_x', 'acc_p_mainX_x', 'acc_p_mainY_x', 'acc_p_subX_x', 'acc_p_subY_x', 'acc_p_difX_x', 'acc_p_difY_x', 'acc_p_cftor_x', 'acc_p_amp_y', 'acc_p_mean_y', 'acc_p_max_y', 'acc_p_std_y', 'acc_p_var_y', 'acc_p_entr_y', 'acc_p_lgEnergy_y', 'acc_p_sma_y', 'acc_p_interq_y', 'acc_p_skew_y', 'acc_p_kurt_y', 'acc_p_rms_y', 'acc_p_mainX_y', 'acc_p_mainY_y', 'acc_p_subX_y', 'acc_p_subY_y', 'acc_p_difX_y', 'acc_p_difY_y', 'acc_p_cftor_y', 'acc_p_amp_z', 'acc_p_mean_z', 'acc_p_max_z', 'acc_p_std_z', 'acc_p_var_z', 'acc_p_entr_z', 'acc_p_lgEnergy_z', 'acc_p_sma_z', 'acc_p_interq_z', 'acc_p_skew_z', 'acc_p_kurt_z', 'acc_p_rms_z', 'acc_p_mainX_z', 'acc_p_mainY_z', 'acc_p_subX_z', 'acc_p_subY_z', 'acc_p_difX_z', 'acc_p_difY_z', 'acc_p_cftor_z', 'acc_p_amp_a', 'acc_p_mean_a', 'acc_p_max_a', 'acc_p_std_a', 'acc_p_var_a', 'acc_p_entr_a', 'acc_p_lgEnergy_a', 'acc_p_sma_a', 'acc_p_interq_a', 'acc_p_skew_a', 'acc_p_kurt_a', 'acc_p_rms_a', 'acc_p_mainX_a', 'acc_p_mainY_a', 'acc_p_subX_a', 'acc_p_subY_a', 'acc_p_difX_a', 'acc_p_difY_a', 'acc_p_cftor_a', 'gyro_p_peakXY1', 'gyro_p_peakXY2', 'gyro_p_peakXY3', 'gyro_p_peakXY4', 'gyro_p_peakXY5', 'gyro_p_energyXYZ', 'gyro_p_concent', 'gyro_p_amp_x', 'gyro_p_mean_x', 'gyro_p_max_x', 'gyro_p_std_x', 'gyro_p_var_x', 'gyro_p_entr_x', 'gyro_p_lgEnergy_x', 'gyro_p_sma_x', 'gyro_p_interq_x', 'gyro_p_skew_x', 'gyro_p_kurt_x', 'gyro_p_rms_x', 'gyro_p_mainX_x', 'gyro_p_mainY_x', 'gyro_p_subX_x', 'gyro_p_subY_x', 'gyro_p_difX_x', 'gyro_p_difY_x', 'gyro_p_cftor_x', 'gyro_p_amp_y', 'gyro_p_mean_y', 'gyro_p_max_y', 'gyro_p_std_y', 'gyro_p_var_y', 'gyro_p_entr_y', 'gyro_p_lgEnergy_y', 'gyro_p_sma_y', 'gyro_p_interq_y', 'gyro_p_skew_y', 'gyro_p_kurt_y', 'gyro_p_rms_y', 'gyro_p_mainX_y', 'gyro_p_mainY_y', 'gyro_p_subX_y', 'gyro_p_subY_y', 'gyro_p_difX_y', 'gyro_p_difY_y', 'gyro_p_cftor_y', 'gyro_p_amp_z', 'gyro_p_mean_z', 'gyro_p_max_z', 'gyro_p_std_z', 'gyro_p_var_z', 'gyro_p_entr_z', 'gyro_p_lgEnergy_z', 'gyro_p_sma_z', 'gyro_p_interq_z', 'gyro_p_skew_z', 'gyro_p_kurt_z', 'gyro_p_rms_z', 'gyro_p_mainX_z', 'gyro_p_mainY_z', 'gyro_p_subX_z', 'gyro_p_subY_z', 'gyro_p_difX_z', 'gyro_p_difY_z', 'gyro_p_cftor_z', 'gyro_p_amp_a', 'gyro_p_mean_a', 'gyro_p_max_a', 'gyro_p_std_a', 'gyro_p_var_a', 'gyro_p_entr_a', 'gyro_p_lgEnergy_a', 'gyro_p_sma_a', 'gyro_p_interq_a', 'gyro_p_skew_a', 'gyro_p_kurt_a', 'gyro_p_rms_a', 'gyro_p_mainX_a', 'gyro_p_mainY_a', 'gyro_p_subX_a', 'gyro_p_subY_a', 'gyro_p_difX_a', 'gyro_p_difY_a', 'gyro_p_cftor_a']
selected_features = ['gyro_fea_autoy', 'acc_fea_auto_num', 'gyro_fea_auto_num', 'acc_peaks_abnormal', 'acc_fea_autoy', 'acc_fea_samplex', 'gyro_fea_samplex', 'acc_peaks_normal', 'gyro_peaks_abnormal', 'gyro_peaks_normal', 'acc_f_mainX_z', 'gyro_t_amp_y', 'acc_a_subY_x', 'acc_a_peakXY3', 'acc_t_zaCor', 'acc_t_xaCor', 'gyro_a_amp_x', 'acc_f_skew_z', 'acc_t_max_a', 'gyro_fea_infory', 'acc_p_interq_x', 'acc_p_lgEnergy_x', 'acc_f_cftor_z', 'gyro_f_skew_x', 'acc_a_std_z', 'acc_t_amp_x', 'acc_f_interq_x', 'gyro_a_mainY_y', 'acc_t_max_x', 'gyro_a_cftor_y', 'acc_f_sma_x']

print((sample_feature3))   #62 features -> 68 feature
print(seg_feature)  #574  -> 568 feature
print(time_feature2)
print(frequency_feature)
print(autocorr_feature)
print(spec_feature)

selected_features = []
print(label_table)
print(Feature)
