from tortoise import fields
from tortoise.models import Model

from datetime import date

from src.plugins.plugin_daily_common.data_pojo import Sign_Info, Get_Award_Info, Prize_Pool_Info


class Daily_Sign(Model):
    """
    群每日签到表
    user_id: 用户QQ号
    last_sign: 上次签到时间
    sign_count: 连续签到天数
    total_sign: 总签到天数
    """
    id = fields.IntField(pk=True, generated=True)
    user_id = fields.BigIntField(index=True, unique=True)
    last_sign = fields.DateField(default=date(2000, 1, 1))
    gold = fields.IntField(default=0)
    sign_count = fields.IntField(default=0)
    total_sign = fields.IntField(default=0)
    lottery_probability = fields.FloatField(default=10.0)  # 抽奖概率，初始为10%

    class Meta:
        table = "plugin_daily_sign"
        table_description = "每日签到表"


    """
    用户签到
    """
    @classmethod
    async def sign_in(cls,
                      user_id:int,
                      base_gold:int,
                      lucky_gold:int,
                      today_lucky:int):
        record, _ = await Daily_Sign.get_or_create(
            user_id=user_id,
        )

        today = date.today()
        record.last_sign = today

        today_gold = base_gold + lucky_gold * today_lucky
        record.gold += today_gold
        all_gold = record.gold

        record.sign_count += 1

        await record.save(update_fields=["gold", "sign_count", "last_sign"])
        return Sign_Info(
            all_gold=all_gold,
            today_gold=today_gold,
            sign_times=record.sign_count,
            today_lucky=today_lucky
        )

    """
    获取用户上次签到时间
    """
    @classmethod
    async def get_last_sign_time(cls,
                                 user_id:int):
        record, _ = await Daily_Sign.get_or_create(
            user_id=user_id,
        )
        return record.last_sign

    """
    获取整个列表
    """
    @classmethod
    async def get_list(cls) -> list:
        data = await Daily_Sign.filter().all()
        data.sort(key = lambda t : t.gold, reverse = True)
        return data

    """
    抽奖功能
    """
    @classmethod
    async def lottery(cls, user_id: int, cost_gold: int) -> Get_Award_Info:
        import random
        
        # 获取或创建用户记录
        record, _ = await Daily_Sign.get_or_create(user_id=user_id)
        
        # 检查金币是否足够
        if record.gold < cost_gold:
            raise ValueError(f"金币不足！当前拥有{record.gold}金币，需要{cost_gold}金币")
        
        # 扣除金币
        record.gold -= cost_gold
        
        # 获取当前概率
        current_probability = record.lottery_probability
        
        # 判断是否中奖
        random_num = random.uniform(0, 100)
        success = random_num < current_probability
        
        reward_gold = 0
        if success:
            # 中奖：奖励为消耗金币的2-3倍
            reward_multiplier = random.uniform(2.0, 3.0)
            reward_gold = int(cost_gold * reward_multiplier)
            record.gold += reward_gold
            # 中奖后重置概率
            record.lottery_probability = 10.0
        else:
            # 未中奖：概率提升5%
            record.lottery_probability = min(record.lottery_probability + 5.0, 100.0)
        
        # 保存记录
        await record.save(update_fields=["gold", "lottery_probability"])
        
        return Get_Award_Info(
            success=success,
            cost_gold=cost_gold,
            current_gold=record.gold,
            current_probability=current_probability,
            reward_gold=reward_gold
        )


class Prize_Pool(Model):
    """
    奖池表
    只有一条记录，用于存储全局奖池金币数量
    """
    id = fields.IntField(pk=True, generated=True)
    total_gold = fields.IntField(default=0)  # 奖池总金币数

    class Meta:
        table = "plugin_prize_pool"
        table_description = "奖池表"

    """
    获取奖池信息
    """
    @classmethod
    async def get_pool(cls):
        pool, _ = await Prize_Pool.get_or_create(id=1)
        return pool

    """
    奖池抽奖功能
    概率计算：基础概率 + (投入金币 / 奖池金币) * 权重
    金币越多，中奖概率越高
    """
    @classmethod
    async def prize_lottery(cls, user_id: int, cost_gold: int) -> Prize_Pool_Info:
        import random
        
        # 获取用户记录
        user_record, _ = await Daily_Sign.get_or_create(user_id=user_id)
        
        # 检查金币是否足够
        if user_record.gold < cost_gold:
            raise ValueError(f"金币不足！当前拥有{user_record.gold}金币，需要{cost_gold}金币")
        
        # 获取奖池
        pool = await cls.get_pool()
        
        # 扣除用户金币
        user_record.gold -= cost_gold
        
        # 计算中奖概率
        # 基础概率：5%
        # 金币加成：投入金币占奖池的比例，最高加成45%
        # 总概率范围：5% - 50%
        base_probability = 5.0
        if pool.total_gold > 0:
            gold_ratio = cost_gold / pool.total_gold
            bonus_probability = min(gold_ratio * 100, 45.0)  # 最高加成45%
        else:
            # 奖池为空时，给予固定加成
            bonus_probability = min(cost_gold / 1000 * 5, 45.0)  # 每1000金币加5%，最高45%
        
        probability = base_probability + bonus_probability
        
        # 判断是否中奖
        random_num = random.uniform(0, 100)
        success = random_num < probability
        
        win_gold = 0
        if success:
            # 中奖：获得奖池所有金币
            win_gold = pool.total_gold + cost_gold  # 包含本次投入
            user_record.gold += win_gold
            # 清空奖池
            pool.total_gold = 0
        else:
            # 未中奖：金币进入奖池
            pool.total_gold += cost_gold
        
        # 保存记录
        await user_record.save(update_fields=["gold"])
        await pool.save(update_fields=["total_gold"])
        
        return Prize_Pool_Info(
            success=success,
            cost_gold=cost_gold,
            current_gold=user_record.gold,
            probability=probability,
            pool_gold=pool.total_gold,
            win_gold=win_gold
        )

    """
    查询奖池金币数量
    """
    @classmethod
    async def get_pool_gold(cls) -> int:
        pool = await cls.get_pool()
        return pool.total_gold



