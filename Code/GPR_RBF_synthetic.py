#The following code is for gaussian process regression with k-fold cv for 100 different seed values and reports the average rmse along with standard deviation
#This code works with synthetic data

import numpy as np
from sklearn.preprocessing import normalize #normalize is not used in the code, but can be tried
from sklearn.utils import shuffle 
import math 

import concurrent.futures
import time

from sklearn.gaussian_process import GaussianProcessRegressor
from sklearn.gaussian_process.kernels import RBF,ConstantKernel, WhiteKernel



import csv
import itertools 
import pandas as pd

global num_features
global crossvalidate_k 

global test_sample_index_list 

global seeds
global length_values

global splitpoints


global seed_lengthval_pair_arr
global seed_start
global seed_step
global final_seed

global best_length_values



test_sample_index_list = []
train_pure_synthetic_index_list = []
splitpoints = []

crossvalidate_k = 7 #number of folds for cross-validation


mydata=pd.read_csv('MLS-LA-LB-LC-LD-Real.csv') #add real datafile name here
mydata=mydata.to_numpy()

num_features = len(mydata[0])-1

features = mydata[:,0:num_features]
output = mydata[:,num_features:]

norm_features = features 


mydata_withsynthetic=pd.read_csv('MLS-LA-LB-LC-LD-Real-Synthetic80svm.csv') #add (real plus synthetic) datafile name here
mydata_withsynthetic=mydata_withsynthetic.to_numpy()


pure_synthetic_features = mydata_withsynthetic[:,0:num_features]
pure_synthetic_output = mydata_withsynthetic[:,num_features:]

#norm_features = normalize(features, axis=0, norm='max') #normalize the features using max norm

#print(norm_features)
#print(mydata)

num_samples = len(mydata)
#print(num_samples)

num_pure_synthetic_samples = len(mydata_withsynthetic)

seed_start = 0
seed_end = 10000 #please change it to 10000
seed_step = 100

seeds = np.arange(seed_start,seed_end,seed_step) 
#print(seeds)

final_seed = (seeds[len(seeds)-1])

test_rmses = np.zeros(len(seeds)) 
train_rmses = np.zeros(len(seeds))

best_length_values = 1.0*np.arange(0,len(seeds),1)


length_values = [0.01, 0.1, 1, 2, 3, 5, 10, 20, 50, 100] 

 
seed_lengthval_pair = []

for seed in seeds:
    for length_val in length_values:
        seed_lengthval_pair.append([seed,length_val])


seed_lengthval__pair_arr = np.array(seed_lengthval_pair)
                                




estind_values = np.arange(len(length_values))

seed_indices = np.arange(len(seeds))



def kfoldcv(seed,lengthval):
    start = time.time()
    
    np.random.seed(int(seed))
    
    sample_index = np.arange(num_samples)
    #print(sampleindex)

    shuffled_indices = shuffle(sample_index)
    #print(shuffled_indices)

    
    test_proportion = 0.2  #set the proportion of test samples 
    num_test = int(test_proportion * num_samples) 
    #print(num_test)

    test_sample_index = shuffled_indices[:num_test]
    
    test_sample_index_list.append(test_sample_index)
    #print(test_sample_index)
    #print(len(test_sample_index))

    #split the remaining part into ten folds 
    train_validate_index = shuffled_indices[num_test:]
    #num_train_validate_samples = len(train_validate_index)
    #print(num_train_validate_samples)

    
    num_synthetic_samples = len(mydata_withsynthetic) - len(mydata) #note: the new file contains original data and synthetic data 
    new_synthetic_indices = np.arange(num_samples, num_samples+num_synthetic_samples,1)
    #print(new_synthetic_indices)
    
    train_validate_puresynthetic_index = np.concatenate( (train_validate_index, new_synthetic_indices) , axis=None)

    
    
    #print ('starting kfoldcv')
    #num_estimators_arg = num_estimators_values[estind]
    #num_estimators_arg = numest

    length_val_arg = lengthval
    
    
    #train_validate_puresynthetic_index = args[1]
    #test_sample_index = args[2]
    
    fold_length = int(math.ceil((1.0*len(train_validate_puresynthetic_index))/crossvalidate_k))
    splitpoints = np.arange(0,len(train_validate_puresynthetic_index),fold_length)
    
    rmses = np.zeros(crossvalidate_k) 
    for i in np.arange(len(splitpoints)):
        #print(i)
        if i<len(splitpoints)-1:
            validate_index = train_validate_puresynthetic_index[splitpoints[i]:splitpoints[i+1]]
        else:
            validate_index = train_validate_puresynthetic_index[splitpoints[i]:]
        #train_index = train_validate_puresynthetic_index[~validate_index] #bala: need to check # x for x in train_validate_puresynthetic_index if x not in validate_index]
        train_index = [x for x in train_validate_puresynthetic_index if x not in validate_index]
        #print(validate_index)
        #print(len(validate_index))
        #print(train_index)
        #print(len(train_index))
        #print('**************************')


        train_feat = pure_synthetic_features[train_index]
        train_feat = [np.reshape(x, (num_features, )) for x in train_feat]

        train_out = pure_synthetic_output[train_index]
        train_out = np.reshape(train_out, (len(train_out),))
        #test_data = mydata[39:,:]
        #print(train_data)

        #print('train')
        #print(i,np.shape(train_feat), np.shape(train_out))

        validate_feat = pure_synthetic_features[validate_index]
        validate_feat = [np.reshape(x, (num_features, )) for x in validate_feat]

        validate_out = pure_synthetic_output[validate_index]
        validate_out = np.reshape(validate_out, (len(validate_out),))
        #test_data = mydata[39:,:]
        #print(train_data)

        #print('validate')
        #print(i,np.shape(validate_feat), np.shape(validate_out))

        #print(len(validate_samples))

         
        
        kernel = ConstantKernel() * RBF(length_scale=length_val_arg) + WhiteKernel()  
        gpr = GaussianProcessRegressor(kernel=kernel, alpha=1e-10, optimizer='fmin_l_bfgs_b', n_restarts_optimizer=0, normalize_y=False, copy_X_train=True,random_state=42) 
        regr=gpr

        regr.fit(train_feat, train_out)
        #print(regr.feature_importances_)
        #print(regr.feature_importances_)

        #pred = regr.predict(train_feat)
        #tmp = ((x,y) for x,y in zip(pred, train_out))
        #print(list(tmp))


        pred = regr.predict(validate_feat)
        #tmp = ((x,y) for x,y in zip(pred, validate_out))
        #print(list(tmp))

        mse = sum((x-y)*(x-y) for x,y in zip(pred,validate_out))/len(validate_feat)
        rmse = np.sqrt(mse)

        #print(i,rmse)
        #print('^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^')

        rmses[i] = rmse

    avg_rmse = np.average(rmses)
        
    return seed,lengthval,time.time() - start,avg_rmse




def compute_testrmse(seed,best_length_val):
    start = time.time()
    
    np.random.seed(int(seed))
    
    sample_index = np.arange(num_samples)
    #print(sampleindex)

    shuffled_indices = shuffle(sample_index)
    #print(shuffled_indices)
    
    test_proportion = 0.2  #set the proportion of test samples 
    num_test = int(test_proportion * num_samples) 
    #print(num_test)

    test_sample_index = shuffled_indices[:num_test]
    
    test_sample_index_list.append(test_sample_index)
    #print(test_sample_index)
    #print(len(test_sample_index))

    #split the remaining part into ten folds 
    train_validate_index = shuffled_indices[num_test:]
    #num_train_validate_samples = len(train_validate_index)
    #print(num_train_validate_samples)
    
    #training set 
    num_synthetic_samples = len(mydata_withsynthetic) - len(mydata) #note: the new file contains original data and synthetic data 
    new_synthetic_indices = np.arange(num_samples, num_samples+num_synthetic_samples,1)
    #print(new_synthetic_indices)
    
    train_validate_puresynthetic_index = np.concatenate( (train_validate_index, new_synthetic_indices) , axis=None)
    
    #print('run:%d num estimators: %d avg. rmse: %f' %(run,num_estimators_arg, avg_rmse))
    
    #training set 
    final_train_feat = pure_synthetic_features[train_validate_puresynthetic_index]
    final_train_feat = [np.reshape(x, (num_features, )) for x in final_train_feat]

    final_train_out = pure_synthetic_output[train_validate_puresynthetic_index]
    final_train_out = np.reshape(final_train_out, (len(final_train_out),))
    
    #test set 
    final_test_feat = norm_features[test_sample_index]
    final_test_feat = [np.reshape(x, (num_features, )) for x in final_test_feat]

    final_test_out = output[test_sample_index]
    final_test_out = np.reshape(final_test_out, (len(final_test_out),))


    final_best_length_val = best_length_val
 
    
    

    kernel = ConstantKernel() * RBF(length_scale=final_best_length_val)  + WhiteKernel()
    gpr = GaussianProcessRegressor(kernel=kernel, alpha=1e-10, optimizer='fmin_l_bfgs_b', n_restarts_optimizer=0, normalize_y=False, copy_X_train=True,random_state=42)
    final_regr=gpr


    final_regr.fit(final_train_feat, final_train_out)

    final_regr.fit(final_train_feat, final_train_out)
    #print(regr.feature_importances_)

    tr_pred = final_regr.predict(final_train_feat)
    final_tr_mse = sum((x-y)*(x-y) for x,y in zip(tr_pred,final_train_out))/len(final_train_feat)
    final_tr_rmse = np.sqrt(final_tr_mse)

    #tmp = ((x,y) for x,y in zip(pred, train_out))
    #print(list(tmp))

    #pred = final_regr.predict()
    pred = final_regr.predict(final_test_feat)
    #tmp = ((x,y) for x,y in zip(pred, final_test_out))
    #print(list(tmp))

    absError = abs(pred-final_test_out)


    final_mse = sum((x-y)*(x-y) for x,y in zip(pred,final_test_out))/len(final_test_feat)
    final_rmse = np.sqrt(final_mse)

    with open('MLS-LA-LB-LC-LD-Real-Synthetic-out.csv', 'a') as csvFile:
        writer = csv.writer(csvFile)
        writer.writerows(zip(itertools.repeat(seed),test_sample_index, pred, final_test_out, absError))
    csvFile.close()



    return seed,best_length_val,time.time() - start, final_rmse, final_tr_rmse




def main():
    avg_rmse_ret = []
    lengthval_ret = [] 
    

   
    
    for seed in seeds: 
        avg_rmse_ret.append([])
        lengthval_ret.append([])    
        
        
    start = time.time()
    
    with concurrent.futures.ProcessPoolExecutor() as executor:
         for seed,lengthval,time_ret,avg_rmse in executor.map(kfoldcv, seed_lengthval__pair_arr[:,0], seed_lengthval__pair_arr[:,1] ):
             seed_index = int((seed-seed_start)/seed_step)
             avg_rmse_ret[seed_index].append(avg_rmse)
             lengthval_ret[seed_index].append(lengthval)
             
             print('seed:%f lengthval: %f time: %f avg_rmse: %f' %(seed, lengthval,time_ret,avg_rmse), flush=True)
    print('k fold cv completed ! Time taken: %f seconds' %(time.time()-start), flush=True )
    

    for seed in seeds: 
        seed_index = int((seed-seed_start)/seed_step)
        tmp = avg_rmse_ret[seed_index]
        #print(tmp)
        argminind=np.argmin(tmp)
        #print(argminind)
        
        lengthlist = lengthval_ret[seed_index]
        best_length_values[seed_index]= (lengthlist[np.argmin(tmp)])
        
        
        print('seed:%d argmin lengthval :%f' %(seed,best_length_values[seed_index]), flush=True)



    start = time.time()        
    with concurrent.futures.ProcessPoolExecutor() as executor:
         for seed,best_length_val,time_ret,test_rmse,train_rmse in executor.map(compute_testrmse, seeds, best_length_values):
             print('seed:%f best length val:%f time: %f test_rmse: %f train rmse: %f' %(seed,best_length_val,time_ret,test_rmse, train_rmse), flush=True)
             seed_index = int((seed-seed_start)/seed_step)
             test_rmses[seed_index]=test_rmse
             train_rmses[seed_index]=train_rmse
    print('Test rmse computed ! Time taken: %f seconds' %(time.time()-start), flush=True )

    print('Test rmse: mean+/-std.dev of %d runs: %f +/- %f' %(len(seeds),np.average(test_rmses), np.std(test_rmses)) , flush=True)
    print('Train rmse: mean+/-std.dev of %d runs: %f +/- %f' %(len(seeds),np.average(train_rmses), np.std(train_rmses)) , flush=True)
    

if __name__ == '__main__':
    start = time.time()
    main()
    total_time = time.time() - start

    print('total time after completion: %f seconds' %(total_time), flush=True)