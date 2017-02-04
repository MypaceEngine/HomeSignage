#!/usr/bin/python3
# -*- coding: utf-8 -*-

import sys
from PyQt5.QtWidgets import (QWidget, QToolTip,QSizePolicy,QApplication,QLabel,QVBoxLayout,QHBoxLayout,QSpacerItem,QStackedLayout,QFrame,QGridLayout)
from PyQt5.QtGui import (QFont, QPalette,QColor,QImage, QPixmap)
from PyQt5.QtCore import QTimer,Qt,QMetaObject,pyqtSlot,Q_ARG,QByteArray
from PyQt5.QtSvg import QSvgWidget
import datetime
import requests
import threading
import time
import feedparser
import re
import tweepy
from bs4 import BeautifulSoup
import const

WEEKDAY = ('月','火','水','木','金','土','日')
WINDDIRECTION=["北","北北東","北東","北東東","東","南東東","南東","南南東","南","南南西","南西","南西西","西","北西西","北西","北北西"]

FULLSCREEN=False
#FULLSCREEN=True

class BaseWidget(QWidget):

    def __init__(self):
        super().__init__()

        self.initUI()


    def initUI(self):

        QToolTip.setFont(QFont('SansSerif', 10))
        self.setStyleSheet('background-color: #000000;')

        layout = QVBoxLayout( self )

        timeLbl=QLabel(self)
        timeLbl.move(0,0)
        timeLbl.setStyleSheet("color: #FFFFFF; ")
        timeLbl.setFont(QFont('SansSerif', 45))
        timeLbl.setText("")
        timeLbl.setAlignment(Qt.AlignCenter)
        self.timeLbl=timeLbl

        layout.addWidget( timeLbl )


        self.bottomLayout=QStackedLayout(self)

        layoutWeather = QVBoxLayout( self )
        self.weatherlayoutT = QHBoxLayout( self )
        self.weatherlayoutB = QHBoxLayout( self )
        verticalSpacer = QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding)
        layoutWeather.addLayout(self.weatherlayoutT )
        layoutWeather.addItem(verticalSpacer)
        layoutWeather.addLayout(self.weatherlayoutB )
        layoutWeather.setContentsMargins(0, 0, 0, 0)
        layoutWeather.setSpacing(0)
        weatherPanel=QFrame(self)
        weatherPanel.setLayout(layoutWeather)

        self.presureMap=QLabel(self)
        self.presureMap.setAlignment(Qt.AlignCenter)

        self.grassMap=QSvgWidget(self)

        pal = QPalette(self.grassMap.palette())
        pal.setColor(QPalette.Background, QColor("#FFFFFF"))
        self.grassMap.setPalette(pal)

        self.googleTrendLayout=QGridLayout(self);
        googleTrendPanel=QFrame(self)
        googleTrendPanel.setLayout(self.googleTrendLayout)

        self.financeTrendLayout=QHBoxLayout(self);
        self.financeTrendLayout.setContentsMargins(0, 0, 0, 0)
        self.financeTrendLayout.setSpacing(0)
        self.financeTrendLayout_LEFT=QVBoxLayout(self);
        self.financeTrendLayout_LEFT.setContentsMargins(0, 0, 0, 0)
        self.financeTrendLayout_LEFT.setSpacing(0)
        self.financeTrendLayout_CENTER=QVBoxLayout(self);
        self.financeTrendLayout_CENTER.setContentsMargins(0, 0, 0, 0)
        self.financeTrendLayout_CENTER.setSpacing(0)
        self.financeTrendLayout_RIGHT=QVBoxLayout(self);
        self.financeTrendLayout_RIGHT.setContentsMargins(0, 0, 0, 0)
        self.financeTrendLayout_RIGHT.setSpacing(0)
        self.financeTrendLayout.addLayout(self.financeTrendLayout_LEFT)
        self.financeTrendLayout.addLayout(self.financeTrendLayout_CENTER)
        self.financeTrendLayout.addLayout(self.financeTrendLayout_RIGHT)
        self.financeTrendPanel=QFrame(self)
        self.financeTrendPanel.setLayout(self.financeTrendLayout)


        self.bottomLayout.addWidget(weatherPanel)
        self.bottomLayout.addWidget(self.presureMap)
        self.bottomLayout.addWidget(googleTrendPanel)
        self.bottomLayout.addWidget(self.financeTrendPanel)
        self.bottomLayout.addWidget(self.grassMap)

        layout.addLayout(self.bottomLayout)

        self.setWindowTitle('Signage')

        if FULLSCREEN :
            self.showFullScreen()
        else :
            self.setFixedSize(800,480)
            self.show()

        self.chgCount=0;
        self.time_draw()

        timeTimer = QTimer(self)
        timeTimer.timeout.connect(self.time_draw)
        timeTimer.start(1000)

        self.execWeather();
        self.execWeatherMap()
        self.exectrend_load()

        self.finance_draw()
        self.execfinance_draw()
        self.execGrass()

    def chgPanel(self):
        try:
            stackIndex=self.bottomLayout.currentIndex()
            stackIndex=stackIndex+1
            if stackIndex >= self.bottomLayout.count():
                stackIndex=0
            self.bottomLayout.setCurrentIndex(stackIndex)
        except:
            print(sys.exc_info())

    def time_draw(self):
        try:
            date= datetime.datetime.today()

            daystr="%d/%02d/%02d(%s)     %02d:%02d" % (date.year, date.month, date.day, WEEKDAY[date.weekday()],date.hour,date.minute)
            self.timeLbl.setText(daystr)

            self.chgCount=self.chgCount+1
            if(self.chgCount>20):
                self.chgPanel();
                self.chgCount=0;
        except:
            print(sys.exc_info())

    def execGrass(self):
        self.grass_draw()
        weatherTimer = threading.Timer(60,self.execGrass)
        weatherTimer.start()

    def grass_draw(self):
        try:
            ru = requests.get("https://github.com/"+const.GITHUB_ID)
            if(ru.status_code==200):
                weather=ru.text
                weather2=re.sub("\n","",weather)
                weather2=re.sub("\r","",weather2)


                pattern = r"<svg[^>]*class=\"js-calendar-graph-svg\">.*?<\/svg>"
                matchOB = re.search(pattern , str(weather2))
                ss=matchOB.group(0)

                ss = re.sub(r'<svg', '<svg xmlns=\"http://www.w3.org/2000/svg\"', ss)
                ss = re.sub(r'<text [^>]* class=\"month\">[^>]*</text>',"", ss)
                ss = re.sub(r'<text text-anchor=\"start\" class=\"wday\" [^>]*>[^>]*</text>',"", ss)
                QMetaObject.invokeMethod(self, "grass_draw_exec", Qt.QueuedConnection,Q_ARG(str, ss))
        except:
            print(sys.exc_info())

    @pyqtSlot(str)
    def grass_draw_exec(self,svginfo):
        self.grassMap.load(QByteArray(svginfo.encode('utf-8')))

    def execWeather(self):
        self.weather_draw()
        weatherTimer = threading.Timer(60,self.execWeather)
        weatherTimer.start()

    def weather_draw(self):
        try:

                r = requests.get('http://api.openweathermap.org/data/2.5/weather?id='+const.OPENWEATHERMAP_ID+'&APPID='+const.OPENWEATHERMAP_APPID)
                if(r.status_code==200):
                    weather=r.json()
                    r = requests.get('http://api.openweathermap.org/data/2.5/forecast?id='+const.OPENWEATHERMAP_ID+'&APPID='+const.OPENWEATHERMAP_APPID)
                    if(r.status_code==200):
                        weatherList=r.json()["list"]
                        QMetaObject.invokeMethod(self, "weather_draw_exec", Qt.QueuedConnection, Q_ARG(object, weather), Q_ARG(object, weatherList))
        except:
            print(sys.exc_info())

    @pyqtSlot(object,object)
    def weather_draw_exec(self,weather,weatherList):
        try:
            while self.weatherlayoutT.count() >0:
                self.weatherlayoutT.removeItem(self.weatherlayoutT.itemAt(0))
            while self.weatherlayoutB.count() >0:
                self.weatherlayoutB.removeItem(self.weatherlayoutB.itemAt(0))
            date= datetime.datetime.today()

            daystr="%02d:%02d" % (date.hour,date.minute)
            item= WeatherPanel()
            item.setInfo(daystr,weather,273.15)
            self.weatherlayoutT.addLayout(item)
            count=0;
            index=0
            for num in range(0, 9):
    #            format = "%Y/%m/%d %H:%M:%S"
                if weatherList[num]["dt"]>time.time() :
                    format = "%H:%M"
                    jst_date = time.strftime(format,time.localtime(weatherList[num]["dt"]))
                    formatH="%H"
                    jst_hour=time.strftime(formatH,time.localtime(weatherList[num]["dt"]))
                    if jst_hour=="00" :
                        verticalSpacer2 = QLabel()
                        verticalSpacer2.setStyleSheet('background-color: #ffffff;')
                        verticalSpacer2.setFixedWidth(5)
                        self.weatherlayoutT.addWidget(verticalSpacer2)
                    item= WeatherPanel()
                    item.setInfo(jst_date,weatherList[num],271.15)
                    self.weatherlayoutT.addLayout(item)
                    count=count+1
                if(count>6):
                    index=num;
                    break

            index=index+1
            for num in range(index, index+8):
                format = "%H:%M"
                jst_date = time.strftime(format,time.localtime(weatherList[num]["dt"]))
                formatH="%H"
                jst_hour=time.strftime(formatH,time.localtime(weatherList[num]["dt"]))
                if jst_hour=="00" :
                    verticalSpacer2 = QLabel()
                    verticalSpacer2.setStyleSheet('background-color: #ffffff;')
                    verticalSpacer2.setFixedWidth(5)
                    self.weatherlayoutB.addWidget(verticalSpacer2)
                item= WeatherPanel()
                item.setInfo(jst_date,weatherList[num],271.15)
                self.weatherlayoutB.addLayout(item)

            self.weatherlayoutT.update()
            self.weatherlayoutB.update()
        except:
            print(sys.exc_info())


    def execWeatherMap(self):
        self.weatherMap_draw()
        weatherMapTimer = threading.Timer(3600,self.execWeatherMap)
        weatherMapTimer.start()

    def weatherMap_draw(self):
        try:
            currentTime=time.time()
            while currentTime>0 :
                curremtTimeInfo=time.localtime(currentTime)

                year=curremtTimeInfo[0]-2000
                month=curremtTimeInfo[1]
                day=curremtTimeInfo[2]
                hour=curremtTimeInfo[3]
                presuremapTime="%02d%02d%02d%02d" % (year,month,day,hour)
                presureMapUrl=str("http://www.jma.go.jp/jp/g3/images/jp_c/")+presuremapTime+str(".png")
                ri = requests.get(presureMapUrl)
                if(ri.status_code==200):
                    image = QImage()
                    image.loadFromData(ri.content)
                    presureMapPixMap=QPixmap(image)

                    presureMapPixMap=presureMapPixMap.scaled(380, 380, Qt.KeepAspectRatioByExpanding, Qt.FastTransformation)
                    QMetaObject.invokeMethod(self, "weatherMap_draw_exec", Qt.QueuedConnection, Q_ARG("QPixmap", presureMapPixMap))
                    break
                currentTime=currentTime-3600
        except:
            print(sys.exc_info())

    @pyqtSlot(QPixmap)
    def weatherMap_draw_exec(self,presureMapPixMap):
        try:
            self.presureMap.setPixmap(presureMapPixMap)
            self.presureMap.update()
        except:
            print(sys.exc_info())


    def exectrend_load(self):
        self.trend_load()
        trendTimer = threading.Timer(300,self.exectrend_load)
        trendTimer.start()

    def trend_load(self):
        try:
            while self.googleTrendLayout.count() >0:
                self.googleTrendLayout.removeItem(self.googleTrendLayout.itemAt(0))

            googleTrendResponse = feedparser.parse("https://www.google.co.jp/trends/hottrends/atom/hourly")
            p = re.compile(r"<[^>]*?>")
            googleTrendArr=p.sub("", googleTrendResponse.entries[0].content[0].value).replace(" ","").strip().split("\n")



            auth = tweepy.OAuthHandler(const.TWITTER_CONSUMER_KEY, const.TWITTER_CONSUMER_SECRET)
            auth.set_access_token(const.TWITTER_ACCESS_TOKEN, const.TWITTER_ACCESS_SECRET)

            api = tweepy.API(auth)

            trends_available=api.trends_place(id=const.TWITTER_PLACE)
            twitterTrend=trends_available[0]["trends"]

            QMetaObject.invokeMethod(self, "trend_load_exec", Qt.QueuedConnection, Q_ARG(object, googleTrendResponse), Q_ARG(object, googleTrendArr), Q_ARG(object, trends_available), Q_ARG(object, twitterTrend))
        except:
            print(sys.exc_info())

    @pyqtSlot(object,object,object,object)
    def trend_load_exec(self,googleTrendResponse,googleTrendArr,trends_available,twitterTrend):
        try:
            while self.googleTrendLayout.count() >0:
                self.googleTrendLayout.removeItem(self.googleTrendLayout.itemAt(0))

            label=CustomLabel()
            label.setAlignment(Qt.AlignLeft)
            eachFont=QFont('SansSerif', 15)
            eachFont.setBold(True)
            label.setFont(eachFont)
            label.setText("Google Hot Trends\n("+ googleTrendResponse.feed.updated+")")
            self.googleTrendLayout.addWidget(label,0,0,2,2)

            trendloaderNum=len(googleTrendArr)
            if trendloaderNum>20:
                trendloaderNum=20

            for num in range(0,trendloaderNum):
                label=CustomLabel()
                label.setAlignment(Qt.AlignLeft)
                label.setFont(QFont('SansSerif', 15))
                label.setText(googleTrendArr[num])
                label.setFixedWidth(175)
                row1=int(num/(trendloaderNum/2))
                row2=num%(trendloaderNum/2)
                self.googleTrendLayout.addWidget(label,row2+2,row1)

            label=CustomLabel()
            label.setAlignment(Qt.AlignLeft)
            eachFont=QFont('SansSerif', 15)
            eachFont.setBold(True)
            label.setFont(eachFont)
            label.setText("Twitter Hot Trends\n("+ trends_available[0]["created_at"]+")")
            self.googleTrendLayout.addWidget(label,0,2,2,2)

            trendloaderNum=len(googleTrendArr)
            if trendloaderNum>20:
                trendloaderNum=20

            for num in range(0,trendloaderNum):
                label=CustomLabel()
                label.setAlignment(Qt.AlignLeft)
                label.setFont(QFont('SansSerif', 15))
                label.setFixedWidth(175)
                label.setText(twitterTrend[num]["name"])
                row1=int(num/(trendloaderNum/2))
                row2=num%(trendloaderNum/2)
                self.googleTrendLayout.addWidget(label,row2+2,row1+2)

            self.googleTrendLayout.update()
        except:
            print(sys.exc_info())

    def execfinance_draw(self):
        self.finance_draw()
        financeTimer = threading.Timer(300,self.execfinance_draw)
        financeTimer.start()

    def finance_draw(self):
        try:

            r = requests.get("https://query.yahooapis.com/v1/public/yql?q=select%20*%20from%20yahoo.finance.xchange%20where%20pair%20in%20(%22USDJPY,EURJPY,GBPJPY%22)&format=json&env=store%3A%2F%2Fdatatables.org%2Falltableswithkeys")
            rateList=r.json()["query"]["results"]["rate"]
            list = []

            for num in range(0,2):
                ri=requests.get("http://ichart.finance.yahoo.com/z?z=b&t=5d&s="+rateList[num]["id"]+"=X&size=z");
                if(ri.status_code==200):
                    image = QImage()
                    image.loadFromData(ri.content)
                    stackExPixMap=QPixmap(image)
                    stackExPixMap=stackExPixMap.scaled(240, 120, Qt.KeepAspectRatioByExpanding, Qt.FastTransformation)
                    info={}
                    info["txt"]=rateList[num]["Name"]+" "+rateList[num]["Rate"]
                    info["pixMap"]=stackExPixMap
                    list.append(info)

            ri=requests.get("http://ichart.finance.yahoo.com/z?z=b&t=5d&s="+rateList[2]["id"]+"=X&size=z");
            if(ri.status_code==200):
                image = QImage()
                image.loadFromData(ri.content)
                stackExPixMap=QPixmap(image)
                stackExPixMap=stackExPixMap.scaled(240, 120, Qt.KeepAspectRatioByExpanding, Qt.FastTransformation)
                info={}
                info["txt"]=rateList[2]["Name"]+" "+rateList[2]["Rate"]
                info["pixMap"]=stackExPixMap
                list.append(info)


            symbol,stockprice = self.get_stockprice("^DJI")
            ri=requests.get("https://ichart.finance.yahoo.com/v?s=^DJI");
            if(ri.status_code==200):
                image = QImage()
                image.loadFromData(ri.content)
                stackExPixMap=QPixmap(image)
                stackExPixMap=stackExPixMap.scaled(240, 120, Qt.KeepAspectRatioByExpanding, Qt.FastTransformation)
                info={}
                info["txt"]=symbol+ " "+stockprice
                info["pixMap"]=stackExPixMap
                list.append(info)

            symbol,stockprice = self.get_stockprice("998407.O")
            ri=requests.get("https://chart.yahoo.co.jp/?code=998407.O&tm=5d&size=e");
            if(ri.status_code==200):
                image = QImage()
                image.loadFromData(ri.content)
                stackExPixMap=QPixmap(image)
                stackExPixMap=stackExPixMap.scaled(240, 120, Qt.KeepAspectRatioByExpanding, Qt.FastTransformation)
                info={}
                info["txt"]=symbol+ " "+stockprice
                info["pixMap"]=stackExPixMap
                list.append(info)

            symbol,stockprice = self.get_stockprice("6758.T")
            ri=requests.get("https://chart.yahoo.co.jp/?code=6501.T&tm=5d&size=e&vip=off");
            if(ri.status_code==200):
                image = QImage()
                image.loadFromData(ri.content)
                stackExPixMap=QPixmap(image)
                stackExPixMap=stackExPixMap.scaled(240, 120, Qt.KeepAspectRatioByExpanding, Qt.FastTransformation)
                info={}
                info["txt"]=symbol+ " "+stockprice
                info["pixMap"]=stackExPixMap
                list.append(info)

            QMetaObject.invokeMethod(self, "finance_draw_exec", Qt.QueuedConnection, Q_ARG(object, list))

        except:
            print(sys.exc_info())

    @pyqtSlot(object)
    def finance_draw_exec(self,list):
        try:
            while self.financeTrendLayout_LEFT.count() >0:
                self.financeTrendLayout_LEFT.removeItem(self.financeTrendLayout_LEFT.itemAt(0))
            while self.financeTrendLayout_CENTER.count() >0:
                self.financeTrendLayout_CENTER.removeItem(self.financeTrendLayout_CENTER.itemAt(0))
            while self.financeTrendLayout_RIGHT.count() >0:
                self.financeTrendLayout_RIGHT.removeItem(self.financeTrendLayout_RIGHT.itemAt(0))

            for num in range(0,len(list)):
                label=CustomLabel()
                label.setText(list[num]["txt"])
                label.setContentsMargins(0, 0, 0, 0)

                stockExImglabel=QLabel()
                stockExImglabel.setAlignment(Qt.AlignCenter)
                stockExImglabel.setPixmap(list[num]["pixMap"])
                stockExImglabel.setContentsMargins(0, 0, 0, 0)

                if num <2:
                    self.financeTrendLayout_LEFT.addWidget(label)
                    self.financeTrendLayout_LEFT.addWidget(stockExImglabel)
                elif num<4:
                    self.financeTrendLayout_CENTER.addWidget(label)
                    self.financeTrendLayout_CENTER.addWidget(stockExImglabel)
                else:
                    self.financeTrendLayout_RIGHT.addWidget(label)
                    self.financeTrendLayout_RIGHT.addWidget(stockExImglabel)

            self.financeTrendPanel.update()
            self.financeTrendLayout.update()
            self.financeTrendLayout_LEFT.update()
            self.financeTrendLayout_CENTER.update()
            self.financeTrendLayout_RIGHT.update()
        except:
            print(sys.exc_info())



    def get_stockprice(self,code):
        try:
            base_url = "http://stocks.finance.yahoo.co.jp/stocks/detail/"
            query = {}
            query["code"] = code
            ret = requests.get(base_url,params=query)
            if(ret.status_code==200):
                soup = BeautifulSoup(ret.content,"lxml")
                stocktable =  soup.find('table', {'class':'stocksTable'})
                symbol =  stocktable.findAll('th', {'class':'symbol'})[0].text
                stockprice = stocktable.findAll('td', {'class':'stoksPrice'})[1].text
                return symbol,stockprice
            else:
                return "",""
        except:
            print(sys.exc_info())

class CustomLabel(QLabel):
    def __init__(self):
        super().__init__()
        self.setStyleSheet("color: #FFFFFF; ")
        self.setFont(QFont('SansSerif', 15))
        self.setContentsMargins(0, 0, 0, 0)
        self.setAlignment(Qt.AlignCenter)

class WeatherPanel(QVBoxLayout):

    def __init__(self):
        super().__init__()
        self.setContentsMargins(0, 0, 0, 0)
        self.setSpacing(0)
        self.initUI()


    def initUI(self):
        try:
            self.dateLbl=CustomLabel()

            self.imgLbl=QLabel()
            self.imgLbl.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred)
            self.imgLbl.setAlignment(Qt.AlignCenter)
            self.imgLbl.setStyleSheet('background-color: #888888;')

            self.templatureLbl=CustomLabel()


            self.winddirecLbl=CustomLabel()
            self.windspeedLbl=CustomLabel()
            self.presureLbl=CustomLabel()

            self.addWidget( self.dateLbl )
            self.addWidget( self.imgLbl )
            self.addWidget( self.templatureLbl )
            self.addWidget( self.winddirecLbl )
            self.addWidget( self.windspeedLbl )
            self.addWidget( self.presureLbl )
#        self.addWidget( self.humidyLbl )
        except:
            print(sys.exc_info())

    def setInfo(self,date,weather,fix_template):
        try:
            iconUrl=str("http://openweathermap.org/img/w/")+str(weather["weather"][0]["icon"])+str(".png")
            ri = requests.get(iconUrl)
            image = QImage()
            image.loadFromData(ri.content)
            weatherPixMap=QPixmap(image)
            templature=str(int(weather["main"]["temp"]-fix_template))

            directTani=360/len(WINDDIRECTION)
            windDict=WINDDIRECTION[0]
            windSpeed=str(int(weather["wind"]["speed"]))+"m"
            if "deg"in weather["wind"] :
                for num in range(0, len(WINDDIRECTION)):
                    if (directTani/2) > abs(weather["wind"]["deg"]-num*directTani):
                        windDict=WINDDIRECTION[num]
            else:
                windDict="-"
            self.dateLbl.setText(date)
            self.imgLbl.setPixmap(weatherPixMap)
            self.templatureLbl.setText(templature+"℃")
            self.winddirecLbl.setText(windDict)
            self.windspeedLbl.setText(windSpeed)
            self.presureLbl.setText(str(int(weather["main"]["pressure"]))+"hPa")
#        self.humidyLbl.setText(str(int(weather["main"]["humidity"]))+"%")
        except:
            print(sys.exc_info())

if __name__ == '__main__':

    app = QApplication(sys.argv)
    ex = BaseWidget()
    sys.exit(app.exec_())