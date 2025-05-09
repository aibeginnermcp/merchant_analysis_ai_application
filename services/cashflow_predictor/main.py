"""现金流预测服务主入口"""
from fastapi import FastAPI, HTTPException
from datetime import datetime, timedelta
import motor.motor_asyncio
from typing import Dict, Any, List

from .predictor import CashFlowPredictor
from .models import CashFlowFeatures, TrainingData
from shared.base_service import BaseAnalysisService
from shared.exceptions import ServiceType, AnalysisException
from shared.models.merchant import AnalysisRequest, AnalysisResponse

class CashFlowService(BaseAnalysisService):
    """现金流预测服务"""
    
    def __init__(self):
        super().__init__(ServiceType.CASH_FLOW)
        self.predictor = CashFlowPredictor()
        self.client = motor.motor_asyncio.AsyncIOMotorClient("mongodb://mongodb:27017")
        self.db = self.client.merchant_analysis
        
    async def analyze(self, request: AnalysisRequest) -> AnalysisResponse:
        """执行现金流分析"""
        try:
            # 获取历史数据
            historical_data = await self._get_historical_data(
                request.merchant_id,
                request.start_date,
                request.end_date
            )
            
            # 准备特征数据
            features = self._prepare_features(historical_data)
            
            # 执行预测
            predictions = self.predictor.predict(features)
            
            # 分析结果
            analysis = self.predictor.analyze_cash_flow(
                request.merchant_id,
                predictions
            )
            
            return AnalysisResponse(
                request_id=request.merchant_id,
                status="success",
                data=analysis.dict(),
                error=None
            )
            
        except Exception as e:
            raise AnalysisException(
                message=f"现金流分析失败: {str(e)}",
                service=self.service_type
            )
    
    async def _get_historical_data(
        self,
        merchant_id: str,
        start_date: datetime,
        end_date: datetime
    ) -> Dict[str, Any]:
        """获取历史数据"""
        data = await self.db.simulated_data.find_one(
            {"merchant_id": merchant_id}
        )
        
        if not data:
            raise HTTPException(
                status_code=404,
                detail=f"未找到商户 {merchant_id} 的历史数据"
            )
            
        return data["data"]
    
    def _prepare_features(self, historical_data: Dict[str, Any]) -> List[CashFlowFeatures]:
        """准备特征数据"""
        features = []
        
        for i in range(len(historical_data["transactions"])):
            transaction = historical_data["transactions"][i]
            cost = historical_data["costs"][i]
            financial = historical_data["financials"][i]
            
            date = datetime.fromisoformat(transaction["date"])
            
            feature = CashFlowFeatures(
                date=date,
                day_of_week=date.weekday(),
                is_weekend=date.weekday() >= 5,
                is_holiday=self._is_holiday(date),
                month=date.month,
                quarter=(date.month - 1) // 3 + 1,
                
                revenue=transaction["revenue"],
                transaction_count=transaction["transaction_count"],
                average_transaction=transaction["average_transaction_value"],
                
                total_cost=sum([
                    cost["raw_material_cost"],
                    cost["labor_cost"],
                    cost["utility_cost"],
                    cost["rent_cost"],
                    cost["other_cost"]
                ]),
                raw_material_cost=cost["raw_material_cost"],
                labor_cost=cost["labor_cost"],
                utility_cost=cost["utility_cost"],
                rent_cost=cost["rent_cost"],
                
                accounts_receivable=financial["accounts_receivable"],
                accounts_payable=financial["accounts_payable"],
                inventory_value=financial["inventory_value"]
            )
            
            features.append(feature)
            
        return features
    
    def _is_holiday(self, date: datetime) -> bool:
        """判断是否节假日（简化版）"""
        # 这里可以集成外部节假日API或使用预定义的节假日列表
        return False
    
    async def health_check(self) -> Dict[str, Any]:
        """健康检查"""
        try:
            # 检查数据库连接
            await self.db.command("ping")
            return {
                "status": "healthy",
                "database": "connected",
                "model_loaded": self.predictor.model is not None,
                "timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            return {
                "status": "unhealthy",
                "database": "disconnected",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }

# 创建FastAPI应用
app = FastAPI(
    title="现金流预测服务",
    description="基于历史数据预测商户未来现金流状况",
    version="1.0.0"
)

# 创建服务实例
service = CashFlowService()

@app.post("/predict")
async def predict_cash_flow(request: AnalysisRequest) -> AnalysisResponse:
    """预测现金流"""
    return await service.handle_request(request)

@app.post("/train")
async def train_model(training_data: TrainingData):
    """训练模型"""
    try:
        validation_score = service.predictor.train(training_data)
        return {
            "status": "success",
            "validation_score": validation_score,
            "message": "模型训练完成"
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"模型训练失败: {str(e)}"
        )

@app.get("/health")
async def health_check():
    """健康检查"""
    return await service.health_check()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8002) 