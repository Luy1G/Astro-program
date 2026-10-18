# -*- coding: utf-8 -*-
"""复制 v2.2 到 final/v3.0"""
import os
import shutil

ROOT = os.path.dirname(os.path.abspath(__file__))
src = os.path.join(ROOT, "Aug12", "v2.2")
dst = os.path.join(ROOT, "final", "v3.0")

os.makedirs(dst, exist_ok=True)

for root, dirs, files in os.walk(src):
    # 跳过 __pycache__
    dirs[:] = [d for d in dirs if d != "__pycache__"]
    rel = os.path.relpath(root, src)
    target_dir = dst if rel == "." else os.path.join(dst, rel)
    os.makedirs(target_dir, exist_ok=True)
    for f in files:
        src_file = os.path.join(root, f)
        dst_file = os.path.join(target_dir, f)
        if f.endswith(".pyc"):
            continue
        shutil.copy2(src_file, dst_file)
        print(f"  ✓ {os.path.join(rel, f)}")

print("\n✅ 复制完成")
