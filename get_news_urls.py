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
        urls_dict[classes_es1[i]].append(aux)
    except:
        continue
    
i = 0
for data in data_es2:
    if data.name == 'h4':
        i += 1
        urls_dict[classes_es2[i]] = []
    
    try:
        aux = data.text +'_'+ data.a['href']
        urls_dict[classes_es2[i]].append(aux)
    except:
        continue
    