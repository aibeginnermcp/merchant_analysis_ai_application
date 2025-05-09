"""
现金流预测服务的存储模块，负责数据持久化
"""
import json
import logging
import os
import motor.motor_asyncio
from typing import Dict, List, Optional, Union, Any
from datetime import datetime
from bson import json_util, ObjectId

from services.cashflow_predictor.models import (
    TimeSeriesData,
    CashflowData,
    PredictionConfig,
    PredictionResult,
    CashflowAnalysis,
    TimeRange
)

class BaseStorage:
    """基础存储接口"""
    
    async def save_cashflow_data(self, data: CashflowData) -> str:
        """保存现金流数据"""
        raise NotImplementedError
    
    async def get_cashflow_data(self, merchant_id: str, time_range: TimeRange) -> Optional[CashflowData]:
        """获取现金流数据"""
        raise NotImplementedError
    
    async def save_prediction(self, prediction: PredictionResult) -> str:
        """保存预测结果"""
        raise NotImplementedError
    
    async def get_prediction(self, prediction_id: str) -> Optional[PredictionResult]:
        """获取预测结果"""
        raise NotImplementedError
    
    async def get_latest_prediction(self, merchant_id: str) -> Optional[PredictionResult]:
        """获取最新预测结果"""
        raise NotImplementedError
    
    async def save_cashflow_analysis(self, analysis: CashflowAnalysis) -> str:
        """保存现金流分析"""
        raise NotImplementedError
    
    async def get_cashflow_analysis(self, merchant_id: str, time_range: TimeRange) -> Optional[CashflowAnalysis]:
        """获取现金流分析"""
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
        self.cashflow_collection = self.db.cashflow_data
        self.prediction_collection = self.db.cashflow_predictions
        self.analysis_collection = self.db.cashflow_analysis
        
        self.logger = logging.getLogger("cashflow_predictor.storage")
    
    async def save_cashflow_data(self, data: CashflowData) -> str:
        """
        保存现金流数据到MongoDB
        
        Args:
            data: 现金流数据
            
        Returns:
            数据ID
        """
        try:
            # 将Pydantic模型转换为字典
            data_dict = data.dict()
            data_dict["created_at"] = datetime.now()
            
            # 检查是否已存在相同时间范围和商户的数据
            existing = await self.cashflow_collection.find_one({
                "merchant_id": data.merchant_id,
                "time_range.start_date": data.time_range.start_date,
                "time_range.end_date": data.time_range.end_date
            })
            
            if existing:
                # 更新已存在的数据
                result = await self.cashflow_collection.update_one(
                    {"_id": existing["_id"]},
                    {"$set": {
                        "data": data_dict["data"],
                        "metadata": data_dict["metadata"],
                        "updated_at": datetime.now()
                    }}
                )
                self.logger.info(f"Updated cashflow data for merchant {data.merchant_id}")
                return str(existing["_id"])
            else:
                # 插入新数据
                result = await self.cashflow_collection.insert_one(data_dict)
                self.logger.info(f"Saved cashflow data for merchant {data.merchant_id} with ID: {result.inserted_id}")
                return str(result.inserted_id)
        except Exception as e:
            self.logger.error(f"Failed to save cashflow data to MongoDB: {e}")
            raise
    
    async def get_cashflow_data(self, merchant_id: str, time_range: TimeRange) -> Optional[CashflowData]:
        """
        获取现金流数据
        
        Args:
            merchant_id: 商户ID
            time_range: 时间范围
            
        Returns:
            现金流数据，如果不存在则返回None
        """
        try:
            # 查询条件
            query = {
                "merchant_id": merchant_id,
                "time_range.start_date": time_range.start_date,
                "time_range.end_date": time_range.end_date
            }
            
            # 查询数据
            result = await self.cashflow_collection.find_one(query)
            
            if result:
                # 移除MongoDB特定字段
                if "_id" in result:
                    result["id"] = str(result.pop("_id"))
                if "created_at" in result:
                    del result["created_at"]
                if "updated_at" in result:
                    del result["updated_at"]
                
                return CashflowData(**result)
            
            return None
        except Exception as e:
            self.logger.error(f"Failed to get cashflow data from MongoDB: {e}")
            return None
    
    async def save_prediction(self, prediction: PredictionResult) -> str:
        """
        保存预测结果到MongoDB
        
        Args:
            prediction: 预测结果
            
        Returns:
            预测ID
        """
        try:
            # 将Pydantic模型转换为字典
            prediction_dict = prediction.dict()
            
            # 添加预测ID和创建时间
            if not prediction_dict.get("metadata"):
                prediction_dict["metadata"] = {}
                
            if not prediction_dict["metadata"].get("prediction_id"):
                prediction_dict["metadata"]["prediction_id"] = f"pred_{ObjectId()}"
                
            prediction_id = prediction_dict["metadata"]["prediction_id"]
            
            # 插入预测结果
            result = await self.prediction_collection.insert_one(prediction_dict)
            self.logger.info(f"Saved prediction for merchant {prediction.merchant_id} with ID: {prediction_id}")
            
            return prediction_id
        except Exception as e:
            self.logger.error(f"Failed to save prediction to MongoDB: {e}")
            raise
    
    async def get_prediction(self, prediction_id: str) -> Optional[PredictionResult]:
        """
        获取预测结果
        
        Args:
            prediction_id: 预测ID
            
        Returns:
            预测结果，如果不存在则返回None
        """
        try:
            # 查询条件
            query = {"metadata.prediction_id": prediction_id}
            
            # 查询数据
            result = await self.prediction_collection.find_one(query)
            
            if result:
                # 移除MongoDB特定字段
                if "_id" in result:
                    result["id"] = str(result.pop("_id"))
                
                return PredictionResult(**result)
            
            return None
        except Exception as e:
            self.logger.error(f"Failed to get prediction from MongoDB: {e}")
            return None
    
    async def get_latest_prediction(self, merchant_id: str) -> Optional[PredictionResult]:
        """
        获取最新预测结果
        
        Args:
            merchant_id: 商户ID
            
        Returns:
            最新预测结果，如果不存在则返回None
        """
        try:
            # 查询条件
            query = {"merchant_id": merchant_id}
            
            # 按创建时间倒序排序，取最新一条
            result = await self.prediction_collection.find_one(
                query,
                sort=[("created_at", -1)]
            )
            
            if result:
                # 移除MongoDB特定字段
                if "_id" in result:
                    result["id"] = str(result.pop("_id"))
                
                return PredictionResult(**result)
            
            return None
        except Exception as e:
            self.logger.error(f"Failed to get latest prediction from MongoDB: {e}")
            return None
    
    async def save_cashflow_analysis(self, analysis: CashflowAnalysis) -> str:
        """
        保存现金流分析到MongoDB
        
        Args:
            analysis: 现金流分析
            
        Returns:
            分析ID
        """
        try:
            # 将Pydantic模型转换为字典
            analysis_dict = analysis.dict()
            
            # 检查是否已存在相同时间范围和商户的分析
            existing = await self.analysis_collection.find_one({
                "merchant_id": analysis.merchant_id,
                "time_range.start_date": analysis.time_range.start_date,
                "time_range.end_date": analysis.time_range.end_date
            })
            
            if existing:
                # 更新已存在的分析
                await self.analysis_collection.update_one(
                    {"_id": existing["_id"]},
                    {"$set": {
                        "metrics": analysis_dict["metrics"],
                        "prediction": analysis_dict["prediction"],
                        "created_at": analysis_dict["created_at"]
                    }}
                )
                self.logger.info(f"Updated cashflow analysis for merchant {analysis.merchant_id}")
                return str(existing["_id"])
            else:
                # 插入新分析
                result = await self.analysis_collection.insert_one(analysis_dict)
                self.logger.info(f"Saved cashflow analysis for merchant {analysis.merchant_id}")
                return str(result.inserted_id)
        except Exception as e:
            self.logger.error(f"Failed to save cashflow analysis to MongoDB: {e}")
            raise
    
    async def get_cashflow_analysis(self, merchant_id: str, time_range: TimeRange) -> Optional[CashflowAnalysis]:
        """
        获取现金流分析
        
        Args:
            merchant_id: 商户ID
            time_range: 时间范围
            
        Returns:
            现金流分析，如果不存在则返回None
        """
        try:
            # 查询条件
            query = {
                "merchant_id": merchant_id,
                "time_range.start_date": time_range.start_date,
                "time_range.end_date": time_range.end_date
            }
            
            # 查询数据
            result = await self.analysis_collection.find_one(query)
            
            if result:
                # 移除MongoDB特定字段
                if "_id" in result:
                    result["id"] = str(result.pop("_id"))
                
                return CashflowAnalysis(**result)
            
            return None
        except Exception as e:
            self.logger.error(f"Failed to get cashflow analysis from MongoDB: {e}")
            return None
    
    async def get_historical_predictions(self, merchant_id: str, limit: int = 10) -> List[PredictionResult]:
        """
        获取历史预测结果
        
        Args:
            merchant_id: 商户ID
            limit: 返回结果数量限制
            
        Returns:
            预测结果列表
        """
        try:
            # 查询条件
            query = {"merchant_id": merchant_id}
            
            # 按创建时间倒序排序
            cursor = self.prediction_collection.find(
                query,
                sort=[("created_at", -1)]
            ).limit(limit)
            
            results = []
            async for doc in cursor:
                # 移除MongoDB特定字段
                if "_id" in doc:
                    doc["id"] = str(doc.pop("_id"))
                
                results.append(PredictionResult(**doc))
            
            return results
        except Exception as e:
            self.logger.error(f"Failed to get historical predictions from MongoDB: {e}")
            return []
    
    async def delete_old_predictions(self, merchant_id: str, keep_count: int = 10) -> int:
        """
        删除旧的预测结果，只保留最新的几条
        
        Args:
            merchant_id: 商户ID
            keep_count: 保留的最新预测数量
            
        Returns:
            删除的文档数量
        """
        try:
            # 获取需要保留的预测ID
            cursor = self.prediction_collection.find(
                {"merchant_id": merchant_id},
                sort=[("created_at", -1)]
            ).limit(keep_count)
            
            keep_ids = []
            async for doc in cursor:
                keep_ids.append(doc["_id"])
            
            if not keep_ids:
                return 0
            
            # 删除不在保留列表中的预测
            result = await self.prediction_collection.delete_many({
                "merchant_id": merchant_id,
                "_id": {"$nin": keep_ids}
            })
            
            deleted_count = result.deleted_count
            self.logger.info(f"Deleted {deleted_count} old predictions for merchant {merchant_id}")
            
            return deleted_count
        except Exception as e:
            self.logger.error(f"Failed to delete old predictions from MongoDB: {e}")
            return 0 