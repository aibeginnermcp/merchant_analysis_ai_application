"""
智能财务哨兵系统单元测试
"""

import unittest
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from pathlib import Path
import shutil
import json

from main import FinancialSentinel
from rule_engine.rule_loader import RuleLoader
from rule_engine.evidence_tracer import EvidenceTracer, Evidence, EvidenceChain
from compliance_checker import ComplianceChecker

class TestFinancialSentinel(unittest.TestCase):
    """智能财务哨兵系统测试类"""
    
    @classmethod
    def setUpClass(cls):
        """测试类初始化"""
        # 创建测试目录
        cls.test_dirs = [
            'test_logs',
            'test_output',
            'test_audit_rules',
            'test_audit_evidence',
            'test_reports'
        ]
        for directory in cls.test_dirs:
            Path(directory).mkdir(parents=True, exist_ok=True)
        
        # 复制规则文件到测试目录
        shutil.copy(
            'audit_rules/financial_rules.yaml',
            'test_audit_rules/financial_rules.yaml'
        )
    
    @classmethod
    def tearDownClass(cls):
        """测试类清理"""
        # 删除测试目录
        for directory in cls.test_dirs:
            shutil.rmtree(directory, ignore_errors=True)
    
    def setUp(self):
        """每个测试用例初始化"""
        self.sentinel = FinancialSentinel()
        self.test_data = self._generate_test_data()
    
    def _generate_test_data(self) -> dict:
        """生成测试数据"""
        # 生成交易数据
        transactions = pd.DataFrame({
            'transaction_id': [f'T{i:06d}' for i in range(10)],
            'amount': np.random.uniform(1000, 500000, 10),
            'date': [
                datetime.now() - timedelta(days=i)
                for i in range(10)
            ],
            'type': np.random.choice(
                ['销售', '采购', '费用报销', '工资'], 10
            )
        })
        
        # 生成费用数据
        expenses = pd.DataFrame({
            'expense_id': [f'E{i:06d}' for i in range(10)],
            'amount': np.random.uniform(1000, 50000, 10),
            'type': np.random.choice(
                ['差旅', '办公', '业务招待'], 10
            ),
            'has_invoice': np.random.choice([True, False], 10, p=[0.8, 0.2])
        })
        
        # 生成关联交易数据
        related_party = pd.DataFrame({
            'transaction_id': [f'R{i:06d}' for i in range(10)],
            'amount': np.random.uniform(10000, 1000000, 10),
            'related_party': [f'关联方{i}' for i in range(10)],
            'disclosure_status': np.random.choice(
                ['已披露', '未披露'], 10, p=[0.7, 0.3]
            )
        })
        
        return {
            'transactions': transactions,
            'expenses': expenses,
            'related_party': related_party
        }
    
    def test_system_initialization(self):
        """测试系统初始化"""
        # 验证系统组件初始化
        self.assertIsInstance(self.sentinel.rule_loader, RuleLoader)
        self.assertIsInstance(self.sentinel.evidence_tracer, EvidenceTracer)
        self.assertIsInstance(self.sentinel.compliance_checker, ComplianceChecker)
        
        # 验证规则加载
        self.assertGreater(len(self.sentinel.rules), 0)
        
        # 验证目录创建
        directories = [
            'logs',
            'output',
            'audit_rules',
            'audit_evidence',
            'reports'
        ]
        for directory in directories:
            self.assertTrue(Path(directory).exists())
    
    def test_rule_statistics(self):
        """测试规则统计"""
        stats = self.sentinel.get_rule_statistics()
        
        # 验证统计结果
        self.assertIn('total_rules', stats)
        self.assertIn('high_severity', stats)
        self.assertIn('medium_severity', stats)
        self.assertIn('low_severity', stats)
        
        # 验证数量关系
        self.assertEqual(
            stats['total_rules'],
            stats['high_severity'] + stats['medium_severity'] + stats['low_severity']
        )
    
    def test_compliance_check(self):
        """测试合规检查"""
        # 执行合规检查
        results = self.sentinel.run_compliance_check(self.test_data)
        
        # 验证结果格式
        self.assertIsInstance(results, dict)
        self.assertTrue(all(isinstance(issues, list) for issues in results.values()))
        
        # 验证问题记录
        for issue_type, issues in results.items():
            for issue in issues:
                self.assertIn('type', issue)
                self.assertIn('severity', issue)
    
    def test_evidence_creation(self):
        """测试证据创建"""
        # 创建测试证据
        evidence = self.sentinel.evidence_tracer.create_evidence(
            evidence_type="测试证据",
            source="测试系统",
            content={"test": "data"},
            related_rule="test_rule",
            metadata={"test": "metadata"}
        )
        
        # 验证证据对象
        self.assertIsInstance(evidence, Evidence)
        self.assertTrue(evidence.id.startswith('E'))
        self.assertEqual(evidence.type, "测试证据")
        
        # 验证证据文件
        evidence_file = Path(f"audit_evidence/{evidence.id}.json")
        self.assertTrue(evidence_file.exists())
        
        # 验证证据内容
        with open(evidence_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
            self.assertEqual(data['type'], "测试证据")
            self.assertEqual(data['content'], {"test": "data"})
    
    def test_evidence_chain(self):
        """测试证据链"""
        # 创建测试证据
        evidence1 = self.sentinel.evidence_tracer.create_evidence(
            evidence_type="测试证据1",
            source="测试系统",
            content={"test": "data1"},
            related_rule="test_rule"
        )
        
        evidence2 = self.sentinel.evidence_tracer.create_evidence(
            evidence_type="测试证据2",
            source="测试系统",
            content={"test": "data2"},
            related_rule="test_rule"
        )
        
        # 创建证据链
        chain = self.sentinel.evidence_tracer.create_evidence_chain(
            evidences=[evidence1, evidence2],
            conclusion="测试结论",
            risk_level="高风险",
            reviewer="测试人员"
        )
        
        # 验证证据链对象
        self.assertIsInstance(chain, EvidenceChain)
        self.assertTrue(chain.id.startswith('C'))
        self.assertEqual(len(chain.evidences), 2)
        
        # 验证证据链文件
        chain_file = Path(f"audit_evidence/{chain.id}.json")
        self.assertTrue(chain_file.exists())
        
        # 验证证据链内容
        with open(chain_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
            self.assertEqual(data['conclusion'], "测试结论")
            self.assertEqual(data['risk_level'], "高风险")
    
    def test_evidence_integrity(self):
        """测试证据完整性"""
        # 创建测试证据
        evidence = self.sentinel.evidence_tracer.create_evidence(
            evidence_type="测试证据",
            source="测试系统",
            content={"test": "data"},
            related_rule="test_rule"
        )
        
        # 验证完整性
        self.assertTrue(
            self.sentinel.evidence_tracer.verify_evidence_integrity(evidence.id)
        )
        
        # 修改证据内容
        evidence_file = Path(f"audit_evidence/{evidence.id}.json")
        with open(evidence_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        data['content']['test'] = "modified"
        
        with open(evidence_file, 'w', encoding='utf-8') as f:
            json.dump(data, f)
        
        # 验证完整性检查失败
        self.assertFalse(
            self.sentinel.evidence_tracer.verify_evidence_integrity(evidence.id)
        )
    
    def test_evidence_search(self):
        """测试证据搜索"""
        # 创建多个测试证据
        for i in range(5):
            self.sentinel.evidence_tracer.create_evidence(
                evidence_type="类型A" if i < 3 else "类型B",
                source="测试系统",
                content={"index": i},
                related_rule="test_rule"
            )
        
        # 搜索类型A的证据
        results = self.sentinel.evidence_tracer.search_evidence({"type": "类型A"})
        self.assertEqual(len(results), 3)
        
        # 搜索类型B的证据
        results = self.sentinel.evidence_tracer.search_evidence({"type": "类型B"})
        self.assertEqual(len(results), 2)

if __name__ == '__main__':
    unittest.main() 