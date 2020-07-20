# -*- coding: utf-8 -*-
"""
Created on Mon Jul 20 17:53:40 2020

@author: lokopobit
"""

from pymongo import MongoClient
import win32com.shell.shell as shell
import numpy as np

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
        return len(aux) == len(np.unique(aux))
    
    def create_mongo_client(open_server=False):
        print('-'*30)
        print('Opening mongo db client')
        print('-'*30)
        if open_server:
            shell.ShellExecuteEx(lpVerb='runas', lpFile='cmd.exe', lpParameters='/c '+'net start MongoDB')    
        client = MongoClient()   
        return client
    
    def open_mongo_db(client, db_name): 
        print('-'*30)
        print('Opening db:', db_name)
        print('-'*30)
        db = client[db_name]
        return db
        
    def close_mongo_db(client, close_server=False):
        print('-'*30)
        print('Closing mongo db client')
        print('-'*30)
        client.close()
        if close_server:
            shell.ShellExecuteEx(lpVerb='runas', lpFile='cmd.exe', lpParameters='/c '+'net stop MongoDB')    
     
    db_name = 'newsHuelva'
    client = create_mongo_client()
    db = open_mongo_db(client, db_name)
    for i in range(len(db.list_collection_names())):
        collection = db.list_collection_names()[i]
        newsp = db[collection]
        print('\n Newspaper:', collection)
        print('\n Number of articles:', newsp.estimated_document_count()) 
        print('\n Authors:', unique_authors(newsp))
        print('\n No duplicated articles:', duplicated_articles(newsp))    

    
    a=newsp.find({'title':{'$eq':'Huelva, líder regional del sector apícola'}})
    for aa in newsp.find({'$text':{'$search':'cortegana', '$language' : "es"}}):
        print('-'*40)
        print(aa['title'])
    
    aux = []
    for art in newsp.find({'authors':'Ignacio Garzón González'}):
        print(art['authors'])
        aux.append(art['description'])
    for aa in a:
        b=newsp.find({'authors':aa})
        print(aa, b.count())
    
    close_mongo_db(client)
    
    
    
# a=newsp.find()
# for aa in a:
#     print(aa)
    
# a=newsp.find({'url':'http://huelva24.com/art/70727/rafael-segovia-ldquo-a-los-onubenses-poder-decir-que-somos-andaluces-nos-sale-muy-caro-rdquo-'})
# for aa in a:
#     # print('*'*90)
#     print(aa['description'])  
    
# client.drop_database('newsHuelva')
    
# [item for item, count in collections.Counter(a).items() if count > 1]
    
# newsp.find_one()
   
# newsp.create_index([("title", 'text')])
