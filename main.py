import requests
import datetime
import os
import hashlib
import hmac

# 1. 取今日热点
def get_hot():
    url = "https://api.hotpepper.cn/api/v1/top10"
    try:
        data = requests.get(url, timeout=10).json()
        return data[0]["title"]
    except Exception:
        return "今日暂无热点数据"

# 2. 推送到飞书
def push_feishu(text):
    import time
    # 直接获取当前 10 位 Unix 时间戳
    ts = str(int(time.time()))
    secret = os.getenv("FEISHU_SECRET", "")
    sign = ""
    if secret:
        string_to_sign = f"{ts}\n{secret}"
        sign = hmac.new(secret.encode(), string_to_sign.encode(), hashlib.sha256).hexdigest()

    body = {
        "timestamp": ts,
        "sign": sign,
        "msg_type": "post",
        "content": {
            "post": {
                "zh_cn": {
                    "title": f"今日口播热点 {datetime.date.today()}",
                    "content": [[{"tag": "text", "text": text}]]
                }
            }
        }
    }
    r = requests.post(os.getenv("FEISHU_WEBHOOK"), json=body)
    print(r.text)  # 把返回打印出来，方便你二次确认

# 3. 主流程
if __name__ == "__main__":
    title = get_hot()
    content = f"【今日最热】{title}\n\n【观点1】…\n【观点2】…\n【互动】你怎么看？"
    push_feishu(content)
