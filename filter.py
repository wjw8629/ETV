import urllib.request
import os

# 目标咪咕直播源网络地址
URL = "https://githubusercontent.com"

def main():
    try:
        req = urllib.request.Request(URL, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req) as response:
            content = response.read().decode('utf-8')
    except:
        return

    lines = content.splitlines()
    txt_lines = ["央视CCTV,#genre"]

    i = 0
    while i < len(lines):
        line = lines[i].strip()
        if not line:
            i += 1
            continue

        if line.startswith("#EXTINF:"):
            # 提取逗号后面的频道真实名称（例如：CCTV1）
            name = line.split(",")[-1].strip() if "," in line else "未知频道"
            next_line = lines[i+1].strip() if i + 1 < len(lines) else ""
            
            # 只要有播放链接，就写入 TXT 格式："频道名,链接"
            if next_line and not next_line.startswith("#"):
                txt_lines.append(f"{name},{next_line}")
                i += 2
                continue
        i += 1

    # 写入生成全新的纯净直播源 txt 文件
    with open("cctv_clean.txt", "w", encoding="utf-8") as f:
        f.write("\n".join(txt_lines))

if __name__ == "__main__":
    main()
