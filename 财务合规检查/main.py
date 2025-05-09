"""
智能财务哨兵系统
主程序入口
"""

import logging
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
import pandas as pd
import numpy as np

from rule_engine.rule_loader import RuleLoader
from rule_engine.evidence_tracer import EvidenceTracer
from compliance_checker import ComplianceChecker
from report_generator.report_generator import ReportGenerator

class FinancialSentinel:
    """智能财务哨兵系统"""
    
    def __init__(self):
        """初始化系统"""
        # 创建必要的目录
        self._create_directories()
        
        # 初始化日志
        self.logger = self._setup_logger()
        
        # 初始化组件
        self.rule_loader = RuleLoader()
        self.evidence_tracer = EvidenceTracer()
        self.compliance_checker = ComplianceChecker()
        self.report_generator = ReportGenerator()
        
        # 加载规则
        self.rules = self.rule_loader.load_rules()
        
        self.logger.info("智能财务哨兵系统初始化完成")
    
    def _create_directories(self) -> None:
        """创建必要的目录"""
        directories = [
            'logs',
            'output',
            'audit_rules',
            'audit_evidence',
            'reports'
        ]
        
        for directory in directories:
            Path(directory).mkdir(parents=True, exist_ok=True)
    
    def _setup_logger(self) -> logging.Logger:
        """设置日志记录器"""
        logger = logging.getLogger("FinancialSentinel")
        logger.setLevel(logging.INFO)
        
        # 创建控制台处理器
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        
        # 创建文件处理器
        file_handler = logging.FileHandler("logs/financial_sentinel.log")
        file_handler.setLevel(logging.INFO)
        
        # 创建格式化器
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        console_handler.setFormatter(formatter)
        file_handler.setFormatter(formatter)
        
        # 添加处理器到日志记录器
        logger.addHandler(console_handler)
        logger.addHandler(file_handler)
        
        return logger
    
    def run_compliance_check(
        self,
        data: Dict[str, pd.DataFrame],
        check_types: Optional[List[str]] = None
    ) -> Dict:
        """
        执行合规检查
        
        Args:
            data: 待检查的数据
            check_types: 要执行的检查类型列表，为None时执行所有检查
            
        Returns:
            Dict: 检查结果
        """
        try:
            self.logger.info("开始执行合规检查")
            
            # 执行合规检查
            results = self.compliance_checker.check_compliance(data)
            
            # 获取历史数据
            historical_data = self._get_historical_data()
            
            # 获取部门维度数据
            department_data = self._get_department_data(results)
            
            # 生成报告
            report_file = self.report_generator.generate_report(
                results,
                historical_data,
                department_data
            )
            
            # 记录检查结果
            self._record_check_results(results)
            
            self.logger.info(f"合规检查完成，报告已生成: {report_file}")
            return results
            
        except Exception as e:
            self.logger.error(f"执行合规检查时发生错误: {str(e)}")
            raise
    
    def _get_historical_data(self) -> List[Dict]:
        """获取历史检查数据"""
        # 这里应该从数据库或其他存储中获取历史数据
        # 示例数据
        return [
            {
                'date': datetime.now() - timedelta(days=i),
                'high_risk_count': np.random.randint(0, 5),
                'medium_risk_count': np.random.randint(3, 8),
                'low_risk_count': np.random.randint(5, 15)
            }
            for i in range(30)
        ]
        
    def _get_department_data(self, results: Dict) -> Dict:
        """获取部门维度的统计数据"""
        department_stats = {}
        
        # 统计各部门的问题数量
        for severity, issues in results.items():
            for issue in issues:
                dept = issue.get('department', '未知部门')
                if dept not in department_stats:
                    department_stats[dept] = {
                        'high': 0,
                        'medium': 0,
                        'low': 0
                    }
                department_stats[dept][severity] += 1
                
        return department_stats
    
    def _record_check_results(self, results: Dict) -> None:
        """
        记录检查结果
        
        Args:
            results: 检查结果
        """
        try:
            # 遍历所有问题
            for issue_type, issues in results.items():
                for issue in issues:
                    # 创建证据
                    evidence = self.evidence_tracer.create_evidence(
                        evidence_type=issue['type'],
                        source="合规检查系统",
                        content=issue,
                        related_rule=issue.get('rule_id', 'unknown'),
                        metadata={
                            'severity': issue['severity'],
                            'check_time': datetime.now().isoformat()
                        }
                    )
                    
                    # 如果是高风险问题，创建证据链
                    if issue['severity'] in ['high', 'critical']:
                        self.evidence_tracer.create_evidence_chain(
                            evidences=[evidence],
                            conclusion=issue.get('description', '发现高风险合规问题'),
                            risk_level=issue['severity'],
                            reviewer="系统自动检查"
                        )
            
        except Exception as e:
            self.logger.error(f"记录检查结果时发生错误: {str(e)}")
            raise
    
    def get_rule_statistics(self) -> Dict[str, int]:
        """
        获取规则统计信息
        
        Returns:
            Dict[str, int]: 规则统计信息
        """
        stats = {
            'total_rules': 0,
            'high_severity': 0,
            'medium_severity': 0,
            'low_severity': 0
        }
        
        # 统计规则数量
        for rule_file in self.rules.values():
            for rule_group in rule_file.values():
                stats['total_rules'] += len(rule_group)
                for rule in rule_group.values():
                    severity = rule['severity'].lower()
                    if severity in ['high', 'critical']:
                        stats['high_severity'] += 1
                    elif severity == 'medium':
                        stats['medium_severity'] += 1
                    else:
                        stats['low_severity'] += 1
        
        return stats
    
    def get_evidence_statistics(self) -> Dict[str, int]:
        """
        获取证据统计信息
        
        Returns:
            Dict[str, int]: 证据统计信息
        """
        stats = {
            'total_evidences': 0,
            'total_chains': 0,
            'high_risk_evidences': 0
        }
        
        # 统计证据数量
        evidence_files = list(Path('audit_evidence').glob('E*.json'))
        chain_files = list(Path('audit_evidence').glob('C*.json'))
        
        stats['total_evidences'] = len(evidence_files)
        stats['total_chains'] = len(chain_files)
        
        # 统计高风险证据
        high_risk = self.evidence_tracer.search_evidence({
            'metadata.severity': 'high'
        })
        stats['high_risk_evidences'] = len(high_risk)
        
        return stats

if __name__ == "__main__":
    # 初始化系统
    sentinel = FinancialSentinel()
    
    # 打印系统状态
    rule_stats = sentinel.get_rule_statistics()
    print("\n规则统计信息:")
    print(f"总规则数: {rule_stats['total_rules']}")
    print(f"高风险规则: {rule_stats['high_severity']}")
    print(f"中风险规则: {rule_stats['medium_severity']}")
    print(f"低风险规则: {rule_stats['low_severity']}")
    
    # 加载测试数据
    from test_compliance_data import ComplianceTestDataGenerator
    test_data = ComplianceTestDataGenerator().generate_test_data(1000)
    
    # 执行合规检查
    results = sentinel.run_compliance_check(test_data)
    
    # 打印检查结果统计
    total_issues = sum(len(issues) for issues in results.values())
    print(f"\n检查完成，共发现 {total_issues} 个问题")
    
    # 打印证据统计
    evidence_stats = sentinel.get_evidence_statistics()
    print("\n证据统计信息:")
    print(f"总证据数: {evidence_stats['total_evidences']}")
    print(f"证据链数: {evidence_stats['total_chains']}")
    print(f"高风险证据: {evidence_stats['high_risk_evidences']}") 