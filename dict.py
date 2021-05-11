def load_dict(fileName):
    """
    读取词典文件
    """
    word_list = []
    with open(fileName, "r", encoding="utf8") as f:
        # 按行读取词典文件，去掉行末换行符
        for word in f:
            word_list.append(word.strip())
    return set(word_list)



def topN(word_list,N):
    """
    display N longest word in word_list
    
    args:
        word_list(set/list)
        N : top N longest you want to see
    
    returns:
        list : top N longest words with length
    """
    word_list=list(word_list)
    word_list.sort(key=lambda i:len(i),reverse=True)
    
    return [[word,"len: "+str(len(word))] for word in word_list[:N]]