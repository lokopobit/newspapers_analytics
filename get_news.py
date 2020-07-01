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
def cleaning(newsp_path, urls, test=False):
    
    base = ['authors', 'date_download', 'date_modify', 'date_publish', 'description', 
            'filename', 'image_url', 'language', 'localpath', 'title', 'title_page', 
            'title_rss', 'source_domain', 'maintext', 'url']
    
    error_files, different_files = [], []
    j = 0
    for file in os.listdir(newsp_path):
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
            print('Files checked:', j)
            
    return error_files, different_files, urls

#
def remove_error_files(newsp_path, error_files):
    for ef in error_files: os.remove(os.path.join(newsp_path, ef))
    
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
                    # collection.insert_one(art)  
                    collection.update(art, art, upsert=True)
    client.close()
    shell.ShellExecuteEx(lpVerb='runas', lpFile='cmd.exe', lpParameters='/c '+'net stop MongoDB')


#
def main():
    store = False
    
    data_path = r'C:\Users\juan\news-please-repo\data'
    newsp_paths_dict = fast_dir_walking(data_path)
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
            error_files, different_files, urls = cleaning(newsp_path, urls_, test=False)
            already_cleaned[newsp_key]['urls'] = urls
            
            remove_error_files(newsp_path, error_files)
            already_cleaned[newsp_key]['paths'].append(newsp_path)
            print(newsp_path.replace(data_path, ''), 'Cleaned.', 'Removed ', len(error_files), ' files')
        
    f = open('already_cleaned.json', 'w') ; json.dump(already_cleaned,f) ; f.close()
        
    if store:
        f = open('already_stored.json', 'r') ; already_stored = json.load(f) ; f.close()
        insert2mongo(dirs_dict, already_stored)
        f = open('already_stored.json', 'w') ; json.dump(dirs_dict,f) ; f.close()
        

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
        return len(aux), len(np.unique(aux)), aux
    
    shell.ShellExecuteEx(lpVerb='runas', lpFile='cmd.exe', lpParameters='/c '+'net start MongoDB')    
    client = MongoClient()
    db = client.newsHuelva
    
    collection = db.list_collection_names()[2]
    newsp = db[collection]
    print(collection)
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
    
    
    
# a=newsp.find()
# for aa in a:
#     print(aa)
    
# a=newsp.find({'url':'http://huelva24.com/art/70727/rafael-segovia-ldquo-a-los-onubenses-poder-decir-que-somos-andaluces-nos-sale-muy-caro-rdquo-'})
# for aa in a:
#     # print('*'*90)
#     print(aa['description'])  
    
# client.drop_database('newsHuelva')
    
# [item for item, count in collections.Counter(a).items() if count > 1]
    
    
    
    
    
    
    
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