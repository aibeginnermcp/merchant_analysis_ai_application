# 成本穿透分析引擎 (已弃用)

**注意**: 此目录已合并至 `services/cost_analyzer`，请使用新目录。

**Note**: This directory has been merged into `services/cost_analyzer`, please use the new directory.

---

## 项目简介
本项目是一个支持多品类成本穿透分析的智能引擎，可以根据不同品类的特性自动分配和分解各类成本，生成详细的成本分析报告和可视化图表。

## 功能特点
- 支持多品类成本分配规则配置
- 自动生成成本明细表和可视化报告
- 提供异常成本预警机制
- 支持交互式规则配置

## 数据格式要求
### 输入数据格式
必需字段：
- SKU_ID: 商品唯一标识
- category: 品类分类 (3C/服饰/食品/家居)
- weight: 重量(kg)
- volume: 体积(m³)
- logistics_cost: 物流成本
- production_cost: 生产成本
- labor_cost: 人工成本
- shelf_life: 保质期(天)
- transport_distance: 运输距离(km)
- complexity: 设计复杂度
- material_type: 材料类型

### 品类规则配置
1. 3C类：
   - 物流成本 = 重量 × 5元/kg
   - 生产成本按BOM清单分配

2. 服饰类：
   - 仓储成本 = 体积 × 80元/m³/月
   - 人工成本：基础款1元/件，定制款5元/件

3. 食品类：
   - 损耗成本：
     - 保质期<7天：10%
     - 保质期7-30天：5%
     - 保质期>30天：2%
   - 冷链运输：3元/kg/100km

4. 家居类：
   - 运输成本 = 体积 × 120元/m³
   - 材料成本：实木15元/件，板材8元/件

## 项目结构
```
├── README.md                 # 项目说明文档
├── notebooks/               # Jupyter notebooks
│   ├── cost_analysis.ipynb  # 成本分析主程序
│   └── data_generator.ipynb # 模拟数据生成器
├── src/                    # 源代码
│   ├── data_processor.py   # 数据预处理模块
│   ├── cost_engine.py      # 成本计算引擎
│   ├── rule_engine.py      # 规则引擎
│   └── visualizer.py       # 可视化模块
├── config/                 # 配置文件
│   └── rules.yaml         # 成本分配规则配置
└── requirements.txt        # 项目依赖
```

## 使用方法
1. 安装依赖：
```bash
pip install -r requirements.txt
```

2. 准备数据：
   - 使用data_generator.ipynb生成模拟数据
   - 或准备符合要求的实际业务数据

3. 运行分析：
   - 打开notebooks/cost_analysis.ipynb
   - 按步骤执行分析流程

## 输出结果
1. 成本明细表（Excel格式）
   - 各品类成本构成
   - 分项成本占比
   - 异常成本标记

2. 可视化报告（PDF格式）
   - 成本占比桑基图
   - 品类成本结构对比图
   - 异常成本预警图表

## 注意事项
- 确保输入数据完整性
- 定期更新成本分配规则
- 关注异常成本预警 