import os
import sys
import numpy as np
import pandas as pd
from sklearn.metrics import average_precision_score, roc_auc_score
from loda import *
from loda_support import *
from ensemble_support import *

def read_dataset(filename):
    df = pd.read_csv(filename)
    pt_ids = np.array(df['point.id'])
    labels = np.array(df['ground.truth'])
    labels = [0 if labels[i] == 'nominal' else 1 for i in range(len(labels))]
    labels = np.array(labels)
    X = np.array(df.iloc[:,6:len(df.columns)])
    return X, labels

def compute_statistics(scores, labels):
    avg_precision = average_precision_score(labels, scores)
    auc = roc_auc_score(labels, scores)
    return auc, avg_precision

def run_LODA(X, labels):
    lodares = loda(X, sparsity=0.3, mink=1, maxk=10)
    model = generate_model_from_loda_result(lodares, X, labels)
    anoms, lbls, _, _, _, detector_scores, detector_wts = (
            model.anoms, model.lbls,
            model.w, model.hists, model.hpdfs, model.nlls, model.proj_wts
        )
    
    return compute_statistics(model.anom_score, labels)
    
def run_for_consolidated_benchmarks(in_dir, out_file, num_runs=50):
    fw=open(out_file,'w')
    list_files = os.listdir(in_dir)
    for in_file in list_files:
        X, labels = read_dataset(os.path.join(in_dir,in_file))
        auc_arr = []
        ap_arr = []
        for i in range(num_runs):
            if(i%5==0):
                print i
            auc, ap = run_LODA(X, labels)
            auc_arr.append(auc)
            ap_arr.append(ap)
        fw.write(str(in_file)+","+str(np.mean(auc_arr))+","+str(np.std(auc_arr))+","+str(np.mean(ap_arr))+","+str(np.std(ap_arr))+"\n")
    fw.close()
    
in_dir = "/nfshome/SHARED/BENCHMARK_HighDim_DATA/Consolidated"
out_file = "/nfshome/hlamba/HighDim_OL/Results/LODA_50.txt"
run_for_consolidated_benchmarks(in_dir,out_file)
    

