# -*- coding: utf-8 -*-
"""清理陨石文件夹中的无效版本"""
import os, shutil

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

to_delete = []

# 1. 所有 __pycache__ 目录
for dirpath, dirnames, filenames in os.walk(ROOT):
    for d in dirnames:
        if d == "__pycache__":
            to_delete.append(os.path.join(dirpath, d))

# 2. Aug10 子目录（所有旧版本）+ docx
aug10 = os.path.join(ROOT, "Aug10")
for item in os.listdir(aug10):
    p = os.path.join(aug10, item)
    if item.endswith(".docx"):
        to_delete.append(p)
    elif os.path.isdir(p):
        to_delete.append(p)

# 3. Aug11 旧版本子目录
aug11 = os.path.join(ROOT, "Aug11")
for item in os.listdir(aug11):
    p = os.path.join(aug11, item)
    if item in ("v1.1.2", "v1.1.3", "v1.1.4", "v1.1.5", "v1.1.6",
                "v2.0", "v2.1"):
        to_delete.append(p)

# 4. Aug11 根目录下的工具脚本和旧数据库
aug11_root_del = ["create_v2.py", "create_v2_html.py", "restart_v2.py",
                  "start_v2.py", "impact_db.json", "工作记录_2026-08-11.md"]
for f in aug11_root_del:
    p = os.path.join(aug11, f)
    if os.path.exists(p):
        to_delete.append(p)

print(f"待删除条目数: {len(to_delete)}")
for p in sorted(to_delete):
    exists = os.path.exists(p)
    is_dir = os.path.isdir(p)
    size = "目录" if is_dir else f"{os.path.getsize(p):,} 字节" if exists else "不存在"
    print(f"  [{'存在' if exists else '不存在'}] {p} ({size})")

print("\n开始删除...")
ok, fail = 0, 0
for p in to_delete:
    try:
        if os.path.isdir(p):
            shutil.rmtree(p)
        else:
            os.remove(p)
        ok += 1
        print(f"  OK: {p}")
    except Exception as e:
        fail += 1
        print(f"  FAIL: {p} -> {e}")

print(f"\n完成: 成功 {ok}, 失败 {fail}")
