# -*- coding: utf-8 -*-
"""
Created on Sun May 24 10:48:29 2020

@author: lokopobit
"""

# Load external libreries
import pandas as pd
import unicodedata
import json
import os
import requests
from bs4 import BeautifulSoup  
from selenium import webdriver
from selenium.webdriver.firefox.options import Options

def start_url_driver(url):
    try:
        options = Options()
        options.headless = True
        geckodriver_path = pd.read_csv('configs_path.csv')['geckodriver_path'].tolist()[0]
        driver = webdriver.Firefox(executable_path=geckodriver_path, options=options)
        driver.implicitly_wait(10)
        driver.get(url)
        return driver
    except:
        print('ERROR: LOADING PAGE ', url)

def create_dict(urls_dict, data_es, classes_es):
    i = 0
    for data in data_es:
        if data.name == 'h4':
            i += 1
            urls_dict[classes_es[i]] = []
        
        try:
            aux = data.text +'_'+ data.a['href']
            d = start_url_driver(data.a['href'])
            # aux = data.text +'_'+ d.current_url
            aux = [data.text, d.current_url]
            urls_dict[classes_es[i]].append(aux)
            d.close()
            print(aux)
        except:
            try:
                d.close()
            except:
                pass
            continue
        
    return urls_dict

def remove_ads(auxs):
    while True:
        try:
            auxs.find('div', {'class':'publi-google-extras'}).decompose()
        except:
            break
    return auxs

def retrieve_urls_index(url):
    
    html_es = requests.get(url).text
    soup_es = BeautifulSoup(html_es, features="lxml")
    
    auxs = soup_es.find(id = 'enlaces-extras-col-izq') ; data_es1 = list(auxs.find("h4").next_siblings)
    classes_es1 = auxs.find_all('h4') ; classes_es1 = [ae.text for ae in classes_es1]
    
    auxs = soup_es.find(id = 'enlaces-extras-col-der') ; 
    auxs = remove_ads(auxs)
    data_es2 = list(auxs)
    classes_es2 = auxs.find_all('h4') ; classes_es2 = [ae.text for ae in classes_es2]
    classes_es2 = classes_es1[-1:] + classes_es2
    
    urls_dict = {}
    urls_dict[classes_es1[0]] = []
    urls_dict = create_dict(urls_dict, data_es1, classes_es1)
        
    urls_dict = create_dict(urls_dict, data_es2, classes_es2)
    return urls_dict

def prensa_es(save=False):
       
    prensa_espannola = 'http://www.tnrelaciones.com/anexo/laprensa/index.html'
    urls_dict = retrieve_urls_index(prensa_espannola)
        
    if save:        
        f = open('prensa_espannola.json', 'w')
        json.dump(urls_dict, f)
        f.close()
        
    return urls_dict

def prensa_autonomica(save=False):

    prensa_autonomica = 'http://www.tnrelaciones.com/anexo/prensautonomica/index.html'
    html_es = requests.get(prensa_autonomica).text
    soup_es = BeautifulSoup(html_es, features="lxml")
    
    auxs = soup_es.find(id = 'enlaces-extras-col-izq') ; 
    urls_autonomicas = [el.a['href'] for el in auxs.find_all("p")]
    auxs = soup_es.find(id = 'enlaces-extras-col-der') ; 
    urls_autonomicas.extend([el.a['href'] for el in auxs.find_all("p")])
    urls_autonomicas = ['http://www.tnrelaciones.com/anexo'+ax[2:] for ax in urls_autonomicas]
    
    urls_dict_autonomicas={}
    for url_autonomica in urls_autonomicas:
        newspaper_name = url_autonomica.split('/')[-2]+'.json'
        if os.path.isfile(newspaper_name):
            continue
        urls_dict = retrieve_urls_index(url_autonomica)
        urls_dict_autonomicas[url_autonomica.split('/')[-2]]=urls_dict
        if save:        
            f = open(newspaper_name, 'w')
            json.dump(urls_dict, f)
            f.close()
            
    return urls_dict_autonomicas
    
    
# urls_dict = prensa_es()     
def remove_accents_prensa():
    
    def apply_encoding(key_):
        
        def remove_accents(input_str):
            nfkd_form = unicodedata.normalize('NFKD', input_str)
            only_ascii = nfkd_form.encode('ASCII', 'ignore')
            return only_ascii
        
        new_key = key_.upper().encode("latin1").decode().title()
        new_key = remove_accents(new_key)
        new_key = new_key.decode('utf-8').replace(' ', '_')          
        return new_key
    
    prensas = os.listdir('json_data/tn_relaciones')
    prensas = [pr for pr in prensas if pr[:7] == 'prensa_']
    
    for prensa in prensas:
        f = open(os.path.join('json_data/tn_relaciones', prensa), 'r')
        prensa_dict = json.load(f)
        f.close()
        
        prensa_dict_new = {}
        for key_ in prensa_dict.keys():
            if prensa_dict[key_] == []:
                continue

            new_key = apply_encoding(key_)
            
            if new_key == 'Incluye_Mas_Medios_Escribiendo_A_Directorios@Tnrelaciones.Com':
                new_key = 'General'
            
            prensa_dict_new[new_key] = prensa_dict[key_]
            
            press_url_new = []
            for press_url in prensa_dict_new[new_key]:
                #press_url0 = '_'.join(press_url.split('_')[:-1])
                #press_url1 = press_url.split('_')[-1]
                press_url0 = press_url[0]
                press_url1 = press_url[1]
                press_url0 = apply_encoding(press_url0)
                press_url = press_url0 + '_' + press_url1
                press_url_new.append(press_url)
                
            prensa_dict_new[new_key] = press_url_new   
            
        f = open(os.path.join('json_data/tn_relaciones', prensa), 'w')
        json.dump(prensa_dict_new,f)
        f.close()
        


