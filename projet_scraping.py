# -*- coding: utf-8 -*-
"""
Created on Mon Feb 28 22:48:35 2022

@author: lucie
"""


import sys
from urllib.request import Request, urlopen
from urllib.error import HTTPError, URLError
from bs4 import BeautifulSoup, Tag, NavigableString, Comment
import pickle
from multiprocessing import Pool, cpu_count
import time
import os
import numpy
urlopen("http://www.google.fr")

#os.chdir("C:/Users/lucie/OneDrive/Documents/Cours/MASTER 1 MAS/S2/PYTHON/projet")


# Définition des fonctions

def validTag(tag):
    if tag.name == "style" or tag.name=="sup":
        return False
    if "class" in tag.attrs :
        for elem in tag.attrs["class"]: #Parcours de toutes les class
            if elem in ['toc', 'homonymie', 'metadata','mw-editsection', 'mwe-math-element', 'bandeau-portail', 'printfooter']:
                return False
    return True



def getSelectedText(montag):
    texte=""
    for c in montag.children:
        #si navigable string on prend
        if type(c)==NavigableString:
            texte+=(c.string).strip()
        elif type(c)==Tag:
            texte += getSelectedText(c)
     
    return texte


def parseURL(mon_url):
    # Ouvrir avec openurl mon_url
    user_agent = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_3) AppleWebKit/537.36 (KHTML,like Gecko) Chrome/35.0.1916.47 Safari/537.36'
    req = Request(mon_url,headers={'User-Agent':user_agent})
    try: # gestion des exceptions avec un bloc try/except
        html = urlopen(req)
    except (HTTPError, URLError) as e:
        sys.exit(e) # sortie du programme avec affichage de l’erreur
    bsObj = BeautifulSoup(html, "lxml") # en utilisant le parser de lxml

    #Acceder au grand titre h1 qui est le premier et le seul de la page
    titre = bsObj.find("h1").get_text()
    #Acceder au texte 
    masoupe = bsObj.find("div",class_="article-content")
    texte = getSelectedText(masoupe)
    return(mon_url,titre,texte)


# Programme principal

if __name__ == '__main__':
    user_agent = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/35.0.1916.47 Safari/537.36'
    full_url = 'https://www.thecanadianencyclopedia.ca/en/browse/things/nature-geography/hydrology'
    req = Request(full_url,headers={'User-Agent':user_agent})
    try: 
        html = urlopen(req)
    except (HTTPError, URLError) as e:
        sys.exit(e) 
    bsObj = BeautifulSoup(html, "lxml") 
    
    nb_doc=int(bsObj.find("div",class_="search-results-counter text-xsmall uppercase").string.split()[3]) 
    ##Je réccupère le nombre de documents, ensuite on le divisera par 20 pour savoir le nombre de pages à tourner.
    doc_page=bsObj.find("div",class_="search-results-counter text-xsmall uppercase").string.split()[1]
    pos1=bsObj.find("div",class_="search-results-counter text-xsmall uppercase").string.split()[1].find('-')
    nb_doc_page=int(doc_page[pos1+1:])
    listeurl=[]
    
    for i in range(int(numpy.trunc(nb_doc/nb_doc_page))+1):
    
        listediv1=bsObj.findAll("div",class_="search-single-info") #les liens se trouvent dans les div de class search-single-info
        
        for i in listediv1:
            listeurl.append(i.find("a").attrs["href"]) #liste des urls des pages
        
        if int(numpy.trunc(nb_doc/20))!=i:
            full_url=bsObj.find("li",class_="page-item active").find_next("a").attrs["href"]
            # on prend le lien du li qui suit celui qui indique la page actuel (si on est sur la page 1, prend le lien du bouton pour la page 2)
            req = Request(full_url,headers={'User-Agent':user_agent})
            try: 
                html = urlopen(req)
            except (HTTPError, URLError) as e:
                sys.exit(e) 
            bsObj = BeautifulSoup(html, "lxml") 
            
        
    
    #Test de parseurl
    #parseURL("https://thecanadianencyclopedia.ca/en/article/wetlands")
    
    
    
    ##Stocker les urls dans un fichier pick
    
    res = []
    with Pool(cpu_count()-1) as p :
        res = p.map(parseURL,listeurl)
    
    with open('hydrology.pick', 'wb') as pickFile:
            pickle.dump(res, pickFile)

 







