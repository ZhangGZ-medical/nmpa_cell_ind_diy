# nmpa_cell_ind_diy

NMPA药物临床试验登记平台数据采集工作流（细胞/生物制品关键词）。

## 功能

完整的NMPA中国药物临床试验登记与信息公示平台数据采集流水线，自动搜索、下载、合并、核对细胞疗法临床试验数据。

## 触发词

NMPA临床试验、药物临床试验登记、细胞疗法试验下载、CDE登记数据、chinadrugtrials、CTR文档下载

## 工作流（6步骤）

| 步骤 | 脚本 | 功能 |
|---|---|---|
| 0 | `cleanup_excel_pages.py` | 清理旧数据 |
| 1 | `download_all_pages.py` | 下载Excel分页列表（断点续传） |
| 2 | `merge_xls.py` | 合并所有分页 |
| 3 | `download_all_docs.py` | 按CTR登记号下载详情docx |
| 4 | `check_missing_ctr.py` | 核对完整性，输出缺失列表 |
| 5 | `count_files.py` | 统计已下载文档数 |

## ⚠️ 2026-05更新

CDE网站已部署F5反爬虫系统，纯Python requests方式已失效。需使用agent-browser（Playwright内核）DOM爬取替代。

## 文件结构

```
nmpa_cell_ind_diy/
├── SKILL.md          # 技能定义与SOP
├── scripts/          # Python采集脚本集
└── README.md         # 本说明文件
```
