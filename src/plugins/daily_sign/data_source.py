import random

from nonebot.adapters.onebot.v11 import Message, MessageSegment
from nonebot.log import logger

from src.plugins.daily_sign.model import Daily_Sign
from src.utils.image_generator import create_sign_in_image

from datetime import date


async def get_sign_in(user_id :int, group_id: int) -> Message:
    msg = Message()

    last_sign = await Daily_Sign.get_last_sign_time(user_id)
    today = date.today()
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

    # 生成签到图片
    try:
        image_buffer = create_sign_in_image(
            sign_rank=sign_num,
            today_gold=data.today_gold,
            all_gold=data.all_gold,
            sign_times=data.sign_times,
            today_lucky=data.today_lucky
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