import numpy as np
import pandas as pd
import nltk
from bs4 import BeautifulSoup
import re
import os
import codecs
from sklearn import feature_extraction
import mpld3
from django.shortcuts import redirect,render, get_object_or_404
from django.urls import reverse
from .models import Patentes,NumerosPatentes
from nltk.stem.snowball import SnowballStemmer
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.cluster import KMeans
from sklearn.manifold import MDS
from IPython import get_ipython
import matplotlib.pyplot as plt
import matplotlib as mpl
import json 
from nltk.tag import pos_tag
#define custom toolbar location
class TopToolbar(mpld3.plugins.PluginBase):
    """Plugin for moving toolbar to top of figure"""

    JAVASCRIPT = """
    mpld3.register_plugin("toptoolbar", TopToolbar);
    TopToolbar.prototype = Object.create(mpld3.Plugin.prototype);
    TopToolbar.prototype.constructor = TopToolbar;
    function TopToolbar(fig, props){
        mpld3.Plugin.call(this, fig, props);
    };

    TopToolbar.prototype.draw = function(){
      // the toolbar svg doesn't exist
      // yet, so first draw it
      this.fig.toolbar.draw();

      // then change the y position to be
      // at the top of the figure
      this.fig.toolbar.toolbar.attr("x", 150);
      this.fig.toolbar.toolbar.attr("y", 400);

      // then remove the draw function,
      // so that it is not called again
      this.fig.toolbar.draw = function() {}
    }
    """
    def __init__(self):
        self.dict_ = {"type": "toptoolbar"}

# load nltk's SnowballStemmer as variabled 'stemmer'
stemmer = SnowballStemmer("english")

def strip_proppers_POS(text):
    tagged = pos_tag(text.split()) #use NLTK's part of speech tagger
    non_propernouns = [word for word,pos in tagged if pos != 'NNP' and pos != 'NNPS']
    return non_propernouns

def tokenize_and_stem(text):
                # first tokenize by sentence, then by word to ensure that punctuation is caught as it's own token
                tokens = [word for sent in nltk.sent_tokenize(text) for word in nltk.word_tokenize(sent)]
                filtered_tokens = []
                # filter out any tokens not containing letters (e.g., numeric tokens, raw punctuation)
                for token in tokens:
                        if re.search('[a-zA-Z]', token):
                                filtered_tokens.append(token)
                stems = [stemmer.stem(t) for t in filtered_tokens]
                return stems

def tokenize_only(text):
    # first tokenize by sentence, then by word to ensure that punctuation is caught as it's own token
    tokens = [word.lower() for sent in nltk.sent_tokenize(text) for word in nltk.word_tokenize(sent)]
    filtered_tokens = []
    # filter out any tokens not containing letters (e.g., numeric tokens, raw punctuation)
    for token in tokens:
        if re.search('[a-zA-Z]', token):
            filtered_tokens.append(token)
    return filtered_tokens

def obtenerdatos(patente):
        # Stopwords, stemming, and tokenizing
        titulo = []
        claims = []
        cip = []
        resumen = []
        
        for patent in patente:
                pais=patent.num_pat_pais.cod_pais
                cod=patent.cod_serie_patente
                codigo=str(pais)
                
                codigo+=str(cod)
                titulo.append(codigo)  
                claims.append(patent.patente.claims_patente)
                #print(claims)
                cip.append(patent.patente.clasificacion.cod_cip)
                resumen.append(patent.patente.resumen_patente)
                
        """print(str(len(titulo)) + ' titulo')
        print(str(len(claims)) + ' claims')
        print(str(len(cip)) + ' CIP')
        print(str(len(resumen)) + ' resumen')"""
        descripciones = []


        for i in range(len(claims)):
                item = claims[i] + resumen[i]
                item= re.sub(r'claims', '',item)
                item= re.sub(r'claimed', '',item)
                item= re.sub(r'claim', '',item)
                item= re.sub(r'method', '',item)
                item= re.sub(r'said', '',item)
                descripciones.append(item)

        # generates index for each item in the corpora (in this case it's just rank) and I'll use this for scoring later
        ranks = []
        for i in range(0,len(titulo)):
                ranks.append(i)

        # load nltk's English stopwords as variable called 'stopwords'
        #stopwords = nltk.corpus.stopwords.words('english')
        #print (stopwords[:10])
        
        
        totalvocab_stemmed = []
        totalvocab_tokenized = []
        for i in descripciones:
                allwords_stemmed = tokenize_and_stem(i)
                totalvocab_stemmed.extend(allwords_stemmed)
                
                allwords_tokenized = tokenize_only(i)
                totalvocab_tokenized.extend(allwords_tokenized)
        
        vocab_frame = pd.DataFrame({'words': totalvocab_tokenized}, index = totalvocab_stemmed)

        
        tfidf_vectorizer = TfidfVectorizer(max_df=0.8, max_features=200000,
                                        min_df=0.2, stop_words='english',
                                        use_idf=True, tokenizer=tokenize_and_stem, ngram_range=(1,3))

        tfidf_matrix = tfidf_vectorizer.fit_transform(descripciones)

        terms = tfidf_vectorizer.get_feature_names()
        #print(terms)

        
        dist = 1 - cosine_similarity(tfidf_matrix)

        num_clusters = 5

        km = KMeans(n_clusters=num_clusters)
        #print(km)
        km.fit(tfidf_matrix)

        clusters = km.labels_.tolist()
        #print (len(clusters))

        films = { 'title': titulo, 'rank': ranks, 'synopsis': descripciones, 'cluster': clusters, 'genre': cip }

        frame = pd.DataFrame(films, index = [clusters] , columns = ['rank', 'title', 'cluster', 'genre'])

        frame['cluster'].value_counts()
        grouped = frame['rank'].groupby(frame['cluster'])
        grouped.mean()

        #print("Top terms per cluster:")
        #print()
        order_centroids = km.cluster_centers_.argsort()[:, ::-1]
      
    #This is purely to help export tables to html and to correct for my 0 start rank (so that Godfather is 1, not 0)
        frame['Rank'] = frame['rank'] + 1
        frame['Title'] = frame['title']

        #export tables to HTML
        #print(frame[['Rank', 'Title']].loc[frame['cluster'] == 1].to_html(index=False))

        MDS()

        # two components as we're plotting points in a two-dimensional plane
        # "precomputed" because we provide a distance matrix
        # we will also specify `random_state` so the plot is reproducible.
        mds = MDS(n_components=2, dissimilarity="precomputed", random_state=1)

        pos = mds.fit_transform(dist)  # shape (n_components, n_samples)

        xs, ys = pos[:, 0], pos[:, 1]

        #set up colors per clusters using a dict
        cluster_colors = {0: '#1b9e77', 1: '#d95f02', 2: '#7570b3', 3: '#e7298a', 4: '#66a61e'}
        cluster_names  ={}
        #set up cluster names using a dict
        for i in range(num_clusters):
                referencias=''
                for ind in order_centroids[i, :6]:
                        referencias +=str(vocab_frame.ix[terms[ind].split(' ')].values.tolist()[0][0].encode('utf-8', 'ignore'))+','
                referencias= re.sub(r'b', '',referencias)
                cluster_names.update({i: referencias})

        df = pd.DataFrame(dict(x=xs, y=ys, label=clusters, title=titulo)) 

        #group by cluster
        groups = df.groupby('label')

        #define custom css to format the font and to remove the axis labeling
        css = """
        text.mpld3-text, div.mpld3-tooltip {
        font-family:Arial, Helvetica, sans-serif;
        }

        g.mpld3-xaxis, g.mpld3-yaxis {
        display: none; }"""
        

        # Plot 
        fig, ax = plt.subplots(figsize=(14,6)) #set plot size
        ax.margins(0.03) # Optional, just adds 5% padding to the autoscaling

        #iterate through groups to layer the plot
        #note that I use the cluster_name and cluster_color dicts with the 'name' lookup to return the appropriate color/label
        for name, group in groups:
                points = ax.plot(group.x, group.y, marker='o', linestyle='', ms=18, label=cluster_names[name], mec='none', color=cluster_colors[name])
                ax.set_aspect('auto')
                labels = [i for i in group.title]
                
                #set tooltip using points, labels and the already defined 'css'
                tooltip = mpld3.plugins.PointHTMLTooltip(points[0], labels,
                                                voffset=10, hoffset=10, css=css)
                #connect tooltip to fig
                mpld3.plugins.connect(fig, tooltip, TopToolbar())    
                
                #set tick marks as blank
                ax.axes.get_xaxis().set_ticks([])
                ax.axes.get_yaxis().set_ticks([])
                
                #set axis as blank
                ax.axes.get_xaxis().set_visible(False)
                ax.axes.get_yaxis().set_visible(False)

        
        ax.legend(numpoints=1) #show legend with only one dot

        #mpld3.show() #show the plot
        plt.close()
        #uncomment the below to export to html

        html = mpld3.fig_to_html(fig)
        #print(html)
        return(html)
        #return (request,"scraper/analisisresult2.html",{'figure':html})

        #DENDOGRAMA       
        """
        from scipy.cluster.hierarchy import ward, dendrogram

        linkage_matrix = ward(dist) #define the linkage_matrix using ward clustering pre-computed distances

        fig, ax = plt.subplots(figsize=(15, 20)) # set size
        ax = dendrogram(linkage_matrix, orientation="right", labels=titulo)

        plt.tick_params(\
        axis= 'x',          # changes apply to the x-axis
        which='both',      # both major and minor ticks are affected
        bottom='off',      # ticks along the bottom edge are off
        top='off',         # ticks along the top edge are off
        labelbottom='off')

        plt.tight_layout() #show plot with tight layout

        #uncomment below to save figure
        plt.savefig('ward_clusters.png', dpi=200) #save figure as ward_clusters
        plt.show()
        plt.close()
        """