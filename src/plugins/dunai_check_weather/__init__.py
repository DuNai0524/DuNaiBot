from nonebot import on_command, get_bot
from nonebot import require, get_driver
from nonebot.matcher import Matcher
from nonebot.params import CommandArg
from nonebot.adapters import Event
from nonebot.adapters.onebot.v11 import Message, MessageSegment, escape
from nonebot.log import logger
from nonebot_plugin_apscheduler import scheduler

import httpx
import json

from ...util.image import image_to_base64, text_to_image

# API 接口 所需用到的参数
url = "https://v0.yiketianqi.com/free/day?"
url_week = "https://v0.yiketianqi.com/free/week?"
appid = "41432358"
appsecret = "3C9Dy2VC"
url_2 = f"http://zh.wttr.in/"
#
# weatherForcast = on_command('三日天气', aliases={"3dw"})
# weatherCheck = on_command('今日天气', aliases={"weather"})

# 定时插件 定时播报
require("nonebot_plugin_apscheduler")

# # 查询今天天气
# @weatherCheck.handle()
# async def today_weather(matcher: Matcher, event: Event, message: Message = CommandArg()):
#     argv = str(message).split(" ")
#     if len(argv) > 1 or len(argv) == 0:
#         await weatherCheck.finish("输入格式为 今日天气+城市 中间有空格")
#         return
#     else:
#         city = argv[0]
#         r = httpx.get(url + "appid=" + appid + "&appsecret=" + appsecret + "&city=" + city)
#         info = json.loads(r.text)
#         await weatherCheck.send("请等待...正在获取天气数据中", at_sender=True)
#         await weatherCheck.send(f"今日api已使用次数: " + str(info['nums']) + " 次\n" + \
#                                 f"====查询天气情况====\n" + \
#                                 f"城市: " + str(info['city']) + "\n" + \
#                                 f"日期: " + str(info['date']) + " " + str(info['week']) + "\n" + \
#                                 f"白天温度: " + str(info['tem_day']) + "\n" + \
#                                 f"晚上温度: " + str(info['tem_night']) + "\n" + \
#                                 f"天气: " + str(info['wea']) + " 更新时间: " + str(info['update_time']))
#
#
# @weatherForcast.handle() async def threeday_weather(matcher: Matcher, message: Message = CommandArg()): argv = str(
# message).split(" ") print(argv)+- if len(argv) > 1 or len(argv) == 0: await weatherForcast.finish("输入格式为 三日天气+城市
# 中间有空格") return else: city = argv[0] await weatherForcast.send("请等待...正在获取天气数据中", at_sender=True) await
# weatherForcast.send(MessageSegment.image(file=url_2 + f"{escape(city)}.png", cache=False), at_sender=True)


'''
以上注释代码均被废除
'''

time_list = get_driver().config.weather_inform_time if hasattr(get_driver().config, "weather_inform_time") else list()


async def send_preWeather_EveryDay():
    qq_list = get_bot().config.weather_inform_group if hasattr(get_driver().config, "weather_inform_group") else list()
    try:
        for group in qq_list:
            r = httpx.get(url_week + "appid=" + appid + "&appsecret=" + appsecret + "&city=" + group["CITY"])
            info = json.loads(r.text)
            await get_bot().call_api("send_group_msg", group_id=group["ID"],
                                     message=f"==== 天气预报====\n" + \
                                             f"本群所属城市: " + str(group["CITY"]) + "\n" + \
                                             f"日期: " + str(info['data'][1]['date']) + "\n" + \
                                             f"白天温度: " + str(info['data'][1]['tem_day']) + "\n" + \
                                             f"晚上温度: " + str(info['data'][1]['tem_night']) + "\n" + \
                                             f"天气: " + str(info['data'][1]['wea']) + "\n" + "更新时间: " + str(
                                         info['update_time']))
    except TypeError:
        logger.error("[天气查询] 插件检测到发送相关设置有误:QQ群与城市设置,请检查.env文件设置")


try:
    for index, time in enumerate(time_list):
        print(time)
        scheduler.add_job(send_preWeather_EveryDay, "cron", hour=time["HOUR"], minute=time["MINUTE"],
                          id=f"weather_{str(index)}")
        logger.info(f"[天气查询] 新建计划任务成功---id:weather_{index},时间为:{time}")
except Exception as e:
    print(e)
    logger.error("[天气查询] 插件检测到发送相关设置有误:时间设置,请检查.env文件设置")
