# -*- coding: utf-8 -*-
"""
Created on Sat May 23 16:55:43 2020

@author: lokopobit
"""

# Load external libreries
from pymongo import MongoClient
import win32com.shell.shell as shell
import os, json
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
def cleaning(data_path, newsp_paths_dict):
    
    def cleaning_aux(newsp_path, urls, test=False):
        data_path = r'C:\Users\juan\news-please-repo\data'
        base = ['authors', 'date_download', 'date_modify', 'date_publish', 'description', 
                'filename', 'image_url', 'language', 'localpath', 'title', 'title_page', 
                'title_rss', 'source_domain', 'maintext', 'url']
    
        error_files, different_files = [], []
        j = 0
        for file in os.scandir(newsp_path):
            file = file.name
            if file[-5:] == '.json':
                try:
                    f = open(os.path.join(newsp_path, file), 'r')
                    art = json.load(f)
                    f.close()
                except:
                    error_files.append(file)
                    continue
                
                keys = list(art.keys())
                if keys != base:
                    different_files.append(file)
                    continue
                
                if art['url'] in urls:
                    error_files.append(file)
                    continue
                else:
                    urls.append(art['url'])
                
                j += 1           
                if test and j >10:          
                    break           
                if j % 10000 == 0:
                    print(newsp_path.replace(data_path, ''), 'Files checked:', j)                                
        return error_files, different_files, urls    
    
    def remove_error_files(newsp_path, error_files):
        for ef in error_files: os.remove(os.path.join(newsp_path, ef))
    
    
    f = open('already_cleaned.json', 'r') ; already_cleaned = json.load(f) ; f.close()   
    # Newspaaper cleaning
    for newsp_key in newsp_paths_dict.keys():
        print('-'*20)
        print('Cleaning', newsp_key)
        print('-'*20)
        for newsp_path in newsp_paths_dict[newsp_key]:
            
            if newsp_key not in already_cleaned.keys():
                already_cleaned[newsp_key] = {}
                already_cleaned[newsp_key]['paths'] = []
                already_cleaned[newsp_key]['urls'] = []
                
            if newsp_path in already_cleaned[newsp_key]['paths']:
                print(newsp_path.replace(data_path, ''), 'Already cleaned')
                continue
            
            urls_ = already_cleaned[newsp_key]['urls']
            error_files, different_files, urls = cleaning_aux(newsp_path, urls_, test=False)
            already_cleaned[newsp_key]['urls'] = urls
            
            remove_error_files(newsp_path, error_files)
            already_cleaned[newsp_key]['paths'].append(newsp_path)
            print(newsp_path.replace(data_path, ''), 'Cleaned.', 'Removed ', len(error_files), ' files')
        
            f = open('already_cleaned.json', 'w') ; json.dump(already_cleaned,f) ; f.close()    


#
def insert2mongo(data_path, newsp_paths_dict):
    def create_mongo_client(open_server=False):
        print('-'*30)
        print('Opening mongo db client')
        print('-'*30)
        if open_server:
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
    # db.list_collection_names()
    # collection = db.test_collection
    
    f = open('already_stored.json', 'r') ; already_stored = json.load(f) ; f.close()
    # Newspaaper cleaning
    for newsp_key in newsp_paths_dict.keys():
        print('-'*20)
        print('Inserting', newsp_key)
        print('-'*20)
        collection = db[newsp_key]
        for newsp_path in newsp_paths_dict[newsp_key]:
            
            if newsp_key not in already_stored.keys():
                already_stored[newsp_key] = []
                
            if newsp_path in already_stored[newsp_key]:
                print(newsp_path.replace(data_path, ''), 'Already inserted')
                continue
            
            for file in os.listdir(newsp_path):
                if file[-5:] == '.json':
                    f = open(os.path.join(newsp_path, file), 'r')
                    art = json.load(f)
                    f.close()
                    collection.insert_one(art)  
                    # collection.update(art, art, upsert=True)
            
            already_stored[newsp_key].append(newsp_path)
            print(newsp_path.replace(data_path, ''), 'Inserted.')
        
            f = open('already_stored.json', 'w') ; json.dump(already_stored,f) ; f.close()    
    
    close_mongo_db(client)


#
def main():
    mongo_store = True
    
    print('*'*50)
    print('Step 1: Cleaning')
    print('*'*50)
    data_path = r'C:\Users\juan\news-please-repo\data'
    newsp_paths_dict = fast_dir_walking(data_path)
    cleaning(data_path, newsp_paths_dict)
        
    if mongo_store:
        print('*'*50)
        print('Step 2: Inserting in mongodb')
        print('*'*50)
        
        insert2mongo(data_path,newsp_paths_dict)
        

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
    collection = db.list_collection_names()[3]
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