import re
import jieba

WordPath='E:/code-Python/week5/final_none_duplicate.txt'
NUM=1525757#总数据量1825757

class Tokenizer:
    def __init__(self, chars, coding, PAD = 0):
        '''输入需要操作的文本完成词典的构建'''
        self.chars=chars
        self.coding=coding
        self.PAD=PAD        
        length=len(chars)
        count=0
        char_list=[]
        for char in chars:
            if count%1000==0:
                print('\rProcessing chars...%4.2f'%(100*count/length)+'%',end='')
            if coding=='c':
                char_list+=list(char)
            elif coding=='w':
                char_list+=list(jieba.cut(char))                
            count+=1
        print('\rProcessing chars...100.00%')    
        char_list=list(set(char_list))
        self.word_dic={'[PAD]':PAD}
        self.num_dic={PAD:'[PAD]'}
        for i in range(len(char_list)):
            print('\rCreating dictionary...%4.2f'%(100*i/len(char_list))+'%',end='')
            self.word_dic[char_list[i]]=i+1+PAD
            self.num_dic[i+1+PAD]=char_list[i]
        print('\rCreating dictionary...100.00%')
    
    def tokenize(self,sentence):
        '''输入一句话，返回分词(字)以后的列表(list_of_chars)'''
        if self.coding=='c':
            return list(sentence)
        elif self.coding=='w':
            return list(jieba.cut(sentence))
    
    def encode(self,list_of_chars):
        '''输入字符的列表返回转换后的数字列表(tokens)'''
        tokens=[]
        for char in list_of_chars:
            tokens.append(self.word_dic[char])
        return tokens
    
    def trim(self,tokens,seq_len):
        '''输入数字列表, 整理数字列表的长度,长度不足的用PAD补足,超过的部分截断'''
        if len(tokens)<seq_len:
            tokens+=[self.PAD]*(seq_len-len(tokens))
        else:
            tokens=tokens[:seq_len]
        return tokens
    
    def decode(self,tokens):
        '''将模型输出的数字列表翻译回句子,如果有PAD则输出"[PAD]" '''
        sentence=''
        for x in tokens:
            sentence+=self.num_dic[x]
        return sentence
    
    def encode_all(self,seq_len):
        '''返回所有文本的长度为seq_len的tokens'''
        list_seq_len_tokens=[]
        length=len(self.chars)
        count=0
        for char in self.chars:
            if count%1000==0:
                print('\rEncoding chars...%4.2f'%(100*count/length)+'%',end='')
            list_seq_len_tokens.append(self.trim(self.encode(self.tokenize(char)),seq_len))
            count+=1
        return list_seq_len_tokens
    
def wash(path):
    '''文本清洗并返回列表'''
    with open (path,encoding='utf-8')as file:
        txt_list=[s.rstrip() for s in file.readlines()]
    count=0
    txt=[]
    for line in txt_list[:NUM]:
        if count % 1000 ==0:
            print('\rWash the data...%4.2f'%float(100*count/NUM)+'%',end='')
        l=line.split('\t')[1]
        #利用正则表达式去除不需要的信息
        text = re.sub(r'(我在这里:|我在:)?http:\\/\\/t.cn\\/.*', "",l)  #去除网址
        text = re.sub('[\[][^\[\]]*[\]]', '', text) #去除方括号中的内容
        text = re.sub('#[^#]+#', '', text)     #去除话题/title
        text = re.sub('@[^\s]+', '', text)     #去除@信息
        text = re.sub('分享图片', '', text)     
        text = re.sub('\s', '', text)           #去除空白字符
        txt.append(text)
        count+=1
    print('\rWash the data...100.00%')
    return txt
   

def build_seq_len(txt_list):
    '''文本的长度分布来寻找合适的seq_len'''
    c_count={}
    w_count={}
    length=len(txt_list)
    count=0
    for item in txt_list:
        if count%1000==0:
            print('\rCalculating the distribution of length...%4.2f'%(100*count/length)+'%',end='')
        c_num=len(list(item))
        w_num=len(list(jieba.cut(item)))
        c_count[c_num]=c_count.get(c_num,0)+1
        w_count[w_num]=w_count.get(w_num,0)+1
        count+=1
    print('\rCalculating the distribution of length...100.00%')
    c_sort_count=sorted(c_count.items(),key=lambda x: x[1])
    w_sort_count=sorted(w_count.items(),key=lambda x: x[1])
    print('按照字构建:')
    print(c_sort_count[-10:])
    print('按照词构建:')
    print(w_sort_count[-10:])
            

if __name__ == '__main__':
    word_lis=wash(WordPath)
    #build_seq_len(word_lis)
    tokenizer=Tokenizer(word_lis,'w')
    all_tokens = tokenizer.encode_all(10)
    for tokens in all_tokens:
        print(tokens, ':\n', tokenizer.decode(tokens))
    