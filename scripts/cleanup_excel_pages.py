#!/usr/bin/env python3
"""
清理 excel_pages 目录中的旧xls文件
在重新下载搜索结果前执行，确保获取最新数据
"""
import os

INPUT_DIR = r'D:\.openclaw\workspace\nmpa_trials\data\excel_pages'

# 检查目录是否存在
if not os.path.exists(INPUT_DIR):
    print(f'目录不存在: {INPUT_DIR}')
    exit(0)

# 获取所有xls文件
files = [f for f in os.listdir(INPUT_DIR) if f.endswith('.xls')]

if not files:
    print('目录为空，无需清理')
    exit(0)

print('=' * 60)
print('清理 excel_pages 目录中的旧xls文件')
print('=' * 60)
print(f'目录: {INPUT_DIR}')
print(f'文件数量: {len(files)} 个')
print()

# 删除文件
deleted = 0
for fname in sorted(files):
    fpath = os.path.join(INPUT_DIR, fname)
    try:
        os.remove(fpath)
        print(f'  删除: {fname}')
        deleted += 1
    except Exception as e:
        print(f'  失败: {fname} - {e}')

print()
print(f'清理完成: 删除了 {deleted}/{len(files)} 个文件')
print('=' * 60)
