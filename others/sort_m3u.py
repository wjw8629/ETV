# -*- coding: utf-8 -*-
import re
from pathlib import Path

# ====================== 配置 ======================
script_dir = Path(__file__).resolve().parent
input_file = script_dir / "mig.m3u"
output_cctv = script_dir / "cctv.migu.m3u"    # 只包含央视的文件（频道名简化）
# =================================================

def parse_m3u(content):
    channels = []
    lines = content.strip().splitlines()
    i = 0
    while i < len(lines):
        line = lines[i].strip()
        if line.startswith("#EXTINF:"):
            extinf = line
            url = ""
            i += 1
            while i < len(lines) and not lines[i].strip().startswith("#EXTINF:"):
                if lines[i].strip() and not lines[i].strip().startswith("#"):
                    url = lines[i].strip()
                i += 1
            if url:
                channels.append((extinf, url))
            continue
        i += 1
    return channels


def get_group_priority_and_key(extinf):
    name_match = re.search(r',(.+?)$', extinf)
    name = name_match.group(1).strip() if name_match else ""

    if "央视" in extinf or any(c in name.upper() for c in ["CCTV", "CGTN"]):
        group = "央视"
        priority = 0
    elif "卫视" in extinf or "卫视" in name:
        group = "卫视"
        priority = 1
    else:
        group = "其它"
        priority = 2

    if group == "央视":
        num_match = re.search(r'CCTV(\d+)', name)
        if num_match:
            num = int(num_match.group(1))
            sort_key = (0, num, name)
        elif "CGTN" in name:
            sort_key = (1, 0, name)
        elif any(x in name for x in ["欧洲", "美洲"]):
            sort_key = (2, 0, name)
        else:
            sort_key = (3, 0, name)
    else:
        sort_key = (0, 0, name)

    return (priority, *sort_key), group


def is_cctv_channel(extinf):
    """严格只保留 CCTV1 ~ CCTV17"""
    name_match = re.search(r',(.+?)$', extinf)
    name = name_match.group(1).strip() if name_match else ""
    
    exclude_keywords = ["美洲", "欧洲", "CGTN", "老故事", "发现之旅", "中学生"]
    
    if any(kw in name for kw in exclude_keywords):
        return False
    
    return bool(re.search(r'CCTV\s*-?\s*(?:1[0-7]|[1-9])\s*\+?(?!\d)', name, re.IGNORECASE))


def update_group_title(extinf, new_group):
    """正确插入 group-title"""
    extinf = re.sub(r'\s*group-title="[^"]*"', '', extinf)
    if ',' in extinf:
        parts = extinf.rsplit(',', 1)
        if len(parts) == 2:
            extinf = f'{parts[0].strip()},group-title="{new_group}",{parts[1].strip()}'
    return extinf.strip()


def simplify_cctv_name(extinf):
    """在央视专用文件中，同时简化 tvg-id、tvg-name 和显示名称"""
    # 提取原始名称
    name_match = re.search(r',(.+?)$', extinf)
    if not name_match:
        return extinf
    
    old_name = name_match.group(1).strip()
    
    # 提取 CCTV + 数字 + 可选的 +
    match = re.search(r'CCTV\s*-?\s*(1[0-7]|[1-9])\s*(\+)?', old_name, re.IGNORECASE)
    if not match:
        return extinf
    
    new_name = f"CCTV{match.group(1)}{'+' if match.group(2) else ''}"
    
    # 同时修改 tvg-id、tvg-name 和显示名称
    extinf = re.sub(r'tvg-id="[^"]*"', f'tvg-id="{new_name}"', extinf)
    extinf = re.sub(r'tvg-name="[^"]*"', f'tvg-name="{new_name}"', extinf)
    
    # 修改显示名称（逗号后面的部分）
    extinf = re.sub(r',.+?$', f',{new_name}', extinf)
    
    return extinf


def main():
    with open(input_file, "r", encoding="utf-8") as f:
        content = f.read()

    channels = parse_m3u(content)

    # 去重
    seen = {}
    unique_channels = []
    for extinf, url in channels:
        tvg_id = re.search(r'tvg-id="([^"]+)"', extinf)
        tvg_name = re.search(r'tvg-name="([^"]+)"', extinf)
        key = (tvg_id.group(1) if tvg_id else "") or (tvg_name.group(1) if tvg_name else "") or extinf
        if key not in seen:
            seen[key] = True
            unique_channels.append((extinf, url))

    cctv_channels = [ch for ch in unique_channels if is_cctv_channel(ch[0])]
    cctv_sorted = sorted(cctv_channels, key=lambda x: get_group_priority_and_key(x[0])[0][1:])

    with open(output_cctv, "w", encoding="utf-8") as f:
        f.write("#EXTM3U\n\n")
        f.write("# ================================== 央视 CCTV 频道 ==================================\n\n")
        for extinf, url in cctv_sorted:
            new_extinf = update_group_title(extinf, "央视")
            new_extinf = simplify_cctv_name(new_extinf)   # ← 关键：简化名称
            f.write(new_extinf + "\n")
            f.write(url + "\n\n")

    print(f"✅ 处理完成！")
    print(f" 输入频道数：{len(channels)}")
    print(f" 去重后频道数：{len(unique_channels)}")
    print(f" 央视 CCTV 频道数：{len(cctv_channels)}")
    print(f" 输出文件（仅央视，已简化名称）：{output_cctv}")


if __name__ == "__main__":
    main()
