# -*- coding: utf-8 -*-
"""
Created on Tue Mar  1 21:37:45 2022

@author: lucie
"""


import os
import pandas as pd
from pandas import DataFrame, Series
import pickle
import re
import math
from wordcloud import WordCloud
from scipy import spatial
import matplotlib.pyplot as plt


# Définition des fonctions
def getTokens(doc):
    regex = r"""\w+"""
    tokens = [word.strip().lower() for word in re.findall(regex, doc)]
    return tokens



# Définitiion des classes

class DTM:
    def __init__(self,liste,stopWords):
        urls=[]
        titres=[]
        for i in liste:
            urls.append(i[0])
            titres.append(i[1])
        
        self.url=urls #liste des URL
        self.titre=titres #liste des titres
        self.stopWords=stopWords
        df = DataFrame(liste)
        df.columns = ['url', 'titre', 'texte']
        #construire un dictionnaire pour chaque texte et mettre dans une liste
        liste_dico=[]
        for tuple in liste:
            texte_brut=tuple[2]
            les_mots=getTokens(texte_brut)
            dico={}
            for mot in les_mots:
                if mot not in self.stopWords:
                    dico[mot]= dico.get(mot,0)+1
            liste_dico.append(dico)
        self.data=DataFrame(liste_dico).fillna(0) #la data frame comptant les occurences de chaque mots dans chaque doc
        
        nbdocs=self.data.shape[0] #nb lignes matrice
        df=self.data.astype('bool').sum()
        
        log_idf=[math.log(nbdocs/value) for value in df]
        self.data=self.data.div(self.data.max(axis=1),axis=0)#sens de la division le axis=0
        self.data=self.data.mul(log_idf,axis=1)
        
                                 
        #ce dico contient la fréquence de chaque mot dans ce texte 
    def __repr__(self):
         return self.data.__repr__()
    def nBest(self,N):
        return self.data.sum().sort_values(ascending=False)[:N]
    def nBestDoc(self,N,indice):
        return self.data.iloc[indice].sort_values(ascending=False)[:N]
    def query(self,requete):
        mots_valides=[mot for mot in getTokens(requete) if mot not in self.stopWords]
        if len(mots_valides)==0:
            return []
        if not all (mot in self.data.columns for mot in mots_valides):
            return []
        les_url=[]
        for i in self.data.index:
            if all ([self.data.loc[i,mot]>0 for mot in mots_valides]):
                les_url.append(self.url[i])            
        return les_url
    
    def queryScore(self,requete,N=10):
        ## ca
        if(N<0):
            return "Vous avez saisi {}, mais N doit être positif".format(N)
        else:
            mots_valides=[mot for mot in getTokens(requete) if mot not in self.stopWords]
            les_score=[]
            if len(mots_valides)==0:
                return []
            if not all (mot in self.data.columns for mot in mots_valides):
                return []
            les_url=[]
            for i in self.data.index:
               # if all ([self.data.loc[i,mot]>0 for mot in mots_valides]):  à décommenter si l'on veut afficher les articles qui répondent à la requpete entière (voir explication ligne 161)
                   score=0
                   for mot_req in mots_valides :
                       score+=self.data[mot_req][i] # somme des tfidf des mots de la requête
                   les_url.append(self.url[i])   #on aggrège les urls  
                   les_score.append(score)
            table=pd.DataFrame({"url":les_url,'score':les_score })
            return list(table.sort_values(by=['score'],ascending=False).url[:N]) #trie et filtre sur les N premiers documents qui correspondent le plus à la requête



    def wordCloud(self,numDoc):
        if (numDoc>self.data.shape[0]):
            return "Vous avez saisi {}, mais le max de numDoc est : {}".format(numDoc,self.data.shape[0])
        elif(numDoc<0):
            return "Vous avez saisi {}, mais numDoc doit être positif".format(numDoc)
        else:
            WC=WordCloud(background_color="linen", colormap="cool").generate_from_frequencies(self.data.loc[numDoc])  #from_frequencies permet de mettre directement notre table self.data et les tf idf
            plt.imshow(WC)
            plt.axis("off")
            plt.show()
    def nMostSimilar(self,numDoc,N=10):
        if (numDoc>self.data.shape[0]):
            return "Vous avez saisi {}, mais le max est : {}".format(numDoc,self.data.shape[0])
        elif(numDoc<0):
            return "Vous avez saisi {}, mais numDoc doit être positif".format(numDoc)
        elif(N<0):
            return "Vous avez saisi {}, mais N doit être positif".format(N)
        else:
            simi=[]
            for i in range(self.data.shape[0]):
                if i != numDoc:
                    cos=1 - spatial.distance.cosine(self.data.loc[numDoc], self.data.loc[i]) #calcul de la similarite entre les articles
                    
                else:
                    cos=0 # pour éviter que l'article qu'on compare arrive en premier
                simi.append(cos)
                
            table=pd.concat([DataFrame(simi),DataFrame(self.titre)],axis=1) #dataframe qui fait correspondre les titres et la similarité
            table.columns=["similarite","titre"] #renommage des colonnes
            return list(table.sort_values(by=['similarite'],ascending=False).titre[:N]) #Retourne la liste des N documents les plus similaires


# Programme principal

os.chdir("C:/Users/lucie/OneDrive/Documents/Cours/MASTER 1 MAS/S2/PYTHON/projet")

with open("hydrology.pick",'rb') as pickFile: #ouverture de mon fichier pick
    doc=pickle.load(pickFile)

#### Création des mots_vides ou stopwords####
mots_vides=pd.read_table("mots_vides.txt",sep="|",header=1)
mots_vides=list(DataFrame(mots_vides).iloc[:,0])


### TEST DU DTM 

monDTM=DTM(doc,mots_vides)



#test méthode query score



#La méthode queryScore : on rentre une requête avec des mots des articles
#On ajoute un score qui est la somme des scores tf idf 
#Je choisis de garder tous les documets dont certains ont des scores à 0 
#Pour que lorsqu'on affiche 12 docs alors qu'il y en a que 2 les 10 derniers ont un score de 0
#De plus cela permet aussi d'afficher les documents qui ont un sur les 2 mots 
#Mais des articles qui ont 1 sur les 2 mots peuvent avoir un plus grand score que ceux qui ont vraiment les 2 mots 
#Si l'on veut que le score soit afficher seulement pour les articles qui répondent à la requête en entier on utilise
# la ligne de code du if (ligne 96 )

print(monDTM.queryScore("arctic",22))
print(monDTM.queryScore("dams"))
print(monDTM.queryScore("powerful stop",6))
print(monDTM.queryScore("canada rain",12))
print(monDTM.queryScore(" hydro corporation judged ",3))
## les entrées incohérentes
print(monDTM.queryScore("the in is ",3))
print(monDTM.queryScore("",3))
print(monDTM.queryScore("hydro corporation judged",-3))

#test méthode wordcloud
#

print(monDTM.wordCloud(0))
print(monDTM.wordCloud(7))
print(monDTM.wordCloud(8))
## les entrées incohérentes
print(monDTM.wordCloud(-1))
print(monDTM.wordCloud(56))

#test méthode nMostSimilar

print(monDTM.nMostSimilar(4,10)) #les 10 premiers documents qui ressemblent le plus au document 4
print(monDTM.nMostSimilar(3,5))
print(monDTM.nMostSimilar(1))
print(monDTM.nMostSimilar(1,0))
## les entrées incohérentes
print(monDTM.nMostSimilar(1,-2))
print(monDTM.nMostSimilar(56,13))
print(monDTM.nMostSimilar(-1,3))











