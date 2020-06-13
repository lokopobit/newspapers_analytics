# -*- coding: utf-8 -*-
"""
Created on Sat May 23 16:55:43 2020

@author: lokopobit
"""

# Load external libreries
from multiprocessing import Pool, Lock
from itertools import product
import json, hjson
from time import sleep
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
            if file.count('_') <= 2: # non articles
                error_files.append(file)
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
    
#
def find_duplicated_articles(path, path1):
    f1 = os.listdir(path)
    f2 = os.listdir(path1)
    for f in f1:
        if f in f2:
            print('cago en diez')

#
def find_article_years(path):
    years = []
    for file in os.listdir(path):
        if file[-5:] == '.json':
            f = open(os.path.join(path, file), 'r')
            art = json.load(f)
            f.close()
            years.append(int(art['date_publish'][:4]))
    return years

def main():
    base = ['authors', 'date_download', 'date_modify', 'date_publish', 'description', 
            'filename', 'image_url', 'language', 'localpath', 'title', 'title_page', 
            'title_rss', 'source_domain', 'maintext', 'url']
    path = r'C:\Users\juan\news-please-repo\data\2020\06\06\huelvabuenasnoticias.com'
    path = r'C:\Users\juan\news-please-repo\data\2020\06\10\diariodehuelva.es'
    path1 = r'C:\Users\juan\news-please-repo\data\2020\06\11\diariodehuelva.es'
    
    # Newspaaper cleaning
    error_files = json_keys_checking(path, base, test=False)
    remove_error_files(path, error_files)
    
def execute_newsplease_cli(newspaper_url):
    config_path = r'C:\Users\juan\news-please-repo\config'
    general_config = ''
    news_config = 'sitelist.hjson'
    
    with lock:
        sleep(10)
        f = open(os.path.join(config_path, news_config), 'r')
        nc = hjson.load(f)
        nc['base_urls'][0]['url'] = newspaper_url
        f.close()
        
        f = open(os.path.join(config_path, news_config), 'w')
        hjson.dump(nc, f)
        f.close()
        
    os.system('cmd /k "news-please"')
        
    
def init_child(lock_):
    global lock
    lock = lock_
    
if __name__ == '__main__':
    lock = Lock()
    p = Pool(2, initializer=init_child, initargs=(lock,))
    # p.starmap(ca, [(3,4), (1,3)])
    urls = ['https://www.diariodehuelva.es/', 'https://www.huelvabuenasnoticias.com/'] #,'http://huelva24.com/']
    p.map(execute_newsplease_cli, urls)
    
    
# os.system('cmd /k "python"')


        

        

    

    


        


