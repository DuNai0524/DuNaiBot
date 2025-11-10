from nonebot_plugin_tortoise_orm import add_model

from nonebot import on_command
from nonebot.log import logger
from nonebot.params import CommandArg
from nonebot.adapters.onebot.v11 import GROUP, GroupMessageEvent, Message
from nonebot.adapters.onebot.v11.bot import Bot

from src.plugins.plugin_daily_common.data_source import get_sign_in, get_Lineup, get_award, get_prize_award, get_prize_pool_info

add_model("src.plugins.plugin_daily_sign.model")


sign = on_command("签到", permission=GROUP)

line_up = on_command("排名", permission=GROUP)

lottery = on_command("抽奖", permission=GROUP)

prize_lottery = on_command("奖池抽奖", aliases={"奖池"}, permission=GROUP)

prize_info = on_command("奖池信息", aliases={"查看奖池"}, permission=GROUP)


"""签到"""
@sign.handle()
async def _(event: GroupMessageEvent, bot: Bot):
    user_id = event.user_id
    group_id = event.group_id
    # print(event)
    # str_info = await bot.get_stranger_info(user_id=user_id)
    # print(str_info['nick'])
    logger.opt(colors=True).info(f"[签到插件] 群 <y>{group_id}</y> : 用户 <y>{user_id}</y> 签到")
    msg = await get_sign_in(user_id, group_id, bot)
    await sign.finish(msg, at_sender=True)


"""获取排名"""
@line_up.handle()
async def _(event: GroupMessageEvent, bot: Bot):
    group_id = event.group_id
    msg = await get_Lineup(group_id, bot)
    await line_up.finish(msg)


"""抽奖"""
@lottery.handle()
async def _(event: GroupMessageEvent, bot: Bot, message: Message = CommandArg()):
    user_id = event.user_id
    group_id = event.group_id
    
    argv = str(message).split(" ")
    
    if len(argv) > 1 or len(argv) == 0:
        await lottery.finish("请输入要消耗的金币数量，例如: 抽奖 100", at_sender=True)
        return
    
    try:
        cost_gold = int(argv[0])
        if cost_gold <= 20:
            await lottery.finish("金币数量必须大于20！", at_sender=True)
            return
    except ValueError:
        await lottery.finish("请输入有效的金币数量！", at_sender=True)
        return
    
    logger.opt(colors=True).info(f"[抽奖插件] 群 <y>{group_id}</y> : 用户 <y>{user_id}</y> 抽奖 {cost_gold} 金币")
    msg = await get_award(user_id, cost_gold, bot)
    await lottery.finish(msg, at_sender=True)


"""奖池抽奖"""
@prize_lottery.handle()
async def _(event: GroupMessageEvent, bot: Bot, message: Message = CommandArg()):
    user_id = event.user_id
    group_id = event.group_id
    
    argv = str(message).strip().split()
    
    if len(argv) == 0:
        await prize_lottery.finish("请输入要投入的金币数量，例如: 奖池抽奖 100", at_sender=True)
        return
    
    try:
        cost_gold = int(argv[0])
        if cost_gold <= 0:
            await prize_lottery.finish("金币数量必须大于0！", at_sender=True)
            return
    except ValueError:
        await prize_lottery.finish("请输入有效的金币数量！", at_sender=True)
        return
    
    logger.opt(colors=True).info(f"[奖池抽奖] 群 <y>{group_id}</y> : 用户 <y>{user_id}</y> 奖池抽奖 {cost_gold} 金币")
    msg = await get_prize_award(user_id, cost_gold, bot)
    await prize_lottery.finish(msg, at_sender=True)


"""查询奖池信息"""
@prize_info.handle()
async def _(event: GroupMessageEvent, bot: Bot):
    logger.opt(colors=True).info(f"[奖池信息] 群 <y>{event.group_id}</y> : 用户 <y>{event.user_id}</y> 查询奖池")
    msg = await get_prize_pool_info(bot)
    await prize_info.finish(msg)