# nmpa_cell_ind_diy

NMPA 药物临床试验登记平台数据采集工作流

## 功能

自动化采集 NMPA 中国药物临床试验登记与信息公示平台的细胞/生物制品临床试验数据。

## 工作流（6步骤）

```bash
# 步骤0：清理旧数据
python scripts/cleanup_excel_pages.py

# 步骤1：下载 Excel 分页列表
python scripts/download_all_pages.py

# 步骤2：合并 Excel 文件
python scripts/merge_xls.py

# 步骤3：下载详情文档
python scripts/download_all_docs.py

# 步骤4：核对完整性
python scripts/check_missing_ctr.py

# 步骤5：统计文件
python scripts/count_files.py
```

## 搜索条件

- 药物名称: `细胞`
- 药物类型: `3`（生物制品）

## 数据目录结构

```
data/
├── excel_pages/              # 分页 Excel
│   ├── clinicaltrials_page_001.xls
│   └── ...
├── all_docs/                 # 详情文档
│   ├── CTR2021XXXX.docx
│   └── ...
├── clinicaltrials_merged_YYYYMMDD.xls  # 合并后的总表
└── missing_ctr_list.txt     # 缺失 CTR 列表
```

## 文件结构

```
nmpa_cell_ind_diy/
├── SKILL.md          # 技能说明文件（完整 SOP）
└── scripts/          # 采集脚本目录
    ├── cleanup_excel_pages.py
    ├── download_all_pages.py
    ├── merge_xls.py
    ├── download_all_docs.py
    ├── check_missing_ctr.py
    └── count_files.py
```

## 注意事项

- 需要保持 Session 和 Cookie 才能正常下载
- 每页间隔 1 秒，每文档间隔 0.5 秒
- CTR 登记号作为 Excel 与 docx 文档的关联键

---
Author: ZhangGZ-medical
