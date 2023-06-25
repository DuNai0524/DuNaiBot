from nonebot import on_command
from nonebot.log import logger
from nonebot.adapters.onebot.v11.bot import Bot
from nonebot.adapters.onebot.v11 import GROUP, GroupMessageEvent, Message, MessageSegment
from nonebot.typing import T_State
from nonebot.params import CommandArg
from nonebot_plugin_tortoise_orm import add_model
from .data_source import get_sign_in, get_choujiang, getGoldList, goldToOthers
from ..dunai_get_award.data_source import get_big_award

import json

add_model("src.plugins.dunai_daily_sign.models")

sign = on_command("签到", permission=GROUP)

award = on_command("抽奖", permission=GROUP)

big_award = on_command("抽奖池", permission=GROUP)

get_listInfo = on_command("金币排名", permission=GROUP)

gold_to_others = on_command("转账", permission=GROUP)


@sign.handle()
async def _(event: GroupMessageEvent):
    user_id = event.user_id
    group_id = event.group_id
    logger.opt(colors=True).info(f"[签到插件] 群 <y>{group_id}</y> : 用户 <y>{user_id}</y> 签到")
    msg = await get_sign_in(user_id, group_id)
    await sign.finish(msg, at_sender=True)


@award.handle()
async def _(event: GroupMessageEvent, message: Message = CommandArg()):
    argv = str(message).split(" ")
    if len(argv) > 1 or len(argv) == 0:
        await award.finish("输入格式为 抽奖 + 抽奖金币数字")
        return
    else:
        user_id = event.user_id
        group_id = event.group_id
        use_gold = int(argv[0])
        logger.opt(colors=True).info(f"[签到插件] 群 <y>{group_id}</y> : 用户 <y>{user_id}</y> 抽奖")
        msg = await get_choujiang(user_id, group_id, use_gold)
        await award.finish(msg, at_sender=True)


@get_listInfo.handle()
async def _(event: GroupMessageEvent, bot: Bot):
    group_id = event.group_id
    msg = await getGoldList(group_id, bot)
    await get_listInfo.finish(msg)


@big_award.handle()
async def _(event: GroupMessageEvent, bot: Bot, state: T_State,message: Message = CommandArg()):
    user_id = event.user_id
    msg = await get_big_award(user_id)
    await big_award.finish(msg, at_sender=True)


@gold_to_others.handle()
async def _(event: GroupMessageEvent, bot: Bot, state: T_State,message: Message = CommandArg()):
    argv = str(message).split(" ")
    if len(argv) == 1 or len(argv) >= 3:
        await gold_to_others.finish("输入格式错误！格式为：转账 [at的人] 金额,请检查输入格式")
    if argv[1].strip().isdigit() is False:
        await gold_to_others.finish("输入格式错误！输入的金币必须是数字！")
    gold = int(argv[1].strip())
    qq = 0
    user_id = event.user_id
    data = json.loads(event.json())
    for msg in data['message']:
        if msg['type'] == 'at':
            qq = int(msg['data']['qq'])
    print(qq)
    print(gold)
    msgs = await goldToOthers(user_id, qq, gold)

    await gold_to_others.finish(msgs, at_sender=True)
