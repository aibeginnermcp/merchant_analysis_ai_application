"""
Gateway服务管理器测试模块
"""
import pytest
from datetime import datetime
from fastapi import FastAPI
from src.gateway.services import ServiceManager

@pytest.mark.asyncio
async def test_service_manager_init():
    """测试服务管理器初始化"""
    # 创建服务管理器
    manager = ServiceManager()
    assert manager._app is None
    
    # 初始化应用
    app = FastAPI()
    await manager.init_app(app)
    assert manager._app is app

@pytest.mark.asyncio
async def test_service_manager_startup(
    mock_db,
    mock_redis,
    mock_queue,
    mock_discovery
):
    """测试服务启动
    
    Args:
        mock_db: Mock数据库连接
        mock_redis: Mock Redis连接
        mock_queue: Mock消息队列连接
        mock_discovery: Mock服务发现连接
    """
    # 创建服务管理器
    manager = ServiceManager()
    app = FastAPI()
    await manager.init_app(app)
    
    # 启动服务
    await manager.startup()
    
    # 验证服务注册
    mock_discovery.register_service.assert_called_once()
    args = mock_discovery.register_service.call_args[1]
    assert args["service_name"] == "merchant-gateway"
    assert "gateway" in args["tags"]

@pytest.mark.asyncio
async def test_service_manager_shutdown(
    mock_db,
    mock_redis,
    mock_queue,
    mock_discovery
):
    """测试服务关闭
    
    Args:
        mock_db: Mock数据库连接
        mock_redis: Mock Redis连接
        mock_queue: Mock消息队列连接
        mock_discovery: Mock服务发现连接
    """
    # 创建服务管理器
    manager = ServiceManager()
    app = FastAPI()
    await manager.init_app(app)
    
    # 启动服务
    await manager.startup()
    
    # 关闭服务
    await manager.shutdown()
    
    # 验证服务注销
    mock_discovery.deregister_service.assert_called_once()

@pytest.mark.asyncio
async def test_service_status(
    mock_db,
    mock_redis,
    mock_queue,
    mock_discovery
):
    """测试服务状态检查
    
    Args:
        mock_db: Mock数据库连接
        mock_redis: Mock Redis连接
        mock_queue: Mock消息队列连接
        mock_discovery: Mock服务发现连接
    """
    # 创建服务管理器
    manager = ServiceManager()
    app = FastAPI()
    await manager.init_app(app)
    
    # 启动服务
    await manager.startup()
    
    # 检查服务状态
    status = await manager.get_service_status()
    assert status["database"] is True
    assert status["cache"] is True
    assert status["queue"] is True
    assert status["discovery"] is True
    
    # 关闭服务
    await manager.shutdown() 