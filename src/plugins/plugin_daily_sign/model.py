from tortoise import fields
from tortoise.models import Model

from datetime import date

from src.plugins.plugin_daily_sign.data_pojo import Sign_Info


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




