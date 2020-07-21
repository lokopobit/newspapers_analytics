# -*- coding: utf-8 -*-
"""
Created on Mon Jul 20 18:14:06 2020

@author: lokopobit
"""

import get_news

# Data cleaning and storing
mongo_store = True

print('*'*50)
print('Step 1: Cleaning')
print('*'*50)
data_path = r'C:\Users\juan\news-please-repo\data'
newsp_paths_dict = get_news.fast_dir_walking(data_path)
get_news.cleaning(data_path, newsp_paths_dict)
    
if mongo_store:
    print('*'*50)
    print('Step 2: Inserting in mongodb')
    print('*'*50)
    
    get_news.insert2mongo(data_path,newsp_paths_dict)

