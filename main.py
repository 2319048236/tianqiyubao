from datetime import date, datetime, timedelta
from collections import defaultdict
from wechatpy import WeChatClient, WeChatClientException
from wechatpy.client.api import WeChatMessage
from borax.calendars.lunardate import LunarDate
from random import randint
import math
import requests
import os
import re
import random
import emoji

nowtime = datetime.utcnow() + timedelta(hours=8)  # 东八区时间
today = datetime.strptime(str(nowtime.date()), "%Y-%m-%d") #今天的日期
today1 = LunarDate.today()

city = os.getenv('CITY')
start_date = os.getenv('START_DATE')
birthday = os.getenv('BIRTHDAY')

app_id = os.getenv('APP_ID')
app_secret = os.getenv('APP_SECRET')

user_ids = os.getenv('USER_ID', '').split("\n")
url="https://lab.magiconch.com/sakana/?v=takina"
template_id = os.getenv('TEMPLATE_ID')
#template_id = os.getenv('TEMPLATE_ID')

#为读取农历生日准备
lubaryear1 = today1.year
n = int(birthday[0:4:1])#读取无用，为理解下面两行留着，可删去
y = int(birthday[5:7])#切片
r = int(birthday[8:])
birthday1 = LunarDate(lubaryear1, y, r)#构建农历日期
birthday2 = birthday1.to_solar_date()#转化成公历日期，输出为字符串

if app_id is None or app_secret is None:
  print('请设置 APP_ID 和 APP_SECRET')
  exit(422)

if not user_ids:
  print('请设置 USER_ID，若存在多个 ID 用空格分开')
  exit(422)

if template_id is None:
  print('请设置 TEMPLATE_ID1')
  exit(422)
  
#if template_id2 is None:
  #print('请设置 TEMPLATE_ID2')
  #exit(422)

# weather 直接返回对象，在使用的地方用字段进行调用。
def get_weather():
  if city is None:
    print('请设置城市')
    return None
  url = "https://v0.yiketianqi.com/api?unescape=1&version=v61&appid=78158848&appsecret=650ylFRx&city=" + city
  res1 = requests.get(url,verify=False)
  if res1.status_code != 200:
    return res1()
  res11 = res1.json()
  return res11['week'],res11['alarm'],res11['aqi'], res11['win'],res11['win_speed'],res11['tem'], res11['tem2'], res11['tem1'],res11['air_tips']

#天行数据接口
def get_weather_wea():
  url = "http://api.tianapi.com/tianqi/index?key=d5edced4967c76fd11899dbe1b753d91&city=" + city
  res2 = requests.get(url,verify=False)
  if res2.status_code != 200:
    return res2()
  res21 = res2.json()['newslist'][0]
  return res21['sunrise'],res21['sunset'],res21['tips'],res21['weather'],res21['pop']

#星座
def get_xingzuo():
  url = "http://api.tianapi.com/star/index?key=d5edced4967c76fd11899dbe1b753d91&astro=双鱼座"
  xingzuo = requests.get(url,verify=False)
  if xingzuo.status_code != 200:
    return get_xingzuo()
  data = xingzuo.json()
  data = "今天的幸运颜色："+str(data['newslist'][5]["content"])+"\n双鱼座的你今日爱情指数："+str(data['newslist'][1]["content"])+"\n速配星座："+str(data['newslist'][7]["content"])+"\n财运指数："+str(data['newslist'][3]["content"])+"\n今天的你："+str(data['newslist'][8]["content"])
  return data

#疫情接口
def get_Covid_19():
  url = "https://covid.myquark.cn/quark/covid/data?city=" + city
  res3 = requests.get(url)
  if res3.status_code != 200:
    return res3()
  if city in ["北京", "上海", "天津", "重庆", "香港", "澳门", "台湾"]:
      res31 = res3.json()["provinceData"]
  else:
      res31 = res3.json()["cityData"]
  return res31["sure_new_loc"],res31["sure_new_hid"],res31["present"],res31["danger"]["1"], res31["danger"]["2"]

#农历接口
def get_lunar_calendar():
  date = today.strftime("%Y-%m-%d")
  url = "http://api.tianapi.com/lunar/index?key=d5edced4967c76fd11899dbe1b753d91&date=" + date
  lunar_calendar = requests.get(url,verify=False)
  if lunar_calendar.status_code != 200:
    return get_lunar_calendar()
  res3 = lunar_calendar.json()['newslist'][0]
  return res3['lubarmonth'],res3['lunarday'],res3['jieqi'],res3['lunar_festival'],res3['festival']

# 纪念日正数
def get_memorial_days_count():
  if start_date is None:
    print('没有设置 START_DATE')
    return 0
  delta = today - datetime.strptime(start_date, "%Y-%m-%d")
  return delta.days

# 生日倒计时
def get_birthday_left():
  if birthday is None:
    print('没有设置 BIRTHDAY')
    return 0
  next = datetime.strptime(birthday2.strftime("%Y-%m-%d"), "%Y-%m-%d")#先转换成datetime.date类型,再转换成datetime.datetime
  if next < datetime.now():
    next = next.replace(year=next.year + 1)
  return (next - today).days

#元旦节倒计时
def get_yuandan():
  yuandan = datetime.strptime(str(today.year) + "-" + "01" + "-" + "01", "%Y-%m-%d")#元旦
  next1 = (datetime.strptime(yuandan.strftime("%Y-%m-%d"), "%Y-%m-%d")-today).days
  if next1<0 or next1>15:
      return None
  elif next1>0 and next1<=15:
      next1 = "距离元旦还有"+str(next1)+"天"
  else:
      next1 = "元旦快乐！！！"
  return next1

#春节倒计时
def get_chunjie():
  spring_festival = LunarDate(lubaryear1, 1, 1).to_solar_date()
  next2 = (datetime.strptime(spring_festival.strftime("%Y-%m-%d"), "%Y-%m-%d")-today).days
  if next2<0 or next2>15:
      return None
  elif next2>0 and next2<=15:
      next2 = "距离大年初一还有"+str(next2)+"天"
  else:
      next2 = "过年好！恭喜发财"
  return next2

#踏青节倒计时
def get_taqing():
  sching_ming_festival = LunarDate(lubaryear1, 3, 5).to_solar_date()
  next3 = (datetime.strptime(sching_ming_festival.strftime("%Y-%m-%d"), "%Y-%m-%d")-today).days
  if next3<0 or next3>0:
      return None
  else:
      next3 = "况是清明好天气，不妨游衍莫忘归"
  return next3

#劳动节倒计时
def get_laodong():
  laodong = datetime.strptime(str(today.year) + "-" + "05" + "-" + "01", "%Y-%m-%d")
  next4 = (datetime.strptime(laodong.strftime("%Y-%m-%d"), "%Y-%m-%d")-today).days
  if next4<0 or next4>15:
      return None
  elif next4>0 and next4<=15:
      next4 = "距离劳动节还有"+str(next4)+"天"
  else:
      next4 = "三天休息日"
  return next4

#端午节倒计时
def get_duanwu():
  duanwu = LunarDate(lubaryear1, 5, 5).to_solar_date()
  next5 = (datetime.strptime(duanwu.strftime("%Y-%m-%d"), "%Y-%m-%d")-today).days
  if next5<0 or next5>15:
      return None
  elif next5>0 and next5 <= 15:
      next5 = "距离端午节还有"+str(next5)+"天"
  else:
      next5 = "今日宜划龙舟，吃粽子"
  return next5

#中秋节倒计时
def get_zhongqiu():
  mid_autumn_festival = LunarDate(lubaryear1, 8, 15).to_solar_date()
  next6 = (datetime.strptime(mid_autumn_festival.strftime("%Y-%m-%d"), "%Y-%m-%d")- today).days
  if  next6< 0:
      return None
  elif next6 > 0 and next6 <= 15:
      next6 = "距离中秋节还有"+str(next6)+"天"
  else:
      next6 = "春江潮水连海平，莲蓉豆沙冰淇淋"
  return next6

#国庆节节倒计时
def get_guoqing():
  guoqing = datetime.strptime(str(today.year) + "-" + "10" + "-" + "01", "%Y-%m-%d")
  next7 = (datetime.strptime(guoqing.strftime("%Y-%m-%d"), "%Y-%m-%d")-today).days
  if next7<0 or next7>15:
      return None
  elif next7>0 and next7<=15:
      next7 = "距离国庆节还有"+str(next7)+"天"
  else:
      next7 = "生在红旗下，长在春风里"
  return next7

# 彩虹屁 接口不稳定，所以失败的话会重新调用，直到成功
def get_words():
  words = requests.get("https://api.shadiao.pro/chp")
  if words.status_code != 200:
    return get_words()
  return words.json()['data']['text']

def format_temperature(temperature):
  return math.floor(temperature)

# 随机颜色
def get_random_color():
  return "#%06x" % random.randint(0, 0xFFFFFF)

try:
  client = WeChatClient(app_id, app_secret)
except WeChatClientException as e:
  print('微信获取 token 失败，请检查 APP_ID 和 APP_SECRET，或当日调用量是否已达到微信限制。')
  exit(502)

wm = WeChatMessage(client)
week,alarm1,aqi,win,win_speed,tem,tem1,tem2,air_tips = get_weather()
sunrise,sunset,tips,weather,pop = get_weather_wea()
lubarmonth,lunarday,jieqi,lunar_festival,festival = get_lunar_calendar()
sure_new_loc,sure_new_hid,present,danger1,danger2 = get_Covid_19()
jieri = get_yuandan(),get_chunjie(),get_taqing(),get_laodong(),get_duanwu(),get_zhongqiu(),get_guoqing()
jieri2 = ''.join(list(filter(None, jieri)))
alarm2 = alarm1.get('alarm_title')

def get_weather_icon(weather):
    weather_icon = "🌈"
    weather_icon_list = ["☀️",  "☁️", "⛅️",
                         "☃️", "⛈️", "🏜️", "🏜️", "🌫️", "🌫️", "🌪️", "🌧️"]
    weather_type = ["晴", "阴", "云", "雪", "雷", "沙", "尘", "雾", "霾", "风", "雨"]
    for index, item in enumerate(weather_type):
        if re.search(item, weather):
            weather_icon = weather_icon_list[index]
            break
    return weather_icon
  
if weather is None:
  print('获取天气失败')
  exit(422)
data = {
  "1": {
    "value":get_xingzuo(),
  },
  "2": {
    "value":"",
  },
  "3": {
    "value":today.strftime('%Y年%m月%d日')+week,
    "color": get_random_color()
  },
  "4": {
    "value": lubarmonth+lunarday+jieqi+lunar_festival+festival,
    "color": get_random_color()
  },
  "5":{
    "value":jieri2,
    "color": get_random_color()
  },
  "6": {
    "value": "",
    "color": get_random_color()
  },
  "7": {
    "value": get_weather_icon(weather)+weather,
    "color": get_random_color()
  },
  "8": {
    "value": "",
    "color": get_random_color()
  },
  "9": {
    "value": city,
    "color": get_random_color()
  },
  "a": {
    "value": "",
    "color": get_random_color()
  },
  "b": {
    "value": tem,
    "color": get_random_color()
  },
   "c": {
    "value": "",
    "color": get_random_color()
  },
  "d": {
    "value": tem1+"℃"+"~"+tem2+"℃",
    "color": get_random_color()
  },
  "e": {
    "value": "",
    "color": get_random_color()
  },
  "f": {
    "value": sunrise,
    "color": get_random_color()
  },
  "g": {
    "value": "",
    "color": get_random_color()
  },
  "h": {
    "value": sunset,
    "color": get_random_color()
  },
  "i": {
    "value": "",
    "color": get_random_color()
  },
  "j": {
    "value": win+win_speed,
    "color": get_random_color()
  },
  "k": {
    "value": "",
    "color": get_random_color()
  },
  "l": {
    "value": pop+"%",
    "color": get_random_color()
  },
  "m": {
    "value": "",
    "color": get_random_color()
  },
  "n": {
    "value": aqi['air_level'],
    "color": get_random_color()
  },
  "o": {
    "value": "",
    "color": get_random_color()
  },
  "p": {
    "value": sure_new_loc,
    "color": get_random_color()
  },
  "q": {
    "value": "",
    "color": get_random_color()
  },
  "r": {
    "value": sure_new_hid,
    "color": get_random_color()
  },
  "s": {
    "value": "",
    "color": get_random_color()
  },
  "t": {
    "value": present,
    "color": get_random_color()
  },
  "u": {
    "value": "",
    "color": get_random_color()
  },
  "v": {
    "value": str(danger1)+"/"+str(danger2),
    "color": get_random_color()
  },
  "w": {
    "value": alarm2,
    "color": "#FF0000"
  },
  "x": {
    "value": "",
    "color": get_random_color()
  },
  "y": {
    "value": get_memorial_days_count(),
    "color": get_random_color()
  },
  "z": {
    "value": "",
    "color": get_random_color()
  },
  "A": {
    "value": get_birthday_left(),
    "color": get_random_color()
  },
  "B": {
    "value": "",
    "color": get_random_color()
  },
  "C": {
    "value": tips,
    "color": get_random_color()
  },
  "D": {
    "value": "",
    "color": get_random_color()
  },
  "E": {
    "value": get_words(),
    "color": get_random_color()
  },
}

if __name__ == '__main__':
  count = 0
  try:
    for user_id in user_ids:
      res = wm.send_template(user_id, template_id, data,url)
      count+=1
  except WeChatClientException as e:
    print('微信端返回错误：%s。错误代码：%d' % (e.errmsg, e.errcode))
    exit(502)

  print("发送了" + str(count) + "条消息")
