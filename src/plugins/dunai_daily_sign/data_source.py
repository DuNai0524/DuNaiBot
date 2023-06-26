import random
from datetime import date
from typing import Any

from nonebot.log import logger
from nonebot.adapters.onebot.v11 import Message, MessageSegment
from nonebot.adapters.onebot.v11.bot import Bot
from nonebot.params import CommandArg

from .models import Daily_Sign
from ..dunai_get_award.models import UserAward


# 签到
async def get_sign_in(user_id: int, group_id: int) -> Message:
    msg = Message()
    last_sign = await Daily_Sign.get_last_sign_time(user_id)

    today = date.today()
    logger.debug(f"last_sign: {last_sign}")
    logger.debug(f"today: {today}")
    if today == last_sign:
        msg += Message("你今天已经签到了!")
        return msg

    sign_num = await Daily_Sign.filter(last_sign=today).count() + 1

    data = await Daily_Sign.sign_in(
        user_id=user_id,
        group_id=group_id,
        base_gold=10,
        lucky_gold=random.randint(1, 50),
        today_lucky=random.randint(1, 10),
    )

    msg_text = f"您本群第 {sign_num} 位 签到完成\n"
    msg_text += f"获得金币: {data.today_gold}\n"
    msg_text += f"现在拥有金币: {data.all_gold}\n"
    msg_text += f"累计签到次数: {data.sign_times}"
    msg += MessageSegment.text(msg_text)
    return msg


# 抽奖
async def get_choujiang(user_id: int, group_id: int, use_gold: int) -> Message:
    msg = Message()

    logger.debug(f"用户：{user_id},进行抽奖")

    user_gold = await Daily_Sign.get_gold(user_id)

    # 判断是否满足入场要求
    if user_gold < use_gold or use_gold < 20 or user_gold < 20:
        msg_text = "Oops:你太穷了，你不允许参加Impart！(20金币为最低入场费)"
        msg += MessageSegment.text(msg_text)
        return msg

    # 进行抽奖操作
    data = await Daily_Sign.get_award(
        user_id=user_id,
        use_gold=use_gold
    )

    award_info = await UserAward.getInfo(
        user_id=user_id,
    )

    msg_text = f"抽奖结果\n"
    if data > user_gold:
        msg_text += f"恭喜中奖！\n"
        msg_text += f"现在拥有金币: {data}\n"
        msg_text += f"保底概率已归零!\n"
        msg_text += f"抽奖次数：{award_info.get_times}"
    else:
        msg_text += f"没有中奖呢QAQ\n"
        msg_text += f"现在拥有金币: {data}\n"
        msg_text += f"下一次中奖概率:{award_info.get_award_chance}\n"
        msg_text += f"抽奖次数：{award_info.get_times}"
    msg += MessageSegment.text(msg_text)
    return msg


# 转账
# 由于两边用户一定存在，因此不需要判断是否用户存在
async def goldToOthers(user_id: int,in_id: int,gold_num:int) -> Message:
    msg = Message()
    print(in_id)
    main_user_gold = await Daily_Sign.get_gold(user_id)
    others_user_gold = await Daily_Sign.get_gold(in_id)
    logger.debug(f"[签到插件] 用户{main_user_gold} 向 用户 {others_user_gold} 转账金币 {gold_num}")
    if gold_num > main_user_gold:
        msg_text = "太多啦，你自己都没钱啦\n"
        msg_text += f"您现在拥有的金币数量:{main_user_gold}\n"
        msg_text += "请转账时要注意不能超过自己的金币数量"
        msg += MessageSegment.text(msg_text)
    else:
        msg_text = "转账情况如下:\n"
        msg_text += "转账前:\n"
        msg_text += f"你拥有的金币:{main_user_gold}\nTa拥有的金币:{others_user_gold}\n"
        status = await Daily_Sign.to_other_gold(user_id, in_id, gold_num)
        others_user_gold = await Daily_Sign.get_gold(in_id)
        main_user_gold -= gold_num
        msg_text += "转账后:\n"
        msg_text += f"你拥有的金币:{main_user_gold}\nTa拥有的金币:{others_user_gold}"
        msg += MessageSegment.text(msg_text)

    return msg


# 获取排名
async def getGoldList(group_id: int, bot: Bot) -> Message:
    msg = Message()
    logger.debug("[签到] 获取金币排名中")
    gold_list = await Daily_Sign.get_list()
    user_list = await bot.get_group_member_list(group_id=group_id)

    msg_text = f"本群金币排名如下:\n"
    index = 1
    for user in gold_list:
        username = get_nickName(user_list, user.user_id)
        if username is not "":
            msg_text += f"{index}. {get_nickName(user_list, user.user_id)}({user.user_id})--{user.gold}金币\n"
            index += 1
    msg += MessageSegment.text(msg_text)
    return msg


def get_nickName(usr_list: list, user_id: int) -> str:
    for t in usr_list:
        if t['user_id'] == user_id:
            return t['nickname']
    return ""
