# -*- coding: utf-8 -*-
"""
Created on Sun Oct 11 18:15:19 2020

@author: lokopobit
"""

from pymongo import MongoClient
from elasticsearch import Elasticsearch
import win32com.shell.shell as shell
from random import sample
from operator import itemgetter 
import json
import os
from urllib.parse import urlparse


#######################################
### FUNCTIONS RELATED TO DATABASES ####
#######################################
def create_mongo_client(open_service=False):
    print('-'*30)
    print('Opening mongo db client')
    print('-'*30)
    if open_service:
        # os.system('cmd /k "C:\\mongodb\\bin\\mongod.exe"') 
        shell.ShellExecuteEx(lpVerb='runas', lpFile='cmd.exe', lpParameters='/c '+'net start MongoDB')    
    client = MongoClient()   
    return client

def open_mongo_db(client, db_name): 
    print('-'*30)
    print('Opening db:', db_name)
    print('-'*30)
    db = client[db_name]
    return db
    
def close_mongo_db(client, close_service=False):
    print('-'*30)
    print('Closing mongo db client')
    print('-'*30)
    client.close()
    if close_service:
        shell.ShellExecuteEx(lpVerb='runas', lpFile='cmd.exe', lpParameters='/c '+'net stop MongoDB')
        

def create_ES_client(open_service=False):
    print('-'*30)
    print('Opening eslasticsearch client')
    print('-'*30)
    if open_service:
        shell.ShellExecuteEx(lpVerb='runas', lpFile='cmd.exe', lpParameters='/c '+'net start elasticsearch-service-x64')    
    client = Elasticsearch()
    return client

def close_ES_service(close_service=False):
    print('-'*30)
    print('Closing elasticsearch service')
    print('-'*30)
    if close_service:
        shell.ShellExecuteEx(lpVerb='runas', lpFile='cmd.exe', lpParameters='/c '+'net stop lasticsearch-service-x64')
        
        


#######################################
    
#######################################
def create_newsp_urls_dict(urls):
    f = open('json_data/already_cleaned.json', 'r') ; already_cleaned = json.load(f) ; f.close()
    for url in urls:
        for key_ in already_cleaned.keys():
            if url.find(key_) != -1:
                already_urls = already_cleaned[key_]['urls']
                break                
        try:
            f = open('json_data/' + key_+'.json', 'w')
            json.dump({key_:already_urls}, f)
            f.close()
        except:
            pass

        
def load_n_per_province(n_pools):
    f = open('json_data/prensas_all.json', 'r') ; prensa_all = json.load(f) ; f.close()
    all_urls = []
    for key_ in prensa_all.keys():
        if len(prensa_all[key_]) < n_pools: continue           
        npools_random_int = sample(range(len(prensa_all[key_])),n_pools)            
        urls = itemgetter(*npools_random_int)(prensa_all[key_])
        all_urls.extend(list(urls))
    all_urls = [au.split('_')[-1] for au in all_urls]
    return all_urls


def load_community(n_pools, community):
    f = open('json_data/prensas_all.json', 'r') ; prensa_all = json.load(f) ; f.close()
    all_urls = []
    for j in range(20):
        for key_ in prensa_all.keys():
            if key_.split('_')[0] not in [community]: continue
            if len(prensa_all[key_]) < n_pools: continue           
            npools_random_int = sample(range(len(prensa_all[key_])),n_pools)            
            urls = itemgetter(*npools_random_int)(prensa_all[key_])
            all_urls.extend(list(urls))
    all_urls = [au.split('_')[-1] for au in all_urls]
    return all_urls
        
        

#######################################
    
#######################################    
    

def fast_data_dir_walking(data_path):
    newsp_paths_dict = {}
    year_dirs = [f.path for f in os.scandir(data_path) if f.is_dir()]
    for year in year_dirs:
        month_dirs = [f.path for f in os.scandir(year) if f.is_dir()]
        for month in month_dirs:
            day_dirs = [f.path for f in os.scandir(month) if f.is_dir()]
            for day in day_dirs:
                newsp_dirs = [f.path for f in os.scandir(day) if f.is_dir()]
                for newsp in newsp_dirs:
                    new_key = newsp.split('\\')[-1]
                    if new_key not in newsp_paths_dict.keys():
                        newsp_paths_dict[new_key] = []
                    newsp_paths_dict[new_key].append(newsp) # Remove data_path from newsp?
    return newsp_paths_dict



def create_prensas_all():
    prensas = os.listdir('json_data')
    prensas = [pr for pr in prensas if pr[:7] == 'prensa_']
    prensas.remove('prensa_espannola.json')
    
    prensas_all={}
    for prensa in prensas:
        f = open(os.path.join('json_data', prensa), 'r')
        prensa_dict = json.load(f)
        f.close()
        
        comunidad = prensa.split('.')[0].split('_')[-1] 
        for key_ in prensa_dict.keys():
            prensas_all_key = comunidad+'_'+key_
            prensas_all[prensas_all_key] = prensa_dict[key_]
        
    f = open('json_data/prensas_all.json', 'w')
    json.dump(prensas_all,f)
    f.close()    
        
    return prensas_all



def remove_underscore_from_prensas_files():
    ###
    ### DON'T RUN
    ###
    
    prensas = os.listdir('json_data')
    prensas = [pr for pr in prensas if pr[:7] == 'prensa_']
    
    for prensa in prensas:
        f = open(os.path.join('json_data', prensa), 'r')
        prensa_dict = json.load(f)
        f.close()

        new_prensa_dict = {}
        for key_,values in prensa_dict.items():
            new_prensa_dict[key_] = []
            for val in values:
                newspaper_name = '_'.join(val.split('_')[:-1])
                newspaper_url = val.split('_')[-1]
                aux = urlparse(newspaper_url)
                if aux.netloc == '': 
                    newspaper_name = val.split('_H')[0]
                    newspaper_url = 'H' + val.split('_H')[1]
                    aux = urlparse(newspaper_url)
                new_prensa_dict[key_].append([newspaper_name,aux.netloc])
                    
        f = open(os.path.join('json_data', prensa), 'w')
        json.dump(new_prensa_dict, f)
        f.close()



def remove_duplicated_urls_from_prensas_all():
    f = open('json_data/prensas_all.json', 'r')
    prensa_dict = json.load(f)
    f.close()    
    
    all_urls =  []
    for key_,values in prensa_dict.items():
        for val in values:
            url = val[1]
            all_urls.append(url)

    unique_urls = list(set(all_urls))
    new_prensa_dict = {}
    for key_,values in prensa_dict.items():
        new_prensa_dict[key_] = []
        for val in values:
            url = val[1]
            if url not in unique_urls:
                new_prensa_dict[key_].append([val[0], url])



