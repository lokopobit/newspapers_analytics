# -*- coding: utf-8 -*-
"""
Created on Sun May 24 10:48:29 2020

@author: lokopobit
"""

# Load external libreries
import requests
from bs4 import BeautifulSoup  

prensa_espannola = 'http://www.tnrelaciones.com/anexo/laprensa/index.html'
prensa_autonomica = 'http://www.tnrelaciones.com/anexo/prensa_andalucia/index.html'

html_es = requests.get(prensa_espannola).text
soup_es = BeautifulSoup(html_es, features="lxml")
classes_es = soup_es.find_all('h4') ; classes_es = [ae.text for ae in classes_es]
auxs = soup_es.find(id = 'enlaces-extras-col-izq') ; data_es1 = list(auxs.find("h4").next_siblings)
classes_es1 = auxs.find_all('h4') ; classes_es1 = [ae.text for ae in classes_es1]
auxs = soup_es.find(id = 'enlaces-extras-col-der') ; data_es2 = list(auxs.find("h4").next_siblings)
classes_es2 = auxs.find_all('h4') ; classes_es2 = [ae.text for ae in classes_es2]

urls_dict = {}
aux = []
i = 0
for data in data_es1:
    if data.name == 'h4':
        aux = []
        i += 1
    
    try:
        aux.append(data.text +'_'+ data.a['href'])
        urls_dict[classes_es1[i]] = aux
    except:
        continue
    
aux = []
i = 0
for data in data_es2:
    if data.name == 'h4':
        aux = []
        i += 1
    
    try:
        aux.append(data.text +'_'+ data.a['href'])
        urls_dict[classes_es2[i]] = aux
    except:
        continue
    