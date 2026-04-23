#!/usr/bin/env python3
import os

output_dir = r'd:\.openclaw\workspace\nmpa_trials\data\all_docs'
files = [f for f in os.listdir(output_dir) if f.endswith('.docx')]
print(f'总文件数: {len(files)}')

# 显示前20个文件名
print('\n前20个文件:')
for f in sorted(files)[:20]:
    print(f'  {f}')
