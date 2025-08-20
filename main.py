import requests
import datetime
import os
import hashlib
import hmac
import time
import random

# 8 大平台热点轮询
def get_hot():
    sources = {
        "微博": "https://api-hot.deno.dev/weibo",
        "知乎": "https://api-hot.deno.dev/zhihu",
        "头条": "https://api-hot.deno.dev/toutiao",
        "百度": "https://api-hot.deno.dev/baidu",
        "B站": "https://api-hot.deno.dev/bilibili",
        "抖音": "https://api-hot.deno.dev/douyin",
        "36氪": "https://api-hot.deno.dev/36kr",
        "财联社": "https://api-hot.deno.dev/cailian"
    }

    hot_list = []
    for name, url in sources.items():
        try:
            data = requests.get(url, timeout=5).json()
            for item in data[:2]:
                hot_list.append(f"【{name}】{item['title']}")
            if len(hot_list) >= 3:
                break
        except Exception:
            continue

    # 兜底：日期+随机梗，永远有内容
    if not hot_list:
        seed = int(datetime.date.today().strftime("%Y%m%d"))
        random.seed(seed)
        fallback = [
            f"【微博】{datetime.date.today()} 热搜第一",
            f"【知乎】{datetime.date.today()} 热门问答",
            f"【头条】{datetime.date.today()} 实时要闻"
        ]
        hot_list = random.sample(fallback, 3)

    return "\n".join(hot_list[:3])

# 飞书推送
def push_feishu(text):
    body = {
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
    print(r.text)

if __name__ == "__main__":
    title = get_hot()
    content = f"【今日最热】{title}\n\n【观点1】…\n【观点2】…\n【互动】你怎么看？"
    push_feishu(content)
