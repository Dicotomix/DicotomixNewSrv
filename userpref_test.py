#!/usr/bin/python3
# -*-coding:latin-1 -*

import numpy as np
import pandas as pd
from time import time

from Userpref import *


### TESTING ###

nbMotsLu = 0

if __name__ == "__main__":
    
    start = time()
    
    print("Creation des preferences utilisateur... ", end="")
    user_pref = Userpref()
    print("Done.\n")
    filename = "seconde_guerre.txt"
    
    i = 0
    #load the corpus to test
    with open(filename, "r", encoding="utf-8") as corpus:
        for line in corpus:
            i += 1
            print("Lecture de la ligne "+str(i))
            #remove last \n and get the list of words
            word_list = line.rstrip().split(' ')
            for word in word_list:
                user_pref.update_pref(word, verbose=False)
                nbMotsLu += 1
    
    totalTime = time() - start
    print('Test execute en {0:0.1f} secondes'.format(totalTime))
    print('Temps (s) moyen par mots : ' + str(totalTime/nbMotsLu) + "("+str(nbMotsLu)+ " mots au total)")
    print('Temps (s) moyen par lignes : ' + str(totalTime/i) + "("+str(i)+ " lignes au total)")
    user_pref.print_most_modif(15)
    