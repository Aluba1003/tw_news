import os
import time
import requests
import feedparser
import yaml
from dotenv import load_dotenv

# 嘗試讀取本地 .env（如果存在）
load_dotenv()

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

def send_telegram(text: str, delay: int):
    if not TELEGRAM_TOKEN or not CHAT_ID:
        print("❌ 缺少 TELEGRAM_TOKEN 或 CHAT_ID")
        return
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    resp = requests.post(url, json={
        "chat_id": CHAT_ID,
        "text": text,
        "disable_web_page_preview": True
    })
    if resp.status_code != 200:
        data = resp.json()
        print("❌ 推播失敗:", data)
        if data.get("error_code") == 429:
            retry_after = data["parameters"]["retry_after"]
            print(f"⏸ 等待 {retry_after} 秒後重試...")
            time.sleep(retry_after)
            return send_telegram(text, delay)
    else:
        print("✅ 推播成功")
    time.sleep(delay)  # 每則訊息之間延遲

def fetch_rss(source_name, url, keywords, match_mode="any"):
    results = []
    try:
        feed = feedparser.parse(url)
        for entry in feed.entries:
            title, link = entry.title, entry.link
            summary = getattr(entry, "summary", getattr(entry, "description", ""))
            text_to_check = f"{title} {summary}"

            if keywords:
                if match_mode == "any" and any(kw in text_to_check for kw in keywords):
                    results.append((source_name, title, link))
                elif match_mode == "all" and all(kw in text_to_check for kw in keywords):
                    results.append((source_name, title, link))
            else:
                results.append((source_name, title, link))
    except Exception as e:
        results.append((source_name, f"【抓取失敗: {e}】", ""))
    return results

def main():
    # 讀取 YAML 設定檔
    with open("sources.yml", "r", encoding="utf-8") as f:
        config = yaml.safe_load(f)

    keywords = config.get("keywords", ["新北"])   # 從 YAML 讀取關鍵字
    match_mode = config.get("match_mode", "any") # 從 YAML 讀取比對模式
    delay = config.get("delay", 1)               # 從 YAML 讀取延遲秒數，預設 1 秒

    for source in config["sources"]:
        if not source.get("enabled", True):
            print(f"⏸ 跳過來源: {source['name']}")
            continue
        name = source["name"]
        url = source["url"]
        results = fetch_rss(name, url, keywords, match_mode)

        # 每則新聞單獨推播
        for src, title, link in results:
            message = f"{src}\n{title}\n{link}"
            send_telegram(message, delay)

if __name__ == "__main__":
    main()
