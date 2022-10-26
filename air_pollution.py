import os
import csv
import numpy as np
import matplotlib.pyplot as plt

DataPath="D:\data\AirPollution"
class NotNumError(ValueError):
    '''异常处理'''
    def __init__(self,file,row,key):
        self.file=file
        self.row=row
        self.key=key
        self.message="{}的第{}行的{}值为空".format(file,row,key)
        

class DataAnalyze():
    '''读入数据,统计时间&空间分布'''
    def __init__(self,data_path):
        self.data_path=data_path
    
    def load_data(self):
        '''加载数据'''
        data_path=self.data_path
        data_dic={}
        for path in os.listdir(data_path):
            if path.split('.')[-1]=='csv':
                with open (data_path+'//'+path,mode='r',encoding='utf-8') as file:
                    data=list(csv.DictReader(file))
                washed=[]
                for i in range(len(data)):
                    row=data[i]
                    for key in row.keys():
                        try:
                            if row[key]=='' or row[key]=='NA':
                                raise NotNumError(path,i,key)
                        except NotNumError as nne:
                            print(nne.message)
                            row[key]=data[i-1][key]
                    washed.append(row)
                area=path.split('_')[2]
                data_dic[area]=washed
        self.data_dic=data_dic
    
    def TimeDistribution(self,area,*pullutions):
        '''时间分布'''
        pollutiondata=self.data_dic[area]
        time_distribution_data={}
        for poll in pullutions:
            data_lis=[0]*48
            datenum=[0]*48
            for row in pollutiondata:
                month=(int(row['year'])-2013)*12+int(row['month'])-3
                data_lis[month]+=float(row[poll])
                datenum[month]+=1
            for i in range(48):
                data_lis[i]/=datenum[i]
            time_distribution_data[poll]=data_lis
        return time_distribution_data
    
    def RoomDistribution(self,year,min_month,max_month,*pollutions):
        '''空间分布'''
        room_distribution_data={}
        for area in self.data_dic.keys():
            room_distribution_area_data={}
            pollutiondata=self.data_dic[area]
            for poll in pollutions:
                data_all=0
                day_num=0
                for row in pollutiondata:
                    if int(row['year'])==year and int(row['month'])>=min_month and int(row['month'])<=max_month:
                        data_all+=float(row[poll])
                        day_num+=1
                    else:
                        continue
                room_distribution_area_data[poll]=data_all/day_num
            room_distribution_data[area]=room_distribution_area_data
        return room_distribution_data
                
        
class DataView():
    '''对分析的结果进行可视化'''
    def __init__(self,time_data,room_data):
        self.time_data=time_data
        self.room_data=room_data

    def TimeView(self):
        time_data=self.time_data
        pollutions=time_data.keys()
        x=list(range(48))
        for poll in pollutions:
            y=time_data[poll]
            plt.plot(x,y)
        plt.xlabel('Time')
        plt.ylabel('Pollution')
        plt.legend(pollutions)
        x_tick=[]
        for i in range(len(x)):
            if (i+3)%12==0:
                x_tick.append(str(2013+(i+3)//12-1)+'.'+str(12))
            else:
                x_tick.append(str(2013+(i+3)//12)+'.'+str((i+3)%12))
        plt.xticks(x,x_tick,rotation=90)
        plt.show()
    
    def RoomView(self):
        room_data=self.room_data
        areas=list(room_data.keys())
        pollutions=list(room_data[areas[0]].keys())
        x=np.arange(len(areas))
        bar_width = 0.25
        num_poll=len(pollutions)
        for i in range(num_poll):
            poll=pollutions[i]
            y=[room_data[area][poll] for area in areas]
            plt.bar(x+bar_width*(i-(num_poll-1)/2),y,bar_width,label=poll)
        plt.xlabel('Room')
        plt.ylabel('Pollution')
        plt.xticks(x,labels=areas)
        plt.legend(pollutions)
        plt.show()
        

if __name__ == '__main__':
    pollution_data=DataAnalyze(DataPath)
    pollution_data.load_data()
    time_data=pollution_data.TimeDistribution('Changping','PM2.5','NO2','O3')
    room_data=pollution_data.RoomDistribution(2014,1,6,'PM2.5','SO2','NO2')
    view=DataView(time_data,room_data)
    view.TimeView()
    view.RoomView()
