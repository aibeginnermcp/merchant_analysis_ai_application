"""
财务合规检查服务的存储模块，负责数据持久化
"""
import json
import logging
import os
import motor.motor_asyncio
from typing import Dict, List, Optional, Union, Any
from datetime import datetime
from bson import json_util, ObjectId

from services.compliance_checker.src.models import (
    TimeRange,
    ComplianceType,
    RiskLevel,
    ComplianceStatus,
    DocumentType,
    ComplianceRule,
    ComplianceViolation,
    ComplianceDocument,
    ComplianceCheckResult
)

class BaseStorage:
    """基础存储接口"""
    
    async def save_rule(self, rule: ComplianceRule) -> str:
        """保存规则"""
        raise NotImplementedError
    
    async def get_rule(self, rule_id: str) -> Optional[ComplianceRule]:
        """获取规则"""
        raise NotImplementedError
    
    async def get_rules_by_type(self, rule_type: ComplianceType) -> List[ComplianceRule]:
        """获取特定类型的规则"""
        raise NotImplementedError
    
    async def save_document(self, document: ComplianceDocument) -> str:
        """保存文档"""
        raise NotImplementedError
    
    async def get_document(self, document_id: str) -> Optional[ComplianceDocument]:
        """获取文档"""
        raise NotImplementedError
    
    async def get_merchant_documents(self, merchant_id: str) -> List[ComplianceDocument]:
        """获取商户的所有文档"""
        raise NotImplementedError
    
    async def save_check_result(self, result: ComplianceCheckResult) -> str:
        """保存检查结果"""
        raise NotImplementedError
    
    async def get_check_result(self, check_id: str) -> Optional[ComplianceCheckResult]:
        """获取检查结果"""
        raise NotImplementedError
    
    async def get_merchant_check_results(
        self, 
        merchant_id: str, 
        time_range: Optional[TimeRange] = None,
        limit: int = 10
    ) -> List[ComplianceCheckResult]:
        """获取商户的检查结果"""
        raise NotImplementedError


class MongoDBStorage(BaseStorage):
    """MongoDB存储实现"""
    
    def __init__(self, connection_string: Optional[str] = None):
        """
        初始化MongoDB存储
        
        Args:
            connection_string: MongoDB连接字符串，如果为None则从环境变量获取
        """
        if connection_string is None:
            connection_string = os.environ.get("MONGODB_URI", "mongodb://localhost:27017")
            
        self.client = motor.motor_asyncio.AsyncIOMotorClient(connection_string)
        self.db = self.client.merchant_analysis
        self.rules_collection = self.db.compliance_rules
        self.documents_collection = self.db.compliance_documents
        self.check_results_collection = self.db.compliance_check_results
        self.violations_collection = self.db.compliance_violations
        
        self.logger = logging.getLogger("compliance_checker.storage")
    
    async def save_rule(self, rule: ComplianceRule) -> str:
        """
        保存规则到MongoDB
        
        Args:
            rule: 合规规则
            
        Returns:
            规则ID
        """
        try:
            # 将Pydantic模型转换为字典
            rule_dict = rule.dict()
            
            # 检查是否已存在相同ID的规则
            existing = await self.rules_collection.find_one({"rule_id": rule.rule_id})
            
            if existing:
                # 更新已存在的规则
                rule_dict["updated_at"] = datetime.now()
                await self.rules_collection.update_one(
                    {"rule_id": rule.rule_id},
                    {"$set": rule_dict}
                )
                self.logger.info(f"Updated rule {rule.rule_id}")
                return rule.rule_id
            else:
                # 插入新规则
                rule_dict["created_at"] = datetime.now()
                result = await self.rules_collection.insert_one(rule_dict)
                self.logger.info(f"Saved rule with ID: {rule.rule_id}")
                return rule.rule_id
        except Exception as e:
            self.logger.error(f"Failed to save rule to MongoDB: {e}")
            raise
    
    async def get_rule(self, rule_id: str) -> Optional[ComplianceRule]:
        """
        获取规则
        
        Args:
            rule_id: 规则ID
            
        Returns:
            合规规则，如果不存在则返回None
        """
        try:
            result = await self.rules_collection.find_one({"rule_id": rule_id})
            if result:
                # 移除MongoDB特定字段
                if "_id" in result:
                    del result["_id"]
                return ComplianceRule(**result)
            return None
        except Exception as e:
            self.logger.error(f"Failed to get rule from MongoDB: {e}")
            return None
    
    async def get_rules_by_type(self, rule_type: ComplianceType) -> List[ComplianceRule]:
        """
        获取特定类型的规则
        
        Args:
            rule_type: 规则类型
            
        Returns:
            规则列表
        """
        try:
            cursor = self.rules_collection.find({"type": rule_type.value})
            rules = []
            async for doc in cursor:
                # 移除MongoDB特定字段
                if "_id" in doc:
                    del doc["_id"]
                rules.append(ComplianceRule(**doc))
            return rules
        except Exception as e:
            self.logger.error(f"Failed to get rules from MongoDB: {e}")
            return []
    
    async def save_document(self, document: ComplianceDocument) -> str:
        """
        保存文档到MongoDB
        
        Args:
            document: 合规文档
            
        Returns:
            文档ID
        """
        try:
            # 将Pydantic模型转换为字典
            document_dict = document.dict()
            
            # 检查是否已存在相同ID的文档
            existing = await self.documents_collection.find_one({"document_id": document.document_id})
            
            if existing:
                # 更新已存在的文档
                document_dict["updated_at"] = datetime.now()
                await self.documents_collection.update_one(
                    {"document_id": document.document_id},
                    {"$set": document_dict}
                )
                self.logger.info(f"Updated document {document.document_id}")
                return document.document_id
            else:
                # 插入新文档
                document_dict["created_at"] = datetime.now()
                result = await self.documents_collection.insert_one(document_dict)
                self.logger.info(f"Saved document with ID: {document.document_id}")
                return document.document_id
        except Exception as e:
            self.logger.error(f"Failed to save document to MongoDB: {e}")
            raise
    
    async def get_document(self, document_id: str) -> Optional[ComplianceDocument]:
        """
        获取文档
        
        Args:
            document_id: 文档ID
            
        Returns:
            合规文档，如果不存在则返回None
        """
        try:
            result = await self.documents_collection.find_one({"document_id": document_id})
            if result:
                # 移除MongoDB特定字段
                if "_id" in result:
                    del result["_id"]
                if "created_at" in result:
                    del result["created_at"]
                if "updated_at" in result:
                    del result["updated_at"]
                return ComplianceDocument(**result)
            return None
        except Exception as e:
            self.logger.error(f"Failed to get document from MongoDB: {e}")
            return None
    
    async def get_merchant_documents(self, merchant_id: str) -> List[ComplianceDocument]:
        """
        获取商户的所有文档
        
        Args:
            merchant_id: 商户ID
            
        Returns:
            文档列表
        """
        try:
            cursor = self.documents_collection.find({"merchant_id": merchant_id})
            documents = []
            async for doc in cursor:
                # 移除MongoDB特定字段
                if "_id" in doc:
                    del doc["_id"]
                if "created_at" in doc:
                    del doc["created_at"]
                if "updated_at" in doc:
                    del doc["updated_at"]
                documents.append(ComplianceDocument(**doc))
            return documents
        except Exception as e:
            self.logger.error(f"Failed to get merchant documents from MongoDB: {e}")
            return []
    
    async def save_check_result(self, result: ComplianceCheckResult) -> str:
        """
        保存检查结果到MongoDB
        
        Args:
            result: 检查结果
            
        Returns:
            检查ID
        """
        try:
            # 将Pydantic模型转换为字典
            result_dict = result.dict()
            
            # 将违规列表单独保存
            if result.violations:
                violation_dicts = []
                for violation in result.violations:
                    vio_dict = violation.dict()
                    vio_dict["check_id"] = result.check_id
                    violation_dicts.append(vio_dict)
                
                await self.violations_collection.insert_many(violation_dicts)
            
            # 保存检查结果
            result_dict["created_at"] = datetime.now()
            await self.check_results_collection.insert_one(result_dict)
            self.logger.info(f"Saved check result with ID: {result.check_id}")
            
            return result.check_id
        except Exception as e:
            self.logger.error(f"Failed to save check result to MongoDB: {e}")
            raise
    
    async def get_check_result(self, check_id: str) -> Optional[ComplianceCheckResult]:
        """
        获取检查结果
        
        Args:
            check_id: 检查ID
            
        Returns:
            检查结果，如果不存在则返回None
        """
        try:
            result = await self.check_results_collection.find_one({"check_id": check_id})
            if not result:
                return None
                
            # 移除MongoDB特定字段
            if "_id" in result:
                del result["_id"]
            if "created_at" in result:
                del result["created_at"]
                
            # 获取关联的违规列表
            violations_cursor = self.violations_collection.find({"check_id": check_id})
            violations = []
            async for vio in violations_cursor:
                if "_id" in vio:
                    del vio["_id"]
                if "check_id" in vio:
                    del vio["check_id"]
                violations.append(ComplianceViolation(**vio))
                
            # 更新违规列表
            result["violations"] = violations
            
            return ComplianceCheckResult(**result)
        except Exception as e:
            self.logger.error(f"Failed to get check result from MongoDB: {e}")
            return None
    
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
        try:
            # 构建查询条件
            query = {"merchant_id": merchant_id}
            if time_range:
                query["check_date"] = {
                    "$gte": datetime.strptime(time_range.start_date, "%Y-%m-%d"),
                    "$lte": datetime.strptime(time_range.end_date, "%Y-%m-%d").replace(hour=23, minute=59, second=59)
                }
            
            # 查询检查结果
            cursor = self.check_results_collection.find(query).sort("check_date", -1).limit(limit)
            results = []
            
            async for res in cursor:
                # 移除MongoDB特定字段
                if "_id" in res:
                    del res["_id"]
                if "created_at" in res:
                    del res["created_at"]
                
                # 获取关联的违规列表
                check_id = res["check_id"]
                violations_cursor = self.violations_collection.find({"check_id": check_id})
                violations = []
                
                async for vio in violations_cursor:
                    if "_id" in vio:
                        del vio["_id"]
                    if "check_id" in vio:
                        del vio["check_id"]
                    violations.append(ComplianceViolation(**vio))
                
                # 更新违规列表
                res["violations"] = violations
                
                results.append(ComplianceCheckResult(**res))
            
            return results
        except Exception as e:
            self.logger.error(f"Failed to get merchant check results from MongoDB: {e}")
            return [] 