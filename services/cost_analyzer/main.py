"""成本分析服务主入口"""
from fastapi import FastAPI, HTTPException
from datetime import datetime
import motor.motor_asyncio
from typing import Dict, Any, List

from .analyzer import CostAnalyzer
from .models import CostAnalysisResult, CostOptimizationPlan
from shared.base_service import BaseAnalysisService
from shared.exceptions import ServiceType, AnalysisException
from shared.models.merchant import AnalysisRequest, AnalysisResponse

class CostAnalysisService(BaseAnalysisService):
    """成本分析服务"""
    
    def __init__(self):
        super().__init__(ServiceType.COST_ANALYSIS)
        self.analyzer = CostAnalyzer()
        self.client = motor.motor_asyncio.AsyncIOMotorClient("mongodb://mongodb:27017")
        self.db = self.client.merchant_analysis
        
    async def analyze(self, request: AnalysisRequest) -> AnalysisResponse:
        """执行成本分析"""
        try:
            # 获取历史数据
            historical_data = await self._get_historical_data(
                request.merchant_id,
                request.start_date,
                request.end_date
            )
            
            # 获取商户类型
            merchant_info = await self._get_merchant_info(request.merchant_id)
            merchant_type = merchant_info.get("type", "retail")
            
            # 执行成本分析
            analysis_result = self.analyzer.analyze_costs(
                request.merchant_id,
                merchant_type,
                historical_data
            )
            
            # 生成优化方案
            optimization_plans = self.analyzer.generate_optimization_plan(
                analysis_result.cost_breakdown,
                merchant_type
            )
            
            # 合并结果
            response_data = {
                **analysis_result.dict(),
                "optimization_plans": [plan.dict() for plan in optimization_plans]
            }
            
            return AnalysisResponse(
                request_id=request.request_id,
                status="success",
                data=response_data,
                error=None
            )
            
        except Exception as e:
            raise AnalysisException(
                message=f"成本分析失败: {str(e)}",
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
    
    async def _get_merchant_info(self, merchant_id: str) -> Dict[str, Any]:
        """获取商户信息"""
        info = await self.db.merchants.find_one(
            {"merchant_id": merchant_id}
        )
        
        if not info:
            raise HTTPException(
                status_code=404,
                detail=f"未找到商户 {merchant_id} 的基本信息"
            )
            
        return info
    
    async def health_check(self) -> Dict[str, Any]:
        """健康检查"""
        try:
            # 检查数据库连接
            await self.db.command("ping")
            return {
                "status": "healthy",
                "database": "connected",
                "analyzer": "initialized",
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
    title="成本分析服务",
    description="分析商户成本结构并提供优化建议",
    version="1.0.0"
)

# 创建服务实例
service = CostAnalysisService()

@app.post("/analyze")
async def analyze_costs(request: AnalysisRequest) -> AnalysisResponse:
    """分析成本结构"""
    return await service.handle_request(request)

@app.get("/health")
async def health_check():
    """健康检查"""
    return await service.health_check()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8003) 