from datetime import datetime

from nonebot.log import logger
from nonebot.adapters.onebot.v11 import Message, MessageSegment
from nonebot.adapters.onebot.v11.bot import Bot

from .models import Store_Info
"""
预计出勤计算公式
人数/2 取整(少于两个人补为一组) * 3.5(一首歌+等待时间最长时间) * 4 (一律按拼机)
实际上就是 人数//2 * 15 = 一轮等待时间
要注意的是，仅仅只代表一台机子的时间
如果当前机厅为奇数个人，则要补到偶数个再进行计算
"""
async def start_line_up(alias:str, line_up_num:int) -> Message:
    msg = Message()
    msg_text = ""
    temp = await Store_Info.getNumInfo(alias)
    if temp == -500:
        msg_text += "没有查询到相应的机厅信息"
    elif temp == -400:
        msg_text += "机厅机子现在处于维修/不能游玩的状态"
    else:
        msg_text += f"{alias}之前机厅的人数: {temp} 人\n"
        msg_text += f"新增 {line_up_num} 人出勤\n"
        now_total = temp+line_up_num
        await Store_Info.updateNumInfo(alias, now_total)
        if now_total == 1:
            group_num = 1
        elif now_total % 2 == 1:
            group_num = now_total//2 + 1
        else:
            group_num = now_total//2
        msg_text += f"现在有 {now_total} 人出勤，即 {group_num} 组人\n"
    msg += MessageSegment.text(msg_text)
    return msg


async def end_line_up(alias:str, line_up_num:int) -> Message:
    msg = Message()
    msg_text = ""
    temp = await Store_Info.getNumInfo(alias)
    if temp == -500:
        msg_text += "没有查询到相应的机厅信息"
    elif temp == -400:
        msg_text += "机厅机子现在处于维修/不能游玩的状态"
    elif temp < line_up_num:
        msg_text += "退勤人数错误！"
    else:
        msg_text += f"{alias}之前机厅的人数: {temp} 人\n"
        msg_text += f"减少 {line_up_num} 人出勤\n"
        now_total = temp-line_up_num
        await Store_Info.updateNumInfo(alias, now_total)
        if now_total == 1:
            group_num = 1
        elif now_total % 2 == 1:
            group_num = now_total//2 + 1
        else:
            group_num = now_total//2
        msg_text += f"现在有 {now_total} 人出勤，即 {group_num} 组人\n"
    msg += MessageSegment.text(msg_text)
    return msg


async def add_store_info(name:str, alias:str, maimai_count:int) -> Message:
    msg = Message()
    msg_text = ""
    re = await Store_Info.getNumInfo(alias)
    if re == -500:
        await Store_Info.addInfo(name, maimai_count, alias)
        msg_text += f"创建机厅成功!\n"
        msg_text += f"机厅名称:{name}\n"
        msg_text += f"机厅别称:{alias}\n"
        msg_text += f"机台数量:{maimai_count}\n"
        msg_text += "查询时请使用别称进行查询!否则无法查询到数据"
    else:
        msg_text += "机厅信息已经存在或别称重复，请尝试其他名称，如果要修改机厅信息请联系Bot开发者(DuNai0524)"
    msg += MessageSegment.text(msg_text)
    return msg


async def get_num_info(alias:str) -> Message:
    msg = Message()
    msg_text = ""
    group_num = 0
    re = await Store_Info.getNumInfo(alias)
    if re == -500:
        msg_text += "没有查询到机厅信息"
    elif re == -400:
        msg_text += "机厅现在处于无法游玩/状态"
    else:
        msg_text += f"{alias}现在有{re}人\n"
        if re == 0:
            group_num = 0
        elif re == 1:
            group_num = 1
        elif re % 2 == 1:
            group_num = re//2 + 1
        else:
            group_num = re//2

        if group_num == 0:
            msg_text += "机厅里面现在没有人哦，现在不需要等待哦"
        elif group_num >0 and group_num <3:
            msg_text += f"几天里现在有大约 {group_num} 组人, 大概需要等{group_num*15}分钟\n"
            time = await Store_Info.getTime(alias)
            msg_text += f"更新时间:{time.strftime('%Y-%m-%d %H:%M:%S')}"
        else:
            msg_text += f"现在机厅人有点多呢QAQ，有大约 {group_num} 组人，大概需要等{group_num*15}分钟呢，要不来把雀先？\n"
            time = await Store_Info.getTime(alias)
            msg_text += f"更新时间:{time.strftime('%Y-%m-%d %H:%M:%S')}"
    msg += MessageSegment.text(msg_text)
    return msg


