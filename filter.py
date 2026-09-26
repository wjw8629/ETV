import urllib.request
import os

URL = "https://raw.githubusercontent.com/ioptu/migu_video/refs/heads/main/cctv.migu.m3u"

def main():
    try:
        req = urllib.request.Request(URL, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req) as response:
            content = response.read().decode('utf-8')
    except:
        return

    lines = content.splitlines()
    txt_lines = ["CCTV,#genre"]

    i = 0
    while i < len(lines):
        line = lines[i].strip()
        if not line:
            i += 1
            continue

        if line.startswith("#EXTINF:"):
            name = line.split(",")[-1].strip() if "," in line else "未知频道"
            next_line = lines[i+1].strip() if i + 1 < len(lines) else ""
            
            if next_line and not next_line.startswith("#"):
                txt_lines.append(f"{name},{next_line}")
                i += 2
                continue
        i += 1

    with open("live.txt", "w", encoding="utf-8") as f:
        f.write("\n".join(txt_lines))

if __name__ == "__main__":
    main()
