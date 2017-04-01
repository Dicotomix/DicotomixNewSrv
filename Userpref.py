#!/usr/bin/python3
# -*-coding:latin-1 -*

import numpy as np
import pandas as pd


class Userpref:
    def __init__(self):
        #parameters
        self.factor = 1e7
        self.weight_scaling = 1e-5    #weight of the user preferences
        self.dictionary_name = "LexiqueCompletNormalise.csv"
        
        
        self.counted_words = 0  #number of words counted (to not have to sum all the time)
        self.user_pref = self.create_user_pref()
    
    
    def create_user_pref(self):
        #load the dictionary
        dico = pd.read_csv(self.dictionary_name, sep=";", encoding="utf-8")
        
        #keep only word and original frequency
        user_pref = dico[["word", "word_freq"]]	
        
        #merge same words together
        #note that here the indexes are now the words
        #access a "word info" with user_pref.loc["desired_word"]
        user_pref = user_pref.groupby("word").sum()
        
        #normalize it again on the factor = 1e7
        user_pref['word_freq'] = user_pref['word_freq']*1e7/user_pref['word_freq'].sum()
        
        #add a column for count words (this is what is used for user preferences)
        user_pref['added_count'] = 0
        
        #rename "word_freq" to "originalFreq" for clarity
        user_pref.rename(columns = {"word_freq" : "originalFreq"}, inplace = True)
        
        #create "actualFreq" for the frequency that will be used
        user_pref['actualFreq'] = user_pref['originalFreq']
        
        return user_pref
    
    
    def count_word(self, word, verbose = True):
        try:
            self.user_pref.ix[word, 'added_count'] += 1  #modify in place
            self.counted_words += 1
        except KeyError as err:
            if verbose:
                print("Error in count_word("+word+",user_pref) : the word '"+word+"' does not exist in the dictionnary.\n")
    
    
    #normalize first, but take care of word that have too low frequency to put them back to a threshold        
    def normalizeFreqs(self, freqs):
 
        threshold = 0.05
        freqs = self.factor*freqs/freqs.sum()
        
        weakPart = freqs[freqs < threshold]
        if len(weakPart) == 0:
            return freqs
        
        strongPart = freqs[freqs >= threshold]
        
        toRedistribute = len(weakPart)*threshold - weakPart.sum()
        
        #note : could not find how to set the Serie to threshold, keeping the indexes, hence this "thing"
        weakPart = weakPart - weakPart + threshold #put it to threshold
        
        strongPart -= toRedistribute/(len(strongPart))
        
        #merge again and put it back in good order
        newFreq = pd.concat([weakPart, strongPart]).sort_index()
        
        #renormalize it exactly to 'factor'
        return self.factor*newFreq/newFreq.sum()
            
    
            
    def get_added_freq(self):
        if self.counted_words == 0:
            return self.factor*self.user_pref['added_count']
        else:
            return self.factor*self.user_pref['added_count']/self.counted_words
    
        
    def get_real_freq(self):
        freqs = self.get_weight()*self.get_added_freq() + self.user_pref['originalFreq']
        
        return self.normalizeFreqs(freqs)
    
    
    def update_pref(self, word, verbose = True):
        self.count_word(word, verbose) #count the word
        
        #update the frequencies
        self.user_pref['actualFreq'] = self.get_real_freq()
    
    
    def get(self):
        return self.user_pref
    
    def get_counted_words(self):
        return sefl.counted_words
    
    def get_weight(self):
        return self.weight_scaling * self.counted_words
    
    def print_most_modif(self, size=10):
        most_modif = self.user_pref
        
       
        deltaFreq = self.user_pref["actualFreq"] - self.user_pref["originalFreq"]
        
        
        absDFreq = abs(deltaFreq) #to order
        
        most_modif = pd.concat([most_modif, deltaFreq, absDFreq], axis=1)
        most_modif.rename(columns = {0 : "deltaFreq", 1 : "absDFreq"}, inplace = True)
        
        most_modif = most_modif.sort_values('absDFreq', ascending=False)
        
        print ("Top "+str(size)+" most modified:")
        print(most_modif[0:size])
    