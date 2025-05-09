"""
证据链追溯系统
用于记录和追踪审计证据
"""

import json
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime
from pathlib import Path
import hashlib
from dataclasses import dataclass, asdict
import networkx as nx
import matplotlib.pyplot as plt

@dataclass
class Evidence:
    """审计证据数据类"""
    id: str
    type: str
    source: str
    content: Any
    timestamp: datetime
    hash: str
    related_rule: str
    metadata: Dict

@dataclass
class EvidenceChain:
    """证据链数据类"""
    id: str
    evidences: List[Evidence]
    conclusion: str
    risk_level: str
    timestamp: datetime
    reviewer: str

class EvidenceTracer:
    """证据追溯器类"""
    
    def __init__(self, evidence_dir: str = "audit_evidence"):
        """
        初始化证据追溯器
        
        Args:
            evidence_dir: 证据存储目录
        """
        self.evidence_dir = Path(evidence_dir)
        self.evidence_dir.mkdir(parents=True, exist_ok=True)
        self.logger = self._setup_logger()
        self.evidence_graph = nx.DiGraph()
        
    def _setup_logger(self) -> logging.Logger:
        """设置日志记录器"""
        logger = logging.getLogger("EvidenceTracer")
        logger.setLevel(logging.INFO)
        
        # 创建控制台处理器
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        
        # 创建文件处理器
        file_handler = logging.FileHandler("logs/evidence_tracer.log")
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
    
    def create_evidence(
        self,
        evidence_type: str,
        source: str,
        content: Any,
        related_rule: str,
        metadata: Dict = None
    ) -> Evidence:
        """
        创建审计证据
        
        Args:
            evidence_type: 证据类型
            source: 证据来源
            content: 证据内容
            related_rule: 相关规则ID
            metadata: 元数据
            
        Returns:
            Evidence: 证据对象
        """
        # 生成证据ID和哈希值
        timestamp = datetime.now()
        content_str = json.dumps(content, sort_keys=True, default=str)
        evidence_hash = hashlib.sha256(content_str.encode()).hexdigest()
        evidence_id = f"E{timestamp.strftime('%Y%m%d%H%M%S')}"
        
        # 创建证据对象
        evidence = Evidence(
            id=evidence_id,
            type=evidence_type,
            source=source,
            content=content,
            timestamp=timestamp,
            hash=evidence_hash,
            related_rule=related_rule,
            metadata=metadata or {}
        )
        
        # 保存证据
        self._save_evidence(evidence)
        
        # 添加到证据图
        self.evidence_graph.add_node(
            evidence_id,
            evidence=asdict(evidence)
        )
        
        self.logger.info(f"创建证据: {evidence_id}")
        return evidence
    
    def create_evidence_chain(
        self,
        evidences: List[Evidence],
        conclusion: str,
        risk_level: str,
        reviewer: str
    ) -> EvidenceChain:
        """
        创建证据链
        
        Args:
            evidences: 证据列表
            conclusion: 结论
            risk_level: 风险等级
            reviewer: 审阅人
            
        Returns:
            EvidenceChain: 证据链对象
        """
        # 生成证据链ID
        timestamp = datetime.now()
        chain_id = f"C{timestamp.strftime('%Y%m%d%H%M%S')}"
        
        # 创建证据链对象
        chain = EvidenceChain(
            id=chain_id,
            evidences=evidences,
            conclusion=conclusion,
            risk_level=risk_level,
            timestamp=timestamp,
            reviewer=reviewer
        )
        
        # 保存证据链
        self._save_evidence_chain(chain)
        
        # 在证据图中添加关系
        for i in range(len(evidences)-1):
            self.evidence_graph.add_edge(
                evidences[i].id,
                evidences[i+1].id,
                chain_id=chain_id
            )
        
        self.logger.info(f"创建证据链: {chain_id}")
        return chain
    
    def _save_evidence(self, evidence: Evidence) -> None:
        """
        保存证据到文件系统
        
        Args:
            evidence: 证据对象
        """
        evidence_path = self.evidence_dir / f"{evidence.id}.json"
        with open(evidence_path, 'w', encoding='utf-8') as f:
            json.dump(asdict(evidence), f, ensure_ascii=False, indent=2, default=str)
    
    def _save_evidence_chain(self, chain: EvidenceChain) -> None:
        """
        保存证据链到文件系统
        
        Args:
            chain: 证据链对象
        """
        chain_path = self.evidence_dir / f"{chain.id}.json"
        with open(chain_path, 'w', encoding='utf-8') as f:
            json.dump(asdict(chain), f, ensure_ascii=False, indent=2, default=str)
    
    def get_evidence(self, evidence_id: str) -> Optional[Evidence]:
        """
        获取证据
        
        Args:
            evidence_id: 证据ID
            
        Returns:
            Optional[Evidence]: 证据对象或None
        """
        evidence_path = self.evidence_dir / f"{evidence_id}.json"
        if not evidence_path.exists():
            return None
        
        with open(evidence_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            data['timestamp'] = datetime.fromisoformat(data['timestamp'])
            return Evidence(**data)
    
    def get_evidence_chain(self, chain_id: str) -> Optional[EvidenceChain]:
        """
        获取证据链
        
        Args:
            chain_id: 证据链ID
            
        Returns:
            Optional[EvidenceChain]: 证据链对象或None
        """
        chain_path = self.evidence_dir / f"{chain_id}.json"
        if not chain_path.exists():
            return None
        
        with open(chain_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            data['timestamp'] = datetime.fromisoformat(data['timestamp'])
            # 加载证据对象
            evidences = []
            for evidence_data in data['evidences']:
                evidence_data['timestamp'] = datetime.fromisoformat(
                    evidence_data['timestamp']
                )
                evidences.append(Evidence(**evidence_data))
            data['evidences'] = evidences
            return EvidenceChain(**data)
    
    def visualize_evidence_chain(
        self,
        chain_id: str,
        save_path: str = None
    ) -> None:
        """
        可视化证据链
        
        Args:
            chain_id: 证据链ID
            save_path: 图片保存路径
        """
        chain = self.get_evidence_chain(chain_id)
        if not chain:
            self.logger.error(f"证据链不存在: {chain_id}")
            return
        
        # 创建子图
        subgraph = nx.DiGraph()
        
        # 添加节点和边
        for i, evidence in enumerate(chain.evidences):
            subgraph.add_node(
                evidence.id,
                evidence=asdict(evidence)
            )
            if i > 0:
                subgraph.add_edge(
                    chain.evidences[i-1].id,
                    evidence.id
                )
        
        # 设置绘图参数
        plt.figure(figsize=(12, 8))
        pos = nx.spring_layout(subgraph)
        
        # 绘制节点
        nx.draw_networkx_nodes(
            subgraph,
            pos,
            node_color='lightblue',
            node_size=2000
        )
        
        # 绘制边
        nx.draw_networkx_edges(
            subgraph,
            pos,
            edge_color='gray',
            arrows=True,
            arrowsize=20
        )
        
        # 添加标签
        labels = {
            node: f"{data['evidence']['type']}\n{data['evidence']['id']}"
            for node, data in subgraph.nodes(data=True)
        }
        nx.draw_networkx_labels(subgraph, pos, labels)
        
        # 添加标题
        plt.title(f"证据链 {chain_id}\n结论: {chain.conclusion}\n"
                 f"风险等级: {chain.risk_level}")
        
        # 保存或显示图片
        if save_path:
            plt.savefig(save_path, bbox_inches='tight')
            plt.close()
        else:
            plt.show()
    
    def search_evidence(
        self,
        criteria: Dict[str, Any]
    ) -> List[Evidence]:
        """
        搜索证据
        
        Args:
            criteria: 搜索条件
            
        Returns:
            List[Evidence]: 符合条件的证据列表
        """
        results = []
        
        for evidence_file in self.evidence_dir.glob("E*.json"):
            with open(evidence_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                match = True
                
                for key, value in criteria.items():
                    if key not in data or data[key] != value:
                        match = False
                        break
                
                if match:
                    data['timestamp'] = datetime.fromisoformat(data['timestamp'])
                    results.append(Evidence(**data))
        
        return results
    
    def verify_evidence_integrity(self, evidence_id: str) -> bool:
        """
        验证证据完整性
        
        Args:
            evidence_id: 证据ID
            
        Returns:
            bool: 完整性验证结果
        """
        evidence = self.get_evidence(evidence_id)
        if not evidence:
            return False
        
        # 重新计算哈希值
        content_str = json.dumps(evidence.content, sort_keys=True, default=str)
        current_hash = hashlib.sha256(content_str.encode()).hexdigest()
        
        # 比较哈希值
        return current_hash == evidence.hash

if __name__ == "__main__":
    # 测试证据追溯系统
    tracer = EvidenceTracer()
    
    # 创建测试证据
    evidence1 = tracer.create_evidence(
        evidence_type="交易记录",
        source="财务系统",
        content={
            "transaction_id": "T20240301001",
            "amount": 100000,
            "date": "2024-03-01"
        },
        related_rule="rule_101",
        metadata={"department": "销售部"}
    )
    
    evidence2 = tracer.create_evidence(
        evidence_type="审批记录",
        source="OA系统",
        content={
            "approval_id": "A20240301001",
            "status": "已拒绝",
            "reason": "超出审批权限"
        },
        related_rule="rule_101",
        metadata={"approver": "张三"}
    )
    
    # 创建证据链
    chain = tracer.create_evidence_chain(
        evidences=[evidence1, evidence2],
        conclusion="发现未经授权的大额支出",
        risk_level="高风险",
        reviewer="李四"
    )
    
    # 可视化证据链
    tracer.visualize_evidence_chain(
        chain.id,
        save_path="output/evidence_chain.png"
    )
    
    # 验证证据完整性
    print(f"证据完整性验证结果: {tracer.verify_evidence_integrity(evidence1.id)}")
    
    # 搜索证据
    results = tracer.search_evidence({"type": "交易记录"})
    print(f"找到 {len(results)} 条交易记录证据") 