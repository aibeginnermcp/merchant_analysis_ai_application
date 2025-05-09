# 智能商户经营分析报表数据生成器

## 项目概述
本项目用于生成符合不同行业特性的商户经营数据，用于测试智能报表生成系统。支持多种商户类型，包括线上电商、线下零售等业态，并提供详细的成本穿透分析数据。

## 支持的商户类型
1. 线上大型服饰电商（如Zara官网）
2. 线上小型3C店铺（如淘宝手机配件店）
3. 线下中型餐饮店（如连锁火锅店）
4. 线下大型游乐场（如城市主题公园）

## 数据表结构

### 1. 用户基础信息表 (user_base)
| 字段名 | 类型 | 描述 | 示例值 |
|-------|------|------|--------|
| user_id | string | 用户唯一标识 | 'u_1001' |
| register_time | datetime | 注册时间 | '2022-01-01 12:00:00' |
| user_type | string | 用户类型 | 'normal/vip' |
| age_group | string | 年龄段 | '25-35' |
| gender | string | 性别 | 'F/M' |
| city_tier | string | 城市等级 | 'T1/T2/T3' |

### 2. 交易流水表 (transaction)
| 字段名 | 类型 | 描述 | 示例值 |
|-------|------|------|--------|
| transaction_id | string | 交易ID | 't_10001' |
| user_id | string | 用户ID | 'u_1001' |
| transaction_time | datetime | 交易时间 | '2022-01-01 12:30:00' |
| amount | float | 交易金额 | 299.00 |
| payment_method | string | 支付方式 | 'alipay/wechat/card' |
| product_id | string | 商品ID | 'p_2001' |
| quantity | int | 数量 | 1 |
| is_refunded | boolean | 是否退款 | false |

### 3. 用户行为日志表 (user_behavior)
| 字段名 | 类型 | 描述 | 示例值 |
|-------|------|------|--------|
| log_id | string | 日志ID | 'l_10001' |
| user_id | string | 用户ID | 'u_1001' |
| behavior_time | datetime | 行为时间 | '2022-01-01 12:15:00' |
| behavior_type | string | 行为类型 | 'view/cart/purchase' |
| page_id | string | 页面/区域ID | 'page_001' |
| stay_time | int | 停留时间(秒) | 120 |
| device_type | string | 设备类型 | 'mobile/pc' |

### 4. NPS调研表 (nps_survey)
| 字段名 | 类型 | 描述 | 示例值 |
|-------|------|------|--------|
| survey_id | string | 调研ID | 's_1001' |
| user_id | string | 用户ID | 'u_1001' |
| survey_time | datetime | 调研时间 | '2022-01-01 14:00:00' |
| nps_score | int | NPS评分 | 9 |
| feedback_text | string | 反馈文本 | '服务很好' |
| survey_channel | string | 调研渠道 | 'sms/email/app' |

### 5. 成本数据表 (cost_data)
| 字段名 | 类型 | 描述 | 示例值 |
|-------|------|------|--------|
| SKU_ID | string | SKU唯一标识 | 'SKU00001' |
| category | string | 品类分类 | '3C/服饰/食品/家居' |
| weight | float | 重量(kg) | 0.5 |
| volume | float | 体积(m³) | 0.01 |
| transport_distance | float | 运输距离(km) | 500 |
| logistics_cost | float | 物流成本 | 25.0 |
| production_cost | float | 生产成本 | 30.0 |
| labor_cost | float | 人工成本 | 10.0 |
| complexity | string | 设计复杂度 | 'basic/custom' |
| material_type | string | 材料类型 | 'wood/board' |
| shelf_life | int | 保质期(天) | 30 |
| bom_components | string | BOM组件 | '电芯,外壳,电路板' |

## 行业特性参数

### 服饰电商
- 退货率：15-25%
- 季节性波动系数：春季1.2，夏季0.8，秋季1.5，冬季1.3
- 促销期流量提升：2-3倍
- 客单价范围：￥200-1500
- 物流成本：按体积计算，80元/m³/月
- 人工成本：基础款1元/件，定制款5元/件

### 3C店铺
- 复购率：10-15%
- 配件连带率：35-45%
- 客单价范围：￥50-3000
- 促销期转化率提升：50-80%
- 物流成本：5元/kg
- 生产成本：基于BOM清单

### 餐饮店
- 午市占比：30-40%
- 晚市占比：50-60%
- 翻台率：午市2-3次，晚市1.5-2次
- 客单价范围：￥80-200/人
- 损耗成本：按保质期计算
- 冷链成本：0.03元/kg/km

### 游乐场
- 周末客流：工作日的2-3倍
- 节假日客流：工作日的3-4倍
- 二次消费率：15-25%
- 客单价范围：￥150-400/人

## 成本计算规则

### 3C类
- 物流成本 = 重量 × 5元/kg
- 生产成本：基于BOM清单（电芯10元，外壳5元，电路板15元）
- 人工成本：8-15元/件

### 服饰类
- 仓储成本 = 体积 × 80元/m³/月
- 人工成本：基础款1元/件，定制款5元/件

### 食品类
- 损耗成本：
  - 保质期<7天：10%
  - 保质期7-30天：5%
  - 保质期>30天：2%
- 冷链运输：3元/kg/100km

### 家居类
- 运输成本 = 体积 × 120元/m³
- 材料成本：实木15元/件，板材8元/件

## 数据质量标准
- 时间范围：最近24个月
- 用户量：5000-10000/商户
- 缺失值比例：3-5%
- 异常数据比例：5-10%
- 成本异常比例：5%（成本超过平均值3倍以上）

## 使用说明
1. 配置文件位于 `config/` 目录
2. 运行 `python main.py` 生成数据
3. 生成的数据位于 `output/` 目录
4. 数据验证报告位于 `reports/` 目录 