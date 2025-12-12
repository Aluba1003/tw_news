import os
import yaml
from dotenv import load_dotenv

load_dotenv()

def load_config():
    # 先讀取 repo 裡的 sources.yml
    config = {}
    if os.path.exists("sources.yml"):
        with open("sources.yml", "r", encoding="utf-8") as f:
            config = yaml.safe_load(f)

    # 再讀取 GitHub Secrets (環境變數 SOURCES_YML)
    secret_sources = os.getenv("SOURCES_YML")
    if secret_sources:
        try:
            secret_config = yaml.safe_load(secret_sources)
            # 合併 sources
            if "sources" in secret_config:
                if "sources" not in config:
                    config["sources"] = []
                config["sources"].extend(secret_config["sources"])
            # 合併其他設定 (keywords, match_mode, delay)
            for key in ["keywords", "match_mode", "delay"]:
                if key in secret_config:
                    config[key] = secret_config[key]
        except Exception as e:
            print(f"❌ 無法解析 SOURCES_YML: {e}")

    return config

def main():
    config = load_config()
    if not config:
        raise ValueError("❌ 沒有找到任何設定 sources.yml 或 SOURCES_YML")

    print("✅ 成功載入設定")
    print(config)

if __name__ == "__main__":
    main()
