# 智能商户经营分析报表数据生成器

本项目用于生成商户经营分析所需的模拟数据，包括交易数据、成本数据和现金流预测数据。

## 项目简介
本项目用于生成符合不同行业特性的商户经营数据，用于测试智能报表生成系统。目前支持以下行业类型：
- 线上大型服饰电商（如Zara官网）
- 线上小型3C店铺（如淘宝手机配件店）
- 线下中型餐饮店（如连锁火锅店）
- 线下大型游乐场（如城市主题公园）

## 功能特点
1. 支持多种商户类型的数据生成
2. 生成数据符合行业特性和业务规律
3. 提供完整的数据字典和业务规则说明
4. 自动生成数据质量报告
5. 支持自定义配置参数

## 安装说明

### 环境要求
- Python 3.8+
- pip 20.0+

### 安装步骤
1. 克隆代码库
```bash
git clone [repository_url]
cd [project_directory]
```

2. 安装依赖
```bash
pip install -r requirements.txt
```

## 使用说明

### 运行数据生成器
```bash
python main.py
```

### 输出文件说明
生成的数据文件将保存在 `output/` 目录下，包括：
- cashflow_transactions_[timestamp].csv: 交易明细数据
- cashflow_daily_cashflow_[timestamp].csv: 每日现金流汇总
- cashflow_merchant_summary_[timestamp].csv: 商户维度汇总

### 数据统计报告
数据统计报告将保存在 `reports/` 目录下，包含：
- 基础统计信息
- 数值字段分布
- 分类字段统计
- 时间序列分析
- 异常值检测结果

### 配置说明
- 基础配置文件：`config/base_config.py`
- 行业特定配置文件：`config/fashion_ecommerce_config.py`等

## 数据说明

### 数据表
1. 用户基础信息表 (user_base)
2. 交易流水表 (transaction)
3. 用户行为日志 (user_behavior)
4. NPS调研结果数据 (nps_survey)

详细的数据字段说明请参考 `DATA_README.md`

## 开发说明

### 项目结构
```
├── config/                 # 配置文件目录
│   ├── base_config.py     # 基础配置
│   └── fashion_ecommerce_config.py  # 服饰电商配置
├── src/                   # 源代码目录
│   ├── generators/        # 数据生成器
│   └── utils/            # 工具函数
├── output/               # 输出数据目录
├── reports/              # 统计报告目录
├── tests/               # 测试代码目录
├── main.py              # 主程序入口
├── requirements.txt     # 项目依赖
└── README.md            # 项目说明
```

### 添加新的行业类型
1. 在 `config/` 目录下创建新的行业配置文件
2. 在 `src/generators/` 目录下创建对应的数据生成器
3. 在 `main.py` 中添加新行业的数据生成逻辑

## 数据质量标准
- 时间范围：最近24个月
- 数据量：每家商户5000-10000个用户样本
- 缺失值比例：3-5%
- 异常数据比例：5-10%

## 注意事项
1. 生成数据前请确保配置参数符合实际业务场景
2. 大数据量生成可能需要较长时间，请耐心等待
3. 建议定期备份生成的数据文件

## 贡献指南
1. Fork 项目
2. 创建功能分支
3. 提交变更
4. 发起 Pull Request

## 许可证
MIT License 

## 数据结构

### 1. 现金流预测数据
现金流预测数据包含以下三个主要数据集：

#### 1.1 交易数据 (transactions)
- date: 交易日期
- merchant_id: 商户ID
- merchant_type: 商户类型（餐饮/零售/服务）
- merchant_size: 商户规模（小型/中型/大型）
- transaction_amount: 交易金额
- settlement_cycle: 结算周期（天）
- expected_collection_date: 预期收款日期
- actual_collection_date: 实际收款日期
- delay_days: 延迟天数
- is_bad_debt: 是否坏账
- bad_debt_rate: 坏账率
- collected_amount: 实际收款金额

#### 1.2 每日现金流汇总 (daily_cashflow)
- date: 日期
- transaction_amount: 当日交易总额
- collected_amount: 当日实际收款总额
- cashflow_gap: 现金流缺口（交易总额 - 实际收款总额）

#### 1.3 商户维度汇总 (merchant_summary)
- merchant_id: 商户ID
- transaction_amount: 交易总额
- collected_amount: 实际收款总额
- delay_days: 平均延迟天数
- is_bad_debt: 坏账笔数
- collection_rate: 回款率

### 2. 行业特定数据
// ... existing code ...

## 数据生成说明

### 现金流预测数据生成逻辑
1. 基于商户规模设置不同的基础交易金额范围
2. 考虑季节性因素（节假日、淡旺季等）
3. 模拟延迟支付和坏账情况
4. 生成预期收款日期和实际收款日期
5. 计算每日和商户维度的现金流汇总数据

### 数据特点
1. 考虑了商户规模对交易金额的影响
2. 包含季节性波动因素
3. 模拟了真实的结算周期和延迟支付情况
4. 提供了坏账风险评估数据
5. 支持现金流预测和风险预警分析

## 注意事项
1. 生成的数据仅用于测试和演示目的
2. 数据中的金额和比率均为模拟值
3. 可根据实际需求调整参数配置

// ... existing code ... 