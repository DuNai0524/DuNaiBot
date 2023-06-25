from pydantic import BaseModel


class UserData(BaseModel):
    all_gold: int
    today_gold: int
    sign_times: int
    today_lucky: int
