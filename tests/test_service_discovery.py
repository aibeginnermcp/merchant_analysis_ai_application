"""服务发现测试模块"""
import pytest
from unittest.mock import Mock, patch
from services.api_gateway.core.service_discovery import ServiceDiscovery

pytestmark = pytest.mark.asyncio

@pytest.fixture
def mock_consul():
    """模拟Consul客户端"""
    with patch("consul.Consul") as mock:
        yield mock.return_value

async def test_get_service_url_success(mock_consul):
    """测试成功获取服务地址"""
    # 准备测试数据
    service_name = "test-service"
    service_nodes = [
        {
            "ServiceID": "test-1",
            "ServiceAddress": "localhost",
            "ServicePort": 8001
        },
        {
            "ServiceID": "test-2",
            "ServiceAddress": "localhost",
            "ServicePort": 8002
        }
    ]
    
    # 模拟Consul响应
    mock_consul.catalog.service.return_value = (None, service_nodes)
    mock_consul.health.checks.return_value = [{"Status": "passing"}]
    
    # 创建服务发现实例
    discovery = ServiceDiscovery()
    
    # 获取服务地址
    url = await discovery.get_service_url(service_name)
    
    # 验证结果
    assert url is not None
    assert url.startswith("http://localhost:800")
    
    # 验证Consul调用
    mock_consul.catalog.service.assert_called_once_with(service_name)
    mock_consul.health.checks.assert_called()

async def test_get_service_url_no_nodes(mock_consul):
    """测试无可用节点时获取服务地址"""
    # 准备测试数据
    service_name = "test-service"
    
    # 模拟Consul响应
    mock_consul.catalog.service.return_value = (None, [])
    
    # 创建服务发现实例
    discovery = ServiceDiscovery()
    
    # 获取服务地址
    url = await discovery.get_service_url(service_name)
    
    # 验证结果
    assert url is None
    
    # 验证Consul调用
    mock_consul.catalog.service.assert_called_once_with(service_name)
    mock_consul.health.checks.assert_not_called()

async def test_get_service_url_unhealthy_nodes(mock_consul):
    """测试所有节点不健康时获取服务地址"""
    # 准备测试数据
    service_name = "test-service"
    service_nodes = [
        {
            "ServiceID": "test-1",
            "ServiceAddress": "localhost",
            "ServicePort": 8001
        }
    ]
    
    # 模拟Consul响应
    mock_consul.catalog.service.return_value = (None, service_nodes)
    mock_consul.health.checks.return_value = [{"Status": "critical"}]
    
    # 创建服务发现实例
    discovery = ServiceDiscovery()
    
    # 获取服务地址
    url = await discovery.get_service_url(service_name)
    
    # 验证结果
    assert url is None
    
    # 验证Consul调用
    mock_consul.catalog.service.assert_called_once_with(service_name)
    mock_consul.health.checks.assert_called()

async def test_register_service_success(mock_consul):
    """测试成功注册服务"""
    # 准备测试数据
    service_name = "test-service"
    service_id = "test-1"
    address = "localhost"
    port = 8001
    tags = ["v1", "test"]
    
    # 模拟Consul响应
    mock_consul.agent.service.register.return_value = None
    
    # 创建服务发现实例
    discovery = ServiceDiscovery()
    
    # 注册服务
    success = await discovery.register_service(
        service_name=service_name,
        service_id=service_id,
        address=address,
        port=port,
        tags=tags
    )
    
    # 验证结果
    assert success is True
    
    # 验证Consul调用
    mock_consul.agent.service.register.assert_called_once_with(
        name=service_name,
        service_id=service_id,
        address=address,
        port=port,
        tags=tags,
        check={
            "http": f"http://{address}:{port}/health",
            "interval": "10s",
            "timeout": "5s"
        }
    )

async def test_register_service_failure(mock_consul):
    """测试注册服务失败"""
    # 准备测试数据
    service_name = "test-service"
    service_id = "test-1"
    address = "localhost"
    port = 8001
    
    # 模拟Consul响应
    mock_consul.agent.service.register.side_effect = Exception("Registration failed")
    
    # 创建服务发现实例
    discovery = ServiceDiscovery()
    
    # 注册服务
    success = await discovery.register_service(
        service_name=service_name,
        service_id=service_id,
        address=address,
        port=port
    )
    
    # 验证结果
    assert success is False
    
    # 验证Consul调用
    mock_consul.agent.service.register.assert_called_once()

async def test_deregister_service_success(mock_consul):
    """测试成功注销服务"""
    # 准备测试数据
    service_id = "test-1"
    
    # 模拟Consul响应
    mock_consul.agent.service.deregister.return_value = None
    
    # 创建服务发现实例
    discovery = ServiceDiscovery()
    
    # 注销服务
    success = await discovery.deregister_service(service_id)
    
    # 验证结果
    assert success is True
    
    # 验证Consul调用
    mock_consul.agent.service.deregister.assert_called_once_with(service_id)

async def test_deregister_service_failure(mock_consul):
    """测试注销服务失败"""
    # 准备测试数据
    service_id = "test-1"
    
    # 模拟Consul响应
    mock_consul.agent.service.deregister.side_effect = Exception("Deregistration failed")
    
    # 创建服务发现实例
    discovery = ServiceDiscovery()
    
    # 注销服务
    success = await discovery.deregister_service(service_id)
    
    # 验证结果
    assert success is False
    
    # 验证Consul调用
    mock_consul.agent.service.deregister.assert_called_once_with(service_id) 