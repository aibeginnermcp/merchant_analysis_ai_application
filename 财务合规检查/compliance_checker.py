"""
财务合规检查器
"""

import pandas as pd
import numpy as np
from datetime import datetime
from typing import Dict, List, Tuple
import re
from collections import defaultdict
import matplotlib.pyplot as plt
import seaborn as sns
from matplotlib.font_manager import FontProperties

class ComplianceChecker:
    """财务合规检查器"""
    
    def __init__(self):
        # 设置中文字体
        plt.rcParams['font.sans-serif'] = ['Arial Unicode MS']  # macOS
        plt.rcParams['axes.unicode_minus'] = False  # 解决负号显示问题
        
        self.risk_weights = {
            '促销预算超支': {
                'base_score': 60,
                'factor': lambda x: min(40, x['exceed_ratio'] * 100)  # 超支比例作为加权因子
            },
            '促销活动未审批': {
                'base_score': 80,
                'factor': lambda x: min(20, x['amount'] / 10000)  # 金额（万元）作为加权因子
            },
            '费用缺少发票': {
                'base_score': 70,
                'factor': lambda x: min(30, x['amount'] / 1000)  # 金额（千元）作为加权因子
            },
            '关联交易未披露': {
                'base_score': 90,
                'factor': lambda x: min(10, x['amount'] / 100000)  # 金额（十万元）作为加权因子
            }
        }
        
        self.risk_levels = [
            (90, '极高风险'),
            (80, '高风险'),
            (70, '中高风险'),
            (60, '中风险'),
            (40, '中低风险'),
            (20, '低风险'),
            (0, '正常')
        ]
        
        self.compliance_rules = self._init_compliance_rules()
        
    def _init_compliance_rules(self) -> Dict:
        """初始化合规检查规则"""
        return {
            'promotion': {
                'budget_exceed': 0.1,  # 促销预算超支阈值
                'approval_required': True  # 是否需要审批
            },
            'expense': {
                'invoice_required': True,  # 是否需要发票
                'approval_required': True,  # 是否需要审批
                'max_cash_amount': 5000  # 现金支付最大金额
            },
            'related_party': {
                'disclosure_required': True,  # 是否需要披露
                'major_transaction_threshold': 500000  # 重大关联交易阈值
            },
            'budget': {
                'variance_threshold': 0.2,  # 预算偏差阈值
                'explanation_required': True  # 是否需要说明
            }
        }
    
    def check_compliance(self, data: Dict[str, pd.DataFrame]) -> Tuple[Dict, str]:
        """执行合规检查"""
        
        # 检查结果存储
        results = {
            'promotion_issues': self._check_promotion_compliance(data['promotions']),
            'expense_issues': self._check_expense_compliance(data['expenses'], data['transactions']),
            'related_party_issues': self._check_related_party_compliance(data['related_party']),
            'budget_issues': self._check_budget_compliance(data['budget'])
        }
        
        # 生成报告
        report = self._generate_compliance_report(results)
        
        return results, report
    
    def _check_promotion_compliance(self, df: pd.DataFrame) -> List[Dict]:
        """检查促销活动合规性"""
        issues = []
        
        # 检查预算超支
        budget_exceed = df[df['actual_cost'] > df['budget'] * (1 + self.compliance_rules['promotion']['budget_exceed'])]
        for _, row in budget_exceed.iterrows():
            issues.append({
                'type': '促销预算超支',
                'severity': '高风险',
                'promotion_id': row['promotion_id'],
                'budget': row['budget'],
                'actual_cost': row['actual_cost'],
                'exceed_ratio': (row['actual_cost'] - row['budget']) / row['budget']
            })
        
        # 检查审批
        no_approval = df[df['approval_id'].isna()]
        for _, row in no_approval.iterrows():
            issues.append({
                'type': '促销活动未审批',
                'severity': '高风险',
                'promotion_id': row['promotion_id'],
                'amount': row['actual_cost']
            })
        
        return issues
    
    def _check_expense_compliance(self, expenses: pd.DataFrame, transactions: pd.DataFrame) -> List[Dict]:
        """检查费用报销合规性"""
        issues = []
        
        # 检查发票
        no_invoice = expenses[~expenses['has_invoice']]
        for _, row in no_invoice.iterrows():
            issues.append({
                'type': '费用缺少发票',
                'severity': '高风险',
                'expense_id': row['expense_id'],
                'amount': row['amount']
            })
        
        # 检查审批
        no_approval = expenses[~expenses['has_approval']]
        for _, row in no_approval.iterrows():
            issues.append({
                'type': '费用未审批',
                'severity': '中风险',
                'expense_id': row['expense_id'],
                'amount': row['amount']
            })
        
        # 检查现金支付限额
        cash_transactions = transactions[
            (transactions['payment_type'] == '现金') & 
            (transactions['amount'] > self.compliance_rules['expense']['max_cash_amount'])
        ]
        for _, row in cash_transactions.iterrows():
            issues.append({
                'type': '现金支付超限',
                'severity': '中风险',
                'transaction_id': row['transaction_id'],
                'amount': row['amount']
            })
        
        return issues
    
    def _check_related_party_compliance(self, df: pd.DataFrame) -> List[Dict]:
        """检查关联交易合规性"""
        issues = []
        
        # 检查信息披露
        undisclosed = df[df['disclosure_status'] == '未披露']
        for _, row in undisclosed.iterrows():
            issues.append({
                'type': '关联交易未披露',
                'severity': '高风险',
                'transaction_id': row['transaction_id'],
                'related_party': row['related_party'],
                'amount': row['amount']
            })
        
        # 检查重大关联交易
        major_transactions = df[df['amount'] > self.compliance_rules['related_party']['major_transaction_threshold']]
        for _, row in major_transactions.iterrows():
            if row['approval_level'] not in ['董事会', '股东大会']:
                issues.append({
                    'type': '重大关联交易审批级别不足',
                    'severity': '高风险',
                    'transaction_id': row['transaction_id'],
                    'amount': row['amount'],
                    'current_approval': row['approval_level']
                })
        
        return issues
    
    def _check_budget_compliance(self, df: pd.DataFrame) -> List[Dict]:
        """检查预算执行合规性"""
        issues = []
        
        # 计算预算偏差
        df['variance_ratio'] = (df['actual_amount'] - df['budget_amount']) / df['budget_amount']
        
        # 检查重大偏差
        significant_variance = df[abs(df['variance_ratio']) > self.compliance_rules['budget']['variance_threshold']]
        for _, row in significant_variance.iterrows():
            if not row['has_variance_explanation']:
                issues.append({
                    'type': '预算重大偏差未说明',
                    'severity': '中风险',
                    'budget_id': row['budget_id'],
                    'department': row['department'],
                    'variance_ratio': row['variance_ratio']
                })
        
        return issues
    
    def _calculate_risk_score(self, issue_type: str, issue_data: Dict) -> float:
        """计算单个问题的风险分数"""
        if issue_type not in self.risk_weights:
            return 0
        
        weight = self.risk_weights[issue_type]
        base_score = weight['base_score']
        factor = weight['factor'](issue_data)
        
        return base_score + factor
    
    def _get_risk_level(self, score: float) -> str:
        """根据分数确定风险等级"""
        for threshold, level in self.risk_levels:
            if score >= threshold:
                return level
        return '正常'
    
    def _generate_risk_visualization(self, results: Dict, save_path: str = 'output/risk_analysis.png'):
        """生成风险分析可视化图表"""
        plt.figure(figsize=(20, 15))
        
        # 设置全局字体
        plt.rcParams['font.size'] = 12
        plt.rcParams['axes.titlesize'] = 14
        plt.rcParams['axes.labelsize'] = 12
        
        # 1. 风险分布饼图
        plt.subplot(2, 2, 1)
        risk_counts = defaultdict(int)
        for issues in results.values():
            for issue in issues:
                score = self._calculate_risk_score(issue['type'], issue)
                level = self._get_risk_level(score)
                risk_counts[level] += 1
        
        colors = ['#FF4B4B', '#FF7F7F', '#FFB4B4', '#FFE9E9', '#B4D8E7', '#8FB9D0', '#69A3C3']
        plt.pie(risk_counts.values(), 
                labels=risk_counts.keys(), 
                autopct='%1.1f%%',
                colors=colors,
                startangle=90)
        plt.title('风险等级分布')
        
        # 2. 问题类型分布条形图
        plt.subplot(2, 2, 2)
        issue_counts = defaultdict(int)
        for issues in results.values():
            for issue in issues:
                issue_counts[issue['type']] += 1
        
        colors = ['#FF4B4B', '#FFB4B4', '#B4D8E7', '#69A3C3']
        plt.bar(range(len(issue_counts)), 
                list(issue_counts.values()),
                color=colors)
        plt.xticks(range(len(issue_counts)), 
                   list(issue_counts.keys()),
                   rotation=45,
                   ha='right')
        plt.title('问题类型分布')
        
        # 3. 金额分布箱线图
        plt.subplot(2, 2, 3)
        amounts_by_type = defaultdict(list)
        for issues in results.values():
            for issue in issues:
                if 'amount' in issue:
                    amounts_by_type[issue['type']].append(issue['amount'])
        
        box_colors = ['#FF4B4B', '#FFB4B4', '#B4D8E7', '#69A3C3']
        box = plt.boxplot([amounts for amounts in amounts_by_type.values()],
                         labels=amounts_by_type.keys(),
                         patch_artist=True)
        
        for patch, color in zip(box['boxes'], box_colors):
            patch.set_facecolor(color)
        
        plt.xticks(rotation=45, ha='right')
        plt.title('金额分布（单位：元）')
        plt.ylabel('金额')
        
        # 4. 风险得分热力图
        plt.subplot(2, 2, 4)
        scores_by_type = defaultdict(list)
        for issues in results.values():
            for issue in issues:
                score = self._calculate_risk_score(issue['type'], issue)
                scores_by_type[issue['type']].append(score)
        
        scores_matrix = []
        for scores in scores_by_type.values():
            scores_matrix.append([np.mean(scores), np.max(scores), np.min(scores)])
        
        sns.heatmap(scores_matrix,
                    xticklabels=['平均分', '最高分', '最低分'],
                    yticklabels=list(scores_by_type.keys()),
                    annot=True,
                    fmt='.1f',
                    cmap='RdYlGn_r',
                    center=60)
        plt.title('风险得分分析')
        
        # 调整布局
        plt.tight_layout(pad=3.0)
        
        # 添加总标题
        plt.suptitle('财务合规风险分析报告', 
                     fontsize=16, 
                     y=1.02)
        
        # 保存图表
        plt.savefig(save_path, 
                    dpi=300,
                    bbox_inches='tight',
                    pad_inches=0.5)
        plt.close()
    
    def _generate_compliance_report(self, results: Dict) -> str:
        """生成合规检查报告"""
        # 生成风险分析图表
        self._generate_risk_visualization(results)
        
        report = []
        report.append("=" * 80)
        report.append("                              财务合规检查报告")
        report.append("=" * 80)
        report.append(f"检查时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report.append("=" * 80 + "\n")
        
        # 1. 风险评分概况
        total_issues = sum(len(issues) for issues in results.values())
        all_scores = []
        risk_level_counts = defaultdict(int)
        
        for issues in results.values():
            for issue in issues:
                score = self._calculate_risk_score(issue['type'], issue)
                all_scores.append(score)
                risk_level_counts[self._get_risk_level(score)] += 1
        
        avg_score = np.mean(all_scores) if all_scores else 0
        max_score = np.max(all_scores) if all_scores else 0
        
        report.append("一、风险评分概况")
        report.append("=" * 40)
        report.append(f"1. 总体风险评分")
        report.append(f"   - 平均风险分数: {avg_score:.1f}")
        report.append(f"   - 最高风险分数: {max_score:.1f}")
        report.append(f"   - 整体风险等级: {self._get_risk_level(avg_score)}")
        report.append("")
        
        report.append("2. 风险等级分布")
        for level, count in risk_level_counts.items():
            report.append(f"   - {level}: {count} 个 ({count/total_issues*100:.1f}%)")
        report.append("")
        
        # 2. 总体情况
        total_issues = sum(len(issues) for issues in results.values())
        high_risk = sum(1 for issues in results.values() 
                        for issue in issues if issue['severity'] == '高风险')
        medium_risk = sum(1 for issues in results.values() 
                          for issue in issues if issue['severity'] == '中风险')
        
        report.append("一、检查总体情况")
        report.append("=" * 40)
        report.append("1. 问题统计")
        report.append(f"   - 发现问题总数: {total_issues}")
        report.append(f"   - 高风险问题数: {high_risk}")
        report.append(f"   - 中风险问题数: {medium_risk}")
        report.append(f"   - 问题分布比例: {high_risk/total_issues*100:.1f}% 高风险, "
                     f"{medium_risk/total_issues*100:.1f}% 中风险\n")
        
        # 2. 金额维度分析
        amount_ranges = {
            '10万以下': (0, 100000),
            '10-50万': (100000, 500000),
            '50-100万': (500000, 1000000),
            '100万以上': (1000000, float('inf'))
        }
        
        amount_distribution = {range_name: 0 for range_name in amount_ranges}
        total_amount = 0
        
        for issues in results.values():
            for issue in issues:
                if 'amount' in issue:
                    amount = issue['amount']
                    total_amount += amount
                    for range_name, (min_amount, max_amount) in amount_ranges.items():
                        if min_amount <= amount < max_amount:
                            amount_distribution[range_name] += 1
                            break
        
        if total_amount > 0:
            report.append("2. 金额维度分析")
            report.append(f"   - 问题涉及总金额: ¥{total_amount:,.2f}")
            report.append("   - 金额分布:")
            for range_name, count in amount_distribution.items():
                if count > 0:
                    report.append(f"     * {range_name}: {count} 个问题")
            report.append("")
        
        # 3. 具体问题分析
        report.append("二、具体问题分析")
        report.append("=" * 40)
        
        # 3.1 促销活动合规情况
        promotion_issues = results['promotion_issues']
        if promotion_issues:
            report.append("1. 促销活动合规情况")
            report.append("-" * 30)
            report.append(f"   - 发现问题数: {len(promotion_issues)}")
            
            # 按问题类型分类
            issue_types = defaultdict(list)
            for issue in promotion_issues:
                issue_types[issue['type']].append(issue)
            
            report.append("   - 问题类型分布:")
            for issue_type, issues in issue_types.items():
                report.append(f"     * {issue_type}: {len(issues)} 个")
                
            report.append("   - 典型问题示例:")
            for issue in sorted(promotion_issues, 
                              key=lambda x: x.get('exceed_ratio', 0) 
                              if x['type'] == '促销预算超支' else 0, 
                              reverse=True)[:3]:
                if issue['type'] == '促销预算超支':
                    report.append(f"     * {issue['promotion_id']}: "
                                f"预算超支 {issue['exceed_ratio']*100:.1f}%")
                else:
                    report.append(f"     * {issue['promotion_id']}: {issue['type']}")
            report.append("")
        
        # 3.2 费用报销合规情况
        expense_issues = results['expense_issues']
        if expense_issues:
            report.append("2. 费用报销合规情况")
            report.append("-" * 30)
            report.append(f"   - 发现问题数: {len(expense_issues)}")
            
            # 按费用类型分类统计
            expense_type_issues = defaultdict(lambda: {'count': 0, 'amount': 0})
            for issue in expense_issues:
                if 'expense_type' in issue:
                    exp_type = issue['expense_type']
                    expense_type_issues[exp_type]['count'] += 1
                    expense_type_issues[exp_type]['amount'] += issue['amount']
            
            report.append("   - 问题分布:")
            for exp_type, stats in expense_type_issues.items():
                report.append(f"     * {exp_type}: {stats['count']} 个, "
                            f"涉及金额 ¥{stats['amount']:,.2f}")
                
            report.append("   - 典型问题示例:")
            for issue in sorted(expense_issues, 
                              key=lambda x: x['amount'], 
                              reverse=True)[:3]:
                issue_id = issue.get('expense_id', issue.get('transaction_id', 'UNKNOWN'))
                report.append(f"     * {issue_id}: {issue['type']} "
                            f"(金额: ¥{issue['amount']:,.2f})")
            report.append("")
        
        # 3.3 关联交易合规情况
        related_party_issues = results['related_party_issues']
        if related_party_issues:
            report.append("3. 关联交易合规情况")
            report.append("-" * 30)
            report.append(f"   - 发现问题数: {len(related_party_issues)}")
            
            # 按问题类型和金额区间统计
            issue_types = defaultdict(lambda: {'count': 0, 'amount': 0})
            amount_ranges = defaultdict(int)
            for issue in related_party_issues:
                issue_types[issue['type']]['count'] += 1
                issue_types[issue['type']]['amount'] += issue['amount']
                amount = issue['amount']
                if amount < 100000:
                    amount_ranges['10万以下'] += 1
                elif amount < 500000:
                    amount_ranges['10-50万'] += 1
                else:
                    amount_ranges['50万以上'] += 1
            
            report.append("   - 问题类型分布:")
            for issue_type, stats in issue_types.items():
                report.append(f"     * {issue_type}: {stats['count']} 个, "
                            f"涉及金额 ¥{stats['amount']:,.2f}")
                
            report.append("   - 金额分布:")
            for range_name, count in amount_ranges.items():
                report.append(f"     * {range_name}: {count} 个")
                
            report.append("   - 典型问题示例:")
            for issue in sorted(related_party_issues, 
                              key=lambda x: x['amount'], 
                              reverse=True)[:3]:
                report.append(f"     * {issue['transaction_id']}: {issue['type']} "
                            f"(金额: ¥{issue['amount']:,.2f}, "
                            f"关联方: {issue['related_party']})")
            report.append("")
        
        # 4. 高风险问题清单
        report.append("三、高风险问题清单")
        report.append("=" * 40)
        high_risk_issues = [issue for issues in results.values() 
                           for issue in issues if issue['severity'] == '高风险']
        
        # 按问题类型分组
        high_risk_by_type = defaultdict(list)
        for issue in high_risk_issues:
            high_risk_by_type[issue['type']].append(issue)
        
        for issue_type, issues in high_risk_by_type.items():
            report.append(f"1. {issue_type}")
            report.append(f"   - 发现 {len(issues)} 个问题")
            report.append("   - 典型案例:")
            
            # 按金额排序，显示前三个最大金额的问题
            sorted_issues = sorted(issues, 
                                 key=lambda x: x.get('amount', 0), 
                                 reverse=True)
            for issue in sorted_issues[:3]:
                details = []
                if 'amount' in issue:
                    details.append(f"金额: ¥{issue['amount']:,.2f}")
                if 'related_party' in issue:
                    details.append(f"关联方: {issue['related_party']}")
                if 'exceed_ratio' in issue:
                    details.append(f"超支比例: {issue['exceed_ratio']*100:.1f}%")
                report.append(f"     * {issue.get('transaction_id', '')} "
                            f"{', '.join(details)}")
            report.append("")
        
        # 5. 整改建议
        report.append("四、整改建议")
        report.append("=" * 40)
        
        if promotion_issues:
            report.append("1. 促销活动管理")
            report.append("   - 加强促销活动预算管理，建立预算预警机制")
            report.append("   - 完善促销活动审批流程，确保所有活动经过适当审批")
            report.append("   - 建立促销效果评估机制，优化资源配置")
            report.append("")
        
        if expense_issues:
            report.append("2. 费用报销管理")
            report.append("   - 严格执行发票管理制度，确保费用报销有效凭证")
            report.append("   - 加强费用预算控制，建立分类管理机制")
            report.append("   - 优化费用报销流程，提高审批效率")
            report.append("")
        
        if related_party_issues:
            report.append("3. 关联交易管理")
            report.append("   - 建立健全关联交易识别和披露机制")
            report.append("   - 严格执行关联交易审批制度，确保审批层级适当")
            report.append("   - 加强关联交易定价管理，确保交易价格公允")
            report.append("")
        
        # 在报告末尾添加风险分析图表说明
        report.append("五、风险分析图表")
        report.append("=" * 40)
        report.append("详细的风险分析图表已生成，包括：")
        report.append("1. 风险等级分布饼图")
        report.append("2. 问题类型分布条形图")
        report.append("3. 金额分布箱线图")
        report.append("4. 风险得分热力图")
        report.append("请查看 output/risk_analysis.png 文件获取可视化分析结果。")
        report.append("")
        
        report.append("=" * 80)
        report.append("                                报告生成完毕")
        report.append("=" * 80)
        
        return "\n".join(report)

if __name__ == "__main__":
    # 读取测试数据
    import glob
    import os
    
    # 获取最新的测试数据文件
    latest_files = {}
    for file in glob.glob('output/compliance_test_*_*.csv'):
        # 使用正则表达式提取数据类型和时间戳
        match = re.search(r'compliance_test_(.+)_(\d{8}_\d{6})\.csv', file)
        if match:
            data_type = match.group(1)
            timestamp = match.group(2)
            if data_type not in latest_files or timestamp > latest_files[data_type][1]:
                latest_files[data_type] = (file, timestamp)
    
    # 读取数据
    test_data = {}
    for data_type, (file, _) in latest_files.items():
        test_data[data_type] = pd.read_csv(file)
        # 转换日期列
        date_columns = [col for col in test_data[data_type].columns if 'date' in col.lower()]
        for col in date_columns:
            test_data[data_type][col] = pd.to_datetime(test_data[data_type][col])
    
    # 执行合规检查
    checker = ComplianceChecker()
    results, report = checker.check_compliance(test_data)
    
    # 保存检查报告
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    report_file = f'reports/compliance_check_report_{timestamp}.txt'
    with open(report_file, 'w', encoding='utf-8') as f:
        f.write(report)
    
    print(f"合规检查完成，报告已保存至: {report_file}") 