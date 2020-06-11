# -*- coding: utf-8 -*-
"""
Created on Sat May 23 16:55:43 2020

@author: lokopobit
"""

# Load external libreries
import json
import os

#
def split_folder(): 
    pre = r'C:\Users\juan\news-please-repo\data\2020\06\06'
    for i in range(10):
        new_folder = os.path.join(pre, '_'+str(i))
        if not os.path.exists(new_folder):
            os.mkdir(new_folder)
         
        j = 0
        while j < 200:
            if i != 9:
                pass
            else:
                pass
    
#
def json_keys_checking(path, base, test=False):
    error_files = []   
    j = 0
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
        
        if test and j >10:          
            break
        
        if j % 10000 == 0:
            print(j)
    return error_files

#
def remove_error_files(path, error_files):
    for ef in error_files: os.remove(os.path.join(path, ef))
    print('Removed ', len(error_files), ' files')
        
base = ['authors', 'date_download', 'date_modify', 'date_publish', 'description', 
        'filename', 'image_url', 'language', 'localpath', 'title', 'title_page', 
        'title_rss', 'source_domain', 'maintext', 'url']
path = r'C:\Users\juan\news-please-repo\data\2020\06\06\huelvabuenasnoticias.com'
path = r'C:\Users\juan\news-please-repo\data\2020\06\10\diariodehuelva.es'
path = r'C:\Users\juan\news-please-repo\data\2020\06\11\diariodehuelva.es'

# Newspaaper cleaning
error_files = json_keys_checking(path, base, test=False)
remove_error_files(path, error_files)
    


        


