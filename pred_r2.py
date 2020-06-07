from sklearn import datasets
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_squared_error
from sklearn.metrics import median_absolute_error
from sklearn.metrics import mean_squared_log_error
from sklearn.metrics import mean_absolute_error
import numpy as np
from sklearn.metrics import r2_score
import pandas as pd
from scipy.stats import pearsonr
from scipy.stats import spearmanr
from sklearn.metrics import roc_auc_score
from sklearn.utils.multiclass import type_of_target
import sys

def cal_pccs(x, y):
    """
    warning: data format must be narray
    :param x: Variable 1
    :param y: The variable 2
    :param n: The number of elements in x
    :return: pccs
    """
    x = np.array(x, dtype=float)
    y = np.array(y, dtype=float)
 
    n = len(x)
    sum_xy = np.sum(np.sum(x*y))
    sum_x = np.sum(np.sum(x))
    sum_y = np.sum(np.sum(y))
    sum_x2 = np.sum(np.sum(x*x))
    sum_y2 = np.sum(np.sum(y*y))
    pcc = (n*sum_xy-sum_x*sum_y)/np.sqrt((n*sum_x2-sum_x*sum_x)*(n*sum_y2-sum_y*sum_y))
    return pcc

def cal_rank(x, y):
    n = len(x)
    f=n*(n**2-1)
#    print (f)
    d = np.array(x)-np.array(y)
#    print (d)
#    print (d**2)
    d2 = np.sum(d**2)
#    print (d2)
    return 1-6*d2/f

file=str(sys.argv[1])
print (file)

ytrue = pd.read_csv('test_bdz.csv')
#ypred = pd.read_csv('pred_moe_rnd.txt3')
ypred = pd.read_csv(file)

ytrue.head()
ypred.head()

vtrue=[]
vpred=[]
for idx, item in ytrue.iterrows():
    smi = item.smiles
    logS = item.logS
#    print (smi, logS)
    vtrue.append(logS)

for idx, item in ypred.iterrows():
    smi = item.smiles
    logS = item.logS
#    print (smi, logS)
    vpred.append(logS)


print (vtrue)
print (vpred)



print ("mean_squared_error (MSE)")
print(mean_squared_error(vtrue, vpred))

print ("RMSE")
print('All rmseResult', np.sqrt(mean_squared_error(vtrue, vpred)))

print ("mean_absolute_error (MAE)")
print('All maeResult', np.mean(np.abs(np.array(vtrue)-np.array(vpred))))

print ("r2_score")
print (r2_score(vtrue, vpred))

print ("pearsonr_BPU")
print (pearsonr(vtrue[:12], vpred[:12]))
print ('BPU pearsonrResult',cal_pccs(vtrue[:12], vpred[:12]))
print (spearmanr(vtrue[:12], vpred[:12]))

print ("pearsonr_BDZ")
print (pearsonr(vtrue[12:31], vpred[12:31]))
print ('BDZ pearsonrResult',cal_pccs(vtrue[12:31], vpred[12:31]))
print (spearmanr(vtrue[12:31], vpred[12:31]))

print ("pearsonr_all")
print (pearsonr(vtrue,vpred))
print ('ALL pearsonrResult',cal_pccs(vtrue,vpred))
print (spearmanr(vtrue,vpred))
