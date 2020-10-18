# -*- coding: utf-8 -*-
"""
Created on Sun Oct 11 18:15:19 2020

@author: lokopobit
"""

from pymongo import MongoClient
from elasticsearch import Elasticsearch
import win32com.shell.shell as shell


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