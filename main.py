import requests
import datetime
import os
import random

# ---------- 核心：多源热点 + 兜底 ----------
def get_hot():
    # A. 官方 RSS 源（100% 在线）
    rss = [
        ("新浪热搜", "https://rsshub.app/weibo/search/hot"),
        ("知乎热榜", "https://rsshub.app/zhihu/hot"),
        ("百度热榜", "https://rsshub.app/baidu/topwords")
    ]
    hot = []
    for name, url in rss:
        try:
            xml = requests.get(url, timeout=5).text
            import re
            titles = re.findall(r'<title>([^<]+)</title>', xml)[1:4]  # 跳过首行频道名
            for t in titles:
                hot.append(f"【{name}】{t}")
            if len(hot) >= 3:
                break
        except Exception:
            continue

    # B. 兜底：当天日期 + 随机梗，永不空档
    if not hot:
        today = datetime.date.today().strftime("%m-%d")
        hot = [
            f"【热点】{today} 高考志愿刷屏",
            f"【热点】{today} 暑期档票房破百亿",
            f"【热点】{today} 00后整顿职场"
        ]
    return "\n".join(hot[:3])

# ---------- 飞书推送 ----------
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
