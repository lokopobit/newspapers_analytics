# -*- coding: utf-8 -*-
"""
Created on Mon Jul 20 18:14:06 2020

@author: lokopobit
"""

#
import pandas as pd

#
import clean_and_store
import execute_newsplease_cli
import auxiliar_functions as auxFuns

execute_multiprocess = True
clean_data = False
mongo_store = False

if __name__ ==  '__main__':
    
    if execute_multiprocess:
        # Scrape data 
        n_pools = 2
        n_min = 2
        execute_newsplease_cli.multiprocess(n_pools, n_min)
    
    
    # Data cleaning and storing    
    if clean_data:
        print('*'*50)
        print('Step 1: Cleaning')
        print('*'*50)
        data_path = pd.read_csv('configs_path.csv')['bbdd_path'].tolist()[0]
        newsp_paths_dict = auxFuns.fast_data_dir_walking(data_path)
        clean_and_store.cleaning(data_path, newsp_paths_dict)
        
    if clean_data and mongo_store:
        print('*'*50)
        print('Step 2: Inserting in mongodb and ES')
        print('*'*50)
        
        clean_and_store.insert2mongo(data_path,newsp_paths_dict)
        clean_and_store.mongo_to_ES()

