"""
测试报告生成
"""

from report_generator.report_generator import ReportGenerator
from datetime import datetime, timedelta
import random

def generate_test_data():
    """生成测试数据"""
    # 生成历史数据
    historical_data = []
    base_date = datetime.now() - timedelta(days=30)
    
    for i in range(30):
        date = base_date + timedelta(days=i)
        historical_data.append({
            'date': date.strftime('%Y-%m-%d'),
            'high_risk_count': random.randint(1, 5),
            'medium_risk_count': random.randint(3, 8),
            'low_risk_count': random.randint(5, 12)
        })
    
    # 生成部门数据
    departments = ['财务部', '销售部', '运营部', '人力资源部', '技术部']
    department_data = []
    
    for dept in departments:
        department_data.append({
            'department': dept,
            'high_risk': random.randint(0, 3),
            'medium_risk': random.randint(2, 6),
            'low_risk': random.randint(4, 10)
        })
    
    # 生成当前问题列表
    issues = [
        {
            'risk_level': '高风险',
            'description': '发现未经授权的大额资金支出',
            'department': '财务部',
            'suggestion': '立即冻结相关账户，启动资金安全审计'
        },
        {
            'risk_level': '高风险',
            'description': '销售收入异常波动',
            'department': '销售部',
            'suggestion': '核实销售记录，排查异常交易'
        },
        {
            'risk_level': '中风险',
            'description': '费用报销延迟提交',
            'department': '运营部',
            'suggestion': '加强费用报销管理，明确提交时限'
        },
        {
            'risk_level': '低风险',
            'description': '小额现金管理不规范',
            'department': '财务部',
            'suggestion': '完善现金管理制度，加强日常检查'
        }
    ]
    
    return {
        'historical_data': historical_data,
        'department_data': department_data,
        'issues': issues
    }

def main():
    """生成测试报告"""
    generator = ReportGenerator()
    test_data = generate_test_data()
    report_file = generator.generate_report(test_data)
    print(f'报告已生成：{report_file}')

if __name__ == '__main__':
    main() 