"""
AI 聊天插件配置
"""
import os
import yaml
from pathlib import Path
from typing import Optional, Dict, Any
from pydantic import BaseModel, Field
from nonebot.log import logger


class Config(BaseModel):
    """AI 聊天插件配置类"""
    
    # Qwen API 配置
    api_key: str = Field(default="", description="Qwen API Key")
    model: str = Field(default="qwen-turbo", description="使用的模型名称")
    
    # 对话配置
    max_tokens: int = Field(default=1500, description="最大生成 token 数")
    temperature: float = Field(default=0.8, description="温度参数，控制随机性")
    top_p: float = Field(default=0.8, description="Top-p 采样参数")
    
    # 功能开关
    enable_context: bool = Field(default=True, description="是否启用上下文记忆")
    context_max_length: int = Field(default=10, description="上下文最大轮数")
    
    # 超时配置
    request_timeout: int = Field(default=60, description="API 请求超时时间（秒）")
    
    # Prompt 文件配置
    prompt_file: str = Field(default="ai_chat_prompt.txt", description="Prompt 文件名")


def get_project_root() -> Path:
    """
    获取项目根目录
    
    Returns:
        Path: 项目根目录路径
    """
    # 从当前文件向上查找项目根目录（包含 pyproject.toml 或 requirements.txt）
    current = Path(__file__).resolve()
    
    for parent in current.parents:
        if (parent / "pyproject.toml").exists() or (parent / "requirements.txt").exists():
            return parent
    
    # 如果找不到，返回当前文件的父目录的父目录的父目录（src/plugins/plugin_ai_chat -> src -> project_root）
    return Path(__file__).resolve().parent.parent.parent.parent


def load_config_from_yaml() -> Config:
    """
    从 YAML 配置文件加载配置
    
    Returns:
        Config: 配置对象
    """
    project_root = get_project_root()
    config_file = project_root / "config" / "ai_chat.yaml"
    
    logger.info(f"[AI Chat Config] 项目根目录: {project_root}")
    logger.info(f"[AI Chat Config] 配置文件路径: {config_file}")
    
    if not config_file.exists():
        logger.warning(f"[AI Chat Config] 配置文件不存在: {config_file}")
        logger.warning(f"[AI Chat Config] 将使用默认配置")
        return Config()
    
    try:
        with open(config_file, "r", encoding="utf-8") as f:
            yaml_config = yaml.safe_load(f)
        
        if yaml_config and "ai_chat" in yaml_config:
            config_dict = yaml_config["ai_chat"]
            logger.info(f"[AI Chat Config] 成功加载配置文件")
            return Config(**config_dict)
        else:
            logger.warning(f"[AI Chat Config] 配置文件格式错误，缺少 'ai_chat' 节点")
            return Config()
    
    except Exception as e:
        logger.error(f"[AI Chat Config] 加载配置文件失败: {e}")
        return Config()


# 创建全局配置实例
plugin_config = load_config_from_yaml()


def get_config() -> Config:
    """
    获取配置
    
    Returns:
        Config: 配置对象
    """
    return plugin_config


def reload_config() -> Config:
    """
    重新加载配置
    
    Returns:
        Config: 配置对象
    """
    global plugin_config
    plugin_config = load_config_from_yaml()
    logger.info("[AI Chat Config] 配置已重新加载")
    return plugin_config


def load_system_prompt() -> str:
    """
    从项目根目录的 config 文件夹加载系统 Prompt
    
    Returns:
        str: 系统 Prompt 内容
    """
    project_root = get_project_root()
    config = get_config()
    prompt_file = project_root / "config" / config.prompt_file
    
    logger.debug(f"[AI Chat Config] 尝试加载 Prompt 文件: {prompt_file}")
    
    try:
        if prompt_file.exists():
            with open(prompt_file, "r", encoding="utf-8") as f:
                prompt = f.read().strip()
                if prompt:
                    logger.info(f"[AI Chat Config] 成功加载 Prompt 文件: {prompt_file.name}")
                    return prompt
        else:
            logger.warning(f"[AI Chat Config] Prompt 文件不存在: {prompt_file}")
    except Exception as e:
        logger.error(f"[AI Chat Config] 读取 Prompt 文件失败: {e}")
    
    # 返回默认 Prompt
    default_prompt = "你是一个友好、乐于助人的 AI 助手。请用简洁、友好的语气回答用户的问题。"
    logger.info("[AI Chat Config] 使用默认 Prompt")
    return default_prompt
