"""
配置示例文件

将此文件重命名为 config_local.py 并填入你的配置
或者直接在 __init__.py 中的 load_config() 调用中设置参数
"""

# ==================== API 配置 ====================
# 通义千问 API Key（必填）
# 获取地址：https://dashscope.console.aliyun.com/
QWEN_API_KEY = "sk-your-api-key-here"

# API 地址（一般不需要修改）
QWEN_API_URL = "https://dashscope.aliyuncs.com/api/v1/services/aigc/text-generation/generation"

# 使用的模型
# 可选值：qwen-turbo, qwen-plus, qwen-max
QWEN_MODEL = "qwen-turbo"


# ==================== 生成参数 ====================
# 最大生成 token 数（影响回复长度）
MAX_TOKENS = 1500

# 温度参数（0-2，越高越随机）
TEMPERATURE = 0.8

# Top-p 采样参数（0-1）
TOP_P = 0.8


# ==================== 系统 Prompt ====================
# 定义 AI 的角色和行为方式
# 你可以根据需要修改这个 Prompt 来改变 AI 的性格和专业领域

# 默认助手
SYSTEM_PROMPT = "你是一个友好、乐于助人的 AI 助手。请用简洁、友好的语气回答用户的问题。"

# 编程专家（示例）
# SYSTEM_PROMPT = "你是一个资深的软件工程师，精通 Python、JavaScript 等编程语言。请用专业但易懂的方式解答技术问题，并在适当时提供代码示例。"

# 猫娘角色（示例）
# SYSTEM_PROMPT = "你是一只可爱的猫娘，名字叫喵酱。你活泼开朗，说话时会在句尾加上'喵~'。你喜欢和主人互动，偶尔会撒娇。"

# 学习导师（示例）
# SYSTEM_PROMPT = "你是一位耐心的学习导师，擅长用简单易懂的方式解释复杂概念。你会通过举例和类比来帮助理解，并鼓励学生思考。"


# ==================== 功能开关 ====================
# 是否启用上下文记忆（多轮对话）
ENABLE_CONTEXT = True

# 上下文最大轮数（每轮包含用户问题和 AI 回复）
CONTEXT_MAX_LENGTH = 10


# ==================== 触发配置 ====================
# 触发 AI 对话的命令前缀
COMMAND_START = ["ai", "AI", "问"]


# ==================== 其他配置 ====================
# API 请求超时时间（秒）
REQUEST_TIMEOUT = 30


# ==================== 使用方法 ====================
# 方法 1：在 __init__.py 中导入并使用这些配置
"""
from .config_example import *

load_config(
    qwen_api_key=QWEN_API_KEY,
    qwen_model=QWEN_MODEL,
    system_prompt=SYSTEM_PROMPT,
    temperature=TEMPERATURE,
    max_tokens=MAX_TOKENS,
    enable_context=ENABLE_CONTEXT,
    context_max_length=CONTEXT_MAX_LENGTH,
)
"""

# 方法 2：直接在 __init__.py 中设置
"""
load_config(
    qwen_api_key="sk-your-api-key",
    system_prompt="你是一个友好的 AI 助手",
    temperature=0.8,
)
"""
