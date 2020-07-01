# -*- coding: utf-8 -*-
"""
Created on Tue Jun 30 12:11:55 2020

@author: lokopobit
"""

from multiprocessing import Pool, Lock
import hjson
from time import sleep
import configparser
import os

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
