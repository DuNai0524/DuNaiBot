from pydantic import BaseModel


class Sign_Info(BaseModel):
    all_gold: int
    today_gold: int
    sign_times: int
    today_lucky: int

class Get_Award_Info(BaseModel):
    success: bool  # 是否中奖
    cost_gold: int  # 消耗的金币
    current_gold: int  # 当前剩余金币
    current_probability: float  # 当前中奖概率
    reward_gold: int = 0  # 奖励金币（中奖时）
