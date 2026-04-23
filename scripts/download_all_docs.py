#!/usr/bin/env python3
"""
下载所有页面所有试验的详情文档
自动获取总页数，支持动态扩展，全局CTR去重
"""
import requests
import os
import time
import re

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8,application/msword',
    'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
    'Referer': 'https://www.chinadrugtrials.org.cn/',
}

session = requests.Session()

# 先访问主页获取cookie
session.get('https://www.chinadrugtrials.org.cn/', headers=headers, timeout=30)

output_dir = './data/all_docs'
os.makedirs(output_dir, exist_ok=True)

print('=' * 70)
print('中国药物临床试验登记与信息公示平台 - 批量下载所有详情文档')
print('=' * 70)
print()
print('【搜索条件】')
print('  药物名称: 细胞')
print('  药物类型: 生物制品')
print()

# 先获取第1页，从中提取总页数
search_data = {
    'drugs_name': '细胞',
    'drugs_type': '3',
    'currentpage': '1',
}
search_url = 'https://www.chinadrugtrials.org.cn/clinicaltrials.searchlist.dhtml'
resp = session.post(search_url, data=search_data, headers=headers, timeout=30)
html_content = resp.text

# 提取总页数和总记录数
pagination_match = re.search(r'共\s*<i>(\d+)</i>\s*页.*共\s*<i>([\d,]+)</i>\s*条', html_content)
if pagination_match:
    total_pages = int(pagination_match.group(1))
    total_records = pagination_match.group(2).replace(',', '')
    print(f'  总页数: {total_pages} 页')
    print(f'  总记录数: {total_records} 条')
else:
    # 备用方案
    page_match = re.search(r'共\s*(\d+)\s*页', html_content)
    if page_match:
        total_pages = int(page_match.group(1))
        print(f'  总页数: {total_pages} 页 (备用提取方式)')
    else:
        print('  [警告] 无法提取总页数，使用默认值31页')
        total_pages = 31

print()
total_downloaded = 0
failed_downloads = []
processed_ctr = set()  # 用于去重，防止同一试验被重复处理

for page_num in range(1, total_pages + 1):
    print('-' * 70)
    print('正在处理第 %d/%d 页...' % (page_num, total_pages))
    print('-' * 70)
    
    # 获取当前页内容（第1页已获取，复用）
    if page_num == 1:
        # 第1页内容已在前面获取，直接使用
        page_html = html_content
    else:
        search_data = {
            'drugs_name': '细胞',
            'drugs_type': '3',
            'currentpage': str(page_num),
        }
        resp = session.post(search_url, data=search_data, headers=headers, timeout=30)
        page_html = resp.text
    
    # 提取所有试验的详情ID和登记号
    lines = page_html.split('\n')
    matches = []
    
    for i, line in enumerate(lines):
        if 'getDetail(this.id)' in line:
            id_match = re.search(r'id="([^"]+)"', line)
            name_match = re.search(r'name="(\d+)"', line)
            
            if id_match and name_match:
                detail_id = id_match.group(1)
                seq_num = name_match.group(1)
                
                # 在接下来的几行中查找CTR登记号
                for j in range(i, min(i + 10, len(lines))):
                    ctr_match = re.search(r'(CTR[a-zA-Z0-9]+)', lines[j])
                    if ctr_match:
                        reg_no = ctr_match.group(1)
                        matches.append((detail_id, seq_num, reg_no))
                        break
    
    # 去重（同一试验可能有多行getDetail）
    seen = set()
    unique_matches = []
    for detail_id, seq_num, reg_no in matches:
        key = (detail_id, seq_num)
        if key not in seen and reg_no not in processed_ctr:
            seen.add(key)
            unique_matches.append((detail_id, seq_num, reg_no))
            processed_ctr.add(reg_no)
    matches = unique_matches
    
    if not matches:
        print('  未找到试验数据')
        continue
    
    print('  找到 %d 个试验' % len(matches))
    
    page_downloaded = 0
    page_skipped = 0
    for detail_id, seq_num, reg_no in matches:
        # 全局序号 = (页码-1) * 20 + 页内序号
        global_seq = (page_num - 1) * 20 + int(seq_num)
        
        # 检查文件是否已存在
        filename = '%s.docx' % reg_no.strip()
        filepath = os.path.join(output_dir, filename)
        
        if os.path.exists(filepath):
            print('  [%04d] %s - SKIP (已存在)' % (global_seq, reg_no.strip()))
            page_skipped += 1
            continue
        
        # 下载文档
        doc_url = 'https://www.chinadrugtrials.org.cn/clinicaltrials.searchlistdetail.dhtml?_export=doc'
        doc_data = {'id': detail_id}
        
        try:
            doc_resp = session.post(doc_url, data=doc_data, headers=headers, timeout=60)
            
            # 检查是否为Word文档
            content_type = doc_resp.headers.get('Content-Type', '')
            is_word = ('word' in content_type.lower() or 
                      'msword' in content_type.lower() or
                      len(doc_resp.content) > 50000)  # 文档通常大于50KB
            
            if is_word and len(doc_resp.content) > 10000:
                with open(filepath, 'wb') as f:
                    f.write(doc_resp.content)
                
                print('  [%04d] %s - OK (%d bytes)' % (global_seq, reg_no.strip(), len(doc_resp.content)))
                page_downloaded += 1
                total_downloaded += 1
            else:
                print('  [%04d] %s - FAIL (无效文件)' % (global_seq, reg_no.strip()))
                failed_downloads.append((page_num, global_seq, reg_no.strip()))
                
        except Exception as e:
            print('  [%04d] %s - ERROR: %s' % (global_seq, reg_no.strip(), str(e)[:50]))
            failed_downloads.append((page_num, global_seq, reg_no.strip()))
        
        # 添加延迟避免请求过快
        time.sleep(0.5)
    
    print('  第%d页完成: 下载%d个, 跳过%d个, 共%d个' % (page_num, page_downloaded, page_skipped, len(matches)))
    
    # 页面间延迟
    if page_num < total_pages:
        time.sleep(2)

print()
print('=' * 70)
print('【下载完成】')
print('  总页数: %d 页' % total_pages)
print('  总试验数: %d 个' % len(processed_ctr))
print('  成功下载: %d 个文档' % total_downloaded)
print('  失败: %d 个' % len(failed_downloads))
if failed_downloads:
    print('  失败列表:')
    for page, seq, reg_no in failed_downloads[:10]:  # 只显示前10个
        print('    - 第%d页 [%04d] %s' % (page, seq, reg_no))
print('  保存目录: %s' % output_dir)
print('=' * 70)
