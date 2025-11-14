"""
AI 聊天插件 - 基于 Qwen 大模型
"""
from nonebot import on_command, on_message
from nonebot.rule import to_me
from nonebot.log import logger
from nonebot.params import CommandArg
from nonebot.adapters.onebot.v11 import Message, MessageEvent
from nonebot.adapters.onebot.v11.bot import Bot

from .config import get_config, reload_config
from .ai_service import call_qwen_api, clear_user_context, split_message


# AI 对话 - 通过 @机器人 触发
ai_chat = on_message(rule=to_me(), priority=10, block=True)

# 清除上下文命令
clear_context = on_command("清除对话", aliases={"重置对话", "清空上下文"}, priority=5)

# 重载配置命令
reload_config_cmd = on_command("重载ai配置", priority=5)


@ai_chat.handle()
async def handle_ai_chat(event: MessageEvent, bot: Bot):
    """处理 AI 对话 - 通过 @机器人 触发"""
    user_id = str(event.user_id)
    # 获取消息文本，去除 @机器人 的部分
    user_message = event.get_plaintext().strip()
    
    if not user_message:
        await ai_chat.finish("你想问我什么呢？", at_sender=True)
        return
    
    logger.opt(colors=True).info(
        f"[AI Chat] 用户 <y>{user_id}</y> 提问: <c>{user_message}</c>"
    )
    
    # 调用 AI API
    ai_reply = await call_qwen_api(
        user_message=user_message,
        user_id=user_id,
        use_context=True
    )
    
    logger.opt(colors=True).info(
        f"[AI Chat] AI 回复: <g>{ai_reply}</g>"
    )
    
    # 将长文本分段发送，使其更像聊天
    segments = split_message(ai_reply, max_length=500)
    
    for i, segment in enumerate(segments):
        # 最后一条消息使用 finish，其他消息使用 send
        if i == len(segments) - 1:
            await ai_chat.finish(segment, at_sender=True)
        else:
            await ai_chat.send(segment, at_sender=True)


@clear_context.handle()
async def handle_clear_context(event: MessageEvent):
    """清除用户的对话上下文"""
    user_id = str(event.user_id)
    clear_user_context(user_id)
    
    logger.opt(colors=True).info(
        f"[AI Chat] 用户 <y>{user_id}</y> 清除了对话上下文"
    )
    
    await clear_context.finish("已清除你的对话记录！", at_sender=True)


@reload_config_cmd.handle()
async def handle_reload_config(event: MessageEvent):
    """重新加载配置"""
    try:
        reload_config()
        await reload_config_cmd.finish("配置已重新加载！", at_sender=True)
    except Exception as e:
        logger.error(f"[AI Chat] 重载配置失败: {e}")
        await reload_config_cmd.finish(f"重载配置失败：{str(e)}", at_sender=True)


logger.opt(colors=True).success(
    "<g>AI Chat Plugin</g> 加载成功！"
)
