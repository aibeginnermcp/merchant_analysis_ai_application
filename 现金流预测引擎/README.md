# 现金流预测引擎 (已弃用)

**注意**: 此目录已合并至 `services/cashflow_predictor`，请使用新目录。

**Note**: This directory has been merged into `services/cashflow_predictor`, please use the new directory.

---

基于ARIMA模型的智能现金流预测系统，帮助商户科学预测未来30天的资金缺口，提供精准的财务决策支持。

## 功能特点

- 基于历史应收账款数据，预测未来30天资金缺口
- 自动异常值检测与处理
- 可视化预测结果（含置信区间）
- 智能风险预警提示
- 交互式模型参数调整
- 支持PDF报告导出

## 数据要求

### 输入数据格式
历史应收账款数据需包含以下字段：
- `date`: 日期 (YYYY-MM-DD)
- `amount`: 金额 (浮点数)
- `merchant_type`: 商户类型 ('online'/'offline')

示例：
```csv
date,amount,merchant_type
2024-01-01,10000.00,online
2024-01-02,12000.00,online
```

### 输出结果
- 预测结果可视化图表
- 财务指标摘要报告
- 风险预警信息
- 可导出PDF格式报告

## 使用方法

1. 安装依赖：
```bash
pip install -r requirements.txt
```

2. 启动Jupyter Notebook：
```bash
jupyter notebook
```

3. 打开 `notebooks/cash_flow_prediction.ipynb`

4. 按照notebook中的说明执行分析

## 评估指标

- MAE (平均绝对误差)
- RMSE (均方根误差)
- 预测准确率 (95%置信区间内的命中率)

## 适用场景

- 适用于需要精确预测短期现金流的中小型商户
- 支持线上/线下不同类型商户的个性化预测
- 特别适合具有季节性波动的业务场景

## 项目结构

```
├── README.md                  # 项目说明文档
├── requirements.txt           # 项目依赖
├── data/                     # 数据目录
│   ├── raw/                 # 原始数据
│   └── processed/           # 处理后的数据
├── notebooks/               # Jupyter notebooks
│   └── cash_flow_prediction.ipynb
├── src/                     # 源代码
│   ├── data_processing.py   # 数据处理模块
│   ├── model.py            # 预测模型模块
│   └── visualization.py    # 可视化模块
└── reports/                # 生成的报告
    └── templates/          # 报告模板
``` 