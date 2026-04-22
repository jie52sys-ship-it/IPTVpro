import requests
import re
from urllib.parse import urlparse

# 目标接口（就是你要解密的ds65地址）
SOURCE_URL = "https://ds65.tv1288.xyz"
OUTPUT_M3U = "live.m3u"
OUTPUT_TXT = "live.txt"

# 模拟浏览器请求头，和你用的解密网站保持一致
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8"
}

def decrypt_source():
    try:
        # 1. 拉取原始接口数据（和你丢进解密网站的步骤一样）
        resp = requests.get(SOURCE_URL, headers=HEADERS, timeout=15)
        resp.raise_for_status()
        raw_data = resp.text
        print(f"✅ 成功拉取原始数据，长度：{len(raw_data)}")

        # 2. 解析数据，提取频道名称和地址（和你截图里的解密格式完全匹配）
        channels = []
        # 匹配直播地址（适配你截图里的m3u8链接）
        url_pattern = re.compile(r'(?<=,)(http://.*?\.m3u8|https://.*?\.m3u8)')
        urls = url_pattern.findall(raw_data)
        
        # 匹配频道名称（适配你截图里的tvg-name格式）
        name_pattern = re.compile(r'tvg-name="(.*?)"')
        names = name_pattern.findall(raw_data)

        # 配对频道名称和地址
        for i, url in enumerate(urls):
            name = names[i] if i < len(names) else f"未知频道{i+1}"
            logo = f"https://raw.githubusercontent.com/wanglindl/TVlogo/main/img/{name}.png"
            # 自动分组，和你截图里的央视卫视分组一致
            if "CCTV" in name or "卫视" in name:
                group = "央视卫视"
            else:
                group = "其他频道"
            channels.append((name, url, logo, group))

        print(f"✅ 解析完成，共获取 {len(channels)} 个频道")
        return channels

    except Exception as e:
        print(f"❌ 解析失败：{str(e)}")
        return []

def save_files(channels):
    # 生成和你截图格式完全一致的标准M3U文件
    with open(OUTPUT_M3U, "w", encoding="utf-8") as f:
        f.write('#EXTM3U x-tvg-url="https://123.tv1288.xyz/2026.xml"\n')
        for name, url, logo, group in channels:
            f.write(f'#EXTINF:-1 tvg-name="{name}" tvg-logo="{logo}" group-title="{group}",{name}\n')
            f.write(f"{url}\n")

    # 同时生成TXT备用格式
    with open(OUTPUT_TXT, "w", encoding="utf-8") as f:
        for name, url, _, _ in channels:
            f.write(f"{name},{url}\n")

if __name__ == "__main__":
    chans = decrypt_source()
    if chans:
        save_files(chans)
        print(f"✅ 已生成解密后的直播源文件：{OUTPUT_M3U}")
    else:
        print("❌ 未解析到有效频道，请检查接口或网络")
