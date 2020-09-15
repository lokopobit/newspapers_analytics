# -*- coding: utf-8 -*-
"""
Created on Mon Jul 20 18:14:06 2020

@author: lokopobit
"""

import pandas as pd
import get_news
import execute_newsplease_cli

execute_multiprocess = False
mongo_store = True
if __name__ ==  '__main__':
    
    if execute_multiprocess:
        # Scrape data 
        n_pools = 3
        n_min = 5
        execute_newsplease_cli.multiprocess(n_pools, n_min)
    
    
    # Data cleaning and storing        
    print('*'*50)
    print('Step 1: Cleaning')
    print('*'*50)
    data_path = pd.read_csv('configs_path.csv')['bbdd_path'].tolist()[0]
    newsp_paths_dict = get_news.fast_dir_walking(data_path)
    get_news.cleaning(data_path, newsp_paths_dict)
        
    if mongo_store:
        print('*'*50)
        print('Step 2: Inserting in mongodb')
        print('*'*50)
        
        get_news.insert2mongo(data_path,newsp_paths_dict)

