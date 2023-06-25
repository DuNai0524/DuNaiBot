from nonebot import on_command
from nonebot.matcher import Matcher
from nonebot.params import CommandArg
from nonebot.adapters import Event
from nonebot.adapters.onebot.v11 import Message, MessageSegment, escape, Bot

get_help = on_command("所有帮助", aliases={"all_help"})
get_help_weather = on_command("天气", aliases={"weather"})
get_help_wordcloud = on_command("词云", aliases={"wordcloud"})

help_str = '''
==================================
帮助文档: https://blog.dunaixdd.cn/index.php/2023/04/18/koyukibot-%e4%bd%bf%e7%94%a8%e6%96%87%e6%a1%a3-v1-0/
==================================
'''

help_str_wordcloud = '''
=========================
词云生成:
发送 
/今日词云,/昨日词云
/本周词云,/本月词云
/年度词云,/历史词云 
即可获取词云。
=========================
'''

help_str_weather = '''
=========================
天气查询:
/今日天气+城市 查询今天天气
/三日天气+城市 查询最近三天天气
=========================
'''


@get_help.handle()
async def get_help_func(bot: Bot, event: Event):
    await get_help.send(Message(help_str))


@get_help_wordcloud.handle()
async def get_wordcloud_help(bot: Bot, event: Event):
    await get_help_wordcloud.send(Message(help_str_wordcloud))


@get_help_weather.handle()
async def get_weather_help(bot: Bot, event: Event):
    await get_help_wordcloud.send(Message(help_str_weather))
