"""
成本穿透分析引擎主程序
"""

import os
import pandas as pd
from datetime import datetime
from analyzers.cost_analysis_report import CostAnalysisReportGenerator
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import uvicorn
import logging
from .api import router as cost_analysis_router

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="成本穿透分析服务",
    description="提供商户成本结构分析、趋势分析、预警和优化建议等功能",
    version="1.0.0"
)

# 配置CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 在生产环境中应该设置具体的允许源
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 全局异常处理
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"全局异常: {str(exc)}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "message": "服务器内部错误",
            "timestamp": datetime.now().isoformat(),
            "path": str(request.url)
        }
    )

# 注册路由
app.include_router(cost_analysis_router)

# 健康检查端点
@app.get("/health")
async def health_check():
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}

# 服务信息端点
@app.get("/")
async def root():
    return {
        "service": "成本穿透分析服务",
        "version": "1.0.0",
        "status": "running",
        "timestamp": datetime.now().isoformat()
    }

def create_output_dirs():
    """创建输出目录"""
    dirs = ['output', 'reports']
    for dir_name in dirs:
        if not os.path.exists(dir_name):
            os.makedirs(dir_name)

def load_cost_data(file_path: str) -> pd.DataFrame:
    """
    加载成本数据
    
    Args:
        file_path: 成本数据文件路径
        
    Returns:
        pd.DataFrame: 成本数据
    """
    return pd.read_csv(file_path)

def main():
    """主程序入口"""
    print("=== 成本穿透分析引擎 ===")
    
    # 创建输出目录
    create_output_dirs()
    
    # 加载成本数据
    cost_data_path = "../生成行业模拟数据/output/cost_cost_data_20250508_110919.csv"  # 使用最新生成的成本数据
    cost_data = load_cost_data(cost_data_path)
    
    # 初始化报告生成器
    report_generator = CostAnalysisReportGenerator()
    
    # 生成分析报告
    report_generator.generate_report(cost_data, 'reports')
    
    print("\n成本穿透分析完成！")

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    ) 