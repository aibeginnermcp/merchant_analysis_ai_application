"""
智能财务哨兵系统 - 报告生成器测试
"""

import unittest
from datetime import datetime, timedelta
import numpy as np
from pathlib import Path
import json
from report_generator.report_generator import ReportGenerator

class TestReportGenerator(unittest.TestCase):
    """报告生成器测试类"""
    
    @classmethod
    def setUpClass(cls):
        """测试类初始化"""
        cls.report_generator = ReportGenerator()
        cls.test_data = cls._generate_test_data()
        
    @staticmethod
    def _generate_test_data():
        """生成测试数据"""
        # 生成当前检查结果
        current_results = {
            'high': [
                {
                    'severity': '高风险',
                    'description': '发现未经授权的大额资金支出',
                    'department': '财务部',
                    'suggestion': '立即冻结相关账户，启动资金安全审计'
                },
                {
                    'severity': '高风险',
                    'description': '关联交易未及时披露',
                    'department': '投资部',
                    'suggestion': '补充披露文件，完善内部控制流程'
                }
            ],
            'medium': [
                {
                    'severity': '中风险',
                    'description': '费用报销单据不完整',
                    'department': '市场部',
                    'suggestion': '要求补充完整的报销凭证'
                },
                {
                    'severity': '中风险',
                    'description': '预算执行超出限额',
                    'department': '研发部',
                    'suggestion': '调整预算分配，加强预算管理'
                },
                {
                    'severity': '中风险',
                    'description': '合同审批流程延迟',
                    'department': '法务部',
                    'suggestion': '优化审批流程，设置审批预警'
                }
            ],
            'low': [
                {
                    'severity': '低风险',
                    'description': '固定资产标签缺失',
                    'department': '行政部',
                    'suggestion': '完善资产管理系统，定期盘点'
                },
                {
                    'severity': '低风险',
                    'description': '员工培训记录未更新',
                    'department': '人力资源部',
                    'suggestion': '及时更新培训档案，完善记录'
                }
            ]
        }
        
        # 生成历史数据（30天）
        historical_data = []
        base_high = 2
        base_medium = 4
        base_low = 3
        
        for i in range(30):
            date = datetime.now() - timedelta(days=i)
            historical_data.append({
                'date': date,
                'high_risk_count': max(0, int(base_high + np.random.normal(0, 1))),
                'medium_risk_count': max(0, int(base_medium + np.random.normal(0, 1.5))),
                'low_risk_count': max(0, int(base_low + np.random.normal(0, 2)))
            })
        
        # 生成部门风险数据
        department_data = {
            '财务部': {'high': 2, 'medium': 3, 'low': 1},
            '投资部': {'high': 1, 'medium': 2, 'low': 2},
            '市场部': {'high': 0, 'medium': 4, 'low': 3},
            '研发部': {'high': 0, 'medium': 2, 'low': 4},
            '法务部': {'high': 1, 'medium': 3, 'low': 2},
            '人力资源部': {'high': 0, 'medium': 1, 'low': 3},
            '行政部': {'high': 0, 'medium': 1, 'low': 4}
        }
        
        return {
            'current_results': current_results,
            'historical_data': historical_data,
            'department_data': department_data
        }
        
    def test_generate_report(self):
        """测试报告生成"""
        # 生成报告
        report_file = self.report_generator.generate_report(
            self.test_data['current_results'],
            self.test_data['historical_data'],
            self.test_data['department_data']
        )
        
        # 验证报告文件是否生成
        self.assertTrue(Path(report_file).exists())
        self.assertTrue(report_file.endswith('.html'))
        
        # 验证报告内容
        with open(report_file, 'r', encoding='utf-8') as f:
            content = f.read()
            
        # 验证关键内容
        self.assertIn('财务合规检查报告', content)
        self.assertIn('风险趋势分析', content)
        self.assertIn('部门风险分布', content)
        self.assertIn('财务部', content)
        self.assertIn('高风险问题', content)

if __name__ == '__main__':
    unittest.main() 