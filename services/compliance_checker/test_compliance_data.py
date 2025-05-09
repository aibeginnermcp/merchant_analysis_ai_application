"""
财务合规检查测试数据生成脚本
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List

class ComplianceTestDataGenerator:
    """财务合规测试数据生成器"""
    
    def __init__(self):
        self.start_date = datetime(2024, 1, 1)
        self.end_date = datetime(2024, 3, 31)
        self.business_types = ['餐饮', '电商', '零售', '服务']
        self.anomaly_ratio = 0.05  # 降低异常比例到5%
        
    def generate_test_data(self, n_samples: int = 1000) -> Dict[str, pd.DataFrame]:
        """生成测试数据集"""
        
        # 基础交易数据
        transactions = self._generate_transaction_data(n_samples)
        
        # 促销活动数据
        promotions = self._generate_promotion_data(n_samples)
        
        # 费用报销数据
        expenses = self._generate_expense_data(n_samples)
        
        # 关联交易数据
        related_party = self._generate_related_party_data(n_samples)
        
        # 预算执行数据
        budget = self._generate_budget_data(n_samples)
        
        return {
            'transactions': transactions,
            'promotions': promotions,
            'expenses': expenses,
            'related_party': related_party,
            'budget': budget
        }
    
    def _generate_transaction_data(self, n_samples: int) -> pd.DataFrame:
        """生成交易数据"""
        return pd.DataFrame({
            'transaction_id': [f'T{i:06d}' for i in range(n_samples)],
            'transaction_date': [self.start_date + timedelta(days=np.random.randint(0, 90)) 
                               for _ in range(n_samples)],
            'business_type': np.random.choice(self.business_types, n_samples),
            'amount': np.random.uniform(1000, 500000, n_samples),  # 调整金额范围
            'payment_type': np.random.choice(['现金', '银行转账', '信用卡', '其他'], n_samples, 
                                          p=[0.05, 0.7, 0.2, 0.05]),  # 调整支付方式比例
            'has_invoice': np.random.choice([True, False], n_samples, p=[0.95, 0.05]),  # 提高合规比例
            'approval_status': np.random.choice(['已批准', '待审批', '已拒绝'], n_samples, 
                                             p=[0.9, 0.08, 0.02])  # 调整审批状态比例
        })
    
    def _generate_promotion_data(self, n_samples: int) -> pd.DataFrame:
        """生成促销活动数据"""
        # 生成基础预算数据
        budgets = np.random.uniform(10000, 100000, n_samples)  # 调整预算范围
        
        # 生成实际成本（大部分在预算范围内）
        actual_costs = []
        for budget in budgets:
            if np.random.random() < self.anomaly_ratio:
                # 异常数据：超预算
                actual_costs.append(budget * (1 + np.random.uniform(0.1, 0.3)))
            else:
                # 正常数据：在预算范围内
                actual_costs.append(budget * np.random.uniform(0.7, 1.0))
        
        return pd.DataFrame({
            'promotion_id': [f'P{i:06d}' for i in range(n_samples)],
            'promotion_type': np.random.choice(['节日促销', '会员活动', '清仓特卖', '新品推广'], n_samples),
            'start_date': [self.start_date + timedelta(days=np.random.randint(0, 60)) 
                          for _ in range(n_samples)],
            'end_date': [self.start_date + timedelta(days=np.random.randint(61, 90)) 
                        for _ in range(n_samples)],
            'budget': budgets,
            'actual_cost': actual_costs,
            'approval_id': [f'PA{i:06d}' if np.random.random() > self.anomaly_ratio else None 
                          for i in range(n_samples)]
        })
    
    def _generate_expense_data(self, n_samples: int) -> pd.DataFrame:
        """生成费用报销数据"""
        # 根据费用类型生成合理的金额范围
        expense_types = np.random.choice(['差旅', '办公', '业务招待', '培训'], n_samples)
        amounts = []
        for exp_type in expense_types:
            if exp_type == '差旅':
                amounts.append(np.random.uniform(1000, 10000))
            elif exp_type == '办公':
                amounts.append(np.random.uniform(100, 5000))
            elif exp_type == '业务招待':
                amounts.append(np.random.uniform(500, 8000))
            else:  # 培训
                amounts.append(np.random.uniform(2000, 15000))
        
        return pd.DataFrame({
            'expense_id': [f'E{i:06d}' for i in range(n_samples)],
            'expense_type': expense_types,
            'amount': amounts,
            'submit_date': [self.start_date + timedelta(days=np.random.randint(0, 90)) 
                           for _ in range(n_samples)],
            'has_invoice': np.random.choice([True, False], n_samples, p=[0.95, 0.05]),
            'has_approval': np.random.choice([True, False], n_samples, p=[0.95, 0.05]),
            'reimbursement_status': np.random.choice(['已报销', '待审批', '已拒绝', '待补充材料'], 
                                                    n_samples, p=[0.8, 0.15, 0.03, 0.02])
        })
    
    def _generate_related_party_data(self, n_samples: int) -> pd.DataFrame:
        """生成关联交易数据"""
        # 生成基础金额
        amounts = np.random.uniform(10000, 500000, n_samples)  # 调整金额范围
        
        # 确定是否为重大关联交易
        is_major = amounts > 200000  # 设定重大关联交易阈值
        
        # 根据交易金额确定审批级别
        approval_levels = []
        for amount, major in zip(amounts, is_major):
            if major:
                if np.random.random() < self.anomaly_ratio:
                    approval_levels.append('总经理办公会')  # 审批级别不足
                else:
                    approval_levels.append(np.random.choice(['董事会', '股东大会']))
            else:
                approval_levels.append(np.random.choice(['总经理办公会', '董事会']))
        
        return pd.DataFrame({
            'transaction_id': [f'RP{i:06d}' for i in range(n_samples)],
            'related_party': [f'关联方{i}' for i in range(n_samples)],
            'transaction_type': np.random.choice(['采购', '销售', '租赁', '服务'], n_samples),
            'amount': amounts,
            'transaction_date': [self.start_date + timedelta(days=np.random.randint(0, 90)) 
                               for _ in range(n_samples)],
            'disclosure_status': np.random.choice(['已披露', '未披露', '待披露'], n_samples, 
                                               p=[0.9, 0.05, 0.05]),  # 提高合规比例
            'approval_level': approval_levels
        })
    
    def _generate_budget_data(self, n_samples: int) -> pd.DataFrame:
        """生成预算执行数据"""
        # 生成基础预算金额
        budget_amounts = np.random.uniform(50000, 300000, n_samples)  # 调整预算范围
        
        # 生成实际执行金额
        actual_amounts = []
        for budget in budget_amounts:
            if np.random.random() < self.anomaly_ratio:
                # 异常数据：重大偏差
                actual_amounts.append(budget * (1 + np.random.uniform(0.2, 0.4)))
            else:
                # 正常数据：在合理范围内
                actual_amounts.append(budget * np.random.uniform(0.8, 1.2))
        
        return pd.DataFrame({
            'budget_id': [f'B{i:06d}' for i in range(n_samples)],
            'department': np.random.choice(['销售部', '市场部', '运营部', '人力资源部'], n_samples),
            'budget_type': np.random.choice(['营销预算', '运营预算', '人力预算', '研发预算'], n_samples),
            'budget_amount': budget_amounts,
            'actual_amount': actual_amounts,
            'period': [f'2024Q1' for _ in range(n_samples)],
            'has_variance_explanation': [True if abs(a-b)/b > 0.2 else np.random.choice([True, False], p=[0.9, 0.1])
                                      for a, b in zip(actual_amounts, budget_amounts)]
        })

if __name__ == "__main__":
    # 生成测试数据
    generator = ComplianceTestDataGenerator()
    test_data = generator.generate_test_data(1000)
    
    # 保存测试数据
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    for name, df in test_data.items():
        df.to_csv(f'output/compliance_test_{name}_{timestamp}.csv', index=False, encoding='utf-8')
    print("测试数据生成完成！") 