"""
AI 聊天插件 - 基于 Qwen 大模型
"""
from nonebot import on_command, on_message
from nonebot.rule import to_me
from nonebot.log import logger
from nonebot.params import CommandArg
from nonebot.adapters.onebot.v11 import Message, MessageEvent
from nonebot.adapters.onebot.v11.bot import Bot

from .config import load_config, get_config
from .ai_service import call_qwen_api, clear_user_context


# 加载配置（可以在这里自定义配置）
load_config(
    # 在这里设置你的配置，例如：
    # qwen_api_key="your-api-key-here",
    # system_prompt="你是一个专业的编程助手，擅长解答技术问题。",
    # temperature=0.7,
)


# AI 对话 - 通过 @机器人 触发
ai_chat = on_message(rule=to_me(), priority=10, block=True)

# 清除上下文命令
clear_context = on_command("清除对话", aliases={"重置对话", "清空上下文"}, priority=5)


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
    
    # 发送"思考中"提示
    await ai_chat.send("正在思考中...", at_sender=True)
    
    # 调用 AI API
    ai_reply = await call_qwen_api(
        user_message=user_message,
        user_id=user_id,
        use_context=True
    )
    
    logger.opt(colors=True).info(
        f"[AI Chat] AI 回复: <g>{ai_reply}</g>"
    )
    
    await ai_chat.finish(ai_reply, at_sender=True)


@clear_context.handle()
async def handle_clear_context(event: MessageEvent):
    """清除用户的对话上下文"""
    user_id = str(event.user_id)
    clear_user_context(user_id)
    
    logger.opt(colors=True).info(
        f"[AI Chat] 用户 <y>{user_id}</y> 清除了对话上下文"
    )
    
    await clear_context.finish("已清除你的对话记录！", at_sender=True)


logger.opt(colors=True).success(
    "<g>AI Chat Plugin</g> 加载成功！"
)
