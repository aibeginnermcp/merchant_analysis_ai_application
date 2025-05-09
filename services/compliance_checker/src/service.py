"""
财务合规检查服务的服务类，提供合规检查API接口
"""
import logging
import uuid
from typing import Dict, List, Optional, Union, Any
from datetime import datetime, timedelta

from services.compliance_checker.src.models import (
    TimeRange,
    ComplianceType,
    RiskLevel,
    ComplianceStatus,
    DocumentType,
    ComplianceRule,
    ComplianceViolation,
    ComplianceDocument,
    ComplianceCheckResult,
    ComplianceCheckRequest
)
from services.compliance_checker.src.checker import ComplianceChecker
from services.compliance_checker.src.storage import MongoDBStorage, BaseStorage

class ComplianceCheckerService:
    """合规检查服务类"""
    
    def __init__(self, storage: Optional[BaseStorage] = None):
        """
        初始化服务
        
        Args:
            storage: 数据存储实例，如果为None则创建默认的MongoDB存储
        """
        self.logger = logging.getLogger("compliance_checker.service")
        self.storage = storage or MongoDBStorage()
        self.checker = ComplianceChecker()
        self._load_rules()
    
    async def _load_rules(self) -> None:
        """加载规则并注册到检查器"""
        # 这里应该从数据库加载所有规则并注册到检查器
        # 在实际实现中，需要修改为从数据库加载
        # 这里为了示例，手动创建一些规则
        
        tax_rule = ComplianceRule(
            rule_id="tax_rule_001",
            type=ComplianceType.TAX,
            name="交易税务申报检查",
            description="检查是否有未申报的交易",
            applies_to=["retail", "restaurant", "service"],
            threshold={"unreported_amount": 10000, "tax_rate": 0.13},
            check_frequency="monthly",
            data_requirements=["transactions", "tax_records"],
            created_at=datetime.now()
        )
        
        accounting_rule = ComplianceRule(
            rule_id="accounting_rule_001",
            type=ComplianceType.ACCOUNTING,
            name="会计准则合规检查",
            description="检查是否符合会计准则",
            applies_to=["retail", "restaurant", "service", "manufacture"],
            threshold={"unclassified_amount": 5000, "balance_threshold": 0.01},
            check_frequency="monthly",
            data_requirements=["transactions"],
            created_at=datetime.now()
        )
        
        licensing_rule = ComplianceRule(
            rule_id="licensing_rule_001",
            type=ComplianceType.LICENSING,
            name="许可证有效性检查",
            description="检查必要的许可证是否有效",
            applies_to=["retail", "restaurant", "service", "manufacture"],
            threshold={
                "required_license_types": ["business", "health", "fire_safety"],
                "expiry_warning_days": 30
            },
            check_frequency="monthly",
            data_requirements=["documents"],
            created_at=datetime.now()
        )
        
        # 保存规则到数据库
        await self.storage.save_rule(tax_rule)
        await self.storage.save_rule(accounting_rule)
        await self.storage.save_rule(licensing_rule)
        
        # 注册规则到检查器
        self.checker.register_rule(tax_rule)
        self.checker.register_rule(accounting_rule)
        self.checker.register_rule(licensing_rule)
    
    async def prepare_merchant_data(self, merchant_id: str, time_range: TimeRange) -> Dict[str, Any]:
        """
        准备商户数据，从数据模拟服务获取
        
        Args:
            merchant_id: 商户ID
            time_range: 时间范围
            
        Returns:
            商户数据
        """
        # 在实际实现中，应该从数据模拟服务获取数据
        # 这里为了示例，生成一些模拟数据
        self.logger.info(f"Preparing data for merchant {merchant_id}")
        
        # 生成一些模拟交易
        transactions = []
        for i in range(50):
            transaction_id = f"tx_{uuid.uuid4().hex[:8]}"
            transactions.append({
                "transaction_id": transaction_id,
                "merchant_id": merchant_id,
                "amount": 100 + i * 10,
                "date": datetime.now() - timedelta(days=i),
                "category": "sales" if i % 3 != 0 else None,
                "type": "debit" if i % 2 == 0 else "credit"
            })
        
        # 生成一些模拟税务记录
        tax_records = []
        for i, tx in enumerate(transactions):
            if i % 4 != 0:  # 25%的交易没有税务记录
                tax_records.append({
                    "record_id": f"tr_{uuid.uuid4().hex[:8]}",
                    "transaction_id": tx["transaction_id"],
                    "transaction_amount": tx["amount"],
                    "tax_amount": tx["amount"] * 0.13,  # 13%的税率
                    "date": tx["date"]
                })
        
        return {
            "merchant_id": merchant_id,
            "transactions": transactions,
            "tax_records": tax_records
        }
    
    async def create_document(
        self,
        merchant_id: str,
        type: DocumentType,
        name: str,
        issue_date: datetime,
        expiry_date: Optional[datetime] = None,
        issuing_authority: str = "监管机构",
        document_number: Optional[str] = None,
        status: str = "valid",
        file_path: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> ComplianceDocument:
        """
        创建新的合规文档
        
        Args:
            merchant_id: 商户ID
            type: 文档类型
            name: 文档名称
            issue_date: 签发日期
            expiry_date: 过期日期
            issuing_authority: 签发机构
            document_number: 文档编号
            status: 状态
            file_path: 文件路径
            metadata: 元数据
            
        Returns:
            创建的文档
        """
        document = ComplianceDocument(
            document_id=f"doc_{uuid.uuid4().hex[:8]}",
            merchant_id=merchant_id,
            type=type,
            name=name,
            issue_date=issue_date,
            expiry_date=expiry_date,
            issuing_authority=issuing_authority,
            document_number=document_number or f"DN{uuid.uuid4().hex[:6].upper()}",
            status=status,
            file_path=file_path,
            metadata=metadata or {}
        )
        
        # 保存到数据库
        await self.storage.save_document(document)
        self.logger.info(f"Created document {document.document_id} for merchant {merchant_id}")
        
        return document
    
    async def get_merchant_documents(self, merchant_id: str) -> List[ComplianceDocument]:
        """
        获取商户的所有文档
        
        Args:
            merchant_id: 商户ID
            
        Returns:
            文档列表
        """
        return await self.storage.get_merchant_documents(merchant_id)
    
    async def check_compliance(self, request: ComplianceCheckRequest) -> ComplianceCheckResult:
        """
        执行合规检查
        
        Args:
            request: 合规检查请求
            
        Returns:
            检查结果
        """
        self.logger.info(f"Checking compliance for merchant {request.merchant_id}")
        
        # 获取商户数据
        data = await self.prepare_merchant_data(request.merchant_id, request.time_range)
        
        # 获取商户文档
        documents = await self.get_merchant_documents(request.merchant_id)
        
        # 如果没有文档，创建一些示例文档
        if not documents:
            documents = await self._create_sample_documents(request.merchant_id)
        
        # 执行合规检查
        result = self.checker.check_compliance(
            merchant_id=request.merchant_id,
            merchant_type="retail",  # 假设为零售商户
            time_range=request.time_range,
            data=data,
            documents=documents,
            check_types=request.check_types
        )
        
        # 保存检查结果
        await self.storage.save_check_result(result)
        
        return result
    
    async def get_check_result(self, check_id: str) -> Optional[ComplianceCheckResult]:
        """
        获取检查结果
        
        Args:
            check_id: 检查ID
            
        Returns:
            检查结果，如果不存在则返回None
        """
        return await self.storage.get_check_result(check_id)
    
    async def get_merchant_check_results(
        self, 
        merchant_id: str, 
        time_range: Optional[TimeRange] = None,
        limit: int = 10
    ) -> List[ComplianceCheckResult]:
        """
        获取商户的检查结果
        
        Args:
            merchant_id: 商户ID
            time_range: 时间范围，可选
            limit: 返回结果数量限制
            
        Returns:
            检查结果列表
        """
        return await self.storage.get_merchant_check_results(merchant_id, time_range, limit)
    
    async def _create_sample_documents(self, merchant_id: str) -> List[ComplianceDocument]:
        """
        为演示创建示例文档
        
        Args:
            merchant_id: 商户ID
            
        Returns:
            创建的文档列表
        """
        now = datetime.now()
        documents = []
        
        # 营业执照
        business_license = await self.create_document(
            merchant_id=merchant_id,
            type=DocumentType.LICENSE,
            name="营业执照",
            issue_date=now - timedelta(days=365),
            expiry_date=now + timedelta(days=365),
            issuing_authority="市场监督管理局",
            document_number="L123456789",
            status="valid"
        )
        documents.append(business_license)
        
        # 卫生许可证
        health_cert = await self.create_document(
            merchant_id=merchant_id,
            type=DocumentType.CERTIFICATE,
            name="卫生许可证",
            issue_date=now - timedelta(days=180),
            expiry_date=now + timedelta(days=180),
            issuing_authority="卫生健康委员会",
            document_number="H987654321",
            status="valid"
        )
        documents.append(health_cert)
        
        # 税务登记证
        tax_cert = await self.create_document(
            merchant_id=merchant_id,
            type=DocumentType.CERTIFICATE,
            name="税务登记证",
            issue_date=now - timedelta(days=730),
            expiry_date=now - timedelta(days=30),  # 已过期
            issuing_authority="税务局",
            document_number="T567891234",
            status="expired"
        )
        documents.append(tax_cert)
        
        return documents 