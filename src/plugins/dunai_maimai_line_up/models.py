from datetime import datetime

from tortoise.models import Model
from tortoise import fields

from .data_pojo import LineUpShopInfo


# 店家信息
class Store_Info(Model):
    id = fields.IntField(pk=True, generated=True)
    name = fields.TextField()
    maimai_count = fields.IntField(default=1)
    person_count = fields.IntField(default=0)
    alias = fields.TextField()
    update_time = fields.DatetimeField(default=datetime(2000, 1, 1, 0, 0, 0))
    status = fields.IntField(default=0)  # 0:正常 1:维修或不能游玩

    class Meta:
        table = "maimai_lineup_storeInfo"
        table_description = "maimai排队功能"

    """
    id 主键
    group_id 所属群
    name 店家名称
    maimai_count 机台数量
    person_count 出勤人数数量
    alias 别称
    update_time 数据更新时间
    status 机台可游玩状态
    """

    # 添加新的店铺信息
    @classmethod
    async def addInfo(
            cls,
            name,
            maimai_count,
            alias,
    ) -> int:
        record, _ = await Store_Info.get_or_create(
            name=name,
            maimai_count=maimai_count,
            alias=alias
        )

        return 200

    # 获取机厅人数
    @classmethod
    async def getNumInfo(
            cls,
            alias,
    ) -> int:
        try:
            record, _ = await Store_Info.get_or_create(
                alias=alias,
            )
        except Exception as e:
            record = None
        print(record)
        if record is None:
            return -500
        if record.status == 1:
            return -400  # 机厅状态表示
        return record.person_count

    # 更新机厅人数
    @classmethod
    async def updateNumInfo(
            cls,
            alias,
            now_person
    ) -> int:
        record, _ = await Store_Info.get_or_create(
            alias=alias
        )
        record.person_count = now_person
        record.update_time = datetime.today()
        await record.save(update_fields=["person_count", "update_time"])
        return record.person_count

    # 更新机厅状态
    @classmethod
    async def updateStatus(
            cls,
            alias,
            status
    ) -> int:
        record, _ = await Store_Info.get_or_create(
            alias=alias,
        )

        record.status = status
        record.update_time = datetime.today()
        await record.save(update_fields=["status", "update_time"])
        return record.status

    # 获取时间
    @classmethod
    async def getTime(
            cls,
            alias,
    ) -> datetime:
        record, _ = await Store_Info.get_or_create(
            alias=alias
        )

        time = record.update_time
        return time
