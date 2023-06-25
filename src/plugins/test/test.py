import requests
import httpx
import json

# API 接口 所需用到的参数
appid = "41432358"
appsecret = "3C9Dy2VC"


url = "https://v0.yiketianqi.com/free/day?"
city = "长沙"


if __name__ == '__main__':
    r = httpx.get(url+"appid="+appid+"&appsecret="+appsecret+"&city="+city)
    info = json.loads(r.text)
    print(info)