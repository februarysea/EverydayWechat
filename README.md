
#### 写在前面

之前看到[@sfyc23](https://github.com/sfyc23/EverydayWechat)大佬在GitHub上的项目想着改一下也弄一个给女朋友，可是大佬的天气查询只支持国内，女朋友现在人在国外交流，只好磨磨蹭蹭按照大佬的思路自己弄了一个。

<!-- more -->
---

#### 基本思路

- [和风天气API](https://www.heweather.com/)-获得天气数据
- [requests](https://github.com/kennethreitz/requests) - 网络请求库
- [pyquery](https://github.com/gawel/pyquery) - jquery的python版本
- [datetime](https://docs.python.org/3/library/datetime.html) - 简便的日期计算库 
- [itchat](https://github.com/littlecodersh/ItChat) - 微信个人号接口
- [APScheduler](https://apscheduler.readthedocs.io/en/latest/) - 定时任务

使用`和风天气API`来得到当地天气预报的基本数据；通过`requests`+`pyquery`从[一个](http://wufazhuce.com/)中获得每天更新的句子；通过`datetime`处理日期方面的数据；利用`itchat`与微信进行通信；利用`APScheduler`和服务器实现每日定时执行的操作，效果如下。

#### 具体实现

- 获取数据

  1. **获取天气数据**

     [和风天气](https://www.heweather.com/)的天气数据开发是一个强大、现代化、开发友好的天气数据服务。

     我仅仅只是调试+每天早上发送数据的时候调用API，使用量并不大，注册普通用户已经足够了。在控制台新建应用会得到一个`key`，之后的调用就要通过这个`key`来验证身份。创建好之后，参考[常规天气数据API](https://dev.heweather.com/docs/api/weather)，就可以得到返回数据。在python中使用`requests`来获取数据。

     ```pyhthon
     url = "https://free-api.heweather.net/s6/weather/{weather-type}?{parameters}"
     ```

     `{weather-type}` 代表不同的天气数据类型有：`now`、`forecast`、`hourly`、`lifestyle`，免费用户只能使用`now`或者`forecast`。`{parameters}`表示可选参数：`location`、`lang`、`unit`、`key` ，在程序中仅需要用到`location`和`key`，`location`可以有很多种选择，比如城市名称、城市ID等等，在程序中使用了城市名称，更多请参阅[[城市列表](https://dev.heweather.com/docs/refer/city)]。`key`就是刚刚新建应用的时候的`key`。

     ```
     url = "https://free-api.heweather.net/s6/weather/forecast?location=Mandalay&key=???" //Mandalay替换成想查询的城市 把???替换成自己的key
     response = requests.get(url=url) 
     text = json.loads(response.text)   //将获得的数据转换成json格式
     ```

     返回的数据一共包括了未来好几天的天气预测，因为程序每天都运行，所以仅需要当天的天气预测即可。

     ```json
     {"HeWeather6": [{
       "basic":{
         "cid":"MM1311874",
         "location":"曼德勒",
         "parent_city":"曼德勒",
         "admin_area":"曼德勒省",
         "cnty":"缅甸",
         "lat":"21.97699928",
         "lon":"96.09200287",
         "tz":"+6.50"}
     },
     
       "update":{
         "loc":"2019-06-03 16:28",
         "utc":"2019-06-03 09:58"},
       "status":"ok",
     
       "daily_forecast":[{
         "cond_code_d":"305",
         "cond_code_n":"305",
         "cond_txt_d":"小雨",
         "cond_txt_n":"小雨",
         "date":"2019-06-03",
         "hum":"79",
         "mr":"05:11",
         "ms":"18:42",
         "pcpn":"4.3",
         "pop":"62",
         "pres":"984",
         "sr":"05:21",
         "ss":"18:46",
         "tmp_max":"34",
         "tmp_min":"26",
         "uv_index":"3",
         "vis":"12",
         "wind_deg":"176",
         "wind_dir":"南风",
         "wind_sc":"1-2","wind_spd":"11"}]}]}
     
     ```

     将得到的数据用`json`表示后，仅留下当天的预测数据。具体参数请参阅[参数对应描述](https://dev.heweather.com/docs/api/weather)。

     ```python
     cityInfo = text['HeWeather6'][0]['basic']['location']
     forecast = text['HeWeather6'][0]['daily_forecast'][0]
     dateInfo = forecast['date']
     dayWeatherInfo = forecast['cond_txt_d']
     nightWeatherInfo = forecast['cond_txt_n']
     humidityInfo = forecast['hum']
     tmpMax = forecast['tmp_max']
     tmpMin = forecast['tmp_min']
     pop = forecast['pop']
     ```

     上面的数据就是需要的天气数据，可以根据自己的需要增加或减少。

  2. **获取一个句子数据**

     [一个](http://wufazhuce.com/)中每日句子的获取比较简单。

     在请求中添加 头部来模拟浏览器访问。

     ```python
     headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.87 Safari/537.36"}
     ```

     使用`pyquery`获取并解析数据，通过chrome的开发者模式观察网页的源码，找到需要句子的特征并提取提取。

     ```python
     doc = pq(url="http://wufazhuce.com", headers=headers)
     wordsInfo = doc.find(".item.active").find(".fp-one-cita").text()
     ```

  3. **获取日期数据**

     使用`datetime`库来计算日期是比较方便的，在这里我计算了我和女朋友在一起的时间和她会过的时间。值得一提的是，用`start`之类的自己创建的日期与`today`相减时会显示到具体的毫秒，在后面添加了`.days`用来获取天数。

     ```python
     today = datetime.datetime.today()
     start = datetime.datetime(2018, 2, 26)
     leave = datetime.datetime(2019, 9, 9)
     daysInfo = (today - start).days
     leaveInfo = (leave - today).days
     ```

  4. **数据汇总**

     数据汇总仅仅是将上述信息汇集成一个字符串。

     ```python
     finalInfo = "早上好!今天是" + dateInfo + ".\n" + \
                  cityInfo + "白天:" + dayWeatherInfo + \
                  ",夜间:" + nightWeatherInfo + ",湿度:" + humidityInfo + "%.\n" \
                  "今日最高温度:" + tmpMax + "℃,最低温度:" + tmpMin + "℃,降雨概率:" + pop +"%.\n" \
                  "每日一句：" + wordsInfo + "\n" + \
                  "今天是我们在一起的：" + str(daysInfo) + "天." + "\n" + \
                  "距离宝贝回家还有：" + str(leaveInfo) + "天." + "\n" + \
                  "祝你拥有美好的一天."
     ```

- 登录微信

  ```python
  itchat.auto_login()
  friend = itchat.search_friends(name="username")  //将username替换成好友的备注
  user_name = friend[0]['UserName']  
  ```

  [itchat](https://github.com/littlecodersh/ItChat)原理是利用python模拟网页，登录网页微信来对微信进行各种处理。执行`itchat.auto_login()后会出现二维码，扫码完成后等一会儿，就会看见控制台输出登录成功的消息。

  官方文档说`search_friends`方法可以搜索用户，有四种搜索方式： 1. 仅获取自己的用户信息 2. 获取特定`UserName`的用户信息 3. 获取备注、微信号、昵称中的任何一项等于`name`键值的用户 4. 获取备注、微信号、昵称分别等于相应键值的用户。但是我自己实验下来只有`name="username`这个参数可以使用，猜测是微信改了其它的接口。`user_name`这个值是返回的用户验证id，如果没有这个id仅仅是依靠备注之类的信息消息是无法发出去的。

- 设置定时操作

  ```python
  scheduler = BlockingScheduler()
  scheduler.add_job(func=sendMessage, trigger='cron',hour=8, minute=0, args=[user_name])
  scheduler.start()
  ```

  [APScheduler](https://apscheduler.readthedocs.io/en/latest/)有四大组件，在程序中仅仅只是很简单的使用，我对这个库的也仅仅只了解了皮毛。

  - 触发器 `triggers` ：用于设定触发任务的条件。
  - 任务储存器 `job stores`：用于存放任务，把任务存放在内存或数据库中。
  - 执行器 `executors`： 用于执行任务，可以设定执行模式为单线程或线程池。
  - 调度器 `schedulers`： 把上方三个组件作为参数，通过创建调度器实例来运行。

  `BlockingScheduler`是阻塞式调度器：适用于只跑调度器的程序。`add_job(func=sendMessage, trigger='cron',hour=21, minute=8, args=[user_name])`表示添加一个新任务，`func`是需要执行的函数，`trigger`是触发器的种类，`corn`是定时调度（某一时刻执行），其它触发器还有`interval`和`date`，分别是间隔调度和定时调度。`hour`和`minute`是执行时间，`args`用来传递`fun`需要的参数，这里特别注意的是func参数那里传递的是整个函数，而不是函数的返回值，所以函数不能带`()`，如果需要传递参数只能用`args`来传递。

  ```python
  def sendMessage(user):
      message = getInfo()
      itchat.send_msg(message, toUserName=user)
  ```

  `sendMessage`调用了`getInfo()`来获取需要发送的信息。

  `    itchat.send_msg(message, toUserName=user)`将信息发送出去。

  整个程序就编写完成了，源代码在我的[Github](https://github.com/februarysea/EverydayWechat)上。

- **部署到服务器**

  我用的是[腾讯云](https://cloud.tencent.com/)一个月10块钱的服务器，除了跑这个程序还可以熟悉一下Linux的操作，感觉还不错。

  ```shell
  scp local_file remote_username@remote_ip:remote_file 
  ```

  将本地的文件传到服务器，`local_file`是本地文件的名称路径，`remote_ip` 是服务器IP，`remote_username`是登录服务器的账户，第二个 `remote_file`是指定文件传到服务器的名称。运行命令后输入登录服务器的密码就行了。

  传输成功后，安装好程序需要的库，运行下面的命令就可以让程序一直运行了。

  ```shell
  nohup python -u morningMessage.py > morningMessage.log 2>&1 &
  ```

  不间断的运行`morningMessage.py`并将运行日志写入` morningMessage.log`中，输入`vim morningMessage.log`

  扫描微信登录二维码，然后`:wq` 退出，再进入就可以看到登录成功的信息了。
