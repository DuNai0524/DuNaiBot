import random

import httpx

from nonebot.adapters.onebot.v11 import Message, MessageSegment
from nonebot.adapters.onebot.v11.bot import Bot
from nonebot.log import logger

from src.plugins.plugin_daily_common.model import Daily_Sign, Prize_Pool
from src.utils.image_generator import create_sign_in_image

from datetime import date


"""
每日签到
"""
async def get_sign_in(user_id :int, group_id: int, bot: Bot) -> Message:
    msg = Message()

    last_sign = await Daily_Sign.get_last_sign_time(user_id)
    today = date.today()
    user_info = await bot.get_stranger_info(user_id=user_id)
    user_name = user_info['nick']
    # logger.debug(f"last_sign: {last_sign}")
    # logger.debug(f"today: {today}")
    if today == last_sign:
        msg += Message("你今天已经签到过了哦~")
        return msg

    sign_num = await Daily_Sign.filter(last_sign=today).count() + 1

    data = await Daily_Sign.sign_in(
        user_id,
        base_gold=10,
        lucky_gold=random.randint(1, 50),
        today_lucky=random.randint(1, 10),
    )

    # 生成一言
    async with httpx.AsyncClient() as client:
        response = await client.get("https://v1.hitokoto.cn?c=a&c=b&c=c&c=d&c=h")
    if response.is_error:
        logger.error("获取一言失败")
        return
    
    res_data = response.json()
    yiyan = res_data["hitokoto"]
    add = ""
    if works := res_data["from"]:
        add += f"《{works}》"
    if from_who := res_data["from_who"]:
        add += f"{from_who}"
    if add:
        yiyan += f"\n——{add}"


    # 生成签到图片
    try:
        image_buffer = await create_sign_in_image(
            sign_rank=sign_num,
            today_gold=data.today_gold,
            all_gold=data.all_gold,
            sign_times=data.sign_times,
            today_lucky=data.today_lucky,
            user_id=user_id,
            yiyan=yiyan,
            user_name=user_name
        )
        
        # 将图片添加到消息中
        msg += MessageSegment.image(image_buffer)
        
    except Exception as e:
        # 如果图片生成失败，回退到文字模式
        logger.error(f"签到图片生成失败: {e}")
        msg_text = f"您本群第 {sign_num} 位 签到完成\n"
        msg_text += f"获得金币: {data.today_gold}\n"
        msg_text += f"现在拥有金币: {data.all_gold}\n"
        msg_text += f"累计签到次数: {data.sign_times}"
        msg += MessageSegment.text(msg_text)

    return msg

"""
抽奖功能
"""
async def get_award(user_id: int, cost_gold: int, bot: Bot) -> Message:
    msg = Message()
    
    try:
        # 执行抽奖
        result = await Daily_Sign.lottery(user_id, cost_gold)
        
        # 构建消息
        if result.success:
            msg_text = f"🎉 恭喜你！抽奖成功！\n"
            msg_text += f"💰 消耗金币: {result.cost_gold}\n"
            msg_text += f"🎁 获得奖励: {result.reward_gold} 金币\n"
            msg_text += f"💵 当前金币: {result.current_gold}\n"
            msg_text += f"📊 本次中奖概率: {result.current_probability:.1f}%\n"
            msg_text += f"🔄 下次抽奖概率已重置为: 10.0%"
        else:
            msg_text = f"😢 很遗憾，本次抽奖未中奖\n"
            msg_text += f"💰 消耗金币: {result.cost_gold}\n"
            msg_text += f"💵 当前金币: {result.current_gold}\n"
            msg_text += f"📊 本次中奖概率: {result.current_probability:.1f}%\n"
            msg_text += f"📈 下次抽奖概率提升至: {result.current_probability + 5.0:.1f}%\n"
            msg_text += f"💪 继续加油，下次一定能中！"
        
        msg += MessageSegment.text(msg_text)
        
    except ValueError as e:
        # 金币不足等错误
        msg += MessageSegment.text(str(e))
    except Exception as e:
        # 其他错误
        logger.error(f"抽奖失败: {e}")
        msg += MessageSegment.text(f"抽奖失败: {str(e)}")
    
    return msg
    

"""
获取排名
"""
async def get_Lineup(group_id: int, bot: Bot) -> Message:
    msg = Message()
    gold_list = await Daily_Sign.get_list()
    group_list = await bot.get_group_member_list(group_id=group_id)

    msg_text = ""
    msg_text += "本群金币排名如下:\n"

    rank = 1
    for user in gold_list:
        for group_user in group_list:
            if user.user_id == group_user['user_id']:
                msg_text += f"第 {rank} 名: {group_user['nickname']} (金币: {user.gold}, 签到次数: {user.sign_count})\n"
                rank += 1
                break

    msg += MessageSegment.text(msg_text)
    return msg


"""
奖池抽奖功能
"""
async def get_prize_award(user_id: int, cost_gold: int, bot: Bot) -> Message:
    msg = Message()
    
    try:
        # 执行奖池抽奖
        result = await Prize_Pool.prize_lottery(user_id, cost_gold)
        
        # 构建消息
        if result.success:
            msg_text = f"🎊🎊🎊 恭喜你中大奖了！🎊🎊🎊\n"
            msg_text += f"💰 投入金币: {result.cost_gold}\n"
            msg_text += f"🎁 赢得奖池: {result.win_gold} 金币\n"
            msg_text += f"💵 当前金币: {result.current_gold}\n"
            msg_text += f"📊 本次中奖概率: {result.probability:.2f}%\n"
            msg_text += f"🏆 奖池已清空，当前奖池: {result.pool_gold} 金币"
        else:
            msg_text = f"💔 很遗憾，未能中奖\n"
            msg_text += f"💰 投入金币: {result.cost_gold}\n"
            msg_text += f"💵 当前金币: {result.current_gold}\n"
            msg_text += f"📊 本次中奖概率: {result.probability:.2f}%\n"
            msg_text += f"🏆 当前奖池: {result.pool_gold} 金币\n"
            msg_text += f"💡 提示: 投入更多金币可以提高中奖概率！"
        
        msg += MessageSegment.text(msg_text)
        
    except ValueError as e:
        # 金币不足等错误
        msg += MessageSegment.text(str(e))
    except Exception as e:
        # 其他错误
        logger.error(f"奖池抽奖失败: {e}")
        msg += MessageSegment.text(f"奖池抽奖失败: {str(e)}")
    
    return msg


"""
查询奖池金币
"""
async def get_prize_pool_info(bot: Bot) -> Message:
    msg = Message()
    
    try:
        pool_gold = await Prize_Pool.get_pool_gold()
        
        msg_text = f"🏆 当前奖池信息\n"
        msg_text += f"💰 奖池金币: {pool_gold}\n"
        msg_text += f"📌 玩法说明:\n"
        msg_text += f"  • 投入金币参与抽奖\n"
        msg_text += f"  • 未中奖金币进入奖池\n"
        msg_text += f"  • 中奖获得奖池全部金币\n"
        msg_text += f"  • 每次投入越多，中奖概率越高！"
        
        msg += MessageSegment.text(msg_text)
        
    except Exception as e:
        logger.error(f"查询奖池失败: {e}")
        msg += MessageSegment.text(f"查询奖池失败: {str(e)}")
    
    return msg
