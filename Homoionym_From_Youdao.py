# -*- coding: utf-8 -*
import os
import re
import time
import json
import platform
import requests
import ConfigParser
from bs4 import BeautifulSoup
import numpy as np
import sys
reload(sys)
sys.setdefaultencoding('utf8')
def session_youdao(url):
    header = {
        'User-Agent': "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:34.0) Gecko/20100101 Firefox/34.0",
        'Host': "www.youdao.com",
        'Referer': "http://dict.youdao.com/",
        'X-Requested-With': "XMLHttpRequest"
    }
    session = requests.Session()
    r = session.post('http://dict.youdao.com/', headers=header)
    #urllib3.disable_warnings()
    try:
      conte=session.get(url)
    except Exception,e:
      print "waiting 10 seconds and restart again"
      time.sleep(10)
      session_youdao(url)
      #conte=session.get(url)
    return conte.content
def session_urban(url):
    header = {
        'User-Agent': "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:34.0) Gecko/20100101 Firefox/34.0",
        'Host': "http://www.urbandictionary.com",
        'Referer': "http://www.urbandictionary.com/define.php",
        'X-Requested-With': "XMLHttpRequest"
    }
    session = requests.Session()
    r = session.post('http://www.urbandictionary.com', headers=header)
    #urllib3.disable_warnings()
    try:
      conte=session.get(url)
    except Exception,e:
      print "waiting 10 seconds and restart again"
      time.sleep(10)
      session_urban(url)
      #conte=session.get(url)
    return conte.content
def youdao_homoionym(word):
    try:
        url='http://dict.youdao.com/search?q='+word
        conte=session_youdao(url)
        soup = BeautifulSoup(conte,'html.parser')
        hom_words_raw=soup.find_all("div",id='synonyms')[0].find_all("a")
        words=[]
        for hom_word in hom_words_raw:
            words.append(hom_word.text.encode('utf-8'))
    except Exception,e:
        words=False
    return words
def urban_homoionym(word):
    try:
        url='http://www.urbandictionary.com/define.php?term='+word
        conte=session_urban(url)
        soup = BeautifulSoup(conte,'html.parser')
        # print soup
        senti_up=soup.find_all("a",class_="up")[0].find_all("span",class_="count")[0].text.encode('utf-8')
        senti_dowm=soup.find_all("a",class_="down")[0].find_all("span",class_="count")[0].text.encode('utf-8')
        # print senti_raw_up,senti_raw_dowm
        hom_words_raw=soup.find_all("div",class_='tags-panel')[0].find_all("a")
        senti=[int(senti_up),int(senti_dowm)]
        words=[]
        for hom_word in hom_words_raw:
            words.append(hom_word.text.encode('utf-8'))

    except Exception,e:
        words=False
        senti=False
    return (words,senti)
    # return words

def read_seed_dic(seed_file):
    seed_dic={}
    lens=10
    lines=open(seed_file,'r').readlines()

    for i in range(len(lines)):
        arr=lines[i].strip().split('\t')
        word=arr[0]
        if not seed_dic.has_key(word):
            seed_dic[word]=[0]*10
        
        if arr[1]=='anger' and arr[2]=='0':
            seed_dic[word][0]=0
        elif arr[1]=='anger' and arr[2]=='1':
            seed_dic[word][0]=1
        elif arr[1]=='anticipation' and arr[2]=='0':
            seed_dic[word][1]=0
        elif arr[1]=='anticipation' and arr[2]=='1':
            seed_dic[word][1]=1
        elif arr[1]=='disgust' and arr[2]=='0':
            seed_dic[word][2]=0
        elif arr[1]=='disgust' and arr[2]=='1':
            seed_dic[word][2]=1
        elif arr[1]=='fear' and arr[2]=='0':
            seed_dic[word][3]=0
        elif arr[1]=='fear' and arr[2]=='1':
            seed_dic[word][3]=1
        elif arr[1]=='joy' and arr[2]=='0':
            seed_dic[word][4]=0
        elif arr[1]=='joy' and arr[2]=='1':
            seed_dic[word][4]=1
        elif arr[1]=='negative' and arr[2]=='0':
            seed_dic[word][5]=0
        elif arr[1]=='negative' and arr[2]=='1':
            seed_dic[word][5]=1
        elif arr[1]=='positive' and arr[2]=='0':
            seed_dic[word][6]=0
        elif arr[1]=='positive' and arr[2]=='1':
            seed_dic[word][6]=1
        elif arr[1]=='sadness' and arr[2]=='0':
            seed_dic[word][7]=0
        elif arr[1]=='sadness' and arr[2]=='1':
            seed_dic[word][7]=1
        elif arr[1]=='surprise' and arr[2]=='0':
            seed_dic[word][8]=0
        elif arr[1]=='surprise' and arr[2]=='1':
            seed_dic[word][8]=1
        elif arr[1]=='trust' and arr[2]=='0':
            seed_dic[word][9]=0
        elif arr[1]=='trust' and arr[2]=='1':
            seed_dic[word][9]=1

    return seed_dic
#通过seed字典，结合有道近义词的分布，找出每一个词语的情感倾向
def build_sword_dic():
    print "building the seed dic..."
    seed_dic=read_seed_dic('Word_Sentiment_Seed.txt')

    def sentiment(word):
        pos = seed_dic[word][1]+seed_dic[word][4]+seed_dic[word][6]+seed_dic[word][8]+seed_dic[word][9]
        neg = seed_dic[word][0]+seed_dic[word][2]+seed_dic[word][3]+seed_dic[word][5]+seed_dic[word][7]    
        if pos>neg:
            return 1
        elif pos==neg:
            return 0
        else:
            return -1
    def sentiment_dis(senti_dis):
        pos = senti_dis[1]+senti_dis[4]+senti_dis[6]+senti_dis[8]+senti_dis[9]
        neg = senti_dis[0]+senti_dis[2]+senti_dis[3]+senti_dis[5]+senti_dis[7]    
        if pos>neg:
            return 1
        elif pos==neg:
            return 0
        else:
            return -1   

    def find_word_sentiment(word):
        from_youdao=False
        from_urban=True     
        if word in seed_dic:
            senti=sentiment(word)
            print "%s is in seed_dic"%(word)
            if senti==1:
                
                fw.write(line+'\t'+'1'+'\n')
            elif senti==0:
                fw.write(line+'\t'+'0'+'\n')
            else:
                fw.write(line+'\t'+'-1'+'\n')
            return True

        else:
            if youdao_homoionym(word) and from_youdao:
                relate_words_youdao=youdao_homoionym(word)
                conterset_youdao=[wor for wor in relate_words_youdao if wor in seed_dic]
            # if len(conterset_youdao)>0:
                senti_dis=np.array([0]*10)
                for wordi in conterset_youdao:
                    senti_dis+=np.array(seed_dic[wordi])
                senti_youdao=sentiment_dis(senti_dis)
            else:
                senti_youdao=False
                
            if urban_homoionym(word)[0] and from_urban:
                relate_words_urban,cons_urban=urban_homoionym(word)
                conterset_urban=[wor for wor in relate_words_urban if wor  in seed_dic]
                senti_dis=np.array([0]*10)
                for wordi in conterset_urban:
                    senti_dis+=np.array(seed_dic[wordi])
                senti_urban=sentiment_dis(senti_dis)
                
            else:
                senti_urban=False
            if from_urban and from_youdao:
                if senti_youdao:
                    print "%s is in youdao and senitment is %d"%(word,senti_youdao)
                    fw.write(line+'\t'+str(senti_youdao)+'\n')
                    return True
                elif senti_urban:
                    print "%s is in urban and senitment is %d"%(word,senti_urban)
                    fw.write(line+'\t'+str(senti_urban)+'\n')
                    return True
                else:
                    return False
            elif from_urban and not from_youdao:
                if senti_urban:
                    print "%s is in urban and senitment is %d"%(word,senti_urban)
                    fw.write(line+'\t'+str(senti_urban)+'\n')
                    return True
                else:
                    return False


        # else:
        #     return False

    print "building the sentiment word dic..."
    fname='dict_sentiment_both.txt'
    
    word_done=[]
    for line_done in open(fname,'r').readlines():
        wordj=line_done.strip().split('\t')[0]
        word_done.append(wordj)
    fw=open(fname,'a')

    for line in open('dict.txt','r').readlines():

        line=line.strip()
        word = line.split('\t')[0]
        if word in word_done:
            pass
        else:
            if find_word_sentiment(word):
                pass
            else:
                if find_word_sentiment(word_complete_1(word)):
                    pass
                elif find_word_sentiment(word_complete_2(word)):
                    pass
                elif find_word_sentiment(word_complete_3(word)):
                    pass
                else:
                    print "%s is in no place.."%(word)
                    fw.write(line+'\t'+'0'+'\n')

def word_complete_1(word):
    if word[-1]=="i":
        word=word[:-1]+'y'
    elif word[-3:-1]=="ie":
        word=word[:-2]+'y'
    else:
        word=word+'e'
    return word
def word_complete_2(word):
    return word+'er'
def word_complete_3(word):
    return word+'al'                   
seed_dic=read_seed_dic('Word_Sentiment_Seed.txt')
words_urban,senti=urban_homoionym('disturb')
words_youdao=youdao_homoionym('let')
print words_urban 
print words_youdao
# print [wor for wor in words_urban if wor in words_youdao]
# print [wor for wor in words_urban if wor in seed_dic]
print [wor for wor in words_youdao if wor in seed_dic] 

# build_sword_dic()