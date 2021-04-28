import string
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import time

from math import log
from tqdm import tqdm



class WordTool():
    """
    初始化wordtool对象，挂载文章
    
    args:
        article(string/list) : 目标文章
        
    returns:
        WordTool
    """
    def __init__(self,article):
        # 确保article为list类型
        if type(article)==type("hello world"):
            self.article=[article]
        else:
            self.article=article
            
        self.totalCharCount=self.getWordCount() # 文章总汉字个数
        print("文章加载成功，一共%s段文字，合计%s个汉字。"%(len(article),self.totalCharCount))
        
        self.pool=set() # 根据文章生成的所有单词组合
        self.candidates=dict() # 从pool中选取出现频数较多的一部分单词
        
        self.punc="""\n--——，。？！：；“”"'‘’,.，。、【 】 “”：；（）《》‘’{}？！⑦()、%^>℃：.”“^-——=&#@￥"""
        self.number="""0123456789"""
        self.letter="".join(list(string.ascii_lowercase)+list(string.ascii_uppercase))
        
    def getWordCount(self,word=None):
        """
        统计单词/字符出现的次数，如果不提供参数，
        返回文章总汉字个数（去除数字、空格、标点符号）
        
        args:
            word(string)
        return
            int
        """
        count=0
        
        if word is None: # 统计文章总汉字个数
            for para in self.article:
                for char in para:
                    if '\u4e00'<= char <= '\u9fa5' and char not in "0123456789 ":
                        count+=1
        else: # 统计word出现次数         
            for para in self.article:
                count+=para.count(word)

        return count
    
    def getCandidates(self,sentence,d):
        """
        从句子中找出所有可能的单词组合
        
        args:
            setence(string)
            d(int) : maximum length of word to be found
        returns:
            set
        """
        windows=[(0,i) for i in range(2,d+1)] # 生成滑动窗口
        result=set()

        words=[] # 这里用一个list方便删除操作
        # 循环每个窗口
        for w in windows:
            # 长度为n的窗口，在长度为s的句子上可以滑动出s-n+1个词
            for i in range(len(sentence)-w[1]+1):
                start=w[0]+i
                end=w[1]+i
                word=sentence[start:end]

                # 检测word是否都是汉字，
                words.append(word)
                for char in word:
                    if '\u4e00'<= char <= '\u9fa5':
                        pass
                    else:
                        words.pop()
                        break

        result.update(set(words))

        return result
    
    def setPool(self,d):
        """
        根据最大词长d，生成所有可能单词组合
        
        args:
            d(int)
        returns:
            更新self.pool
        """
        for para in tqdm(self.article):
            self.pool.update(self.getCandidates(para,d))

        time.sleep(0.5) # 这句没啥用，为了美观
        print("生成%s种可能单词组合"%(len(self.pool)))
        
    def countPool(self):
        """
        为pool中的单词统计词频
        
        returns:
            更新self.pool
        """
        temp=dict()
        for word in tqdm(self.pool):
            temp[word]=self.getWordCount(word)
        self.pool=temp
    
    def setCandidates(self,min_freq):
        """
        初步筛选候选词
        
        args:
            min_freq(int) : 词频阈值，频数>=此数才会被考虑
            
        returns:
            更新self.candidates
        """
        for word,freq in tqdm(self.pool.items()):
            if freq>=min_freq:
                self.candidates[word]={'freq':freq}

        time.sleep(0.5) # 这句没啥用，为了美观
        print("共筛选出%s个频数大于%s的单词"%(len(self.candidates),min_freq))
        
    def getNeighboor(self,word):
        """
        统计单词左邻字和右邻字的出现次数
        
        args:
            word(string)
        returns:
            neightboor_l(dict) : 左邻字
            neightboor_r(dict) : 左邻字
        """
        neightboor_l=dict()
        neightboor_r=dict()

        for string in self.article:
            length=len(string)
            start=0
            while True:
                index=string.find(word,start)
                if index==-1: # 无结果
                    break
                if index==0 and length==len(word): # 有结果且单词和句子重合
                    char_l="<BOS>"
                    char_r="<EOS>"
                elif index==0: # 有结果且在开头
                    char_l="<BOS>"
                    char_r=string[index+len(word)]
                elif index==length-len(word): # 有结果且在末尾
                    char_l=string[index-1]
                    char_r="<EOS>"
                else: # 有结果，在句子中间
                    char_l=string[index-1]
                    char_r=string[index+len(word)]
                
                # 如果左右邻字是标点符号，标记出来
                if char_l in self.punc:
                    char_l="<BOS>"
                if char_r in self.punc:
                    char_r="<EOS>"
                    
                # 如果左右邻字是字母，标记出来
                if char_l in self.letter:
                    char_l="<LETTER>"
                if char_r in self.letter:
                    char_r="<LETTER>"
                    
                # 如果左右邻字是数字，标记出来
                if char_l in self.number:
                    char_l="<NUM>"
                if char_r in self.number:
                    char_r="<NUM>"
                
                
                # 将左邻字、右邻字更新到neightboor中
                if char_l in neightboor_l:
                    neightboor_l[char_l]+=1
                else:
                    neightboor_l[char_l]=1
                if char_r in neightboor_r:
                    neightboor_r[char_r]+=1
                else:
                    neightboor_r[char_r]=1
                start=index+1

        return neightboor_l,neightboor_r
    
    def getEntropy(self,neighboor):
        """
        计算平均信息熵
        
        args:
            neightboor(dict) : 邻字以及其出现次数
            
        returns:
            float
        """
        count=sum(value for _,value in neighboor.items())
        result=sum(-log(value/count)*(value/count) for _,value in neighboor.items())

        return result
        
    def setCandidatesEntropy(self):
        """
        获取candidates的左右邻字，并更新信息熵
        
        returns:
            更新self.candidates
        """
        for word,_ in tqdm(self.candidates.items()):
            l,r=self.getNeighboor(word)
            
            self.candidates[word]["neighboor_left"]=l
            self.candidates[word]["neighboor_right"]=r
            self.candidates[word]["entropy_left"]=self.getEntropy(l)
            self.candidates[word]["entropy_right"]=self.getEntropy(r)
    
    def p(self,word):
        """
        计算字或者词在原文中出现的概率
        """
        return self.getWordCount(word)/self.totalCharCount
    
    def getCondensity(self,word):
        """
        计算单词的凝聚度
        """

        # 单词分成2份，共有length-1种分法
        combinations=[]
        n=len(word)-1
        for i in range(n):
            l=word[0:i+1]
            r=word[i+1:]
            combinations.append((l,r))

        condensity=[]
        for pattern in combinations:
            condensity.append(self.p(word)/(self.p(pattern[0])*self.p(pattern[1])))

        return min(condensity)
    
    def setCondensity(self):
        for word,_ in tqdm(self.candidates.items()):
            self.candidates[word]['condensity']=self.getCondensity(word)
    
    def display(self,
                sort="freq",
                min_freq=0,
                min_entropy_left=0,
                min_entropy_right=0,
                min_condensity=0,
                user_dict=None
               ):
        """
        按照阈值展示词表，
        如果提供已知词表给user_dict参数，则只展示新词
        
        args:
            sort(string) : freq,entropy_left,entropy_right,condensity

        returns:
            pd.Dataframe
            更新self.data为展示的词表
        """
        data=[]
        for word,info in self.candidates.items():
            if user_dict is not None:
                if word in user_dict:
                    continue
            f=info['freq']
            el=info['entropy_left']
            er=info['entropy_right']
            c=info['condensity']
            if f>=min_freq and el>=min_entropy_left and er>=min_entropy_right and c>=min_condensity:
                data.append([word,f,el,er,c])

        # sort
        if sort=="freq":
            data.sort(key=lambda x:x[1],reverse=True)
        elif sort=="entropy_left":
            data.sort(key=lambda x:x[2],reverse=True)
        elif sort=="entropy_right":
            data.sort(key=lambda x:x[3],reverse=True)
        else:
            data.sort(key=lambda x:x[4],reverse=True)

        d = {'频数':[i[1] for i in data],
             '左信息熵':[i[2] for i in data],
             '右信息熵':[i[3] for i in data],
             '右右信息熵':[i[2]+i[3] for i in data],
             '凝聚度':[i[4] for i in data]
            }
        pd.set_option('display.max_rows', None)
        df=pd.DataFrame(d,index=[i[0] for i in data])
        self.data=data

        return df

    def generateDict(self,path,seg="  "):
        """
        输入分词过的文章，自动生成词表
        
        args:
            path(string) : path to article
            seg(string) : word seg token
            
        return:
            set
        """
        result=set()
        with open(path,encoding="utf-8") as f:
            content=f.readlines()
        
        for para in content:
            word_list=para.split(seg)
            temp=[]
            for word in word_list:
                if len(word)<=1:
                    continue
                temp.append(word)
                for char in word:
                    if '\u4e00'<= char <= '\u9fa5':
                        pass
                    else:
                        temp.pop()
                        break
            result.update(temp)
            
        print("共检索到%s个单词"%(len(result)))
        return result