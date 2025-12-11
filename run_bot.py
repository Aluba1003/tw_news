import os
import requests
import feedparser
import yaml
from dotenv import load_dotenv

# 嘗試讀取本地 .env（如果存在）
load_dotenv()

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

def send_telegram(text: str):
    if not TELEGRAM_TOKEN or not CHAT_ID:
        print("❌ 缺少 TELEGRAM_TOKEN 或 CHAT_ID")
        return
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    resp = requests.post(url, data={"chat_id": CHAT_ID, "text": text})
    if resp.status_code != 200:
        print("❌ 推播失敗:", resp.text)
    else:
        print("✅ 推播成功")

def fetch_rss(source_name, url, keywords, match_mode="any"):
    results = []
    try:
        feed = feedparser.parse(url)
        for entry in feed.entries:
            title, link = entry.title, entry.link
            if keywords:
                if match_mode == "any" and any(kw in title for kw in keywords):
                    results.append((source_name, title, link))
                elif match_mode == "all" and all(kw in title for kw in keywords):
                    results.append((source_name, title, link))
            else:
                results.append((source_name, title, link))
        if not results:
            results.append((source_name, "【沒有符合的新聞】", ""))
    except Exception as e:
        results.append((source_name, f"【抓取失敗: {e}】", ""))
    return results

def main():
    # 讀取 YAML 設定檔
    with open("sources.yml", "r", encoding="utf-8") as f:
        config = yaml.safe_load(f)

    # 關鍵字設定
    keywords = ["新北"]   # 只推播含有「新北」的新聞
    match_mode = "any"

    # 抓取並推播
    for source in config["sources"]:
        if not source.get("enabled", True):
            print(f"⏸ 跳過來源: {source['name']}")
            continue
        name = source["name"]
        url = source["url"]
        results = fetch_rss(name, url, keywords, match_mode)
        for src, title, link in results:
            message = f"{src}\n{title}\n{link}"
            send_telegram(message)

if __name__ == "__main__":
    main()
