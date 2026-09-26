import urllib.request
import ssl
import os

URL = "https://raw.githubusercontent.com/ioptu/migu_video/refs/heads/main/cctv.migu.m3u"

def main():
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE
    
    try:
        req = urllib.request.Request(URL, headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'})
        with urllib.request.urlopen(req, context=ctx, timeout=30) as response:
            content = response.read().decode('utf-8', errors='ignore')
    except:
        return

 
    lines = content.replace('\r\n', '\n').replace('\r', '\n').split('\n')
    txt_lines = ["央视CCTV,#genre"]

    for idx, line in enumerate(lines):
        clean_line = line.strip()
        if clean_line.startswith("http://") or clean_line.startswith("https://"):
            name = "未知频道"
            if idx > 0:
                prev_line = lines[idx-1].strip()
                if prev_line.startswith("#EXTINF:"):
                    name = prev_line.split(",")[-1].strip()
                else:
                    name = prev_line[:20]
            
            txt_lines.append(f"{name},{clean_line}")


    current_dir = os.path.dirname(os.path.abspath(__file__))
    output_file = os.path.join(current_dir, "cctv_clean.txt")

    with open(output_file, "w", encoding="utf-8") as f:
        f.write("\n".join(txt_lines))

if __name__ == "__main__":
    main()
