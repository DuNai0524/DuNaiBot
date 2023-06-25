from nonebot import on_command
from nonebot.log import logger
from nonebot.adapters.onebot.v11.bot import Bot
from nonebot.adapters.onebot.v11 import GROUP, GroupMessageEvent, Message, MessageSegment
from nonebot.typing import T_State
from nonebot.params import CommandArg
from nonebot_plugin_tortoise_orm import add_model
from .data_source import get_num_info,start_line_up,end_line_up,add_store_info

add_model("src.plugins.dunai_maimai_line_up.models")

end_linpUp = on_command("退勤", permission=GROUP)

start_lineUp = on_command("出勤", permission=GROUP)

addInfo = on_command("新增机厅", permission=GROUP)

checkNum = on_command("查询人数", permission=GROUP)


@addInfo.handle()
async def _(event:GroupMessageEvent, message: Message = CommandArg()):
    argv = str(message).split(" ")
    if len(argv) < 3 or len(argv) > 3:
        await addInfo.finish("请检查输入格式: 新增机厅 机厅名称 别称 机台数量", at_sender=True)
        return
    else:
        name = argv[0]
        alias = argv[1]
        maimai_count = int(argv[2])
        msg = await add_store_info(name,alias,maimai_count)
        await addInfo.finish(msg)


@checkNum.handle()
async def _(event:GroupMessageEvent, message: Message = CommandArg()):
    argv = str(message).split(" ")
    msg = await get_num_info(argv[0])
    await checkNum.finish(msg)


@start_lineUp.handle()
async def _(event:GroupMessageEvent, message: Message = CommandArg()):
    argv = str(message).split(" ")
    if len(argv) < 2 or len(argv) > 2:
        await start_lineUp.finish("请检查输入格式: 出勤 别名 人数", at_sender=True)
    if argv[1].isdigit():
        msg = await start_line_up(argv[0], int(argv[1]))
        await start_lineUp.finish(msg)
    else:
        await start_lineUp.finish("输入格式错误：出勤 别名 数量")


@end_linpUp.handle()
async def _(event:GroupMessageEvent, message: Message = CommandArg()):
    argv = str(message).split(" ")
    if len(argv) < 2 or len(argv) > 2:
        await end_linpUp.finish("请检查输入格式: 出勤 别名 人数", at_sender=True)
    if argv[1].isdigit():
        msg = await end_line_up(argv[0], int(argv[1]))
        await start_lineUp.finish(msg)
    else:
        await start_lineUp.finish("输入格式错误：退勤 别名 数量")