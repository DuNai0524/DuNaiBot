from pydantic import BaseModel
from datetime import date


class LineUpShopInfo(BaseModel):
    name: str
    group_id: int
    maimai_count: int
    person_count: int
    update_time: date
    alias: str

