from pydantic import BaseModel


# 抽奖功能 基本信息
class AwardInfo(BaseModel):
    get_award_chance: int  # 增加概率
    get_times: int  # 抽奖次数
