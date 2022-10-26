import os
from PIL import Image
from PIL import ImageFilter
import  matplotlib.pyplot as plt

Imagedir_Path='E://code-markdown//现代程序设计//week6'

class Filter:
    '''Filter基类'''
    def __init__(self,image,*data):
        self.image=image
        self.data=data
        
class Filter_contour(Filter):
    '''边缘提取子类'''
    def process(self):
        return self.image.filter(ImageFilter.CONTOUR)

class Filter_sharpen(Filter):
    '''锐化处理子类'''
    def process(self):
        return self.image.filter(ImageFilter.SHARPEN)

class Filter_blur(Filter):
    '''模糊处理子类'''
    def process(self):
        return self.image.filter(ImageFilter.BLUR)
    
class Filter_zoom(Filter):
    '''缩放处理子类'''
    def process(self):
        rate=self.data[0]
        width=int(self.image.size[0]*rate)
        height=int(self.image.size[1]*rate)
        return self.image.resize((width,height))

class Filter_crop(Filter):
    '''裁剪处理子类'''
    def process(self):
        box=list(self.data[:4])
        width=int(self.image.size[0])
        height=int(self.image.size[1])
        box[0]*=width
        box[1]*=height
        box[2]*=width
        box[3]*=height
        return self.image.crop(box)

class ImageShop:
    def __init__(self,image_type,image_path):
        self.type=image_type
        self.path=image_path
    
    def load_images(self):
        '''从路径加载特定格式的图片并返回图片实例列表'''
        image_type=self.type
        file_path=self.path
        image_lis=[]
        if os.path.isfile(file_path):
            image_lis.append(Image.open(file_path))
        else:
            for file in os.listdir(file_path):
                if file.split('.')[-1]==image_type:
                    image_lis.append(Image.open(file_path+'//'+file))
        self.imageslist=image_lis
    
    def __batch_ps(self,image_lis,subfilter,*data):
        '''处理图片的内部方法'''
        image_lis_new=[]
        for image in image_lis:
            image_lis_new.append(subfilter(image,*data).process())
        return image_lis_new
    
    def batch_ps(self,*data):
        '''处理图片的外部方法'''
        filters=[]
        for item in data:
            if type(item)==type:
                filters.append([item])
            else:
                filters[-1].append(item)
        image_lis=self.imageslist
        for filter in filters:
            image_lis=self.__batch_ps(image_lis,*filter)
        self.processedimage=image_lis
    
    def display(self,image_lis,row,col):
        '''处理效果展示'''
        for i in range(row*col):
            if i>=len(image_lis):
                break
            plt.subplot(row,col,i+1)
            plt.axis('off')
            plt.imshow(image_lis[i])
        plt.show()
    
    def save_images(self,imagelis,path,name):
        '''保存处理过的图片'''
        for i in range (len(imagelis)):
            imagelis[i].save(path+'//'+name+str(i)+'.jpg')

class TestImageShop:
    '''测试类'''
    def __init__(self):
        imageshop_1=ImageShop('jpg',Imagedir_Path)
        imageshop_1.load_images()
        imageshop_1.batch_ps(Filter_contour,
                             Filter_sharpen,
                             Filter_blur,
                             Filter_zoom,2,
                             Filter_crop,0,0.1,0.9,0.8)
        imageshop_1.display(imageshop_1.imageslist,2,3)
        imageshop_1.display(imageshop_1.processedimage,2,3)
        image1=imageshop_1.imageslist[2]
        imagelis=[]
        imagelis.append(Filter_contour(image1).process())
        imagelis.append(Filter_sharpen(image1).process())
        imagelis.append(Filter_blur(image1).process())
        imagelis.append(Filter_zoom(image1,1.5).process())
        imagelis.append(Filter_crop(image1,0.25,0.25,0.7,0.7).process())
        imageshop_1.display(imagelis,2,3)
        imageshop_1.save_images(imagelis,Imagedir_Path,'processed_')
                

if __name__=='__main__':
    TestImageShop()