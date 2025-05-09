# 财务合规检查 (已弃用)

**注意**: 此目录已合并至 `services/compliance_checker`，请使用新目录。

**Note**: This directory has been merged into `services/compliance_checker`, please use the new directory.

---

# 智能财务哨兵系统

## 项目简介

智能财务哨兵系统是一个企业级财务风险防控平台，基于规则引擎和机器学习技术，为企业提供全方位的财务合规检查和风险预警服务。

### 主要功能

1. 合规检查
   - 支持200+预置审计规则
   - 动态规则加载和更新
   - 多维度风险评估
   - 自动生成审计报告

2. 证据管理
   - 完整的证据生命周期管理
   - 证据链构建和可视化
   - 证据完整性验证
   - 灵活的证据搜索功能

3. 风险预警
   - 实时风险监控
   - 多级预警机制
   - 自动整改建议
   - 风险趋势分析

4. 报告生成
   - 标准化审计报告
   - 可视化分析图表
   - 多维度数据统计
   - 整改建议跟踪

## 系统架构

```
financial_sentinel/
├── audit_rules/           # 审计规则目录
│   └── financial_rules.yaml   # 财务审计规则
├── rule_engine/           # 规则引擎模块
│   ├── rule_loader.py     # 规则加载器
│   └── evidence_tracer.py # 证据追溯器
├── tests/                 # 测试目录
│   └── test_financial_sentinel.py  # 单元测试
├── logs/                  # 日志目录
├── output/               # 输出目录
├── reports/              # 报告目录
├── audit_evidence/       # 证据存储目录
├── main.py              # 主程序入口
├── compliance_checker.py # 合规检查器
└── requirements.txt     # 依赖配置
```

## 安装说明

1. 环境要求
   - Python 3.8+
   - 操作系统：Linux/macOS/Windows

2. 安装步骤
   ```bash
   # 克隆代码库
   git clone https://github.com/your-org/financial-sentinel.git
   cd financial-sentinel

   # 创建虚拟环境
   python -m venv venv
   source venv/bin/activate  # Linux/macOS
   # 或
   .\venv\Scripts\activate  # Windows

   # 安装依赖
   pip install -r requirements.txt
   ```

## 使用方法

1. 基本使用
   ```python
   from main import FinancialSentinel
   
   # 初始化系统
   sentinel = FinancialSentinel()
   
   # 加载数据
   data = {
       'transactions': transactions_df,
       'expenses': expenses_df,
       'related_party': related_party_df
   }
   
   # 执行合规检查
   results = sentinel.run_compliance_check(data)
   ```

2. 规则管理
   ```python
   # 获取规则统计
   stats = sentinel.get_rule_statistics()
   print(f"总规则数: {stats['total_rules']}")
   print(f"高风险规则: {stats['high_severity']}")
   
   # 重新加载规则
   sentinel.rule_loader.reload_rules()
   ```

3. 证据管理
   ```python
   # 创建证据
   evidence = sentinel.evidence_tracer.create_evidence(
       evidence_type="交易记录",
       source="财务系统",
       content=transaction_data,
       related_rule="rule_101"
   )
   
   # 创建证据链
   chain = sentinel.evidence_tracer.create_evidence_chain(
       evidences=[evidence1, evidence2],
       conclusion="发现未经授权的大额支出",
       risk_level="高风险",
       reviewer="张三"
   )
   
   # 验证证据完整性
   is_valid = sentinel.evidence_tracer.verify_evidence_integrity(evidence.id)
   ```

## 配置说明

1. 规则配置
   - 规则文件位置：`audit_rules/financial_rules.yaml`
   - 规则格式：
     ```yaml
     rule_type:
       rule_id:
         name: 规则名称
         description: 规则描述
         condition: 触发条件
         severity: 严重程度
         action: 响应动作
         references: 参考依据
     ```

2. 日志配置
   - 日志级别：INFO
   - 日志文件：`logs/financial_sentinel.log`
   - 日志格式：时间 - 模块 - 级别 - 消息

3. 输出配置
   - 报告输出：`reports/`
   - 证据存储：`audit_evidence/`
   - 图表输出：`output/`

## 开发指南

1. 代码规范
   - 遵循PEP 8规范
   - 使用类型注解
   - 编写完整的文档字符串

2. 测试规范
   - 运行测试：`python -m unittest tests/test_financial_sentinel.py`
   - 测试覆盖率要求：>80%
   - 每个功能模块必须有对应的测试用例

3. 版本控制
   - 使用Git管理代码
   - 遵循语义化版本规范
   - 重要更新必须有changelog

## 常见问题

1. Q: 如何添加新的审计规则？
   A: 在`audit_rules/financial_rules.yaml`中按照规则格式添加新规则，系统会自动加载。

2. Q: 如何自定义报告格式？
   A: 修改`compliance_checker.py`中的`_generate_compliance_report`方法。

3. Q: 如何扩展风险评估模型？
   A: 在`compliance_checker.py`中添加新的风险评估逻辑。

## 更新日志

### v1.0.0 (2024-03-01)
- 初始版本发布
- 支持基础合规检查功能
- 实现证据链追溯系统
- 添加报告生成功能

## 贡献指南

1. Fork 项目
2. 创建特性分支
3. 提交代码
4. 创建Pull Request

## 许可证

MIT License

## 联系方式

- 项目维护者：张三
- 邮箱：zhangsan@example.com
- 问题反馈：https://github.com/your-org/financial-sentinel/issues 