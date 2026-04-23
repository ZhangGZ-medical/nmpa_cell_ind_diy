---
name: nmpa_cell_ind_diy
description: |
  NMPA药物临床试验登记平台数据采集工作流（细胞/生物制品关键词）
  触发词：NMPA临床试验、药物临床试验登记、细胞疗法试验下载、CDE登记数据、
  chinadrugtrials、clinicaltrials登记号下载、CTR文档下载
---

# NMPA 细胞/生物制品临床试验数据采集

本skill封装完整的NMPA中国药物临床试验登记与信息公示平台数据采集工作流。

## 搜索条件
- 药物名称: `细胞`
- 药物类型: `3`（生物制品）

## 工作流（6步骤）

### 步骤0：清理旧数据
```bash
python scripts/cleanup_excel_pages.py
```
删除 `data/excel_pages/` 中所有旧xls文件，确保下载最新数据。

### 步骤1：下载Excel分页列表
```bash
python scripts/download_all_pages.py
```
- 动态获取总页数（自动适应官网更新）
- 断点续传：已存在且>1KB的文件自动跳过
- 输出到 `data/excel_pages/` 目录

### 步骤2：合并Excel文件
```bash
python scripts/merge_xls.py
```
- 合并所有xls分页文件为一个
- 输出文件名带日期后缀：`clinicaltrials_merged_YYYYMMDD.xls`

### 步骤3：下载详情文档
```bash
python scripts/download_all_docs.py
```
- 根据Excel中的CTR登记号下载所有详情docx文档
- 全局CTR去重，防止跨页重复
- 输出到 `data/all_docs/` 目录

### 步骤4：核对完整性
```bash
python scripts/check_missing_ctr.py
```
- 自动查找最新的merged Excel
- 对比Excel中的CTR与已下载的docx
- 输出缺失列表到 `data/missing_ctr_list.txt`

### 步骤5：统计文件
```bash
python scripts/count_files.py
```
统计已下载的docx文档数量。

## 快速执行
```bash
cd {workspace}
python scripts/cleanup_excel_pages.py
python scripts/download_all_pages.py
python scripts/merge_xls.py
python scripts/download_all_docs.py
python scripts/check_missing_ctr.py
python scripts/count_files.py
```

## 数据目录结构
```
data/
├── excel_pages/              # 分页Excel
│   ├── clinicaltrials_page_001.xls
│   ├── clinicaltrials_page_002.xls
│   └── ...
├── all_docs/                 # 详情文档
│   ├── CTR2021XXXX.docx
│   └── ...
├── clinicaltrials_merged_YYYYMMDD.xls  # 合并后的总表
└── missing_ctr_list.txt     # 缺失CTR列表
```

## 注意事项
- 需要保持Session和Cookie才能正常下载
- 每页间隔1秒，每文档间隔0.5秒，避免请求过快
- CTR登记号作为Excel与docx文档的关联键
