# -*- coding: utf-8 -*-
"""检查所有文件的创建时间，识别可能放错文件夹的文件"""
import os
import sys
from datetime import datetime

ROOT = os.path.dirname(os.path.abspath(__file__))

# 定义各文件夹应该属于的日期范围
folder_expected = {
    "Aug10": "2025-08-10",
    "Aug11": "2025-08-11",
    "Aug12": "2025-08-12",
}

def get_create_time(filepath):
    """获取文件创建时间（Windows 下使用 st_ctime）"""
    try:
        stat = os.stat(filepath)
        # Windows 下 st_ctime 实际上是创建时间
        return datetime.fromtimestamp(stat.st_ctime)
    except Exception as e:
        return None

def main():
    print("=" * 70)
    print("文件创建时间检查 - 陨石项目目录")
    print("=" * 70)
    print()
    
    # 收集所有文件
    files_info = []
    for root, dirs, files in os.walk(ROOT):
        # 跳过 __pycache__
        dirs[:] = [d for d in dirs if d != "__pycache__"]
        for f in files:
            fpath = os.path.join(root, f)
            ctime = get_create_time(fpath)
            if ctime:
                relpath = os.path.relpath(fpath, ROOT)
                # 判断属于哪个子文件夹
                parts = relpath.split(os.sep)
                top_folder = parts[0] if len(parts) > 1 else "(根目录)"
                files_info.append({
                    "relpath": relpath,
                    "top_folder": top_folder,
                    "ctime": ctime,
                    "ext": os.path.splitext(f)[1].lower(),
                })
    
    # 按创建时间排序
    files_info.sort(key=lambda x: x["ctime"])
    
    print(f"共发现 {len(files_info)} 个文件\n")
    
    # 按顶层文件夹分组
    by_folder = {}
    for fi in files_info:
        f = fi["top_folder"]
        if f not in by_folder:
            by_folder[f] = []
        by_folder[f].append(fi)
    
    # 输出每个文件夹的时间范围
    print("-" * 70)
    print("【各文件夹时间范围】")
    print("-" * 70)
    for folder in sorted(by_folder.keys()):
        files = by_folder[folder]
        times = [f["ctime"] for f in files]
        if times:
            min_t = min(times)
            max_t = max(times)
            print(f"  {folder:20s} | 最早: {min_t.strftime('%Y-%m-%d %H:%M:%S')} | 最晚: {max_t.strftime('%Y-%m-%d %H:%M:%S')} | 文件数: {len(files)}")
    
    # 检查异常：文件夹内文件的创建日期与文件夹预期日期不匹配
    print()
    print("-" * 70)
    print("【异常检查】")
    print("-" * 70)
    
    issues_found = False
    
    for folder, expected_date_str in folder_expected.items():
        expected_date = datetime.strptime(expected_date_str, "%Y-%m-%d")
        if folder in by_folder:
            for fi in by_folder[folder]:
                fi_date = fi["ctime"]
                diff_days = (fi_date.date() - expected_date.date()).days
                if abs(diff_days) > 1:  # 相差超过1天
                    issues_found = True
                    print(f"  ⚠️  {fi['relpath']}")
                    print(f"     创建时间: {fi['ctime'].strftime('%Y-%m-%d %H:%M:%S')}")
                    print(f"     所在文件夹: {folder} (预期日期: {expected_date_str})")
                    if diff_days > 0:
                        print(f"     → 文件比预期晚 {diff_days} 天")
                    else:
                        print(f"     → 文件比预期早 {abs(diff_days)} 天")
                    print()
    
    # 检查根目录文件是否合理
    root_files = [fi for fi in files_info if fi["top_folder"] == "(根目录)"]
    if root_files:
        print("-" * 70)
        print("【根目录文件】")
        print("-" * 70)
        for fi in root_files:
            print(f"  📄 {fi['relpath']}")
            print(f"     创建时间: {fi['ctime'].strftime('%Y-%m-%d %H:%M:%S')}")
            print(f"     扩展名: {fi['ext']}")
            print()
    
    # 检查 _js_build 中的非 JS/非构建文件
    js_build_dir = os.path.join(ROOT, "Aug12", "_js_build")
    if os.path.isdir(js_build_dir):
        print("-" * 70)
        print("【_js_build 目录内容检查】")
        print("-" * 70)
        for fi in by_folder.get("Aug12", []):
            if "_js_build" in fi["relpath"]:
                ext = fi["ext"]
                if ext not in (".js", ".py", ".json", ".html", ".md", ".txt"):
                    print(f"  ⚠️  异常文件类型: {fi['relpath']} (类型: {ext})")
    
    if not issues_found and len(root_files) == 0:
        print("  ✅ 未发现明显异常！")
    
    print()
    print("=" * 70)
    print("检查完成")
    print("=" * 70)

if __name__ == "__main__":
    main()
