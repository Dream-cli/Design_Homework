import os
import sys
from tqdm import tqdm
from pysnooper import snoop
from functools import wraps
from playsound import playsound
from memory_profiler import profile
from line_profiler import LineProfiler


SoundPath="D:\\data\\Decorate\\sound"
OutPath="D:\\data\\Decorate\\test"
filePath="D:\\data\\Decorate\\aas\\a.txt"

def PathDecorator(func):
    def wrapper(path):
        if os.path.exists(path):
            if os.path.isfile(path):
                path = os.path.dirname(path)
                print('路径为文件而非文件夹,已更改路径为当前文件所在文件夹,路径为{}'.format(path))
        else:
            print('路径不存在')
            os.makedirs(path)
            print('文件夹创建完成')
        func(path)
    return wrapper

@PathDecorator
def save(path):
    pass

class SoundDecorator():
    def __init__(self,flag=0):
        self.flag=flag
    
    def ring(self,arg):
        t=type(arg)
        if t == int:
            playsound(SoundPath+"\\"+"1.mp3")
        elif t == tuple:
            playsound(SoundPath+"\\"+"2.mp3")
        elif t == list or t==str or t==dict:
            playsound(SoundPath+"\\"+"3.mp3")
        else:
            playsound(SoundPath+"\\"+"4.mp3")
    
    def __call__(self,func):
        @wraps(func)
        def wrapper(*args):
            res=func(*args)
            if self.flag == 1:
                for r in res:
                    self.ring(r)
            else:
                self.ring(res)
            return res
        return wrapper

@SoundDecorator(flag=0)
def sound1(a,b):
    return a, (a,b,a+b),str(a),[a,b]

@SoundDecorator(flag=1)
def sound2(a,b):
    return a, (a,b,a+b)

def OutPutDecorator(outputpath):
    def wrapper0(func):
        def wrapper1(*args):
            save_stdout=sys.stdout
            with open (outputpath,mode='w')as file:
                sys.stdout=file
                func(*args)
            sys.stdout=save_stdout
        return wrapper1
    return wrapper0

lp=LineProfiler()
class TestDecorate():
    def __init__(self):
        pass
    
    @OutPutDecorator(filePath)
    def output(self):
        for i in range(10**5):
            print("----"+"{}".format(str(i))+"----")
    
    @lp
    def loop_0(self):
        count=0
        for i in range(10):
            count+=1
    
    
    @profile(precision=4)
    def loop_1(self):
        count=0
        for i in range(10**5):
            count+=1
    
    
    def loop_2(self):
        count=0
        for i in tqdm(range(10*8)):
            count+=1
    
    @snoop()
    def loop_3(self):
        count=0
        for i in range(10):
            count+=1


if __name__=='__main__':
    save("D:\\data\\Decorate\\ad")
    save(filePath)
    sound1(1,2)
    sound2(1,2)
    TestDecorate().output()
    print('\n\nline_profiler\n\n')
    TestDecorate().loop_0()
    lp.print_stats()
    print('\n\nmemory_profiler\n\n')
    TestDecorate().loop_1()
    print('\n\ntqdm\n\n')
    TestDecorate().loop_2()
    print('\n\npysnooper \n\n')
    TestDecorate().loop_3()