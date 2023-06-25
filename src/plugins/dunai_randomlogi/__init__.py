import random

from nonebot.adapters.onebot.v11 import GROUP, GroupMessageEvent, GROUP_ADMIN
from nonebot import on_command, require

require("nonebot_plugin_datastore")

random_logi = on_command("随机logi", aliases={"随个logi"})

namelist = ["明哥", "团哥", "DuNai", "新星", "佑子", "微笑", "叉哥", "猴哥", "K宝", "租凭", "圆姐", "陆哥",
            "Daylight", "Dust", "阿鱼", "朱云杰"]


@random_logi.handle()
async def who_is_logi():
    n = len(namelist)
    the_man = random.randint(1, n)
    the_name = namelist[the_man-1]
    await random_logi.finish(the_name+"是Logi")
