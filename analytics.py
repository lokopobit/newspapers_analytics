# -*- coding: utf-8 -*-
"""
Created on Tue Sep 29 19:11:55 2020

@author: lokopobit
"""


from sklearn.feature_extraction.text import CountVectorizer
import numpy as np

# Calculate the ngram containment for one answer file/source file pair in a df
def calculate_containment(a_text, s_text, n):
    '''Calculates the containment between a given answer text and its associated source text.
       This function creates a count of ngrams (of a size, n) for each text file in our data.
       Then calculates the containment by finding the ngram count for a given answer text, 
       and its associated source text, and calculating the normalized intersection of those counts.
    '''  
    
    try:
        counts = CountVectorizer(analyzer='word', ngram_range=(n,n))
        ngrams = counts.fit_transform([a_text, s_text])
        ngram_array = ngrams.toarray()
        
        a_text0 = np.array(ngram_array[0])
        # s_text0 = np.array(ngram_array[1])
        
        inter = sum(min(a_s) for a_s in list(zip(ngram_array[0].tolist(), ngram_array[1].tolist())))
        return inter / np.sum(a_text0)
    except:
        # print('ERROR: Cannot compute containment')
        return 0
	

# Compute the normalized LCS given an answer text and a source text
def lcs_norm_word(a_text, s_text):
    '''Computes the longest common subsequence of words in two texts; returns a normalized value.
       :param answer_text: The pre-processed text for an answer text
       :param source_text: The pre-processed text for an answer's associated source text
       :return: A normalized LCS value'''
    
    try:
        a_list = a_text.split()
        s_list = s_text.split()
        
        init_mat = np.zeros((len(s_list)+1, len(a_list)+1))
        for i in range(1, len(s_list)+1):
            for j in range(1, len(a_list)+1):
                if s_list[i-1] == a_list[j-1]: # diagonal addition
                    
                    init_mat[i,j] = init_mat[i-1,j-1] + 1
                else: # max of top/left values
                    init_mat[i,j] = max(init_mat[i,j-1], init_mat[i-1,j])
                    
        
        return init_mat[-1,-1] / len(a_list)
    except:
        return 0
