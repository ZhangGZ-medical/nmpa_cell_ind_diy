"""合并 excel_pages 目录下所有 xls (XML Spreadsheet) 文件为一个 xls 文件。
仅合并，不修改文字内容。"""
import os
import xml.etree.ElementTree as ET
from copy import deepcopy
from datetime import datetime

NS = {
    'ss': 'urn:schemas-microsoft-com:office:spreadsheet',
    'o': 'urn:schemas-microsoft-com:office:office',
    'x': 'urn:schemas-microsoft-com:office:excel',
    'html': 'http://www.w3.org/TR/REC-html40',
}

INPUT_DIR = r'D:\.openclaw\workspace\nmpa_trials\data\excel_pages'
# 使用日期后缀命名输出文件（如 clinicaltrials_merged_20260421.xls）
date_suffix = datetime.now().strftime('%Y%m%d')
OUTPUT_FILE = rf'D:\.openclaw\workspace\nmpa_trials\data\clinicaltrials_merged_{date_suffix}.xls'

# 读取所有xls文件并按文件名排序
files = sorted([f for f in os.listdir(INPUT_DIR) if f.endswith('.xls')])
print(f"找到 {len(files)} 个xls文件")

# 解析第一个文件作为模板
first_path = os.path.join(INPUT_DIR, files[0])
tree = ET.parse(first_path)
root = tree.getroot()

# 找到Worksheet和Table
ws = root.find('.//ss:Worksheet', NS)
table = ws.find('ss:Table', NS)

# 保留前两行（标题行+表头行），删除其余数据行
all_rows = table.findall('ss:Row', NS)
header_rows = all_rows[:2]  # 第1行是标题，第2行是表头
data_rows = all_rows[2:]    # 数据行需要从第一个文件保留

# 清除所有现有行
for row in list(table):
    table.remove(row)

# 重新添加标题和表头行
for row in header_rows:
    table.append(row)

# 重新添加第一个文件的数据行
for row in data_rows:
    table.append(row)

print(f"文件1: {files[0]} - {len(data_rows)} 行数据")

# 从第2个文件开始，只追加数据行（跳过标题和表头）
for fname in files[1:]:
    fpath = os.path.join(INPUT_DIR, fname)
    try:
        t = ET.parse(fpath)
        r = t.getroot()
        w = r.find('.//ss:Worksheet', NS)
        tbl = w.find('ss:Table', NS)
        rows = tbl.findall('ss:Row', NS)
        # 跳过前2行（标题+表头），只追加数据行
        for row in rows[2:]:
            table.append(deepcopy(row))
        data_count = len(rows) - 2 if len(rows) > 2 else 0
        print(f"文件 {fname}: {data_count} 行数据")
    except Exception as e:
        print(f"跳过 {fname}: {e}")

# 注册命名空间以保持输出格式
ET.register_namespace('', 'urn:schemas-microsoft-com:office:spreadsheet')
ET.register_namespace('o', 'urn:schemas-microsoft-com:office:office')
ET.register_namespace('x', 'urn:schemas-microsoft-com:office:excel')
ET.register_namespace('html', 'http://www.w3.org/TR/REC-html40')

# 写入合并后的文件
tree.write(OUTPUT_FILE, encoding='UTF-8', xml_declaration=True)

# 统计总行数
total_rows = len(table.findall('ss:Row', NS))
total_data = total_rows - 2
print(f"\n合并完成！输出: {OUTPUT_FILE}")
print(f"总行数: {total_rows} (标题1行 + 表头1行 + 数据{total_data}行)")
