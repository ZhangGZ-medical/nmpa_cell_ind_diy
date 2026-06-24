#!/usr/bin/env python3
"""
NMPA CDE数据采集 - 浏览器自动化版
适用场景：CDE网站反爬虫（F5 JS挑战）导致纯requests失效时使用
依赖：agent-browser (npm install -g agent-browser && agent-browser install)
"""

import subprocess, time, csv, os
from pathlib import Path

WORKSPACE = Path(r"D:\.openclaw\workspace\nmpa_trials")
OUTPUT_DIR = WORKSPACE / "data" / "excel_pages"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# 搜索参数
DRUG_NAME = "细胞"
DRUG_TYPE = "3"  # 生物制品
TOTAL_PAGES = 32  # 需要手动确认总页数

def run_browser_command(*args):
    """运行agent-browser命令并返回输出"""
    cmd = ["agent-browser"] + list(args)
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
    return result.stdout.strip(), result.stderr.strip()

def init_browser():
    """初始化浏览器并导航到CDE网站"""
    print("启动浏览器...")
    # 启动浏览器（后续所有操作共享session）
    run_browser_command("--args", "--disable-blink-features=AutomationControlled",
                         "--user-agent", "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36",
                         "open", "https://www.chinadrugtrials.org.cn/")
    run_browser_command("wait", "3000")
    print("  已打开CDE主页")

    # 导航到搜索页面
    run_browser_command("eval", "location.href='/clinicaltrials.searchlist.dhtml'")
    run_browser_command("wait", "--load", "networkidle")

    # 展开高级搜索
    run_browser_command("eval", "document.querySelector('.subSearchBtn') ? document.querySelector('.subSearchBtn[onclick*=\"secondLevel\"]').click() : null")
    run_browser_command("wait", "1000")

    # 设置搜索参数并通过searchList提交
    js = f"""
var f = document.getElementById('searchfrm');
f.elements['drugs_name'].value = '{DRUG_NAME}';
f.elements['drugs_type'].value = '{DRUG_TYPE}';
f.elements['secondLevel'].value = '1';
searchList();
"""
    run_browser_command("eval", js)
    run_browser_command("wait", "--load", "networkidle")
    print("  搜索条件已设置并提交")

def scrape_page(page_num):
    """爬取单页数据"""
    # 导航到该页
    js_nav = f"var f=document.getElementById('searchfrm'); f.elements['currentpage'].value='{page_num}'; f.action='/clinicaltrials.searchlist.dhtml'; f.submit()"
    run_browser_command("eval", js_nav)
    run_browser_command("wait", "--load", "networkidle")
    time.sleep(1.5)

    # 提取数据（JSON格式避免转义问题）
    js_extract = """
var rows = document.querySelectorAll('table tbody tr');
var data = [];
rows.forEach(function(tr) {
  var cells = tr.querySelectorAll('td');
  if (cells.length === 6) {
    var row = [];
    cells.forEach(function(td) { row.push(td.textContent.trim()); });
    data.push(row);
  }
});
JSON.stringify(data);
"""
    out, err = run_browser_command("eval", js_extract)
    
    # 去掉eval返回的JSON字符串外层引号
    if out.startswith('"') and out.endswith('"'):
        out = out[1:-1]
        # 还原转义
        out = out.replace('\\"', '"')
    
    import json
    try:
        rows = json.loads(out)
    except json.JSONDecodeError:
        print(f"  JSON解析失败: {out[:100]}...")
        return []
    
    return rows


def main():
    all_rows = []
    csv_path = OUTPUT_DIR / f"clinicaltrials_scraped_{time.strftime('%Y%m%d')}.csv"
    
    print(f"开始爬取 {TOTAL_PAGES} 页...")
    print(f"搜索: {DRUG_NAME} / 药物类型: {DRUG_TYPE}")
    print()
    
    init_browser()
    
    for page in range(1, TOTAL_PAGES + 1):
        try:
            rows = scrape_page(page)
            all_rows.extend(rows)
            print(f"  [{page:2d}/{TOTAL_PAGES}] {len(rows)} rows - total: {len(all_rows)}")
        except Exception as e:
            print(f"  [{page:2d}/{TOTAL_PAGES}] ERROR: {e}")
            break
    
    # 保存CSV
    with open(csv_path, 'w', newline='', encoding='utf-8-sig') as f:
        w = csv.writer(f)
        w.writerow(['序号', '登记号', '试验状态', '药物名称', '适应症', '试验通俗题目'])
        w.writerows(all_rows)
    
    print(f"\n完成! {len(all_rows)} 行数据保存到 {csv_path}")
    
    # 关闭浏览器
    run_browser_command("close", "--all")


if __name__ == "__main__":
    main()
