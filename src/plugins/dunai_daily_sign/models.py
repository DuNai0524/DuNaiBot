import random

from nonebot.log import logger

from datetime import date

from tortoise import fields
from tortoise.models import Model

from .data_pojo import UserData

from ..dunai_get_award.models import UserAward


class Daily_Sign(Model):
    id = fields.IntField(pk=True, generated=True)  # 主键
    user_id = fields.IntField()  # 用户QQ号
    group_id = fields.IntField()  # 所在QQ群号
    gold = fields.IntField(default=0)  # 金币所有量
    sign_times = fields.IntField(default=0)  # 签到次数
    last_sign = fields.DateField(default=date(2000, 1, 1))  # 上一次签到时间

    class Meta:
        table = "daily_sign"
        table_description = "用户签到表"

    """
    添加签到记录并返回签到数据
    user_id 用户id
    group_id 群id
    gold 拥有金币
    lucky_gold 获得的幸运金币
    today_lucky 今日幸运值
    """

    @classmethod
    async def sign_in(
            cls,
            user_id: int,
            group_id: int,
            base_gold: int,
            lucky_gold: int,
            today_lucky: int,

    ) -> UserData:
        record, _ = await Daily_Sign.get_or_create(
            user_id=user_id,
        )

        today = date.today()
        record.last_sign = today

        today_gold = base_gold + lucky_gold * today_lucky
        record.gold += today_gold
        all_gold = record.gold

        record.sign_times += 1
        record.group_id = group_id

        await record.save(update_fields=["last_sign", "gold", "sign_times","group_id"])
        return UserData(
            all_gold=all_gold,
            today_gold=today_gold,
            sign_times=record.sign_times,
            today_lucky=today_lucky
        )

    """
    获取最近的签到时间
    """

    @classmethod
    async def get_last_sign_time(
            cls,
            user_id: int,
    ) -> date:
        record, _ = await Daily_Sign.get_or_create(
            user_id=user_id,

        )
        return record.last_sign

    """
    获取金币
    """

    @classmethod
    async def get_gold(
            cls,
            user_id: int,
    ) -> int:
        record, _ = await Daily_Sign.get_or_create(
            user_id=user_id
        )
        return record.gold

    """
    调整/更新金币
    """

    @classmethod
    async def adjust_gold(
            cls,
            adjust: int,
            user_id: int,
    ) -> int:
        record, _ = await Daily_Sign.get_or_create(
            user_id=user_id
        )
        record.gold = adjust
        await record.save(update_fields=["gold"])
        return record.gold

    """
    抽奖
    1/10,通过用户的金币
    """
    @classmethod
    async def get_award(
            cls,
            user_id: int,
            use_gold: int,

    ) -> int:
        record, _ = await Daily_Sign.get_or_create(
            user_id=user_id,
        )

        award_info = await UserAward.getInfo(
            user_id=user_id,
        )

        # 抽奖逻辑部分
        base_chance = 0
        end_chance = base_chance + award_info.get_award_chance

        all_gold = record.gold
        n1 = random.randint(1, 101)
        logger.debug(f"抽奖插件:用户 {user_id} 抽奖, 现有概率: {award_info.get_award_chance}, 中奖点数:{n1}")
        if base_chance <= n1 <= end_chance:
            all_gold += use_gold
            award_info.get_award_chance = 10
        else:
            all_gold -= use_gold
            award_info.get_award_chance += 5

        award_info.get_times += 1
        record.gold = all_gold

        await record.save(update_fields=["gold"])
        await UserAward.updateInfo(
            user_id=user_id,
            get_award_chance=award_info.get_award_chance,
            get_times=award_info.get_times
        )

        return all_gold

    # 获取金币排名
    @classmethod
    async def get_list(
            cls,
    ) -> list:
        data = await Daily_Sign.filter().all()
        print(data)
        data.sort(key=lambda t:t.gold, reverse=True)
        return data


    # 转账功能
    @classmethod
    async def to_other_gold(
            cls,
            main_qq:int,
            in_qq:int,
            gold:int,
    ) -> int:
        record_main,_ = await Daily_Sign.get_or_create(user_id=main_qq)
        record_others,_ = await Daily_Sign.get_or_create(user_id=in_qq)

        record_main.gold -= gold
        record_others.gold += gold

        await record_main.save(update_fields=["gold"])
        await record_others.save(update_fields=["gold"])

        return 200
