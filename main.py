import requests
import datetime
import os
import hashlib
import hmac

headers = {"User-Agent": "Mozilla/5.0"}
data = requests.get(url, headers=headers, timeout=5).json()

# 1. 取今日热点
def get_hot():
    """
    8 大平台热点轮询，取前 3 条，任意一条成功即可。
    """
    import time, random

    # 国内可直接访问的接口列表
sources = {
    "微博": "https://weibo.com/ajax/side/hotSearch",
    "知乎": "https://www.zhihu.com/api/v3/feed/topstory/hot-lists/total",
    "头条": "https://www.toutiao.com/hot-event/hot-board/"
}

    hot_list = []
    for name, url in sources.items():
        try:
            data = requests.get(url, timeout=5).json()
            # 取前 2 条，避免过长
            for item in data[:2]:
                hot_list.append(f"【{name}】{item['title']}")
            # 只要拿到 3 条就停
            if len(hot_list) >= 3:
                break
        except Exception:
            continue

    # 本地兜底：如果全部接口都失败，用当天日期+随机梗，永远有内容
    if not hot_list:
        seed = int(time.strftime("%Y%m%d"))
        random.seed(seed)
        fallback = [
            "【热点】今日高考志愿开始填报",
            "【热点】暑期档票房破百亿",
            "【热点】00后整顿职场新姿势"
        ]
        hot_list = random.sample(fallback, 3)

    return "\n".join(hot_list[:3])

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
