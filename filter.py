import urllib.request
import ssl

URL = "https://raw.githubusercontent.com/ioptu/migu_video/refs/heads/main/cctv.migu.m3u"

def main():
    try:
        # 忽略可能存在的 SSL 证书验证问题，防止在服务器端请求中断
        ctx = ssl.create_default_context()
        ctx.check_hostname = False
        ctx.verify_mode = ssl.CERT_NONE
        
        req = urllib.request.Request(URL, headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'})
        with urllib.request.urlopen(req, context=ctx, timeout=30) as response:
            content = response.read().decode('utf-8')
    except:
        return

    lines = content.splitlines()
    txt_lines = ["央视CCTV,#genre"]

    for i in range(len(lines)):
        line = lines[i].strip()
        
        if line.startswith("#EXTINF:"):
            # 严格以最后一个逗号来截取频道名字
            name = line.split(",")[-1].strip() if "," in line else "未知频道"
            
            # 自动向后查找第一条可用的播放链接
            next_url = ""
            for j in range(i + 1, min(i + 6, len(lines))):
                sub_line = lines[j].strip()
                if sub_line.startswith("http://") or sub_line.startswith("https://"):
                    next_url = sub_line
                    break
            
            if next_url:
                txt_lines.append(f"{name},{next_url}")

    if len(txt_lines) > 1:
        with open("cctv_clean.txt", "w", encoding="utf-8") as f:
            f.write("\n".join(txt_lines))

if __name__ == "__main__":
    main()
