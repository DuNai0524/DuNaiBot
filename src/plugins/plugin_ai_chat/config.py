"""
AI 聊天插件配置
"""
import os
from pathlib import Path
from typing import Optional
from pydantic import BaseModel, Field


class Config(BaseModel):
    """AI 聊天插件配置类"""
    
    # Qwen API 配置
    qwen_api_key: str = Field(default="", description="Qwen API Key")
    qwen_model: str = Field(default="qwen-turbo", description="使用的模型名称")
    
    # 对话配置
    max_tokens: int = Field(default=1500, description="最大生成 token 数")
    temperature: float = Field(default=0.8, description="温度参数，控制随机性")
    top_p: float = Field(default=0.8, description="Top-p 采样参数")
    
    # 功能开关
    enable_context: bool = Field(default=True, description="是否启用上下文记忆")
    context_max_length: int = Field(default=10, description="上下文最大轮数")
    
    # 超时配置
    request_timeout: int = Field(default=60, description="API 请求超时时间（秒）")


# 创建全局配置实例
plugin_config = Config()


def load_config(**kwargs) -> Config:
    """
    加载配置
    
    Args:
        **kwargs: 配置参数
        
    Returns:
        Config: 配置对象
    """
    global plugin_config
    for key, value in kwargs.items():
        if hasattr(plugin_config, key):
            setattr(plugin_config, key, value)
    return plugin_config


def get_config() -> Config:
    """
    获取配置
    
    Returns:
        Config: 配置对象
    """
    return plugin_config


def load_system_prompt() -> str:
    """
    从配置文件加载系统 Prompt
    
    Returns:
        str: 系统 Prompt 内容
    """
    prompt_file = Path(__file__).parent / "config" / "prompt.txt"
    
    try:
        if prompt_file.exists():
            with open(prompt_file, "r", encoding="utf-8") as f:
                prompt = f.read().strip()
                if prompt:
                    return prompt
    except Exception as e:
        print(f"读取 Prompt 配置文件失败: {e}")
    
    # 返回默认 Prompt
    return "你是一个友好、乐于助人的 AI 助手。请用简洁、友好的语气回答用户的问题。"
