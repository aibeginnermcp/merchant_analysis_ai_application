# 餐饮行业数据字典

## 概述
本文档详细说明了餐饮行业模拟数据生成器产生的各个数据表的结构和字段含义。所有数据都经过业务验证，确保符合真实餐饮行业的特征。

## 数据表清单

### 1. 顾客基础信息表 (customer_base)
记录所有顾客的基本信息和属性。

| 字段名 | 类型 | 描述 | 示例值 |
|--------|------|------|---------|
| customer_id | string | 顾客唯一标识 | c_a1b2c3d4 |
| first_visit | datetime | 首次光顾时间 | 2023-01-15 12:30:00 |
| customer_type | string | 顾客类型 | member/regular |
| age_group | string | 年龄段 | 25-34 |
| gender | string | 性别 | male/female |
| city_tier | string | 城市等级 | 一线城市 |
| spicy_preference | boolean | 是否喜欢辣 | true/false |
| is_vegetarian | boolean | 是否素食 | true/false |
| seafood_preference | boolean | 是否喜欢海鲜 | true/false |
| alcohol_preference | boolean | 是否饮酒 | true/false |
| lifetime_value | float | 顾客终身价值 | 2580.50 |

### 2. 堂食订单表 (dine_in_orders)
记录餐厅内就餐的订单信息。

| 字段名 | 类型 | 描述 | 示例值 |
|--------|------|------|---------|
| order_id | string | 订单唯一标识 | o_b1c2d3e4 |
| customer_id | string | 顾客ID | c_a1b2c3d4 |
| restaurant_type | string | 餐厅类型 | casual_dining |
| price_level | string | 价格等级 | medium |
| order_time | datetime | 下单时间 | 2023-01-15 12:30:00 |
| party_size | int | 就餐人数 | 4 |
| dining_duration | int | 用餐时长(分钟) | 90 |
| total_amount | float | 订单总金额 | 368.50 |
| payment_method | string | 支付方式 | mobile_pay |
| is_member | boolean | 是否会员 | true/false |

### 3. 外卖订单表 (delivery_orders)
记录外卖订单的详细信息。

| 字段名 | 类型 | 描述 | 示例值 |
|--------|------|------|---------|
| order_id | string | 订单唯一标识 | d_c1d2e3f4 |
| customer_id | string | 顾客ID | c_a1b2c3d4 |
| restaurant_type | string | 餐厅类型 | fast_food |
| price_level | string | 价格等级 | low |
| order_time | datetime | 下单时间 | 2023-01-15 18:30:00 |
| items_count | int | 商品数量 | 2 |
| total_amount | float | 订单总金额 | 68.50 |
| delivery_fee | float | 配送费 | 8.00 |
| platform | string | 配送平台 | meituan |
| commission | float | 平台佣金 | 12.33 |
| payment_method | string | 支付方式 | alipay |
| delivery_time | int | 配送时长(分钟) | 35 |
| delivery_distance | float | 配送距离(公里) | 2.5 |
| is_member | boolean | 是否会员 | true/false |

### 4. 服务质量表 (service_quality)
记录订单的服务质量评价和投诉信息。

| 字段名 | 类型 | 描述 | 示例值 |
|--------|------|------|---------|
| order_id | string | 订单ID | o_b1c2d3e4 |
| customer_id | string | 顾客ID | c_a1b2c3d4 |
| rating_time | datetime | 评价时间 | 2023-01-15 14:30:00 |
| overall_score | int | 总体评分 | 4 |
| food_taste_score | int | 口味评分 | 5 |
| service_attitude_score | int | 服务态度评分 | 4 |
| environment_score | int | 环境评分 | 4 |
| price_performance_score | int | 性价比评分 | 3 |
| has_complaint | boolean | 是否有投诉 | true/false |
| complaint_type | string | 投诉类型 | food_quality |
| resolution_time | int | 解决时长(分钟) | 30 |
| complaint_status | string | 投诉状态 | resolved |

## 数据质量控制

所有生成的数据都经过以下质量控制：

1. **完整性检查**
   - 必填字段不允许为空
   - 外键关系完整性保证
   - ID字段唯一性验证

2. **合理性检查**
   - 时间范围验证
   - 数值范围验证
   - 枚举值验证

3. **业务规则验证**
   - 订单金额与就餐人数匹配
   - 配送时间与距离关联
   - 会员折扣正确应用

4. **异常值处理**
   - 添加合理的异常值（约5-10%）
   - 保持异常分布的真实性
   - 记录异常产生的原因

## 数据使用建议

1. **数据分析方向**
   - 客流量分析
   - 营收分析
   - 会员价值分析
   - 服务质量分析
   - 外卖业务分析

2. **注意事项**
   - 注意处理异常值
   - 考虑节假日因素
   - 关注时间序列特征
   - 注意数据关联关系 