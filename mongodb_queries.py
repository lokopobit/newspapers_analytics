# -*- coding: utf-8 -*-
"""
Created on Mon Jul 20 17:53:40 2020

@author: lokopobit
"""

from bson.objectid import ObjectId
import numpy as np

import auxiliar_functions as auxFuns
from analytics import calculate_containment, lcs_norm_word

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
            
    def find_document_by_id(collection, document_id):
        return list(collection.find({'_id' : ObjectId(document_id)}))
        
     
    client = auxFuns.create_mongo_client()
    db_names_to_exclude = ['admin','config','local']
    all_db_names = client.list_database_names()
    for ax in db_names_to_exclude: all_db_names.remove(ax)
    db_name = all_db_names[-1]
    db = auxFuns.open_mongo_db(client, db_name)
    for i in range(len(db.list_collection_names())):
        collection = db.list_collection_names()[i]
        newsp = db[collection]
        print('\n Newspaper:', collection)
        print('\n Number of articles:', newsp.estimated_document_count()) 
        print('\n Authors:', unique_authors(newsp))
        print('\n No duplicated articles:', duplicated_articles(newsp))    
        print('-'*30)

    # Containment per newspaper, per province and per provinces
    containment_per_newsp = {}
    for collection in db.list_collection_names()[2:3]:
        newsp = db[collection]
        newsp_article = newsp.find() ; newsp_articles = []
        containment_per_newsp[collection] = []
        for article in newsp_article: newsp_articles.append(article)
        
        for article1 in newsp_articles:
            print(newsp_articles.index(article1))
            if newsp_articles.index(article1)+1 == len(newsp_articles): break 
            for article2 in newsp_articles[newsp_articles.index(article1)+1:]:
                print(newsp_articles.index(article2))
                # containment = calculate_containment(article1['title'],article2['title'],4)
                containment = 0
                lcs_norm_word_ = lcs_norm_word(article1['maintext'],article2['maintext'])
                if containment > 0.7 or lcs_norm_word_ > 0.7:
                    print('+'*100, containment)
                    print(article1['date_publish'],article1['title'],article1['description'], article1['url'])
                    print('-'*100)
                    print(article2['date_publish'],article2['title'],article2['description'], article2['url'])
                    # c.append(containment)
        

    # all_containments = {}
    # for db_name1 in all_db_names:
    #     if all_db_names.index(db_name1)+1 == len(all_db_names): break
    #     for db_name2 in all_db_names[all_db_names.index(db_name1)+1:]:
    #         containment_dict_name = db_name1 + ' vs ' + db_name2
    #         articles1 = db[]

    
    
    

    
    
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
    
    auxFuns.close_mongo_db(client)
    
    
    
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
    
    
def ES_Queries():
    # https://dzone.com/articles/23-useful-elasticsearch-example-queries
    
    # match_all ¿?
    
    a = {'query':{'multi_match':{'query':'no','fields':['maintext']}}} # search for specific terms within multiple fields
    
    # match_phrase 
    
    client.search(index='newshuelva',body=a)
    
    
    
    
    
