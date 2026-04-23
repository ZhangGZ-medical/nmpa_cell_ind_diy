#!/usr/bin/env python3
"""
下载所有页面的Excel文件
动态获取总页数，支持断点续传
"""
import requests
import os
import time
import re

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8,application/vnd.ms-excel,application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
    'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
    'Referer': 'https://www.chinadrugtrials.org.cn/',
}

session = requests.Session()

# 先访问主页获取cookie
session.get('https://www.chinadrugtrials.org.cn/', headers=headers, timeout=30)

output_dir = './data/excel_pages'
os.makedirs(output_dir, exist_ok=True)

print('=' * 60)
print('中国药物临床试验登记与信息公示平台 - 批量下载Excel')
print('=' * 60)
print()
print('【搜索条件】')
print('  药物名称: 细胞')
print('  药物类型: 生物制品')
print()

# 先获取第1页，从中提取总页数
search_data_first = {
    'drugs_name': '细胞',
    'drugs_type': '3',
    'currentpage': '1',
}
search_url = 'https://www.chinadrugtrials.org.cn/clinicaltrials.searchlist.dhtml'
resp_first = session.post(search_url, data=search_data_first, headers=headers, timeout=30)
html_content = resp_first.text

pagination_match = re.search(r'共\s*<i>(\d+)</i>\s*页.*共\s*<i>([\d,]+)</i>\s*条', html_content)
if pagination_match:
    total_pages = int(pagination_match.group(1))
    total_records = pagination_match.group(2).replace(',', '')
    print('  总页数: %d页 (动态获取)' % total_pages)
    print('  总记录数: %s条' % total_records)
else:
    total_pages = 31
    print('  总页数: %d页 (使用默认值)' % total_pages)
print()
downloaded = 0
skipped = 0
failed = []

for page_num in range(1, total_pages + 1):
    filename = 'clinicaltrials_page_%03d.xls' % page_num
    filepath = os.path.join(output_dir, filename)
    
    # 检查文件是否已存在且有效（大于1KB）
    if os.path.exists(filepath):
        file_size = os.path.getsize(filepath)
        if file_size > 1000:
            print('第 %d/%d 页... [SKIP] 已存在 (%d bytes)' % (page_num, total_pages, file_size))
            skipped += 1
            continue
    
    print('正在下载第 %d/%d 页...' % (page_num, total_pages), end=' ')
    
    # POST方式提交搜索表单（带_export=xls参数和currentpage参数）
    search_data = {
        'drugs_name': '细胞',
        'drugs_type': '3',  # 生物制品
        'currentpage': str(page_num),
    }
    
    # Excel下载接口
    excel_url = 'https://www.chinadrugtrials.org.cn/clinicaltrials.searchlist.dhtml?_export=xls'
    
    try:
        # 下载Excel文件
        resp = session.post(excel_url, data=search_data, headers=headers, timeout=60)
        
        # 检查是否为Excel文件
        content_type = resp.headers.get('Content-Type', '')
        is_excel = ('excel' in content_type.lower() or 
                    'spreadsheet' in content_type.lower() or 
                    resp.content[:4] == b'\xd0\xcf\x11\xe0' or  # xls格式
                    resp.content[:4] == b'PK\x03\x04')  # xlsx格式
        
        if is_excel and len(resp.content) > 1000:  # 确保文件有内容
            with open(filepath, 'wb') as f:
                f.write(resp.content)
            
            print('[OK] %d bytes' % len(resp.content))
            downloaded += 1
        else:
            print('[FAIL] 无效文件')
            failed.append(page_num)
            
    except Exception as e:
        print('[ERROR] %s' % str(e)[:50])
        failed.append(page_num)
    
    # 添加延迟避免请求过快
    if page_num < total_pages:
        time.sleep(1)

print()
print('=' * 60)
print('【下载完成】')
print('  总页数: %d 页' % total_pages)
print('  新下载: %d 页' % downloaded)
print('  已存在跳过: %d 页' % skipped)
print('  失败: %d 页' % len(failed))
if failed:
    print('  失败页码: %s' % str(failed))
print('  保存目录: %s' % output_dir)
print('=' * 60)
