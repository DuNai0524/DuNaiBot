"""
AI 服务模块 - 调用 Qwen API（使用 DashScope SDK）
"""
from typing import List, Dict, Optional
from nonebot.log import logger

try:
    import dashscope
    from dashscope import Generation
    DASHSCOPE_AVAILABLE = True
except ImportError:
    DASHSCOPE_AVAILABLE = False
    logger.warning("[AI Chat] dashscope 库未安装，请运行: pip install dashscope")

from .config import get_config, load_system_prompt


class ConversationContext:
    """对话上下文管理"""
    
    def __init__(self, max_length: int = 10):
        self.max_length = max_length
        self.contexts: Dict[str, List[Dict[str, str]]] = {}
    
    def add_message(self, user_id: str, role: str, content: str):
        """添加消息到上下文"""
        if user_id not in self.contexts:
            self.contexts[user_id] = []
        
        self.contexts[user_id].append({
            "role": role,
            "content": content
        })
        
        # 限制上下文长度
        if len(self.contexts[user_id]) > self.max_length * 2:
            self.contexts[user_id] = self.contexts[user_id][-self.max_length * 2:]
    
    def get_context(self, user_id: str) -> List[Dict[str, str]]:
        """获取用户的上下文"""
        return self.contexts.get(user_id, [])
    
    def clear_context(self, user_id: str):
        """清除用户的上下文"""
        if user_id in self.contexts:
            del self.contexts[user_id]


# 全局上下文管理器
conversation_manager = ConversationContext()


async def call_qwen_api(
    user_message: str,
    user_id: Optional[str] = None,
    use_context: bool = True
) -> str:
    """
    调用 Qwen API 获取回复（使用 DashScope SDK）
    
    Args:
        user_message: 用户消息
        user_id: 用户 ID，用于上下文管理
        use_context: 是否使用上下文
        
    Returns:
        str: AI 回复内容
    """
    if not DASHSCOPE_AVAILABLE:
        return "错误：dashscope 库未安装，请运行: pip install dashscope"
    
    config = get_config()
    
    # 检查 API Key
    if not config.api_key:
        return "错误：未配置 Qwen API Key，请在 config/ai_chat.yaml 中设置 api_key"
    
    # 设置 API Key
    dashscope.api_key = config.api_key
    
    # 构建消息列表
    messages = []
    
    # 加载并添加系统 Prompt
    system_prompt = load_system_prompt()
    if system_prompt:
        messages.append({
            "role": "system",
            "content": system_prompt
        })
    
    # 添加历史上下文
    if use_context and config.enable_context and user_id:
        context = conversation_manager.get_context(user_id)
        messages.extend(context)
    
    # 添加当前用户消息
    messages.append({
        "role": "user",
        "content": user_message
    })
    
    try:
        logger.info(f"[AI Chat] 调用 DashScope API，模型: {config.model}")
        logger.debug(f"[AI Chat] 消息数量: {len(messages)}")
        
        # 调用 DashScope API
        response = Generation.call(
            model=config.model,
            messages=messages,
            result_format='message',
            max_tokens=config.max_tokens,
            temperature=config.temperature,
            top_p=config.top_p,
        )
        
        # 检查响应状态
        if response.status_code == 200:
            ai_reply = response.output.choices[0].message.content
            
            logger.debug(f"[AI Chat] API 调用成功")
            
            # 保存上下文
            if use_context and config.enable_context and user_id:
                conversation_manager.add_message(user_id, "user", user_message)
                conversation_manager.add_message(user_id, "assistant", ai_reply)
            
            return ai_reply
        else:
            logger.error(f"[AI Chat] API 调用失败: {response.code} - {response.message}")
            return f"抱歉，API 请求失败：{response.message}"
    
    except Exception as e:
        logger.error(f"[AI Chat] 发生错误: {str(e)}")
        return f"抱歉，发生了错误：{str(e)}"


def clear_user_context(user_id: str):
    """清除用户的对话上下文"""
    conversation_manager.clear_context(user_id)
    logger.info(f"[AI Chat] 清除用户 {user_id} 的对话上下文")
