# -*- coding: utf-8 -*-
"""
Created on Sun May 24 10:48:29 2020

@author: lokopobit
"""

# Load external libreries
import json
import requests
from bs4 import BeautifulSoup  
from selenium import webdriver
from selenium.webdriver.firefox.options import Options

def start_url_driver(url):
    try:
        options = Options()
        options.headless = True
        driver = webdriver.Firefox(executable_path=r'C:\Users\juan\Documents\geckodriver-v0.26.0-win64\geckodriver.exe', options=options)
        driver.implicitly_wait(10)
        driver.get(url)
        return driver
    except:
        print('PROBLEM LOADING INITIAL PAGE')

prensa_espannola = 'http://www.tnrelaciones.com/anexo/laprensa/index.html'
prensa_autonomica = 'http://www.tnrelaciones.com/anexo/prensa_andalucia/index.html'

html_es = requests.get(prensa_espannola).text
soup_es = BeautifulSoup(html_es, features="lxml")

auxs = soup_es.find(id = 'enlaces-extras-col-izq') ; data_es1 = list(auxs.find("h4").next_siblings)
classes_es1 = auxs.find_all('h4') ; classes_es1 = [ae.text for ae in classes_es1]

auxs = soup_es.find(id = 'enlaces-extras-col-der') ; 
while True:
    try:
        auxs.find('div', {'class':'publi-google-extras'}).decompose()
    except:
        break
data_es2 = list(auxs)
classes_es2 = auxs.find_all('h4') ; classes_es2 = [ae.text for ae in classes_es2]
classes_es2 = classes_es1[-1:] + classes_es2

urls_dict = {}
i = 0
urls_dict[classes_es1[i]] = []
for data in data_es1:
    if data.name == 'h4':
        i += 1
        urls_dict[classes_es1[i]] = []
    
    try:
        aux = data.text +'_'+ data.a['href']
        d = start_url_driver(data.a['href'])
        aux = data.text +'_'+ d.current_url
        urls_dict[classes_es1[i]].append(aux)
        d.close()
        print(aux)
    except:
        continue
    
i = 0
for data in data_es2:
    if data.name == 'h4':
        i += 1
        urls_dict[classes_es2[i]] = []
    
    try:
        aux = data.text +'_'+ data.a['href']
        d = start_url_driver(data.a['href'])
        aux = data.text +'_'+ d.current_url
        urls_dict[classes_es2[i]].append(aux)
        d.close()
        print(aux)
    except:
        continue
    
# f = open('prensa_espannola.json', 'w')
# json.dump(urls_dict, f)