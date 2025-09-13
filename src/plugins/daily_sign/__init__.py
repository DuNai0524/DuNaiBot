from nonebot_plugin_tortoise_orm import add_model

from nonebot import on_command
from nonebot.log import logger
from nonebot.adapters.onebot.v11 import GROUP, GroupMessageEvent
from nonebot.adapters.onebot.v11.bot import Bot

from src.plugins.daily_sign.data_source import get_sign_in

add_model("src.plugins.daily_sign.model")


sign = on_command("签到", permission=GROUP)


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