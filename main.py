import requests
import datetime
import os
import hashlib
import hmac

# 1. 取今日热点
def get_hot():
    sources = {
        "微博": "https://api.hotpepper.cn/api/v1/weibo",
        "知乎": "https://api-hot.deno.dev/zhihu",
        "头条": "https://api-hot.deno.dev/toutiao",
        "抖音": "https://api-hot.deno.dev/douyin",
        "百度": "https://api-hot.deno.dev/baidu",
        "36氪": "https://api-hot.deno.dev/36kr"
    }
    hot_list = []
    for name, url in sources.items():
        try:
            data = requests.get(url, timeout=5).json()[:3]  # 取前 3
            for item in data:
                hot_list.append(f"【{name}】{item['title']}")
        except Exception:
            continue
    # 去重后取前 3 条
    unique = list(dict.fromkeys(hot_list))[:3]
    return "\n".join(unique) if unique else "今日暂无热点数据"

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
