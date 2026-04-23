#!/usr/bin/env python3
"""
核对已下载的docx文件与Excel中的CTR号码
查找哪些CTR号码没有下载docx文档
"""
import os
import glob
from datetime import datetime

# 路径设置
docs_dir = r'D:\.openclaw\workspace\nmpa_trials\data\all_docs'
data_dir = r'D:\.openclaw\workspace\nmpa_trials\data'

# 自动找到最新的 merged 文件
merged_files = glob.glob(os.path.join(data_dir, 'clinicaltrials_merged_*.xls'))
if merged_files:
    # 按文件名排序，取最新的（日期最大的）
    excel_path = max(merged_files)
else:
    excel_path = os.path.join(data_dir, 'clinicaltrials_merged.xls')

print('=' * 70)
print('CTR号码核对报告')
print('=' * 70)
print(f'Excel文件: {excel_path}')

# 1. 读取Excel中的所有CTR号码
print('\n【1】读取Excel数据...')

# 文件是XML格式，使用pandas读取
import pandas as pd
import re

# 尝试读取XML格式的Excel文件
try:
    df = pd.read_html(excel_path)[0]
    
    print(f'Excel总行数: {len(df)}')
    print(f'列名: {list(df.columns)}')
    
    # 查找登记号列
    reg_col = None
    for col in df.columns:
        if '登记号' in str(col) or 'CTR' in str(col).upper():
            reg_col = col
            break
    
    if reg_col is None:
        print('错误：找不到登记号列')
        exit(1)
    
    print(f'登记号列名: {reg_col}')
    
    # 提取CTR号码
    excel_ctrs = set()
    for val in df[reg_col].dropna():
        ctr = str(val).strip().upper()
        if ctr.startswith('CTR'):
            excel_ctrs.add(ctr)
    
    print(f'Excel中CTR号码数量: {len(excel_ctrs)}')
    
except Exception as e:
    print(f'错误：{e}')
    # 备用方案：直接读取文本提取CTR
    print('\n尝试备用方案：直接读取文件提取CTR...')
    with open(excel_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    excel_ctrs = set(re.findall(r'CTR\d+', content.upper()))
    print(f'从文本中提取的CTR号码数量: {len(excel_ctrs)}')



# 2. 获取已下载的docx文件中的CTR号码
print('\n【2】读取已下载的docx文件...')
downloaded_ctrs = set()
for filename in os.listdir(docs_dir):
    if filename.endswith('.docx'):
        ctr = filename.replace('.docx', '').strip().upper()
        if ctr.startswith('CTR'):
            downloaded_ctrs.add(ctr)

print(f'已下载的CTR号码数量: {len(downloaded_ctrs)}')

# 3. 核对差异
print('\n【3】核对结果...')

# Excel中有但还没下载的
missing_in_downloads = excel_ctrs - downloaded_ctrs
# 已下载但Excel中没有的（可能多余下载的）
extra_downloads = downloaded_ctrs - excel_ctrs

print(f'\nExcel中有但尚未下载的CTR号码: {len(missing_in_downloads)} 个')
if missing_in_downloads:
    print('缺失列表:')
    for ctr in sorted(missing_in_downloads):
        print(f'  {ctr}')

print(f'\n已下载但Excel中没有的CTR号码: {len(extra_downloads)} 个')
if extra_downloads:
    print('多余列表:')
    for ctr in sorted(extra_downloads):
        print(f'  {ctr}')

print(f'\n成功匹配的CTR号码: {len(excel_ctrs & downloaded_ctrs)} 个')

# 4. 保存缺失列表到文件
if missing_in_downloads:
    missing_file = r'D:\.openclaw\workspace\nmpa_trials\data\missing_ctr_list.txt'
    with open(missing_file, 'w', encoding='utf-8') as f:
        f.write('缺失的CTR号码列表（Excel中有但未下载）\n')
        f.write('=' * 50 + '\n')
        for ctr in sorted(missing_in_downloads):
            f.write(f'{ctr}\n')
    print(f'\n缺失列表已保存到: {missing_file}')

print('\n' + '=' * 70)
