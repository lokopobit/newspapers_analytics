# -*- coding: utf-8 -*-
"""
Created on Tue Jun 30 12:11:55 2020

@author: lokopobit
"""

import pandas as pd
from multiprocessing import Pool, Lock
import hjson, json
from time import sleep
from datetime import datetime
import subprocess
import psutil
import configparser
import os

#    
def execute_newsplease_cli(newspaper_url):
    # global procs_pid
    # config_path = pd.read_csv('configs_path.csv')['config_path'].tolist()[0]
    # general_config = 'config.cfg'
    # news_config = 'sitelist.hjson'
    
    with lock:
        sleep(20)
        config_path = pd.read_csv('configs_path.csv')['config_path'].tolist()[0]
        general_config = 'config.cfg'
        news_config = 'sitelist.hjson'
        f = open(os.path.join(config_path, news_config), 'r')
        nc = hjson.load(f)
        nc['base_urls'][0]['url'] = newspaper_url
        f.close()
        
        f = open(os.path.join(config_path, news_config), 'w')
        hjson.dump(nc, f)
        f.close()
        
        config = configparser.RawConfigParser()
        config.read(os.path.join(config_path,general_config))
        config.set('Scrapy', 'JOBDIRNAME', 'jobdir'+newspaper_url.split('.')[1]+str(datetime.today()).replace(':','-'))
        with open(os.path.join(config_path,general_config), 'w') as configfile:
            config.write(configfile)
        
    # os.system('cmd /k "news-please"')
    proc=subprocess.Popen(['news-please'], shell=False)
    f = open('json_data/process_PIDs.txt', 'a')
    f.write('\n '+str(proc.pid))
    f.close()

#        
def init_child(lock_):
    global lock
    lock = lock_
 
#
def multiprocess(n_pools):

    def kill(proc_pid):
        process = psutil.Process(proc_pid)
        for proc in process.children(recursive=True):
            proc.kill()
        process.kill()
    
    def create_newsp_urls_dict(urls):
        f = open('json_data/already_cleaned.json', 'r') ; already_cleaned = json.load(f) ; f.close()
        for url in urls:
            for key_ in already_cleaned.keys():
                if url.find(key_) != -1:
                    already_urls = already_cleaned[key_]['urls']
                    break
            f = open('json_data/' + key_+'.json', 'w')
            json.dump({key_:already_urls}, f)
            f.close()
       
    lock = Lock()
    p = Pool(n_pools, initializer=init_child, initargs=(lock,))
    # p.starmap(ca, [(3,4), (1,3)])
    all_urls = ['https://www.diariodehuelva.es/', 'https://www.huelvabuenasnoticias.com/', 'http://huelva24.com/',
            'https://huelvaya.es/', 'https://www.huelvainformacion.es/', 'http://www.huelvahoy.com/']
    
    n_min = 5
    range_ = list(range(0,len(all_urls)+1,n_pools))
    for i in range(len(range_)):
        if range_[i] == len(all_urls):
            continue
        
        urls = all_urls[range_[i]:range_[i+1]]
        create_newsp_urls_dict(urls)
        p.map(execute_newsplease_cli, urls)
        
        sleep(60*n_min)
        f = open('json_data/process_PIDs.txt', 'r')
        procs_pid = f.readlines()
        f.close()
        
        aux=[]
        for ax in procs_pid:
            try:
                aux.append(int(ax.replace('\n', ' ')))
            except:
                continue
    
        for proc_pid in aux: 
            try:
                kill(proc_pid)
            except:
                continue
            
        os.remove('json_data/process_PIDs.txt')






