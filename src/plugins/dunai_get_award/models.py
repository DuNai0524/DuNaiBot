from tortoise.models import Model
from tortoise import fields

from .data_pojo import AwardInfo


class UserAward(Model):
    id = fields.IntField(pk=True, generated=True)  # 主键
    user_id = fields.IntField()
    group_id = fields.IntField()
    get_award_chance = fields.IntField(default=10)
    get_times = fields.IntField(default=0)

    class Meta:
        table = "user_award"
        table_description = "抽奖保底统计"

    """
    抽奖保底机制统计
    id 主键
    user_id QQ号
    group_id 群号
    get_award_chance 未中奖增加概率
    get_times 抽奖次数
    """

    """
    保底机制解释
    底金20起步
    初始中奖概率10%
    每次没抽到+5%
    抽到之后增加概率归零
    """

    @classmethod
    async def getInfo(
            cls,
            user_id,
    ) -> AwardInfo:
        record, _ = await UserAward.get_or_create(
            user_id=user_id,
        )

        return AwardInfo(
            get_award_chance=record.get_award_chance,
            get_times=record.get_times
        )

    @classmethod
    async def updateInfo(
            cls,
            user_id,
            get_award_chance,
            get_times,
    ) -> AwardInfo:
        record, _ = await UserAward.get_or_create(
            user_id=user_id,
        )

        record.get_award_chance = get_award_chance
        record.get_times = get_times

        await record.save(update_fields=['get_times','get_award_chance'])
        return AwardInfo(
            get_award_chance=record.get_award_chance,
            get_times=record.get_times
        )

