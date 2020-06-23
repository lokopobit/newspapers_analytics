# -*- coding: utf-8 -*-
"""
Created on Sat May 23 16:55:43 2020

@author: lokopobit
"""

# Load external libreries
from multiprocessing import Pool, Lock
from pymongo import MongoClient
import win32com.shell.shell as shell
import json, hjson
from time import sleep
import configparser
import os
import numpy as np

#
def fast_dir_walking(data_path):
    dirs_dict = {}
    year_dirs = [f.path for f in os.scandir(data_path) if f.is_dir()]
    for year in year_dirs:
        month_dirs = [f.path for f in os.scandir(year) if f.is_dir()]
        for month in month_dirs:
            day_dirs = [f.path for f in os.scandir(month) if f.is_dir()]
            for day in day_dirs:
                newsp_dirs = [f.path for f in os.scandir(day) if f.is_dir()]
                for newsp in newsp_dirs:
                    new_key = newsp.split('\\')[-1]
                    if new_key not in dirs_dict.keys():
                        dirs_dict[new_key] = []
                    dirs_dict[new_key].append(newsp) # Remove data_path from newsp?
    return dirs_dict
                        
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
            # if file.count('_') <= 2: # non articles
            #     error_files.append(file)
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
def find_duplicated_articles(paths):

    for path1 in paths:
        f1 = os.listdir(path1)
        for path2 in paths:
            f2 = os.listdir(path2)
            if path1 == path2:
                continue
            else:
                aux = np.intersect1d(f1, f2)
                print(aux)

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
    store = True
    base = ['authors', 'date_download', 'date_modify', 'date_publish', 'description', 
            'filename', 'image_url', 'language', 'localpath', 'title', 'title_page', 
            'title_rss', 'source_domain', 'maintext', 'url']
    
    data_path = r'C:\Users\juan\news-please-repo\data'
    dirs_dict = fast_dir_walking(data_path)
    f = open('already_cleaned.json', 'r') ; already_cleaned = json.load(f) ; f.close()
    
    # Newspaaper cleaning
    for key_ in dirs_dict.keys():
        for newsp in dirs_dict[key_]:
            print(newsp)
            if key_ not in already_cleaned.keys():
                already_cleaned[key_] = []
                
            if newsp in already_cleaned[key_]:
                print('Already cleaned')
                continue
            error_files = json_keys_checking(newsp, base, test=False)
            remove_error_files(newsp, error_files)
        # find_duplicated_articles(dirs_dict[key_])
        
    f = open('already_cleaned.json', 'w') ; json.dump(dirs_dict,f) ; f.close()
        
    if store:
        f = open('already_stored.json', 'r') ; already_stored = json.load(f) ; f.close()
        insert2mongo(dirs_dict, already_stored)
        f = open('already_stored.json', 'w') ; json.dump(dirs_dict,f) ; f.close()
        

#    
def execute_newsplease_cli(newspaper_url):
    config_path = r'C:\Users\juan\news-please-repo\config'
    general_config = 'config.cfg'
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
        
        config = configparser.RawConfigParser()
        config.read(os.path.join(config_path,general_config))
        config.set('Scrapy', 'JOBDIRNAME', 'jobdir'+newspaper_url.split('.')[1])
        with open(os.path.join(config_path,general_config), 'w') as configfile:
            config.write(configfile)
        
    os.system('cmd /k "news-please"')

#        
def init_child(lock_):
    global lock
    lock = lock_
 
#
def multiprocess(n_pools):
    lock = Lock()
    p = Pool(n_pools, initializer=init_child, initargs=(lock,))
    # p.starmap(ca, [(3,4), (1,3)])
    urls = ['https://www.diariodehuelva.es/', 'https://www.huelvabuenasnoticias.com/', 'http://huelva24.com/']
    urls = ['https://huelvaya.es/', 'https://www.huelvainformacion.es/', 'http://www.huelvahoy.com/']
    p.map(execute_newsplease_cli, urls)
    
#
def insert2mongo(dirs_dict, already_stored):
    # os.system('cmd /k "C:\\mongodb\\bin\\mongod.exe"')    
    shell.ShellExecuteEx(lpVerb='runas', lpFile='cmd.exe', lpParameters='/c '+'net start MongoDB')    
    client = MongoClient()
    db = client.newsHuelva
    db.list_collection_names()
    # collection = db.test_collection
    
    for key_ in dirs_dict.keys():
        collection = db[key_]
        for newsp in dirs_dict[key_]:
            print(newsp)
            if key_ not in already_stored.keys():
                already_stored[key_] = []
            
            if newsp in already_stored[key_]:
                continue
            for file in os.listdir(newsp):
                if file[-5:] == '.json':
                    f = open(os.path.join(newsp, file), 'r')
                    art = json.load(f)
                    f.close()
                    collection.insert_one(art)  
    client.close()
    shell.ShellExecuteEx(lpVerb='runas', lpFile='cmd.exe', lpParameters='/c '+'net stop MongoDB')

#
def mongoQueries():
    
    def unique_authors(newsp):
        aux = []
        for art in newsp.find():
            aux.extend(art['authors'])
        a = np.unique(aux)
        return a
    
    def duplicated_articles(newsp):
        a=newsp.find()
        aux=[]
        for aa in a:
            aux.append(aa['url'])        
        return len(aux), len(np.unique(aux))
    
    shell.ShellExecuteEx(lpVerb='runas', lpFile='cmd.exe', lpParameters='/c '+'net start MongoDB')    
    client = MongoClient()
    db = client.newsHuelva
    
    newsp = db[db.list_collection_names()[3]]
    print(newsp.estimated_document_count())
 
    # newsp.find_one()

    print(unique_authors(newsp))
    print(duplicated_articles(newsp))    

    
    a=newsp.find({'title':{'$eq':'Huelva, líder regional del sector apícola'}})
    for aa in a:
        print(aa['date_publish'])
        print(aa['url'])
    
    aux = []
    for art in newsp.find({'authors':'Jesús Pelayo'}):
        aux.append(art['description'])
    for aa in a:
        b=newsp.find({'authors':aa})
        print(aa, b.count())
    
    client.close()
    shell.ShellExecuteEx(lpVerb='runas', lpFile='cmd.exe', lpParameters='/c '+'net stop MongoDB')
    
    
    


        


