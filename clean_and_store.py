# -*- coding: utf-8 -*-
"""
Created on Sat May 23 16:55:43 2020

@author: lokopobit
"""

# Load external libreries
import os, json
from elasticsearch.helpers import parallel_bulk
from collections import deque
from tqdm import tqdm
import time

#
import auxiliar_functions as auxFuns
                      
    
#
def cleaning(data_path, newsp_paths_dict):
    
    def cleaning_newsp_path(data_path, newsp_path, urls, test=False):
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
                if test and j >10: break           
                if j % 10000 == 0:
                    print(newsp_path.replace(data_path, ''), 'Files checked:', j)
                    
            elif file[-5:] == '.html':
                error_files.append(file)

                      
        return error_files, different_files, urls    
    
    def remove_error_files(newsp_path, error_files):
        for ef in error_files: os.remove(os.path.join(newsp_path, ef))
    
    
    f = open('json_data/already_cleaned.json', 'r') ; already_cleaned = json.load(f) ; f.close()   
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
            error_files, different_files, urls = cleaning_newsp_path(data_path, newsp_path, urls_, test=False)
            already_cleaned[newsp_key]['urls'] = urls
            
            remove_error_files(newsp_path, error_files)
            already_cleaned[newsp_key]['paths'].append(newsp_path)
            print(newsp_path.replace(data_path, ''), 'Cleaned.', 'Removed ', len(error_files), ' files')
        
            f = open('json_data/already_cleaned.json', 'w') ; json.dump(already_cleaned,f) ; f.close()    


#
def insert2mongo(data_path, newsp_paths_dict):         
    f = open('json_data/prensas_all.json', 'r') ; prensa_all = json.load(f) ; f.close()
    db_names = []
    for key_, values in prensa_all.items():  
        if key_.find('eportivos') != -1 or key_.find('eneral') != -1:
            continue
        for newsp_key in newsp_paths_dict.keys():
            aux = [val for val in values if val.find(newsp_key) != -1]
            if aux != []:
                print(key_, newsp_key)
                db_names.append(key_)
    
    for db_name in db_names:
        client = auxFuns.create_mongo_client()
        db = auxFuns.open_mongo_db(client, db_name)
        # db.list_collection_names()
        # collection = db.test_collection
        
        f = open('json_data/already_stored.json', 'r') ; already_stored = json.load(f) ; f.close()
        # Newspaaper cleaning
        for newsp_key in newsp_paths_dict.keys():
            aux = [val for val in prensa_all[db_name] if val.find(newsp_key) != -1] 
            if aux == []:
                continue
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
            
                f = open('json_data/already_stored.json', 'w') ; json.dump(already_stored,f) ; f.close()    
        
        auxFuns.close_mongo_db(client)


def mongo_to_ES():
    
    if not os.path.exists('json_data/mongo_to_ES_dict.json'):
        mongo_to_ES_dict = {}
    else:
        f = open('json_data/mongo_to_ES_dict.json', 'r')
        mongo_to_ES_dict = json.load(f)
        f.close()
    
    ES_client = auxFuns.create_ES_client()
    MG_client = auxFuns.create_mongo_client()
    
    db_names_to_exclude = ['admin','config','local','newsHuelva']
    all_db_names = MG_client.list_database_names()
    for ax in db_names_to_exclude: all_db_names.remove(ax)
    for db_name in all_db_names:
        if db_name not in mongo_to_ES_dict.keys(): mongo_to_ES_dict[db_name] = {}
        db = auxFuns.open_mongo_db(MG_client, db_name)
        collections = db.list_collection_names()
        for collection in collections:
            if collection not in mongo_to_ES_dict[db_name].keys():
                mongo_to_ES_dict[db_name][collection] = []
            newsp = db[collection]
    
            actions = []
            ES_index = (db_name+'_'+collection).lower()
            for data in tqdm(newsp.find(), total=newsp.count()):
                if str(data['_id']) in mongo_to_ES_dict[db_name][collection]:
                    continue
                else:
                    mongo_to_ES_dict[db_name][collection].append(str(data['_id']))
                
                data.pop('_id')
                action = {
                    "_index": ES_index,
                    "_type": 'string',
                    "_source": data
                }
                actions.append(action)
                
                # Dump x number of objects at a time
                if len(actions) >= 100:
                    deque(parallel_bulk(ES_client, actions), maxlen=0)
                    actions = []
                time.sleep(.01)
                
    f = open('json_data/mongo_to_ES_dict.json', 'w')
    json.dump(mongo_to_ES_dict, f)
    f.close()
     
# #
# def find_article_years(path):
#     years = []
#     for file in os.listdir(path):
#         if file[-5:] == '.json':
#             f = open(os.path.join(path, file), 'r')
#             art = json.load(f)
#             f.close()
#             years.append(int(art['date_publish'][:4]))
#     return years    

   
# #
# def split_folder(): 
#     pre = r'C:\Users\juan\news-please-repo\data\2020\06\06'
#     for i in range(10):
#         new_folder = os.path.join(pre, '_'+str(i))
#         if not os.path.exists(new_folder):
#             os.mkdir(new_folder)
         
#         j = 0
#         while j < 200:
#             if i != 9:
#                 pass
#             else:
#                 pass

# REMOVE ALL HTMLs
# data_path = pd.read_csv('configs_path.csv')['bbdd_path'].tolist()[0]
# newsp_paths_dict = auxFuns.fast_data_dir_walking(data_path)
# for newsp_key in newsp_paths_dict.keys():
#     for newsp_path in newsp_paths_dict[newsp_key]:
#         error_files = []
#         for file in os.scandir(newsp_path):
#             file = file.name
#             if file[-5:] == '.html':
#                 error_files.append(file)
        
#         remove_error_files(newsp_path, error_files)
    
    
    
    
    
    
    
    
    