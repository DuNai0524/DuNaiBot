import random

from nonebot.log import logger
from nonebot.adapters.onebot.v11 import Message, MessageSegment
from nonebot.adapters.onebot.v11.bot import Bot

from ..dunai_daily_sign.models import Daily_Sign

# 懒得新写一个表了，直接用一个特定用户
award_user_id = 114514

# 一次抽奖的数量
award_num = 10


async def get_big_award(user_id:int) -> Message:
    msg = Message()
    user_gold = await Daily_Sign.get_gold(user_id)
    msg_text = ""

    if user_gold < 10:
        msg_text += "你的金币数量不够呢QAQ(最低入场费为10金币)"
        msg += MessageSegment.text(msg_text)
        return msg

    total_gold = await Daily_Sign.get_gold(award_user_id)

    logger.log(f"[抽奖]用户{user_id}进行大奖池抽奖")
    # 两个1-100之间的随机数 相等则是中奖
    rand_1 = random.randint(1,100)
    rand_2 = random.randint(1,100)
    logger.log(f"[抽奖]参数1:{rand_1},参数2:{rand_2}")
    if rand_1 == rand_2:
        msg_text += "恭喜中奖!\n"
        msg_text += f"获得金币:{total_gold + award_num}\n"
        user_gold += total_gold + award_num
        total_gold = 0
        await Daily_Sign.adjust_gold(total_gold,award_user_id)
        await Daily_Sign.adjust_gold(user_gold,user_id)
        msg_text += f"现在您拥有的金币数量:{user_gold}\n"
        msg_text += f"奖池已经归零!"
    else:
        msg_text += "没有中奖呢QAQ\n"
        total_gold += award_num
        user_gold -= award_num
        await Daily_Sign.adjust_gold(total_gold,award_user_id)
        await Daily_Sign.adjust_gold(user_gold,user_id)
        msg_text += f"现在您拥有的金币数量:{user_gold}\n"
        msg_text += f"奖池中金币数量:{total_gold}"
    msg += MessageSegment.text(msg_text)
    return msg
