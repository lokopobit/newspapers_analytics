# -*- coding: utf-8 -*-
"""
Created on Sat May 23 16:55:43 2020

@author: lokopobit
"""

# Load external libreries
import json
import os

path = r'C:\Users\juan\news-please-repo\data\2020\06\06\huelvabuenasnoticias.com'

j = 0
base = ['authors', 'date_download', 'date_modify', 'date_publish', 'description', 
        'filename', 'image_url', 'language', 'localpath', 'title', 'title_page', 
        'title_rss', 'source_domain', 'maintext', 'url']
error_files = []
for file in os.listdir(path):
    if file[-5:] == '.json':
        try:
            f = open(os.path.join(path, file), 'r')
            art = json.load(f)
            f.close()
        except:
            error_files.append(file)
            continue
        keys = list(art.keys())
        if keys != base:
            print('amos tu manco')
    j += 1
    
    # if (j >10):
    #     break
    
    if j % 10000 == 0:
        print(j)
        
        

# pre = r'C:\Users\juan\news-please-repo\data\2020\06\06'
# for i in range(10):
#     new_folder = os.path.join(pre, '_'+str(i))
#     if not os.path.exists(new_folder):
#         os.mkdir(new_folder)
     
#     j = 0
#     while j < 
#     if i != 9:
        
#     else:
    

# files = os.listdir(path)

        


