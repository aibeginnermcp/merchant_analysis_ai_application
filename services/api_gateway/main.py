"""
API网关服务的主入口，整合所有微服务
"""
import os
import logging
import sys
import time
import uuid
import httpx
import json
from fastapi import FastAPI, Request, Response, HTTPException, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi.openapi.utils import get_openapi
from fastapi.openapi.docs import get_swagger_ui_html
from jose import JWTError, jwt
from datetime import datetime, timedelta
import prometheus_client
from prometheus_client import Counter, Histogram
from typing import Dict, List, Optional, Union, Any

# JWT相关配置
SECRET_KEY = os.environ.get("JWT_SECRET", "your-secret-key")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 1440  # 24小时

# 服务地址配置
SERVICE_ENDPOINTS = {
    "data_simulator": os.environ.get("DATA_SIMULATOR_URL", "http://data_simulator:8000"),
    "cashflow_predictor": os.environ.get("CASHFLOW_PREDICTOR_URL", "http://cashflow_predictor:8002"),
    "cost_analyzer": os.environ.get("COST_ANALYZER_URL", "http://cost_analyzer:8001"),
    "compliance_checker": os.environ.get("COMPLIANCE_CHECKER_URL", "http://compliance_checker:8003")
}

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)]
)

logger = logging.getLogger("api_gateway")

# 创建FastAPI应用
app = FastAPI(
    title="商户智能分析平台API网关",
    description="整合数据模拟、现金流预测、成本分析和合规检查服务的API网关",
    version="1.0.0"
)

# 跨域配置
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 生产环境应该限制来源
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 监控指标
REQUEST_COUNT = Counter(
    "api_gateway_request_count", 
    "Number of requests received",
    ["method", "endpoint", "status_code"]
)
REQUEST_LATENCY = Histogram(
    "api_gateway_request_latency_seconds", 
    "Request latency in seconds",
    ["method", "endpoint"]
)

# OAuth2 scheme
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# 模拟用户数据库
# 在实际生产环境中，应该使用真实的数据库
USERS_DB = {
    "admin": {
        "username": "admin",
        "full_name": "Administrator",
        "email": "admin@example.com",
        "hashed_password": "$2b$12$IQfLKlbVcSYX1hiYHYVRwu7YrOcK1yPOl6O5XWI7.6VY1LlXaG9gO",  # "password"
        "disabled": False,
        "role": "admin"
    },
    "user": {
        "username": "user",
        "full_name": "Normal User",
        "email": "user@example.com",
        "hashed_password": "$2b$12$IQfLKlbVcSYX1hiYHYVRwu7YrOcK1yPOl6O5XWI7.6VY1LlXaG9gO",  # "password"
        "disabled": False,
        "role": "user"
    }
}

class User:
    def __init__(self, username: str, email: str, full_name: str, disabled: bool, role: str):
        self.username = username
        self.email = email
        self.full_name = full_name
        self.disabled = disabled
        self.role = role

def verify_password(plain_password: str, hashed_password: str) -> bool:
    # 在实际生产环境中，应该使用密码哈希比较
    # 这里简化处理，直接比较
    return hashed_password == "$2b$12$IQfLKlbVcSYX1hiYHYVRwu7YrOcK1yPOl6O5XWI7.6VY1LlXaG9gO"

def get_user(username: str) -> Optional[User]:
    if username not in USERS_DB:
        return None
    user_dict = USERS_DB[username]
    return User(
        username=user_dict["username"],
        email=user_dict["email"],
        full_name=user_dict["full_name"],
        disabled=user_dict["disabled"],
        role=user_dict["role"]
    )

def authenticate_user(username: str, password: str) -> Optional[User]:
    user = get_user(username)
    if not user:
        return None
    if not verify_password(password, USERS_DB[username]["hashed_password"]):
        return None
    return user

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

async def get_current_user(token: str = Depends(oauth2_scheme)) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    user = get_user(username)
    if user is None:
        raise credentials_exception
    return user

async def get_current_active_user(current_user: User = Depends(get_current_user)) -> User:
    if current_user.disabled:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user

@app.middleware("http")
async def metrics_middleware(request: Request, call_next):
    """收集请求指标的中间件"""
    start_time = time.time()
    
    # 为请求添加追踪ID
    request_id = str(uuid.uuid4())
    request.state.request_id = request_id
    
    try:
        response = await call_next(request)
        status_code = response.status_code
        REQUEST_COUNT.labels(
            method=request.method, 
            endpoint=request.url.path, 
            status_code=status_code
        ).inc()
        
        # 添加请求ID到响应头
        response.headers["X-Request-ID"] = request_id
        
        return response
    except Exception as e:
        logger.exception(f"Request failed: {e}")
        status_code = 500
        return JSONResponse(
            status_code=status_code,
            content={"detail": "Internal server error", "request_id": request_id}
        )
    finally:
        duration = time.time() - start_time
        REQUEST_LATENCY.labels(
            method=request.method, 
            endpoint=request.url.path
        ).observe(duration)

@app.get("/health")
async def health_check():
    """健康检查接口"""
    # 检查所有后端服务的健康状态
    results = {}
    async with httpx.AsyncClient() as client:
        for service_name, url in SERVICE_ENDPOINTS.items():
            try:
                response = await client.get(f"{url}/health", timeout=5.0)
                results[service_name] = "healthy" if response.status_code == 200 else "unhealthy"
            except Exception:
                results[service_name] = "unavailable"
    
    overall_status = "healthy" if all(status == "healthy" for status in results.values()) else "degraded"
    return {
        "status": overall_status,
        "services": results
    }

@app.get("/metrics")
async def metrics():
    """导出Prometheus监控指标"""
    return prometheus_client.generate_latest()

@app.post("/api/v1/token", response_model=dict)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    """获取JWT访问令牌"""
    user = authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username, "role": user.role}, 
        expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

@app.get("/api/v1/users/me", response_model=dict)
async def read_users_me(current_user: User = Depends(get_current_active_user)):
    """获取当前用户信息"""
    return {
        "username": current_user.username,
        "email": current_user.email,
        "full_name": current_user.full_name,
        "role": current_user.role
    }

# 代理目标服务的请求
@app.api_route("/api/v1/data-simulator/{path:path}", methods=["GET", "POST", "PUT", "DELETE"])
async def proxy_data_simulator(path: str, request: Request, current_user: User = Depends(get_current_active_user)):
    """代理到数据模拟服务"""
    return await proxy_request(request, "data_simulator", path)

@app.api_route("/api/v1/cashflow/{path:path}", methods=["GET", "POST", "PUT", "DELETE"])
async def proxy_cashflow_predictor(path: str, request: Request, current_user: User = Depends(get_current_active_user)):
    """代理到现金流预测服务"""
    return await proxy_request(request, "cashflow_predictor", path)

@app.api_route("/api/v1/cost/{path:path}", methods=["GET", "POST", "PUT", "DELETE"])
async def proxy_cost_analyzer(path: str, request: Request, current_user: User = Depends(get_current_active_user)):
    """代理到成本分析服务"""
    return await proxy_request(request, "cost_analyzer", path)

@app.api_route("/api/v1/compliance/{path:path}", methods=["GET", "POST", "PUT", "DELETE"])
async def proxy_compliance_checker(path: str, request: Request, current_user: User = Depends(get_current_active_user)):
    """代理到合规检查服务"""
    return await proxy_request(request, "compliance_checker", path)

# 整合分析接口
@app.post("/api/v1/integrated-analysis", response_model=dict)
async def integrated_analysis(request: Request, current_user: User = Depends(get_current_active_user)):
    """执行整合分析，调用所有服务"""
    try:
        # 解析请求体
        data = await request.json()
        merchant_id = data.get("merchant_id")
        time_range = data.get("time_range")
        
        if not merchant_id or not time_range:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="merchant_id and time_range are required"
            )
        
        # 并行调用各服务
        results = {}
        async with httpx.AsyncClient() as client:
            # 现金流预测
            if "cashflow" in data.get("analysis_types", ["cashflow"]):
                cashflow_data = {
                    "merchant_id": merchant_id,
                    "time_range": time_range,
                    "config": data.get("cashflow_config")
                }
                try:
                    cashflow_response = await client.post(
                        f"{SERVICE_ENDPOINTS['cashflow_predictor']}/api/v1/predict",
                        json=cashflow_data,
                        timeout=60.0
                    )
                    if cashflow_response.status_code == 200:
                        results["cashflow"] = cashflow_response.json()
                    else:
                        results["cashflow"] = {"error": f"Failed with status {cashflow_response.status_code}"}
                except Exception as e:
                    results["cashflow"] = {"error": str(e)}
            
            # 成本分析
            if "cost" in data.get("analysis_types", ["cost"]):
                cost_data = {
                    "merchant_id": merchant_id,
                    "time_range": time_range,
                    "include_trend": data.get("include_cost_trend", True),
                    "include_suggestions": data.get("include_cost_suggestions", True)
                }
                try:
                    cost_response = await client.post(
                        f"{SERVICE_ENDPOINTS['cost_analyzer']}/api/v1/analyze",
                        json=cost_data,
                        timeout=60.0
                    )
                    if cost_response.status_code == 200:
                        results["cost"] = cost_response.json()
                    else:
                        results["cost"] = {"error": f"Failed with status {cost_response.status_code}"}
                except Exception as e:
                    results["cost"] = {"error": str(e)}
            
            # 合规检查
            if "compliance" in data.get("analysis_types", ["compliance"]):
                compliance_data = {
                    "merchant_id": merchant_id,
                    "time_range": time_range,
                    "check_types": data.get("compliance_check_types"),
                    "include_documents": data.get("include_documents", True)
                }
                try:
                    compliance_response = await client.post(
                        f"{SERVICE_ENDPOINTS['compliance_checker']}/api/v1/check",
                        json=compliance_data,
                        timeout=60.0
                    )
                    if compliance_response.status_code == 200:
                        results["compliance"] = compliance_response.json()
                    else:
                        results["compliance"] = {"error": f"Failed with status {compliance_response.status_code}"}
                except Exception as e:
                    results["compliance"] = {"error": str(e)}
        
        # 创建集成响应
        integrated_result = {
            "request_id": str(uuid.uuid4()),
            "merchant_id": merchant_id,
            "time_range": time_range,
            "results": results,
            "timestamp": datetime.now().isoformat()
        }
        
        return integrated_result
    except Exception as e:
        logger.exception(f"Integrated analysis failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Integrated analysis failed: {str(e)}"
        )

async def proxy_request(request: Request, service_name: str, path: str):
    """
    代理请求到目标服务
    
    Args:
        request: 原始请求
        service_name: 目标服务名称
        path: 请求路径
        
    Returns:
        代理响应
    """
    if service_name not in SERVICE_ENDPOINTS:
        raise HTTPException(status_code=404, detail=f"Service {service_name} not found")
    
    target_url = f"{SERVICE_ENDPOINTS[service_name]}/api/v1/{path}"
    
    # 获取请求内容
    body = await request.body()
    headers = dict(request.headers)
    
    # 移除Host头，避免代理问题
    if "host" in headers:
        del headers["host"]
    
    # 添加追踪ID
    headers["X-Request-ID"] = str(uuid.uuid4())
    
    # 转发请求
    async with httpx.AsyncClient() as client:
        try:
            response = await client.request(
                method=request.method,
                url=target_url,
                headers=headers,
                content=body,
                params=request.query_params,
                timeout=60.0
            )
            
            # 构建响应
            return Response(
                content=response.content,
                status_code=response.status_code,
                headers=dict(response.headers),
                media_type=response.headers.get("content-type")
            )
        except httpx.RequestError as e:
            logger.error(f"Request to {service_name} failed: {e}")
            raise HTTPException(status_code=503, detail=f"Service {service_name} unavailable")

def start():
    """启动应用"""
    import uvicorn
    uvicorn.run(
        "services.api_gateway.main:app",
        host=os.environ.get("HOST", "0.0.0.0"),
        port=int(os.environ.get("PORT", 8080)),
        reload=os.environ.get("DEBUG", "false").lower() == "true",
        log_level="info"
    )

if __name__ == "__main__":
    start() 