from pydantic import BaseModel


class Sign_Info(BaseModel):
    all_gold: int
    today_gold: int
    sign_times: int
    today_lucky: int