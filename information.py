# -*- coding: utf-8 -*-
import requests
import json
import datetime
from pyquery import PyQuery as pq
from apscheduler.schedulers.blocking import BlockingScheduler
import itchat


def getInfo():
    # get weather information
    url = "https://free-api.heweather.net/s6/weather/forecast?location=Mandalay&key=？"
    response = requests.get(url=url)
    text = json.loads(response.text)
    cityInfo = text['HeWeather6'][0]['basic']['location']
    forecast = text['HeWeather6'][0]['daily_forecast'][0]
    dateInfo = forecast['date']
    dayWeatherInfo = forecast['cond_txt_d']
    nightWeatherInfo = forecast['cond_txt_n']
    humidityInfo = forecast['hum']
    sunriseInfo = forecast['sr']
    sunsetInfo = forecast['ss']
    tmpMax = forecast['tmp_max']
    tmpMin = forecast['tmp_min']
    pop = forecast['pop']

    # get ONE information
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.87 Safari/537.36",
    }
    doc = pq(url="http://wufazhuce.com", headers=headers)
    wordsInfo = doc.find(".item.active").find(".fp-one-cita").text()

    # get time information
    today = datetime.datetime.today()
    start = datetime.datetime(2018, 2, 26)
    daysInfo = (today - start).days

    finalInfo = "早上好!今天是" + dateInfo + ".\n" + \
                cityInfo + "白天:" + dayWeatherInfo + \
                ",夜间:" + nightWeatherInfo + ",湿度:" + humidityInfo + "%.\n" \
                "今日最高温度:" + tmpMax + "℃,最低温度:" + tmpMin + "℃,降雨概率:" + pop + "%.\n" \
                "每日一句：" + wordsInfo + "\n" + \
                "今天是我们在一起的：" + str(daysInfo) + "天." + "\n" + \
                "日出时间:" + sunriseInfo + ".\n" \
                                        "日落时间:" + sunsetInfo + ".\n" + \
                "祝你拥有美好的一天."
    # print(finalInfo)
    return finalInfo


def sendMessage(user, message):
    print(user)
    print(message)
    itchat.send_msg(message, toUserName=user)


message = getInfo()
itchat.auto_login()
friend = itchat.search_friends(name="Bin")
user_name = friend[0]['UserName']

# send message on time
scheduler = BlockingScheduler()
scheduler.add_job(func=sendMessage, trigger='cron',
                  hour=8, minute=0, args=[user_name, message])
scheduler.start()


