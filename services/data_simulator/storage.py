"""
数据模拟服务的存储模块，负责数据持久化
"""
import json
import logging
from typing import Dict, List, Optional, Union
import os
import motor.motor_asyncio
from datetime import datetime
from bson import json_util

from services.data_simulator.models import (
    Transaction, 
    CostItem,
    SimulationResult,
    TimeRange,
    Merchant
)

class BaseStorage:
    """基础存储接口"""
    
    async def save_transactions(self, transactions: List[Transaction]) -> bool:
        """保存交易数据"""
        raise NotImplementedError
    
    async def save_costs(self, costs: List[CostItem]) -> bool:
        """保存成本数据"""
        raise NotImplementedError
    
    async def save_simulation_result(self, result: SimulationResult) -> str:
        """保存模拟结果"""
        raise NotImplementedError
    
    async def get_transactions(self, merchant_id: str, time_range: TimeRange) -> List[Transaction]:
        """获取交易数据"""
        raise NotImplementedError
    
    async def get_costs(self, merchant_id: str, time_range: TimeRange) -> List[CostItem]:
        """获取成本数据"""
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
        self.transactions_collection = self.db.transactions
        self.costs_collection = self.db.costs
        self.simulations_collection = self.db.simulations
        self.merchants_collection = self.db.merchants
        
        self.logger = logging.getLogger("data_simulator.storage")
    
    async def save_transactions(self, transactions: List[Transaction]) -> bool:
        """
        保存交易数据到MongoDB
        
        Args:
            transactions: 交易数据列表
            
        Returns:
            是否保存成功
        """
        if not transactions:
            return True
            
        try:
            # 将Pydantic模型转换为字典
            transactions_dict = [transaction.dict() for transaction in transactions]
            result = await self.transactions_collection.insert_many(transactions_dict)
            self.logger.info(f"Saved {len(result.inserted_ids)} transactions to MongoDB")
            return True
        except Exception as e:
            self.logger.error(f"Failed to save transactions to MongoDB: {e}")
            return False
    
    async def save_costs(self, costs: List[CostItem]) -> bool:
        """
        保存成本数据到MongoDB
        
        Args:
            costs: 成本数据列表
            
        Returns:
            是否保存成功
        """
        if not costs:
            return True
            
        try:
            # 将Pydantic模型转换为字典
            costs_dict = [cost.dict() for cost in costs]
            result = await self.costs_collection.insert_many(costs_dict)
            self.logger.info(f"Saved {len(result.inserted_ids)} cost items to MongoDB")
            return True
        except Exception as e:
            self.logger.error(f"Failed to save costs to MongoDB: {e}")
            return False
    
    async def save_simulation_result(self, result: SimulationResult) -> str:
        """
        保存模拟结果到MongoDB
        
        Args:
            result: 模拟结果
            
        Returns:
            模拟结果ID
        """
        try:
            # 转换为字典并移除大型列表（交易和成本），单独存储
            result_dict = result.dict()
            transactions = result_dict.pop("transactions")
            costs = result_dict.pop("costs")
            
            # 添加模拟结果的摘要统计信息
            result_dict["transaction_count"] = len(transactions)
            result_dict["cost_count"] = len(costs)
            result_dict["created_at"] = datetime.now()
            
            # 保存模拟结果
            insert_result = await self.simulations_collection.insert_one(result_dict)
            simulation_id = str(insert_result.inserted_id)
            
            # 保存交易和成本数据，带上模拟ID
            if transactions:
                for transaction in transactions:
                    transaction["simulation_id"] = simulation_id
                await self.transactions_collection.insert_many(transactions)
                
            if costs:
                for cost in costs:
                    cost["simulation_id"] = simulation_id
                await self.costs_collection.insert_many(costs)
                
            self.logger.info(f"Saved simulation result with ID: {simulation_id}")
            return simulation_id
        except Exception as e:
            self.logger.error(f"Failed to save simulation result to MongoDB: {e}")
            raise
    
    async def get_transactions(self, merchant_id: str, time_range: TimeRange) -> List[Transaction]:
        """
        根据商户ID和时间范围获取交易数据
        
        Args:
            merchant_id: 商户ID
            time_range: 时间范围
            
        Returns:
            交易数据列表
        """
        try:
            start_date = datetime.strptime(time_range.start_date, "%Y-%m-%d")
            end_date = datetime.strptime(time_range.end_date, "%Y-%m-%d").replace(hour=23, minute=59, second=59)
            
            query = {
                "merchant_id": merchant_id,
                "timestamp": {
                    "$gte": start_date,
                    "$lte": end_date
                }
            }
            
            cursor = self.transactions_collection.find(query)
            transactions = await cursor.to_list(length=None)
            return [Transaction(**transaction) for transaction in transactions]
        except Exception as e:
            self.logger.error(f"Failed to get transactions from MongoDB: {e}")
            return []
    
    async def get_costs(self, merchant_id: str, time_range: TimeRange) -> List[CostItem]:
        """
        根据商户ID和时间范围获取成本数据
        
        Args:
            merchant_id: 商户ID
            time_range: 时间范围
            
        Returns:
            成本数据列表
        """
        try:
            start_date = datetime.strptime(time_range.start_date, "%Y-%m-%d")
            end_date = datetime.strptime(time_range.end_date, "%Y-%m-%d").replace(hour=23, minute=59, second=59)
            
            query = {
                "merchant_id": merchant_id,
                "timestamp": {
                    "$gte": start_date,
                    "$lte": end_date
                }
            }
            
            cursor = self.costs_collection.find(query)
            costs = await cursor.to_list(length=None)
            return [CostItem(**cost) for cost in costs]
        except Exception as e:
            self.logger.error(f"Failed to get costs from MongoDB: {e}")
            return []
            
    async def save_merchant(self, merchant: Merchant) -> str:
        """
        保存商户信息到MongoDB
        
        Args:
            merchant: 商户信息
            
        Returns:
            商户ID
        """
        try:
            merchant_dict = merchant.dict()
            merchant_dict["created_at"] = datetime.now()
            merchant_dict["updated_at"] = datetime.now()
            
            # 检查是否已存在该商户
            existing = await self.merchants_collection.find_one({"merchant_id": merchant.merchant_id})
            if existing:
                # 更新已存在的商户
                merchant_dict["updated_at"] = datetime.now()
                await self.merchants_collection.update_one(
                    {"merchant_id": merchant.merchant_id},
                    {"$set": merchant_dict}
                )
                return merchant.merchant_id
            
            # 插入新商户
            result = await self.merchants_collection.insert_one(merchant_dict)
            self.logger.info(f"Saved merchant with ID: {merchant.merchant_id}")
            return merchant.merchant_id
        except Exception as e:
            self.logger.error(f"Failed to save merchant to MongoDB: {e}")
            raise
    
    async def get_merchant(self, merchant_id: str) -> Optional[Merchant]:
        """
        根据ID获取商户信息
        
        Args:
            merchant_id: 商户ID
            
        Returns:
            商户信息，如果不存在则返回None
        """
        try:
            result = await self.merchants_collection.find_one({"merchant_id": merchant_id})
            if result:
                # 移除MongoDB特定字段
                if "_id" in result:
                    del result["_id"]
                return Merchant(**result)
            return None
        except Exception as e:
            self.logger.error(f"Failed to get merchant from MongoDB: {e}")
            return None 